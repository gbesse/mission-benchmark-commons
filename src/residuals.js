export function residualWindows(report, windowSec = 60) {
  const fail = () => {
    throw new TypeError('Résidus invalides / Invalid residuals / Residuos inválidos');
  };
  const samples = report?.result?.samples;
  if (
    !Array.isArray(samples) ||
    samples.length > 100000 ||
    !Number.isFinite(windowSec) ||
    windowSec <= 0
  )
    fail();
  const windows = new Map();
  let previous = -Infinity;
  const vector = (x) => Array.isArray(x) && x.length === 3 && x.every(Number.isFinite);
  const distance = (a, b) => Math.hypot(...a.map((v, i) => v - b[i]));
  for (const s of samples) {
    if (
      !Number.isFinite(s.timeSec) ||
      s.timeSec < 0 ||
      s.timeSec <= previous ||
      !vector(s.basiliskM) ||
      !vector(s.orekitM) ||
      !vector(s.referenceM)
    )
      fail();
    previous = s.timeSec;
    const key = Math.floor(s.timeSec / windowSec),
      agreement = distance(s.basiliskM, s.orekitM),
      residual = distance(s.orekitM, s.referenceM);
    if (!Number.isFinite(agreement) || !Number.isFinite(residual)) fail();
    if (!windows.has(key))
      windows.set(key, {
        startSec: key * windowSec,
        endSec: (key + 1) * windowSec,
        samples: 0,
        engineMaxM: -1,
        referenceMaxM: -1,
        engineSquares: 0,
        referenceSquares: 0,
      });
    const w = windows.get(key);
    w.samples++;
    if (agreement > w.engineMaxM) {
      w.engineMaxM = agreement;
      w.engineWorstTimeSec = s.timeSec;
    }
    if (residual > w.referenceMaxM) {
      w.referenceMaxM = residual;
      w.referenceWorstTimeSec = s.timeSec;
    }
    w.engineSquares += agreement * agreement;
    w.referenceSquares += residual * residual;
    if (!Number.isFinite(w.engineSquares) || !Number.isFinite(w.referenceSquares)) fail();
  }
  return {
    windows: [...windows.values()].map(({ engineSquares, referenceSquares, ...w }) => ({
      ...w,
      engineRmsM: Math.sqrt(engineSquares / w.samples),
      referenceRmsM: Math.sqrt(referenceSquares / w.samples),
    })),
    engineExecuted: false,
    frameAndUnits: 'caller-must-supply-common-frame-and-metres',
  };
}

export function residualBudget(
  report,
  { windowSec = 60, engineToleranceM, referenceToleranceM } = {},
) {
  if (
    !Number.isFinite(engineToleranceM) ||
    engineToleranceM < 0 ||
    !Number.isFinite(referenceToleranceM) ||
    referenceToleranceM < 0
  )
    throw new TypeError('Tolérances invalides / Invalid tolerances / Tolerancias inválidas');
  const result = residualWindows(report, windowSec);
  return {
    windows: result.windows.map((w) => ({
      ...w,
      engineAgreementWithinTolerance: w.engineMaxM <= engineToleranceM,
      referenceWithinTolerance: w.referenceMaxM <= referenceToleranceM,
    })),
    engineToleranceM,
    referenceToleranceM,
    engineExecuted: false,
    referenceTruthIndependentlyValidated: false,
  };
}
