# Manifest und Provenienz – Entwickleranalyse v2

## Archividentität

| Feld | Wert |
|---|---|
| Archiv-ID | `EXT-ANALYSIS-2026-08-25-02` |
| Archivierungszeit | 2026-08-25 17:22:13 CEST |
| Vorgängerprüfung | `EXT-ANALYSIS-2026-08-25-01` |
| Arbeitsverzeichnis | `C:\Users\Hubert111\Documents\ChatGPT\Aurelia` |
| Remote | `https://github.com/redshift-three67/aurelia.git` |
| Remote-/Servermutation | keine |
| Normativer Status | externer Planungsinput; nicht kanonisch |

## Git-Bezug

| Fläche | Commit bei Prüfung | Befund |
|---|---|---|
| `codex/aurelia-vorbereitung` | `a726346c74b02af811fc833151f7031ead431dac` | v1/v2 und Projekt-Control untracked; keine installierte vollständige Dependency-Fläche |
| `codex/aurelia-kanon-implementation` | `b20ee873347c5fd767e2089c993f1cf93a625def` | sauber; maßgeblicher jüngerer Kanonzustand |
| `codex/aurelia-g0-governance` | `a6a8e7dca456d14a6748b204b787b235fdedf9be` | Design final; G0-Pläne/Status-HTML untracked |
| `main` | `b858ccdd258bb98d29cdf6622ce26f94a8524b3e` | keine Übertragung in diesem Vorgang |

## Quelldateien und SHA-256

| Datei | Bytes | Zeilen | SHA-256 |
|---|---:|---:|---|
| `source/original-pasted-text-v2.txt` | 9170 | 61 | `BFBDE109FA299A0E2BC234C809A2783B297E8BC4DC7A8242220C13C6BA896BD6` |
| `source/expanded-analysis-v2/00_METADATA_UND_LESEANLEITUNG.md` | 2357 | 35 | `35B114F2A23DD7577C71756D0A401FB744285D46B4C15BDA17882EBA8BCB519F` |
| `source/expanded-analysis-v2/01_EXECUTIVE_SUMMARY.md` | 4230 | 50 | `E4FE6143525FB366EEC8AAD81D311600E9217D5B666F10162A83BC5B40204FE2` |
| `source/expanded-analysis-v2/02_IST_ANALYSE_CODEBASIS.md` | 5855 | 69 | `8C27CE8141BD9C8465FD7CBC7D23898588E338F5A7A1CE974E6A0E37B3D6D6CC` |
| `source/expanded-analysis-v2/03_IST_ANALYSE_SERVER_MG1.md` | 4415 | 57 | `D209414C54EE29A6D16FAB278FA9954C8759A249611C73A3DCA7A3E4E3CF76A8` |
| `source/expanded-analysis-v2/04_LUECKEN_UND_RISIKEN.md` | 6279 | 63 | `2FB0A5218600F6CD7F4285F2BF1652EC255BE93AAB42206EE15ED7D34B92C822` |
| `source/expanded-analysis-v2/05_ERGAENZENDE_INNOVATIONEN.md` | 4549 | 44 | `004D204EB41B7D2694E9855B2D06FCF506EAB6CE7CB7A45C4C08A1C3ACE7AF9B` |
| `source/expanded-analysis-v2/06_PHASENPLAN_SUBSCHRITTE.md` | 9306 | 114 | `B8684ED0E41FEFF62BE08294444C99123E91FD8B4ECFD92DDF35D7B1374D0178` |
| `source/expanded-analysis-v2/07_VORGEHENSWEISE_UND_FAZIT.md` | 4172 | 55 | `84A344FFF8D135EBD5CF543423B21E3FED11D82D13CAAF8CEF7F1E4F89D31BCC` |

## Durch Codex reproduzierte lokale Prüfungen

| Prüfung | Vorbereitung | Kanon |
|---|---|---|
| `npm test` | rot: 0 Skripttests; App-Data-Modultest kann Dependency nicht auflösen; 14 Gate-Identity-Tests grün | Exit 0; 24 Quelltests grün, aber weiterhin 0 Skripttests durch Windows-Glob |
| `npm run typecheck` | rot; Dependencyfläche fehlt, fremder/effektiver Compiler meldet `vite/client` und `baseUrl` | grün mit lokalem TypeScript 5.9.3 |
| `npm run check:canon` | Befehl/Validator im älteren Branch nicht vorhanden | grün: `decision locks and active wording agree` |
| `npm run lint` | nicht maßgeblich geprüft | grün |
| direkte `scripts/*.test.mjs` | nicht maßgeblich | 161 Tests: 146 grün, 15 rot |
| `npm run check:auth` | ohne Devserver unbestimmt/rot | ohne Devserver unbestimmt/rot |

Die 15 direkten Skripttestfehler umfassen reale Projekt-/Template-Drifts sowie
Windows-spezifische Symlink-Beschränkungen. Sie beweisen den Bedarf einer
sauberen Testklassifikation; sie machen nicht jeden betroffenen Produktpfad
automatisch defekt.

## Server-Verifikation

Codex versuchte ausschließlich lesend und mit `BatchMode=yes`, die in v2
genannte SSH-Identität zu erreichen. Die Verbindung scheiterte vor einer
Session mit `Permission denied (publickey,password)`. Damit wurden keine
Serverbefehle ausgeführt und keine Serveraussage unabhängig bestätigt.

Die v2-Serverbefunde werden daher als `reported-by-developer/unverified-by-codex`
klassifiziert. Ein fehlendes Rohbefehls-, Zeit-, Host-Key- und Hashprotokoll
verhindert eine beweissichere Übernahme.
