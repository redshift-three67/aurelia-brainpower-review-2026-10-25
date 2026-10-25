"""Bounded, synthetic three-process RadiWorks diagnostic; never uses live homes."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "runtime/rw-gv-binding-20261003"
CATALOG = ROOT / "runtime/radiworks-catalog-releases/e33ea136d8ea448fada7524757385ee4/data/ESSENCES/ESSENCES_BACHFLOWERS_RATES.txt"
PYTHON = Path(r"C:\Users\Hubert111\Documents\Radiworks\radiworks_port\engine\.venv\Scripts\python.exe")
PORTS = (8111, 8112, 8113)
SEEDS = (20261003, 20261004, 20261005)
DATABASE = "ESSENCES_BACHFLOWERS_RATES"
VECTORS = (
    {"surname": "Testperson-Alpha", "givenName": "Probe-A", "birthDate": "1991-01-01", "place": "Testort-A", "focus": "Synthetischer Fokus A", "optionalImage": None},
    {"surname": "Testperson-Beta", "givenName": "Probe-B", "birthDate": "1992-02-02", "place": "Testort-B", "focus": "Synthetischer Fokus B", "optionalImage": "image-B.svg"},
    {"surname": "Testperson-Gamma", "givenName": "Probe-C", "birthDate": "1993-03-03", "place": "Testort-C", "focus": "Synthetischer Fokus C", "optionalImage": "image-C.svg"},
)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def save(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def api(port: int, route: str, body=None, method: str | None = None):
    if port not in PORTS:
        raise ValueError("Only allocated test ports may be used")
    payload = None if body is None else json.dumps(body).encode()
    request = Request(f"http://127.0.0.1:{port}{route}", data=payload,
                      headers={"Content-Type": "application/json"}, method=method)
    try:
        with build_opener(ProxyHandler({})).open(request, timeout=10) as response:
            return json.load(response)
    except HTTPError as error:
        raise RuntimeError(f"test port {port}: {route} HTTP {error.code}: {error.read().decode()[:400]}") from error


def prepare(run: Path) -> list[dict]:
    for port in PORTS:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", port))
    source = run / "source"
    shutil.copytree(CANDIDATE / "engine/src", source / "engine/src",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(CANDIDATE / "webapp", source / "webapp")
    data = run / "catalog/ESSENCES"
    data.mkdir(parents=True)
    before = hashlib.sha256(CATALOG.read_bytes()).hexdigest()
    shutil.copyfile(CATALOG, data / CATALOG.name)
    assert hashlib.sha256((data / CATALOG.name).read_bytes()).hexdigest() == before
    assert hashlib.sha256(CATALOG.read_bytes()).hexdigest() == before
    source_manifest = [{"path": str(p.relative_to(source)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                       for p in sorted(source.rglob("*")) if p.is_file()]
    save(run / "SOURCE.json", {"catalog_sha256": before, "source_files": source_manifest})
    images = run / "synthetic-images"
    images.mkdir()
    vectors = [dict(value) for value in VECTORS]
    for vector, colour in zip(vectors[1:], ("#226699", "#996622")):
        path = images / vector["optionalImage"]
        path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8"><rect width="8" height="8" fill="{colour}"/></svg>', encoding="utf-8")
        vector["imageSha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    save(run / "INPUTS.json", {"synthetic_only": True, "vectors": vectors, "seeds": SEEDS,
                              "database": DATABASE, "image_usage": "manifest only; not a supported analysis input"})
    return vectors


def control_case(port: int, index: int, vector: dict, duration: float) -> dict:
    name = " ".join(vector[key] for key in ("givenName", "surname", "birthDate", "place"))
    case = api(port, "/cases", {"name": name, "description": "Nur synthetische Testdaten", "focus": vector["focus"]})
    controls = {}
    order = [seed for seed in SEEDS if seed != SEEDS[index]] + [SEEDS[index]]
    for seed in order:
        response = api(port, "/analysis", {"database": DATABASE, "mode": "seeded", "seed": seed})
        controls[str(seed)] = {"result": response["result"], "resultDigest": digest(response["result"]),
                               "draft": response["draft"], "passport": response["passport"]}
    measured = None
    for counter in range(22):
        measured = api(port, "/analysis/gv-round", {"expected_draft_id": response["draft"]["id"], "expected_counter": counter})
    assert measured is not None
    assert sum(rate["gv"] > 0 for rate in measured["result"]["rateObjects"][:21]) == 21
    draft_id = measured["draftId"]
    api(port, f"/drafts/{draft_id}/transition", {"status": "ready"})
    promoted = api(port, f"/drafts/{draft_id}/promote", {"max_rates": 8, "seconds_per_rate": int(duration) + 120})
    assert promoted["broadcastEntries"]
    current = api(port, "/cases/current")
    reference = api(port, "/cases/current/ref")["ref"]
    session = current["sessionList"][-1]
    for item in promoted["broadcastEntries"]:
        binding = item["observationBinding"]
        assert binding["caseRef"] == reference and binding["sessionId"] == session["sessionId"]
        assert binding["scope"] == current["scope"]
        assert binding["draftId"] == draft_id
    return {"port": port, "name": name, "focus": vector["focus"], "scope": case["scope"], "controls": controls,
            "caseRef": reference, "sessionId": session["sessionId"], "draftId": draft_id,
            "finalAnalysisDigest": digest(session["analysisResult"]), "finalAnalysis": session["analysisResult"],
            "broadcastEntries": promoted["broadcastEntries"], "broadcastObservedFromUtc": utc()}


def snapshot(case: dict) -> dict:
    queue = api(case["port"], "/broadcast/queue")
    expected = {item["broadcastId"]: item["observationBinding"] for item in case["broadcastEntries"]}
    active = queue["active"]
    assert {item["broadcastId"] for item in active} == set(expected), "A selected broadcast left the active queue before final observation"
    for item in active:
        assert item["observationBinding"] == expected[item["broadcastId"]]
    return {"port": case["port"], "utc": utc(), "elements": [{"broadcastId": item["broadcastId"],
            "progress": item["progress"], "resonanceCount": item["resonanceCount"]} for item in active],
            "resonanceTotals": queue["resonanceTotals"]}


def run_probe(duration: float) -> Path:
    if duration <= 0 or duration > 1260:
        raise ValueError("Duration must be in (0, 1260]; only 1260 is a full requested run")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run = ROOT / "runtime" / ("rw-vector-probe-" + stamp)
    run.mkdir(exist_ok=False)
    save(ROOT / "runtime/rw-vector-probe-current.json", {"run": str(run), "duration": duration})
    processes = []
    handles = []
    receipt = {"startedUtc": utc(), "requestedSeconds": duration, "full21MinuteRun": False, "success": False}
    try:
        vectors = prepare(run)
        for index, port in enumerate(PORTS):
            home = run / f"case-{index + 1}"
            home.mkdir()
            env = os.environ.copy()
            env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(run / "source/engine/src"),
                        "RADIOWORKS_HOME": str(home), "RADIOWORKS_DATA_DIR": str(run / "catalog"),
                        "RADIOWORKS_SCOPE_MODE": "local", "RADIOWORKS_LOCAL_TENANT_ID": "synthetic-probe",
                        "RADIOWORKS_LOCAL_CLIENT_ID": f"case-{index + 1}", "RADIOWORKS_LOCAL_JOB_ID": stamp})
            env.pop("RADIOWORKS_JOURNAL_KEY", None)
            log = (run / f"engine-{port}.log").open("w", encoding="utf-8")
            handles.append(log)
            program = "from radiworks.main import create_app; import uvicorn; uvicorn.run(create_app(),host='127.0.0.1',port=" + str(port) + ",log_level='warning',access_log=False)"
            child = subprocess.Popen([str(PYTHON), "-c", program], env=env, stdout=log, stderr=log,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            processes.append(child)
        deadline = time.monotonic() + 40
        for port, child in zip(PORTS, processes):
            while True:
                if child.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError(f"Test engine {port} did not start")
                try:
                    assert api(port, "/ping")["result"] == "pong"
                    break
                except (OSError, AssertionError):
                    time.sleep(.2)
        cases = [control_case(port, i, vectors[i], duration) for i, port in enumerate(PORTS)]
        for seed in SEEDS:
            assert len({case["controls"][str(seed)]["resultDigest"] for case in cases}) == 1
        assert len({case["caseRef"] for case in cases}) == 3
        assert len({case["sessionId"] for case in cases}) == 3
        assert len({digest(case["scope"]) for case in cases}) == 3
        save(run / "CONTROLS.json", cases)
        receipt.update({"pids": [p.pid for p in processes], "ports": PORTS, "cases": len(cases),
                        "sameSeedResultsEqual": True, "controlMatrix": "3 cases x 3 seeds",
                        "differentSeedResultDigests": [case["controls"][str(SEEDS[i])]["resultDigest"] for i, case in enumerate(cases)]})
        started = time.monotonic()
        receipt["jointObservationStartedUtc"] = utc()
        previous = {}
        samples = 0
        print(json.dumps({"event": "joint_observation_started", "run": str(run), "duration": duration, "pids": receipt["pids"]}), flush=True)
        with (run / "samples.jsonl").open("w", encoding="utf-8") as log, concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            while True:
                elapsed = time.monotonic() - started
                observations = list(pool.map(snapshot, cases))
                for observation in observations:
                    for item in observation["elements"]:
                        key = (observation["port"], item["broadcastId"])
                        assert item["resonanceCount"] >= previous.get(key, 0)
                        previous[key] = item["resonanceCount"]
                log.write(json.dumps({"elapsedSeconds": elapsed, "observations": observations}, ensure_ascii=False) + "\n")
                log.flush()
                samples += 1
                save(run / "PROGRESS.json", {"elapsedSeconds": elapsed, "samples": samples, "caseTotals": [sum(item["resonanceCount"] for item in value["elements"]) for value in observations]})
                if samples == 1 or elapsed >= duration:
                    print(json.dumps({"elapsedSeconds": elapsed, "samples": samples}), flush=True)
                if elapsed >= duration:
                    break
                time.sleep(min(5, duration - elapsed))
        for case in cases:
            current = api(case["port"], "/cases/current")
            session = current["sessionList"][-1]
            assert current["name"] == case["name"] and current["focus"] == case["focus"]
            assert session["sessionId"] == case["sessionId"] and digest(session["analysisResult"]) == case["finalAnalysisDigest"]
            assert api(case["port"], "/cases/current/ref")["ref"] == case["caseRef"]
            stop = api(case["port"], "/broadcast/all", method="DELETE")
            after = api(case["port"], "/broadcast/queue")
            assert not after["queued"] and not after["active"]
            case["stopReceipt"] = stop
        source = json.loads((run / "SOURCE.json").read_text())
        for entry in source["source_files"]:
            assert hashlib.sha256((run / "source" / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
        receipt.update({"success": True, "jointObservedSeconds": time.monotonic() - started, "samples": samples,
                        "full21MinuteRun": duration == 1260 and elapsed >= 1260,
                        "finalResonanceCounts": [{"port": case["port"], "counts": value["resonanceTotals"]} for case, value in zip(cases, observations)],
                        "analysisAndCaseIdentityUnchanged": True, "sourceBytesUnchanged": True,
                        "broadcastEntropy": "Unmodified factory seed 0; not independent stochastic streams"})
        save(run / "CONTROLS.json", cases)
    except BaseException as error:
        receipt["failure"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        for child in processes:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)
        for handle in handles:
            handle.close()
        receipt.update({"endedUtc": utc(), "testProcessesStopped": all(child.poll() is not None for child in processes)})
        save(run / "RESULT.json", receipt)
    print(json.dumps({"event": "complete", "run": str(run), "success": receipt["success"], "full21MinuteRun": receipt["full21MinuteRun"]}), flush=True)
    return run


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=1260)
    args = parser.parse_args()
    run_probe(args.seconds)
