"""Summarize completed synthetic evidence without querying any running engine."""
import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def summarize(run: Path) -> dict:
    run = run.resolve()
    if not run.is_relative_to(ROOT / "runtime") or not run.name.startswith("rw-vector-probe-"):
        raise ValueError("Expected a bounded probe directory in this workspace")
    receipt = json.loads((run / "RESULT.json").read_text(encoding="utf-8"))
    if not receipt["success"] or not receipt["testProcessesStopped"]:
        raise ValueError("A failed or unfinished run cannot be accepted")
    cases = json.loads((run / "CONTROLS.json").read_text(encoding="utf-8"))
    if len(cases) != 3 or [case["port"] for case in cases] != [8111, 8112, 8113]:
        raise ValueError("Expected exactly three isolated cases")
    samples = [json.loads(line) for line in (run / "samples.jsonl").read_text(encoding="utf-8").splitlines()]
    minimum = samples[-1]["elapsedSeconds"] - samples[0]["elapsedSeconds"]
    full = receipt["full21MinuteRun"] and samples[-1]["elapsedSeconds"] >= 1260
    seeds = sorted(cases[0]["controls"])
    matrix = {seed: len({case["controls"][seed]["resultDigest"] for case in cases}) == 1 for seed in seeds}
    assert all(matrix.values())
    rows = []
    for number, case in enumerate(cases, 1):
        chosen_seed = seeds[number - 1]
        final = case["finalAnalysis"]
        totals = receipt["finalResonanceCounts"][number - 1]["counts"]
        rows.append({"case": number, "port": case["port"], "selectedSeed": int(chosen_seed),
                     "rates": len(final["rateObjects"]), "measuredRateGv": sum(rate["gv"] > 0 for rate in final["rateObjects"]),
                     "caseGvAfterRound": final["generalVitality"], "broadcasts": len(case["broadcastEntries"]),
                     "simulatedResonances": sum(totals.values()), "resonatedSignatures": len(totals)})
    with (run / "analysis-comparison.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("case", "seed", "rank", "rate", "EW", "potency", "level", "analysis_case_GV"))
        for number, case in enumerate(cases, 1):
            for seed in seeds:
                result = case["controls"][seed]["result"]
                for rank, rate in enumerate(result["rateObjects"], 1):
                    writer.writerow((number, seed, rank, rate["nameOrRate"], rate["energeticValue"], rate["potency"], rate["level"], result["generalVitality"]))
    with (run / "resonance-comparison.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("case", "port", "broadcast_id", "session_id", "original_rate_index", "signature", "count"))
        for number, case in enumerate(cases, 1):
            totals = receipt["finalResonanceCounts"][number - 1]["counts"]
            for entry in case["broadcastEntries"]:
                writer.writerow((number, case["port"], entry["broadcastId"], entry["observationBinding"]["sessionId"],
                                 entry["observationBinding"]["rateIndex"], entry["signature"], totals.get(entry["signature"], 0)))
    rank_comparisons = []
    for (i, a), (j, b) in itertools.combinations(enumerate(cases), 2):
        ra = a["controls"][seeds[i]]["result"]["rateObjects"]
        rb = b["controls"][seeds[j]]["result"]["rateObjects"]
        names_a = {rate["nameOrRate"] for rate in ra}
        names_b = {rate["nameOrRate"] for rate in rb}
        rank_comparisons.append({"cases": [i + 1, j + 1], "fullRateSetsEqual": names_a == names_b,
                                 "top21CommonRates": len({rate["nameOrRate"] for rate in ra[:21]} & {rate["nameOrRate"] for rate in rb[:21]}),
                                 "orderedRateListsEqual": [rate["nameOrRate"] for rate in ra] == [rate["nameOrRate"] for rate in rb]})
    summary = {"fullRequested21MinuteRun": bool(full), "requestedSeconds": receipt["requestedSeconds"],
               "finalSampleElapsedSeconds": samples[-1]["elapsedSeconds"], "betweenFirstAndLastSamplesSeconds": minimum,
               "samples": len(samples), "sameSeedMatrixEqual": matrix, "cases": rows,
               "selectedDifferentSeedDigests": len(set(receipt["differentSeedResultDigests"])),
               "rankComparisons": rank_comparisons, "analysisAndCaseIdentityUnchanged": receipt["analysisAndCaseIdentityUnchanged"],
               "imageInputExercised": False, "imageReason": "Only manifest context; no supported normal-analysis image input",
               "interpretation": "Numeric differences follow seed changes. No evidence of vector-conditioned suitability. Resonances are simulated; factory seed 0 and unequal queue sizes confound cross-case counts."}
    (run / "SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = [{"path": str(path.relative_to(run)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                for path in sorted(run.rglob("*")) if path.is_file() and path.name != "EVIDENCE_MANIFEST.json"]
    (run / "EVIDENCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    current = json.loads((ROOT / "runtime/rw-vector-probe-current.json").read_text(encoding="utf-8"))
    print(json.dumps(summarize(Path(current["run"])), ensure_ascii=False, indent=2))
