import test from 'node:test';
import assert from 'node:assert/strict';
import { residualBudget, replay } from '../src/index.js';
test('agreement of engines does not pass independent reference tolerance', () => {
  const report = {
    result: {
      samples: [{ timeSec: 0, basiliskM: [0, 0, 0], orekitM: [0, 0, 0], referenceM: [100, 0, 0] }],
    },
  };
  const x = residualBudget(report, { engineToleranceM: 1, referenceToleranceM: 10 });
  assert.equal(x.windows[0].engineAgreementWithinTolerance, true);
  assert.equal(x.windows[0].referenceWithinTolerance, false);
});
test('actual recorded sample replay classified without new engine execution', async () => {
  const x = residualBudget(await replay(), { engineToleranceM: 100, referenceToleranceM: 100 });
  assert.ok(x.windows.length > 0);
  assert.equal(x.engineExecuted, false);
});
