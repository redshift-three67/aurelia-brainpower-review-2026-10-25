# CUDA-Scheduler (D17, gesetzt)

Hardware: RTX 4000 SFF Ada, 20 GB, **kein MIG**.
VRAM (C03, gesetzt): 2 GB Runtime · 16 GB Job-Pool · 2 GB Kopf.

Isolation-Schlüssel: `(tenant_id, client_id, job_id)`.
Auch zwei Jobs desselben Klienten (Analyse A / Analyse B / Harmonisierung DSP)
teilen keinen Buffer und keinen Default-Stream.

Virtuelle Timer liegen **nicht** hier. Siehe [21-timer.md](21-timer.md).

20 Klienten = Belegung. GPU-DSP typisch 1–4 Occupancies, Rest Queue.
Kein Overcommit, kein Fake-Job, kein MIG.
