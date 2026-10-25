import test from "node:test";
import assert from "node:assert/strict";
import { compareRateGv, analysisTrialLabel } from "../../../webapp/js/views/gv_presentation.js";

test("rate GV color comparison is based on the latest case GV, not the auto average", () => {
  assert.equal(compareRateGv(900, 700), "higher");
  assert.equal(compareRateGv(700, 700), "equal");
  assert.equal(compareRateGv(600, 700), "lower");
  assert.equal(compareRateGv(0, 700), "unset");
  assert.equal(compareRateGv(900, null), "unset");
});

test("analysis trials never reuse the manual GV step counter", () => {
  assert.equal(analysisTrialLabel({ numberOfTrials: 1695 }), "Analyseversuche: 1695");
  assert.equal(analysisTrialLabel({ numberOfTrials: null }), "Analyseversuche: —");
});
