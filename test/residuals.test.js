import test from 'node:test';
import assert from 'node:assert/strict';
import { residualWindows, replay } from '../src/index.js';
test('agreement is not agreement with truth', () => {
  const report = {
    result: {
      samples: [{ timeSec: 0, basiliskM: [0, 0, 0], orekitM: [0, 0, 0], referenceM: [100, 0, 0] }],
    },
  };
  const x = residualWindows(report);
  assert.equal(x.windows[0].engineMaxM, 0);
  assert.equal(x.windows[0].referenceRmsM, 100);
  assert.equal(x.engineExecuted, false);
});
test('recorded engine samples produce independent residuals', async () => {
  const report = await replay();
  const x = residualWindows(report);
  assert.ok(x.windows.length > 0);
  assert.equal(
    x.windows.reduce((n, w) => n + w.samples, 0),
    report.result.samples.length,
  );
});
test('unsorted timestamps cannot silently cross windows', () =>
  assert.throws(() =>
    residualWindows({
      result: {
        samples: [
          { timeSec: 1, basiliskM: [0, 0, 0], orekitM: [0, 0, 0], referenceM: [0, 0, 0] },
          { timeSec: 1, basiliskM: [0, 0, 0], orekitM: [0, 0, 0], referenceM: [0, 0, 0] },
        ],
      },
    }),
  ));
