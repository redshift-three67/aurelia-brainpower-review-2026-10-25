# RadiWorks — Trennung von Runtime-Home und Rate-Katalog

**Status:** Sanitierte technische Evidenz, kein automatischer Aurelia-Kanon.

- `RADIOWORKS_HOME` enthält nur schreibbare Laufzeitdaten wie Cases, Drafts, Konfiguration und private Journale.
- `RADIOWORKS_DATA_DIR` benennt einen expliziten read-only Rate-Katalog; ohne Variable bleibt der kompatible Fallback `${RADIOWORKS_HOME}/data`.
- Ein Katalogwechsel wird beim kontrollierten Prozessstart indiziert. `GET /databases` ist der nichtmutierende Readiness-Nachweis vor Analysen.
- Der Rate-Katalog darf nicht durch implizite Projektpfade, Fallkopien oder Runtime-Migrationen vermischt werden.

Eine Übernahme als Plattformkonvention erfolgt ausschließlich über Aurelia-Governance.
