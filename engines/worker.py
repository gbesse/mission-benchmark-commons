import contextlib

import hashlib

import importlib.metadata

import io

import json

import math

import os

from pathlib import Path

import subprocess

import sys

import tempfile

def sha(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def verified(runtime, name):
    manifest = json.loads((Path(__file__).parent / "datasets.json").read_text())
    data = next(x for x in manifest["datasets"] if x["id"] == name)
    path = runtime / data["file"]
    if path.stat().st_size != data["bytes"] or sha(path) != data["sha256"]:
        raise ValueError("DATASET_INTEGRITY")
    return path, data

def version(name):
    return importlib.metadata.version(name)

def satellite(runtime):
    from sgp4.api import Satrec
    path, data = verified(runtime, "iss-2026-10-10")
    lines = path.read_text().splitlines()
    sat = Satrec.twoline2rv(lines[1], lines[2])
    return sat, data

def benchmark(runtime, config):
    import numpy as np
    from Basilisk.utilities import SimulationBaseClass, simIncludeGravBody, macros
    from Basilisk.simulation import spacecraft
    step = config["stepSec"]
    if step not in [10, 30, 60, 120] or config["profile"] not in ["iss", "moon"]:
        raise ValueError("CONFIG")
    sample = 120
    duration = 10800 if config["profile"] == "iss" else 86400
    times = np.arange(0, duration + sample, sample)
    if config["profile"] == "iss":
        sat, data = satellite(runtime)
        def truth(t):
            error, r, v = sat.sgp4(sat.jdsatepoch, sat.jdsatepochF + t / 86400)
            if error: raise ValueError("SGP4")
            return np.array([*r, *v]) * 1000
        initial = truth(0)
        mu = 3.986004418e14
        epoch = {"julianDate": sat.jdsatepoch + sat.jdsatepochF, "frame": "TEME_FIXED_AXES"}
        sources = [data]
        reference = "SGP4_PERTURBED_REFERENCE"
    else:
        import spiceypy as spice
        kernel, data = verified(runtime, "de440s")
        leaps, leap_data = verified(runtime, "naif0012")
        spice.furnsh(str(kernel)); spice.furnsh(str(leaps))
        et = spice.str2et("2026-10-10T12:00:00")
        def truth(t):
            state, _ = spice.spkezr("MOON", et + t, "J2000", "NONE", "EARTH")
            return np.array(state) * 1000
        initial = truth(0)
        mu = 4.035032355e14  # Earth + Moon gravitational parameters, m^3/s^2.
        epoch = {"utc": "2026-10-10T12:00:00Z", "frame": "J2000"}
        sources = [data, leap_data]
        reference = "JPL_DE440S_GEOMETRIC_EARTH_MOON"
    truth_states = np.array([truth(float(t)) for t in times])
    sim = SimulationBaseClass.SimBaseClass()
    sim.CreateNewProcess("dynamics").addTask(sim.CreateNewTask("orbit", macros.sec2nano(step)))
    body = spacecraft.Spacecraft(); body.ModelTag = "commons"
    gravity = simIncludeGravBody.gravBodyFactory()
    earth = gravity.createEarth(); earth.isCentralBody = True; earth.mu = mu
    gravity.addBodiesTo(body)
    body.hub.r_CN_NInit = initial[:3].tolist(); body.hub.v_CN_NInit = initial[3:].tolist()
    sim.AddModelToTask("orbit", body)
    log = body.scStateOutMsg.recorder(macros.sec2nano(sample))
    sim.AddModelToTask("orbit", log)
    sim.InitializeSimulation(); sim.ConfigureStopTime(macros.sec2nano(duration)); sim.ExecuteSimulation()
    bsk = np.column_stack([log.times() / 1e9, log.r_BN_N, log.v_BN_N])
    if len(bsk) != len(times) or not np.array_equal(bsk[:, 0], times): raise ValueError("SAMPLE_ALIGNMENT")
    settings = json.loads((runtime / "runtime.json").read_text())
    cp = str(runtime / "classes") + os.pathsep + str(runtime / "jars" / "*")
    command = [settings["java"], "-cp", cp, "OrekitAdapter", *[str(float(x)) for x in initial], str(mu), str(duration), str(sample)]
    orekit = np.array(json.loads(subprocess.check_output(command, timeout=25, text=True)))
    difference = np.linalg.norm(bsk[:, 1:4] - orekit[:, 1:4], axis=1)
    residual = np.linalg.norm(orekit[:, 1:4] - truth_states[:, :3], axis=1)
    energy = .5 * np.sum(bsk[:, 4:] ** 2, axis=1) - mu / np.linalg.norm(bsk[:, 1:4], axis=1)
    drift = float(np.max(np.abs((energy - energy[0]) / energy[0])))
    maximum = float(difference.max())
    return {"engines": [{"name": "Basilisk", "version": version("bsk"), "method": "RK4"}, {"name": "Orekit", "version": "13.1.9", "method": "KeplerianPropagator"}, {"name": "SGP4" if config["profile"] == "iss" else "CSPICE / SpiceyPy", "version": version("sgp4" if config["profile"] == "iss" else "spiceypy"), "method": reference}], "sources": sources, "epoch": epoch, "muM3S2": mu, "durationSec": duration, "sampleSec": sample, "maxEngineDifferenceM": maximum, "maxReferenceResidualM": float(residual.max()), "relativeEnergyDrift": drift, "toleranceM": 100, "passed": maximum <= 100, "samples": [{"timeSec": float(t), "basiliskM": bsk[i, 1:4].tolist(), "orekitM": orekit[i, 1:4].tolist(), "referenceM": truth_states[i, :3].tolist(), "engineDifferenceM": float(difference[i]), "referenceResidualM": float(residual[i])} for i, t in enumerate(times)]}

def main():
    runtime = Path(sys.argv[1]).resolve()
    kind = sys.argv[2]
    config = json.loads(sys.stdin.read(4096))
    with contextlib.redirect_stdout(io.StringIO()):
        result = {"benchmark": benchmark}[kind](runtime, config)
    print(json.dumps(result, allow_nan=False, separators=(",", ":")))

if __name__ == "__main__":
    main()
