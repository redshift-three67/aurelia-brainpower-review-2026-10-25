# Deferred Full Pytest Suite

Date: 2026-07-03

The full pytest suite is intentionally deferred for this session because prior
runs on this Windows machine showed OpenBLAS memory-allocation failures under
high RAM/CPU pressure. The targeted web, launcher, and CLI option tests remain
the active verification surface for the current changes.

Deferred verification command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\ -q
```

Recommended conditions before running:

- Close nonessential local services and browser windows.
- Keep the important process on port 8090 running undisturbed.
- Run with low parallelism/no xdist.
- If OpenBLAS allocation failures recur, rerun failing tests individually before
  treating them as code regressions.
