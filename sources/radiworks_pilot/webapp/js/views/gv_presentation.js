export function compareRateGv(rateGv, caseGv) {
  if (!Number.isFinite(rateGv) || rateGv <= 0 ||
      !Number.isFinite(caseGv) || caseGv <= 0) return "unset";
  if (rateGv === caseGv) return "equal";
  return rateGv > caseGv ? "higher" : "lower";
}

export function analysisTrialLabel(result) {
  const count = result?.numberOfTrials;
  return `Analyseversuche: ${Number.isInteger(count) && count >= 0 ? count : "—"}`;
}
