# Manifest und Provenienz

## Archividentität

| Feld | Wert |
|---|---|
| Archiv-ID | `EXT-ANALYSIS-2026-08-25-01` |
| Freigabe xHigh | 2026-08-25 16:40 CEST |
| Archivierungszeit | 2026-08-25 17:00:19 CEST |
| Arbeitsverzeichnis | `Lokaler Operator-Arbeitsbereich (Pfad nicht veröffentlicht)` |
| Remote | `https://github.com/redshift-three67/aurelia.git` |
| Schreibzugriffe Remote/Server | keine |
| Normativer Status | nicht kanonisch; externer Planungsinput |

## Git-Bezug der Verifikation

| Fläche | Branch/Referenz | Commit bei Prüfung | Zustand |
|---|---|---|---|
| Vorbereitung | `codex/aurelia-vorbereitung` | `a726346c74b02af811fc833151f7031ead431dac` | Entwicklerordner untracked |
| Kanon | `codex/aurelia-kanon-implementation` | `b20ee873347c5fd767e2089c993f1cf93a625def` | sauber |
| G0-Design | `codex/aurelia-g0-governance` | `a6a8e7dca456d14a6748b204b787b235fdedf9be` | G0-Pläne und Status-HTML untracked |
| Remote-Basis | `main` | `b858ccdd258bb98d29cdf6622ce26f94a8524b3e` | keine Übertragung in diesem Vorgang |

## Unveränderte Quellen und SHA-256

| Datei | Bytes | Zeilen | SHA-256 |
|---|---:|---:|---|
| `source/original-pasted-text.txt` | 39877 | 471 | `6F46C2C53FF0A50487A3789AF7BE5294B397CDFD1A715A6AC952B0FA194443B4` |
| `source/expanded-analysis/00_EXECUTIVE_SUMMARY_UND_GESAMTURTEIL.md` | 5351 | 64 | `7EA2E57FD3A794E091DA52909B27FFE697DBE2E4C2566D98654E2BB8FFA87738` |
| `source/expanded-analysis/01_ARCHITEKTUR_UND_CODEBASIS_AUDIT.md` | 11318 | 135 | `E5E4550F559D602C4146499445ABE7690A0797DD92D36C79F8D121E39AD37286` |
| `source/expanded-analysis/02_LUECKEN_RISIKEN_UND_SCHWACHSTELLEN.md` | 8043 | 96 | `7B4D0FC0227F74A477310FA7D66BF0AECCEC9E6604758E5E8563462237CFFD11` |
| `source/expanded-analysis/03_ERGAENZENDE_INNOVATIONEN.md` | 8042 | 110 | `4CDDFDD93BC02EBF76FBB980817C4448AAAE9665D12A2E2F718C8B20AB9F7B77` |
| `source/expanded-analysis/04_PHASEN_UND_SUBSCHRITT_UMSETZUNGSPLAN.md` | 14243 | 207 | `440B49ADB9B1B422B05EF4FD0B467F8423D8777251D0CFC273411CFF18586062` |
| `source/expanded-analysis/05_HANDLUNGSEMPFEHLUNGEN_UND_FAZIT.md` | 6189 | 75 | `1200118E19DCE95A8E175B0110D5FC47FFAED26BF31466A098EC3D91DB81076D` |
| `source/expanded-analysis/06_SERVER_INVENTUR_M_G1_ISTSITUATION.md` | 5886 | 86 | `1F7892724AC87E00939F32BCE261A4A4AB5C2F52334E4D841C531D8EACE51D8D` |

Die Hashwerte beziehen sich auf die jeweiligen Quelldateien unmittelbar vor
der Archivierung. Die Abschlussprüfung vergleicht sie erneut mit den Kopien.

## Prüfungsumfang

Vollständig verifiziert wurden:

- das 471-zeilige Ausgangsdokument;
- die Dateien `00` bis `05`;
- Kanon, Code, Migrationen, dokumentierte Entscheidungen und G0-Design;
- Branchzustände und relevante Testbefehle;
- ausgewählte Rechts-, Hardware-, PostgreSQL-, CUDA-, PGlite-, Grammatik-,
  Merkle-/ZKP- und p-adische Aussagen anhand von Primärquellen.

Nicht Bestandteil dieser abgeschlossenen Verifikation war:

- Datei `06_SERVER_INVENTUR_M_G1_ISTSITUATION.md`, da sie erst bei der
  Archivierung zusätzlich sichtbar wurde;
- eine eigene SSH- oder sonstige Live-Verifikation des dort beschriebenen
  Servers;
- Änderungen am M-G1, an GitHub oder an produktiven Diensten.

## Vertraulichkeitshinweis

Datei `06` nennt Zielhost, IP-Adresse, SSH-Benutzer, Dienste und Pfade. Diese
Informationen sind als interne Infrastrukturmetadaten zu behandeln. Vor einer
GitHub-Übertragung ist eine gesonderte Freigabe oder eine sanitierte Fassung
erforderlich.
