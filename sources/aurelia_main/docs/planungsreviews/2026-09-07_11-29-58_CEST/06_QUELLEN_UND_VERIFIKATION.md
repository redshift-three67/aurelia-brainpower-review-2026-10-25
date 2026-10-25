# 06 – Quellen, Fingerabdrücke und Dokumentverifikation

Erfassung der Dateifingerabdrücke: 2026-09-07T11:39:27+02:00. Zeitzone Europe/Berlin.

Die Hashes beschreiben die lokal gelesenen Dateibytes, einschließlich möglicher Zeilenendeunterschiede. Sie sind keine Remote-, Freigabe- oder Secret-Freigabeprüfung. Keine historischen Analyse-Rohquellen wurden kopiert. Änderungen seit dieser Aufnahme erfordern einen gezielten Vergleich, keine automatische Rücksetzung.

## Ausgangsstände

- ROOT: Branch `codex/aurelia-vorbereitung`, Commit `8706186`.
- K1: Branch `codex/aurelia-konsolidierung`, HEAD `1185a68ed984b525686764f995513355701929e3`.
- K1 uncommittiert: `package.json`; unversioniert: `scripts/test-runner.mjs`, `scripts/test-runner.test.mjs`.
- ROOT enthält daneben vier bereits vorhandene unversionierte September-Analyseordner; sie wurden nicht geändert.
- Die Originalpläne wurden nicht verändert. Zeilennummern in Dokument 01 beziehen sich auf diese Aufnahme.

## Quellenmanifest

Pfade sind relativ zum Projekt-Hauptverzeichnis. Links führen zu den lokal vorhandenen Originalen; eine spätere Änderung des Originals ist über den Hash erkennbar.

| Quelle | Bytes | SHA-256 |
|---|---:|---|
| [AGENTS.project.md](../../../AGENTS.project.md) | 6138 | `68be8122f7f6e71fd499e8a8dd49619b4d893b3b0dc8ecd78321806faadbe3b4` |
| [AURELIA-ÜBERGABE-2026-08-30.md](../../../AURELIA-ÜBERGABE-2026-08-30.md) | 10747 | `08b3e3bd171cc197b4e99a592f52f05271590930d53247895eef08371f2b570b` |
| [aurelia-tiefenanalyse-v6-2026-08-28/aurelia-status-live.html](../../../aurelia-tiefenanalyse-v6-2026-08-28/aurelia-status-live.html) | 23556 | `0010fc74dd9f78c077ebeaa63de9a2b3030fa53be7219649241ba591e34e0b98` |
| [.worktrees/aurelia-konsolidierung/AGENTS.project.md](../../../.worktrees/aurelia-konsolidierung/AGENTS.project.md) | 6372 | `25b90d3f5817ef2c00f8d4cd14b4ce867ebd8256d4be8b2e24da5d2b35757449` |
| [.worktrees/aurelia-konsolidierung/docs/STATUS.md](../../../.worktrees/aurelia-konsolidierung/docs/STATUS.md) | 2673 | `8c7e086832a02c8ba9207d6c9a6855b2d4d8ce96745a72ec1ce97a8ad37e43d9` |
| [.worktrees/aurelia-konsolidierung/docs/09-roadmap.md](../../../.worktrees/aurelia-konsolidierung/docs/09-roadmap.md) | 1979 | `fefb0ce95b5c76c80ae04db01ab39968d86a61a1c13c8ec8b92ef29e86012df5` |
| [.worktrees/aurelia-konsolidierung/docs/project-control/K1-STATUS.md](../../../.worktrees/aurelia-konsolidierung/docs/project-control/K1-STATUS.md) | 12056 | `92e0377ab245ebb162c7b8f3a66b918b7f258e7021b8911bee212392d4e17688` |
| [.worktrees/aurelia-konsolidierung/docs/project-control/README.md](../../../.worktrees/aurelia-konsolidierung/docs/project-control/README.md) | 8003 | `bb191e1afc94f5c6168483d2478da79aaac6eb5458839f0ce711034fd1e136d7` |
| [.worktrees/aurelia-konsolidierung/docs/project-control/QUALITY-ROUTING.md](../../../.worktrees/aurelia-konsolidierung/docs/project-control/QUALITY-ROUTING.md) | 7331 | `87ec87e9a582aa157f73b8185148c63c79c3e8d0093c19875ca6b3a7f976688f` |
| [.worktrees/aurelia-konsolidierung/docs/project-control/ground-zero/GATE-STATUS.md](../../../.worktrees/aurelia-konsolidierung/docs/project-control/ground-zero/GATE-STATUS.md) | 2444 | `41b71d7c0f22b431b63fd79a7cd36a9e9e1b47272152e776b861a16ed9bd6206` |
| [.worktrees/aurelia-konsolidierung/docs/superpowers/plans/2026-08-25-aurelia-k1-canon-consolidation.md](../../../.worktrees/aurelia-konsolidierung/docs/superpowers/plans/2026-08-25-aurelia-k1-canon-consolidation.md) | 53433 | `da5b614cf83c960f74c0da94669bf0886e1343848fdf78cd2980a2abcc88491f` |
| [.worktrees/aurelia-konsolidierung/docs/superpowers/specs/2026-08-25-aurelia-k1-canon-consolidation-design.md](../../../.worktrees/aurelia-konsolidierung/docs/superpowers/specs/2026-08-25-aurelia-k1-canon-consolidation-design.md) | 17199 | `7205545f39de9bc9fbf62af14d0b91cd6482a2d0a42c643a6ffdde80433fe133` |
| [.worktrees/aurelia-konsolidierung/package.json](../../../.worktrees/aurelia-konsolidierung/package.json) | 3507 | `54f18ea804c96b8349845f52c1c5c51a1a81939e7eba486953a08926fda3dfc8` |
| [.worktrees/aurelia-konsolidierung/package-lock.json](../../../.worktrees/aurelia-konsolidierung/package-lock.json) | 274680 | `c6a78102b26e4924281d0b684ac604b72bd0f754bf329f930198087a82eefe0c` |
| [.worktrees/aurelia-konsolidierung/src/lib/concept/canon.ts](../../../.worktrees/aurelia-konsolidierung/src/lib/concept/canon.ts) | 662 | `524e484dd925cad0bdaf3e446490f2055445f8ac1dab4dcd74f170b1b7b89309` |
| [.worktrees/aurelia-konsolidierung/scripts/canon-contract.mjs](../../../.worktrees/aurelia-konsolidierung/scripts/canon-contract.mjs) | 35941 | `c87fa1627fdf55c35edca4730dcc7f1a0aec9a108a929b52b85c2b8c8b9ed101` |
| [.worktrees/aurelia-konsolidierung/scripts/check-project-control-k1.mjs](../../../.worktrees/aurelia-konsolidierung/scripts/check-project-control-k1.mjs) | 13400 | `36e5974caebe9db6c4a247a7a985f88b22b624afeed5b676503241636867d34f` |
| [.worktrees/aurelia-konsolidierung/scripts/test-runner.mjs](../../../.worktrees/aurelia-konsolidierung/scripts/test-runner.mjs) | 3617 | `38627c9f330a5297fec6aa10f6990c64e5f5e714b5473f5702aca78418b203c8` |
| [.worktrees/aurelia-konsolidierung/scripts/test-runner.test.mjs](../../../.worktrees/aurelia-konsolidierung/scripts/test-runner.test.mjs) | 8420 | `cf82703e88e7868387397e0208b5c8797dd99fa1d72e5b979620b8bd7b4de5e4` |
| [.worktrees/aurelia-konsolidierung/scripts/with-app-env.mjs](../../../.worktrees/aurelia-konsolidierung/scripts/with-app-env.mjs) | 4731 | `50af35a2740a5943e4dc3265a1bad51ea68a37335e6039091e064e3a9e2787fa` |
| [.worktrees/aurelia-konsolidierung/scripts/check-auth-invariant.mjs](../../../.worktrees/aurelia-konsolidierung/scripts/check-auth-invariant.mjs) | 4312 | `291f8e98536fd8480bcf0473e2d9afc9a72d9f1ee0108009f1b5c222ba3744cc` |
| [.worktrees/aurelia-konsolidierung/scripts/browser-smoke.mjs](../../../.worktrees/aurelia-konsolidierung/scripts/browser-smoke.mjs) | 6219 | `74c6bb0439b1d83782f9d95f7b0836d61bd06538badddf03be2a8085602a1e82` |
| [.worktrees/aurelia-konsolidierung/vite.config.ts](../../../.worktrees/aurelia-konsolidierung/vite.config.ts) | 6933 | `eb5334e0c70efe08217898d90e5313cf44ef4850189ed752c2c9b5c73db2f1af` |
| [.worktrees/aurelia-konsolidierung/src/lib/db.ts](../../../.worktrees/aurelia-konsolidierung/src/lib/db.ts) | 9763 | `ba21e7c67fbb336f507a4d1b063db191dda15fcb7ef09a6e5d351c23ffab204b` |

## Erstellte Dokumente

SHA-256 der Dokumente 00/README bis 05. Dieses Quellenmanifest enthält bewusst keinen Hash seiner selbst.

| Datei | Bytes | SHA-256 |
|---|---:|---|
| [01_IST_STAND_UND_REVIEW.md](01_IST_STAND_UND_REVIEW.md) | 7997 | `ca78814b923ff34b3a4e83eaf5156d6cd29b017b163d48591e6ba4fdff963936` |
| [02_ALT_NEU_VERGLEICH.md](02_ALT_NEU_VERGLEICH.md) | 6869 | `87f8e0fa3e22d45dfb5ffd19dfdda9b1e861d1d90e3f1b7bb61db4e99406ac2e` |
| [03_EMPFOHLENE_UMSETZUNGSPLANUNG.md](03_EMPFOHLENE_UMSETZUNGSPLANUNG.md) | 22040 | `99d5b3103cfddcbd0c4f9f1248b32bb000b0735ce1851601a0fcc9c56dd8b53b` |
| [04_WEITERE_LUECKEN_UND_VERBESSERUNGEN.md](04_WEITERE_LUECKEN_UND_VERBESSERUNGEN.md) | 8703 | `0779d0f48ad372275979cd2ad1f29ae208e6f6dae45d3f5b6b6e6c17bf207d46` |
| [05_ENTWICKLER_LLM_UEBERGABE.md](05_ENTWICKLER_LLM_UEBERGABE.md) | 4579 | `936513f068b63b5a434068b4356460515e12f75b8d1b6a703fdca4e8c1dadf98` |
| [README.md](README.md) | 4349 | `1032f395f8ea7a3bb9de04942beca3b2ae64d58fa127de5504ab9fe64ed2e34f` |

## Frische lesende Fachprüfungen

| Befehl in K1 | Ergebnis am 07.09.2026 |
|---|---|
| `node --experimental-strip-types scripts/canon-contract.mjs` | Exit 0; keine Fehlerausgabe |
| `node scripts/check-project-control-k1.mjs` | Exit 0; keine Fehlerausgabe |
| `node --version` | `v22.22.0` |

Die Test-Suites, Typecheck, Lint, Builds und Browserabnahmen wurden in diesem Dokumentationsauftrag nicht ausgeführt. Ihre Befehle in Dokument 03 sind zukünftige Abnahmeschritte. Die Dokumentprüfung wird nach Erstellung separat durchgeführt; sie ist keine Produktabnahme.

## Ergebnis der Dokumentprüfung

Die Paketprüfung nach Erstellung wurde mit Exit 0 abgeschlossen:

| Prüfung | Ergebnis |
|---|---|
| Markdown-Dateien | 7 vorhanden; UTF-8 lesbar |
| Lokale Markdown-Dateiverweise | 36 geprüft, alle Ziele vorhanden |
| Quellen-/Dokumentfingerabdrücke | 30 SHA-256-Werte und Dateigrößen geprüft, alle identisch |
| Altplan-Abdeckung | Tasks 1–14 vollständig in der Vergleichstabelle |
| Neue Pakete | E0–E8 vollständig in Dokument 03 |
| Codeblock-Begrenzungen | ausgeglichen |
| Ersatzzeichen / nachgestellte Leerzeichen | keine gefunden |
| Root-Gitstatus | nur neuer Dokumentationsbereich zusätzlich zu den bereits vorhandenen Analyseordnern |
| K1-Gitstatus | unverändert: Package-Änderung und zwei unversionierte Runner-Dateien |

Dies ist eine technische Dokumentprüfung plus primäre inhaltliche Gegenprüfung, keine unabhängige Zweitbegutachtung und keine Freigabe der vorgeschlagenen Implementierung. Der ergänzte Prüfbericht wird nicht in seinen eigenen Hash aufgenommen. Es wurden keine Dateien außerhalb des neu angelegten Dokumentationsordners geschrieben.
