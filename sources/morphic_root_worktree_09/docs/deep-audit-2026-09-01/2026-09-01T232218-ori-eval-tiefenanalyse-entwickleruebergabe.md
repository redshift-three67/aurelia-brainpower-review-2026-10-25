# Tiefenanalyse: Ori Eval — sichere PoC-Integration in RadiMorphic

**Dokumenttyp:** Erneute Tiefenanalyse + Übergabedokument für einen Entwickler
**Zeitstempel:** 2026-09-01T232218+02:00 (Erzeugt 2026-09-01 23:22:18 +02:00)
**Arbeitsmodus:** Streng lesend (Read-Only-Analyse)
**Erzeugte Artefakte:** ausschließlich dieses Dokument
**Nicht verändert:** keine Code-, Konfigurations- oder Projektdatei; keine Installation; keine Ausführung von Ori

---

## 1. Auftrag, Methode und Grenzen

**Auftrag:** Erneute, vertiefte Sicherheits- und Machbarkeitsanalyse von OpenRouter **Ori Eval** für den Einsatz im Projekt RadiMorphic. Ergebnis ist ein eigenständiges, zeitgestempeltes Dokument, das ein Entwickler als Arbeitsgrundlage übernehmen kann.

**Methode (streng lesend):**
- Erneuter Abruf und Quellenlesen des Ori-Installers (Volltext) und der Release-Metadaten.
- Abgleich mit der vorherigen Sicherheitsprüfung (Veraltet? Nein — siehe Abschnitt 3).
- Auswertung der projekteigenen Sicherheitsbaseline (DSGVO, Mandantentrennung, Klartextdaten).
- Prüfung des lokalen Arbeitsbaumzustands auf Datenbestände, die ein repo-scanendes Werkzeug erfassen würde (nur Existenz und Dateianzahl, **keine Inhalte**).

**Bewusst nicht durchgeführt:**
- Ori wurde **nicht installiert** und **nicht ausgeführt**.
- Kein Netzwerkzugriff auf produktive Daten, kein API-Aufruf gegen Modelle.
- Keine Änderung am Repository, kein Commit, kein Staging.

**Konsequenz:** Alle Aussagen zu Ori beruhen auf öffentlich abrufbaren Artefakten (Installer-Quelltext, Release-Metadaten, Hashes) und auf dokumentierten Datenwegen. Aussagen über das geschlossene Binary-Verhalten zur Laufzeit sind naturgemäß **nicht vollständig belegbar** und werden als solches gekennzeichnet.

---

## 2. Verifizierte Projekt-Ausgangslage

| Merkmal | Verifizierter Stand 2026-09-01 |
|---|---|
| Aktiver Arbeitsort | `C:\morphic_v1\.worktrees\operator-workbench-phase1` |
| Branch | `report-ux-polish` |
| HEAD | `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4` — *docs: pin Debian Radimorphic integration path* |
| HEAD deckt sich mit | `upstream/gate5-linux-migration-20260809` |
| Gate-Status | Gate 4 ACCEPTED · **Gate 5 NICHT accepted** · Gate 6 blockiert |
| Kanonischer Debian-Pfad | `/opt/Prototypen/Radimorphic` |
| Remote | `https://github.com/redshift-three67/radimorphic.git` (Windows-Remotename `upstream`, im Fresh Clone i. d. R. `origin`) |
| Root-Checkout `C:\morphic_v1` | Nur Multi-Worktree-Container (`master@411ff09`), **nicht** die Quelle, nicht verwenden |

**Wichtig für den Entwickler:** Der PoC berührt Gate 5 in keiner Weise. Gate 5 bleibt ein offener, nicht akzeptierter Zustand; die Gate-5- und Gate-6-Arbeit läuft unverändert separat weiter. Der Ori-PoC ist ein **paralleles, isoliertes Vorhaben** und darf keine Gate-5-Bytes verändern.

---

## 3. Ori — neuverifizierter Befund (Stand 2026-09-01)

**Zentrale Feststellung: Die vorherige Prüfung ist NICHT veraltet.** Der verifizierte Release ist identisch mit dem zuvor geprüften Stand. Die frühere Bewertung bleibt damit voll gültig.

### 3.1 Release und Artefakte

| Merkmal | Wert |
|---|---|
| Tag | `cli-0.12.1-e1631f8` |
| Name | `Ori CLI 0.12.1+e1631f8` |
| Veröffentlicht | 2026-08-31T16:37:05Z |
| `immutable` | **true** |
| `prerelease` | false |
| Build-Quelle | `OpenRouterIncubator/ori@e1631f8a8454ab792895b3d9318902941f90beea` (Repo **nicht öffentlich verifizierbar**) |

**Artefakt-Hashes (verifiziert):**

| Asset | Größe (Bytes) | SHA-256 |
|---|---:|---|
| `ori-linux-x64` | 109.020.360 | `c9b67ee18ae892045dc55266cc9285f9b9e8b5d9e1827d5fdb89c87773057a7d` |
| `ori-linux-x64-musl` | 102.643.160 | `2776ebc58ab1d170b53e015d8ec9123b934e72754731795b74c63f7ed418b918` |
| `ori-linux-arm64` | 109.168.632 | `414c8b152597863a46674474df93deed58ce5f930d938e63499718dde756b0d7` |
| `ori-linux-arm64-musl` | 102.108.272 | `c398e5fe29e748fe66e82133ebc68d489b364d94f34bd859a906963799509188` |
| `ori-darwin-arm64` | 80.559.776 | `85e8dc95e96f2da3211707bbc4055bf058ff6f47b9c944862256308bdf0fc501` |
| `ori-darwin-x64` | 87.318.832 | `304ab1cf8c1115469c34b2e50aac28aefef4086a7f3178536b6c06474c33f56c` |
| `ori-windows-x64.exe` | 105.344.000 | `b58eb65408555fa7ed2330550b8c84939ec9c9b75c7ba8b3e93079b5e408d2fd` |
| `SHA256SUMS` | 960 | `12efbf9f4e6942e2a6c2965a694ce2e4ffa24ea2247b03ecf776fe4ebcca2ad2` |
| `install.sh` | 17.159 | `34be5881c5f98202892c2001e62946c1991ddd87bccde4b4367c1f9ea5d50986` |
| `install.ps1` | 6.987 | `fed1986149f8dd95e4bbb672a6ac43d0c43374072a10b6b3c66e2e3751e83810` |
| `version` | 15 | `fed003f0796a76faf18f4dc2bac247e7ef5b1bb2d82972dffb54a49c106ecbd2` |
| `LICENSE` | 11.341 | `ee6f303260558acde280e51efed82d48c189ca64a8b4807568409f0ed23058cf` |
| `NOTICE` | 310 | `8cfae42bd1d691f592e7ff9707d5539d76fc002f509b18ca49c4c0be6022917b` |

**Für den PoC relevant ist ausschließlich `ori-linux-x64`** (Ziel ist ein Linux-Container). Der Hash `c9b67ee1…` ist der zu prüfende Referenzwert.

**Fehlende Vertrauensanker (weiterhin bestätigt):** Im Release existieren **keine** Signatur (`.sig`), **kein** Sigstore-/Cosign-Nachweis, **kein** SLSA-Provenance-Dokument und **keine** SBOM. `LICENSE` und `NOTICE` sind vorhanden, ersetzen aber keine Lieferkettentransparenz.

### 3.2 Installer-Verhalten (aus dem Quelltext gelesen)

**Positiv zu bewerten:**
- HTTPS wird erzwungen (`curl --proto '=https'`), zusätzlich `-f` und `--retry`.
- SHA-256-Prüfung gegen `SHA256SUMS` (`verify_download`, Auswahl über `awk '$2 == name'`).
- Atomare Installation: `mktemp` → `cp` → `chmod +x` → `mv -f`.
- **Symlink-Schutz:** `verify_symlink_safe()` überschreibt `/usr/local/bin/ori` nur, wenn das Ziel unter `$HOME/.local/`, `/usr/local/` oder `$HOME/.npm-global/` liegt; sonst Warnung und Überspringen.
- `ORI_INSTALL_DIR` muss absolut sein und darf kein `..` enthalten.

**Kritisch / zu begrenzen:**
- **Systemeingriffe:** `patch_rc_path()` schreibt einen Markerblock (`# >>> ori >>>`) in `.zshrc` bzw. `.bashrc` sowie zusätzlich in `.profile` und `.bash_profile`. `ensure_usr_local_link()` legt/ersetzt `/usr/local/bin/ori` an, bei Bedarf über `sudo` (`has_passwordless_sudo()`).
- **Bewegliche Quelle:** Download-Basis ist `releases/latest/download`. Das konkrete Release ist zwar `immutable`, der `latest`-Pointer kann aber auf ein neues Release wandern → **immer pinnen**, nie `/latest` verwenden.
- **Telemetrie (standardmäßig aktiv):** Ziel `https://openrouter.ai/api/v1/ori/telemetry`, gesendet per Exit-Trap. Nutzlast enthält `install_id`, `session_id`, `ts`, `cli_version`, `os`, `arch`, `channel`, `libc`, `status`, `stage`. Abschaltung nur über `ORI_TELEMETRY=0` (oder `false`).
- **Alpha-Kanal:** `ORI_CHANNEL=alpha` lädt ein Pre-Release von `raw.githubusercontent.com/.../version-alpha`. Für uns **verboten** — nur `stable`.
- Die Runtime-Telemetrie des Binaries selbst ist öffentlich nicht ausreichend dokumentiert.

---

## 4. Projektspezifische Risikoanalyse gegen die RadiMorphic-Sicherheitsbaseline

Grundlage: `docs/deep-audit-2026-07-10/PHASE_2_SECURITY_DSGVO_AUTH_MULTITENANT.md`. Die dortige Baseline ist für die Ori-Frage entscheidend, weil sie den **Schutzbedarf der Daten** definiert, die ein repo-scanendes Werkzeug potenziell erfasst.

| Kürzel | Befund (Schwere) | Relevanz für Ori |
|---|---|---|
| **S-07** (hoch) | Personenbezogene und potenziell Gesundheitsdaten liegen **in Klartext** in JSON/Exporten; Dateinamen enthalten Identifikatoren. Verschlüsselung at rest: „nicht gefunden". | Ori liest laut Dokumentation Datendateien (CSV/JSONL), Prompts, Tests und erwartete Antworten → direkter Abflussweg für Klartextdaten. |
| **S-05** (hoch) | Tenant-Isolation ist nur **Pfadkonvention**; `MORPHIC_TENANT_ID` nicht aus authentisiertem Principal; explizite Output-Pfade nicht isoliert. | Mandantenbezüge sind über Pfade/Dateinamen sichtbar und würden mitgelesen. |
| **S-13** (hoch) | Web-Scan-Launcher übergibt harten Exportroot `C:\Benutzer_Archive_Start`; Tenant-Suffix-Logik greift dort nicht. | Daten liegen auch außerhalb tenant-suffixierter Pfade → ein „wir scannen nur tenant-isolierte Bereiche"-Argument trägt nicht. |
| **S-14** (hoch) | Dynamische Werte werden teils unescaped via `innerHTML` eingebettet. | Kontext: Das Projekt hat bekannte Härtungslücken; zusätzliche Fremdwerkzeuge erhöhen die Angriffsfläche. |
| DSGVO | Rechtsgrundlage, TOMs, AV-Vertrag, Schlüsselmanagement, Aufbewahrung sind **nicht im Code abgebildet**. | Ein Ori-Lauf mit realen Daten wäre ohne AV-Vertrag/DPA nicht belastbar begründbar. |
| Auth | Echte AuthN/AuthZ/RBAC **nicht vorhanden**; `operator_context.py` ist laut Eigenaussage nur Vorbereitungsschicht. | Kein kompensierendes Rollenmodell, das einen Fremdzugriff begrenzen könnte. |

**Schlussfolgerung:** RadiMorphic verarbeitet reale Klienten- und Gesundheitsdaten **unverschlüsselt**. Ori überträgt Testprompts und -daten an Kandidatenmodelle sowie Kriterien/Ergebnisse an ein Judge-Modell. Die Kombination ist ohne belastbare Isolation **nicht verantwortbar**.

---

## 5. Neu verifizierte lokale Gefahrenstelle (hoch)

Im **aktiven Worktree** liegen vier ungetrackte Mandanten-/Exportverzeichnisse. Geprüft wurde **nur Existenz und Dateianzahl**, keine Inhalte:

| Verzeichnis (ungetrackt) | Dateien |
|---|---:|
| `Benutzer_Archive__manual-acceptance` | 3.156 |
| `Benutzer_Archive__manual-gate4-tenant` | 1.248 |
| `Benutzer_Archive__live-gate-v6-tenant` | 660 |
| `Benutzer_Archive__webui-acceptance-9700` | 330 |
| **Summe** | **5.394** |

Zusätzlich ungetrackt: `data/harmonization_jobs/harm_ba41c018.lock`.

Diese Verzeichnisse sind in `git status` als `??` (untracked) sichtbar, liegen aber **im Arbeitsbaum**. Ein Werkzeug, das Verzeichnisse rekursiv nach Prompts/Tools/Datendateien durchsucht, erfasst sie. Gemäß S-07/S-13 können darin Klienten- und Gesundheitsdaten im Klartext liegen, z. T. mit identifizierenden Dateinamen.

**Hartes Verbot (für den Entwickler bindend):**
> Ori — oder ein vergleichbar repo-scanendes Werkzeug — darf **niemals** im aktiven Worktree `C:\morphic_v1\.worktrees\operator-workbench-phase1`, im Root-Container `C:\morphic_v1` oder unter `/opt/Prototypen/Radimorphic` ausgeführt werden.

Vor jedem späteren, über den Fixture-PoC hinausgehenden Versuch sind diese Verzeichnisse aus dem Arbeitsbaum zu entfernen bzw. auszulagern — **nicht** nur per `.gitignore` zu verstecken.

---

## 6. Aktualisierte Risikomatrix

| Prio | Befund | Beleg / Stand | Gegenüber Vorprüfung |
|---|---|---|---|
| **P1** | Geschlossenes Binary (~109 MB) ohne öffentlich prüfbaren Quellcode, ohne SBOM, ohne Signatur, ohne Provenance. SHA-256 schützt nur vor Transferfehlern, nicht vor Herkunftsfälschung. | Release-Metadaten 2026-09-01 | **Bestätigt, unverändert** |
| **P1** | Datenabfluss an OpenRouter + Modellanbieter (Kandidaten- und Judge-Modell). Provider-Policies uneinheitlich, teils Trainingsnutzung; OpenRouter garantiert Anbieterverhalten nicht. | Ori-Docs, Privacy, Provider-Logging | **Bestätigt** |
| **P1** | Ausführung im aktiven Worktree würde 5.394 Dateien ungetrackter Mandantenexporte einbeziehen → potenzieller Abfluss realer Klienten-/Gesundheitsdaten (Klartext, S-07). | Eigene Messung 2026-09-01 | **NEU, hoch** |
| **P1** | Installer verändert rc-Dateien und `/usr/local/bin`, ggf. mit `sudo` → als `root` oder auf dem Debian-Server inakzeptabler Schadensradius. | Installer-Quelltext | **Bestätigt, präzisiert** |
| **P2** | Bewegliche Installationsquelle (`releases/latest`, `curl \| bash`); Release zwar `immutable`, Pointer aber wandernd. | Installer-Quelltext | **Bestätigt, nuanciert** |
| **P2** | Telemetrie standardmäßig aktiv (Opt-out `ORI_TELEMETRY=0` vorhanden). | Installer-Quelltext | **Bestätigt** |
| **P2** | Alpha-Kanal verfügbar (`ORI_CHANNEL=alpha`) → Pre-Release-Risiko, muss verboten werden. | Installer-Quelltext | **NEU** |
| **P2** | Speicherort, Dateirechte und Verschlüsselung persistierter Ori-Credentials öffentlich nicht ausreichend dokumentiert. | Ori-Dokumentation | **Bestätigt** |
| **P2** | Natürlichsprachliches Kostenlimit ist kein belegter harter Gesamtdeckel → Guardrails/Key-Budget zwingend. | Guardrails-Docs | **Bestätigt** |
| **P3** | Keine Drittanbieter-SBOM trotz vorhandener `LICENSE`/`NOTICE`. | Release-Metadaten | **Bestätigt** |
| Positiv | HTTPS erzwungen · SHA-256-Prüfung · atomare Installation · Symlink-Guard · Release `immutable` | Installer + Release | **Bestätigt** |

---

## 7. Freigabeentscheidung

| Einsatzszenario | Entscheidung |
|---|---|
| Produktiv / Debian-Server `/opt/Prototypen/Radimorphic` | **ABGELEHNT** |
| Aktiver Worktree (Mandantenexporte, Gate-5-Bytes) | **ABGELEHNT** |
| Realer RadiMorphic-Quellbaum oder reale Klientendaten | **ABGELEHNT** |
| Isolierter Funktions-Smoke mit synthetischem Fixture im Container | **VERTRETBAR unter den Bedingungen in Abschnitt 8** |

Begründung in einem Satz: Es gibt **keinen Hinweis auf offensichtliche Malware** im geprüften Installer, aber das zentrale Binary ist nicht quelloffen verifizierbar, und das Projekt hält unverschlüsselte Klienten-/Gesundheitsdaten in Reichweite eines repo-scanenden Werkzeugs — daraus folgt Isolationspflicht, kein generelles Verbot eines kontrollierten Fixture-Tests.

---

## 8. Isolationsdesign (vom Auftraggeber festgelegt)

Vom Nutzer verbindlich gewählte Eckpunkte:

| Entscheidung | Wert |
|---|---|
| Ausführungsort | **Container auf Windows** (Docker Desktop + WSL2) |
| Runtime | Docker Desktop mit WSL2-Backend |
| Datenbasis | **Rein synthetisches Mini-Projekt** — keine RadiMorphic-Dateien, keine Klientendaten, keine `.git`-Historie, keine Secrets |
| Ziel | **Sicherer Funktions-Smoke** — Ori läuft im Container, sieht nur das Fixture, respektiert read-only/Netz-/Kostenlimits, erzeugt einen kleinen Eval-Report |

**Harte Regeln (bindend):**

1. **Kein Mount** des aktiven Worktrees, des Root-Containers `C:\morphic_v1` oder von `/opt/Prototypen/Radimorphic`.
2. Nur **ein dediziertes Fixture-Verzeichnis read-only** einbinden; kein Mount von `Benutzer_Archive__*`.
3. `/tmp` als **einziger beschreibbarer** Arbeitsbereich (tmpfs).
4. Container **ohne privilegierte Rechte**; **kein** `docker.sock`-Mount; **kein** Host-Netzwerk; keine Capability-Erweiterung.
5. Netzwerk-Egress per **Allowlist** begrenzen (Download: GitHub-Releases; Betrieb: `openrouter.ai`), idealerweise über separates Docker-Netz mit Proxy — keine pauschale Freigabe.
6. **Gepinntes Release** `cli-0.12.1-e1631f8` laden, **nicht** `/latest`. SHA-256 **außerhalb** des Downloads gegen `c9b67ee18ae892045dc55266cc9285f9b9e8b5d9e1827d5fdb89c87773057a7d` verifizieren.
7. `ORI_TELEMETRY=0` setzen; `ORI_CHANNEL` **nicht** auf `alpha` setzen.
8. Dedizierter, **kurzlebiger** OpenRouter-Key: ZDR aktiv, Modell-/Provider-Allowlist, Prompt-Logging/Training aus, **hartes Budget**, Guardrail tatsächlich dem Key zugewiesen (Zuweisung verifizieren — häufige Fehlerquelle).
9. Kein persistenter Credential-Speicher im Container; Key nach dem Lauf **widerrufen**; Container/Volume/Image anschließend löschen.
10. Nachweis führen, dass **kein** Projekt- oder Mandantenpfad im Container sichtbar ist (Mount-Liste).

---

## 9. Kosten- und Schlüsselstrategie — OFFENER PARAMETER

**Wichtig:** Die Frage nach dem konkreten Budgetbetrag wurde vom Auftraggeber **nicht beantwortet**. Das Budget ist daher ein **offener Parameter** und muss **vor** dem ersten Start festgelegt werden. Es wird hier bewusst **kein** Betrag unterstellt.

Mindestanforderungen an den Key:

- Kleiner, **hart gedeckelter** Betrag über OpenRouter-Guardrail/Key-Budget — kein ungedeckelter Key.
- **ZDR aktiviert** (Zero Data Retention) — verringert, beseitigt aber das Restrisiko nicht, da Plugins/Tools eigene Policies haben können und In-Memory-Caching laut Dokumentation nicht als Speicherung gilt.
- **Modell- und Provider-Allowlist**; Logging/Training deaktiviert.
- **Guardrail-Zuweisung an genau diesen Key verifizieren** (nicht nur anlegen).
- Nach dem Smoke: **Key widerrufen** und Verbrauch dokumentieren.

---

## 10. Verifikations- und Abnahmekriterien (Nachweispflicht)

Der Entwickler liefert zu jedem Punkt einen konkreten Beleg (Befehl + Ausgabe):

- [ ] Container-Definition/Image dokumentiert, Basis-Image mit Datum/Version.
- [ ] Mount-Liste zeigt **ausschließlich** Fixture (read-only) + `/tmp`.
- [ ] Kein Projekt-/Mandantenpfad gemountet (Beleg via `docker inspect` bzw. `mount`).
- [ ] Binary-Hash verifiziert gegen `c9b67ee18ae892045dc55266cc9285f9b9e8b5d9e1827d5fdb89c87773057a7d`.
- [ ] `ORI_TELEMETRY=0` im Container gesetzt (Beleg via `env`).
- [ ] `ORI_CHANNEL` nicht `alpha` (Beleg via `env`).
- [ ] Egress-Allowlist aktiv und nachgewiesen.
- [ ] Key mit ZDR + Allowlist + Budget; Guardrail-Zuweisung geprüft.
- [ ] Dry-Run ohne Modellaufruf erfolgreich (Installation, `--version`, Hilfe).
- [ ] Smoke-Lauf gegen Fixture erzeugt erwarteten, kleinen Report.
- [ ] Keine Lesezugriffe außerhalb des Fixtures (über read-only-Mounts + optionale Audit/Strace-Sichtung, soweit vertretbar).
- [ ] **Aktiver Worktree unverändert:** `git status --short --branch` und HEAD weiterhin `151e2bb`.
- [ ] Anschließend: Key widerrufen, Container/Volume/Image entfernt, Ergebnis + Kosten dokumentiert.

---

## 11. Übergabe an den Entwickler — Reihenfolge und Stop-Gates

**Reihenfolge:**

1. **Budget festlegen** (Stop-Gate: ohne festes Budget kein Start).
2. **Synthetisches Fixture definieren** — kleine, klar umrissene Aufgabe mit erwarteter Antwort; keine RadiMorphic-Bestandteile.
3. **Container-Definition erstellen** (Docker Desktop/WSL2) mit gepinntem Download und Hash-Prüfung im Build.
4. **Dry-Run ohne API-Key / ohne Modellaufruf** — prüft Startbarkeit des Binary und Datenzugriff, ohne Kosten und ohne Datenabfluss.
5. **Erst dann** Smoke mit Modellaufruf gegen das Fixture.
6. Auswertung → Key-Widerruf → Löschung von Container/Volume/Image → Dokumentation.

**Stop-Gates (Abbruchbedingungen):**

- Kein Ori-Lauf gegen `/opt/Prototypen/Radimorphic`, den aktiven Worktree oder `C:\morphic_v1`.
- Keine Änderung an Gate-5-Bytes; Gate 5/6 bleiben vom PoC unberührt.
- Bei unerwarteten Lesezugriffen außerhalb des Fixtures: **sofort abbrechen**, Key widerrufen, Vorfall dokumentieren.
- Ein reiner Tool-Completion-Fehler ohne Verdict ist **kein** negatives Ergebnis; nur die Prüfung wiederholen, wenn der Eingabestand unverändert ist.

---

## 12. Offene Punkte — Rückfragen an OpenRouter

Vor jeder Ausweitung über den Fixture-Smoke hinaus zu klären:

1. Vollständiger Quellcode, reproduzierbarer Build und SBOM?
2. Signierte Artefakte (Cosign/Sigstore) oder SLSA-Provenance geplant?
3. Welche **exakten** Repository-Ausschnitte überträgt der Authoring-Agent an Modelle? Maximale Größe? Lässt sich eine Include-Whitelist erzwingen?
4. Runtime-Telemetrie des Binaries: Umfang, Inhalt, Aufbewahrungsfrist, Opt-out?
5. Speicherort, Dateirechte und Verschlüsselung persistierter Credentials?
6. Besteht ein **AV-Vertrag / DPA** (DSGVO)? Werden Inputs für Training genutzt?
7. Gibt es eine dokumentierte, **harte** Gesamtkostenbremse?
8. Ist `--hermetic` eine echte Sandbox (Netzwerk, Prozesse, Dateisystem) oder nur ein Ausschluss von Personas/Skill-Roots?

Solange diese Punkte nicht belastbar geklärt sind, bleibt jede Ausweitung auf reale Projektdaten **unzulässig**.

---

## Anhang A — Ori-Belegquellen (alle gelesen am 2026-09-01)

| Quelle | URL |
|---|---|
| Installer (Shell) | `https://openrouter.ai/labs/ori/install.sh` |
| Release-Metadaten (API) | `https://api.github.com/repos/OpenRouterLabs/ori-releases/releases/latest` |
| Release (HTML) | `https://github.com/OpenRouterLabs/ori-releases/releases/tag/cli-0.12.1-e1631f8` |
| Release-Repository | `https://github.com/OpenRouterLabs/ori-releases` |
| Agentenanweisung | `https://openrouter.ai/skills/spawn-ori-eval` |
| Ori Eval Dokumentation | `https://openrouter.ai/docs/guides/ori/eval` |
| Zero Data Retention | `https://openrouter.ai/docs/guides/features/zdr` |
| Guardrails | `https://openrouter.ai/docs/guides/features/guardrails` |
| Datenschutz | `https://openrouter.ai/privacy` |
| Provider-Logging | `https://openrouter.ai/docs/guides/privacy/provider-logging` |

## Anhang B — Projektbelege (gelesen am 2026-09-01)

| Dokument | Relevanz |
|---|---|
| `PROJECT_MEMORY/00_CURRENT_STATE.md` | Golden Record, Gate-Status, Arbeitsort |
| `PROJECT_MEMORY/2026-08-09-gate5-linux-migration-handoff.md` | Debian-Pfad, Migrationsbranch, Fortsetzungspunkt |
| `docs/deep-audit-2026-07-10/PHASE_2_SECURITY_DSGVO_AUTH_MULTITENANT.md` | S-05, S-07, S-13, S-14, DSGVO-Abgleich |

## Anhang C — Lokale Prüfbefehle (lesend)

```powershell
# Arbeitsort und Stand
git branch --show-current
git log -1 --format='%H %d %s'
git status --short --branch

# Existenz ungetrackter Mandanten-/Exportverzeichnisse (nur Anzahl)
foreach ($d in @('Benutzer_Archive__live-gate-v6-tenant','Benutzer_Archive__manual-gate4-tenant',
                 'Benutzer_Archive__manual-acceptance','Benutzer_Archive__webui-acceptance-9700')) {
  if (Test-Path -LiteralPath $d) {
    $c = (Get-ChildItem -LiteralPath $d -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    "$d EXISTS files=$c"
  } else { "$d MISSING" }
}
```

**Für den PoC zu prüfender Referenz-Hash (Linux-x64):**

```text
Asset:   ori-linux-x64
Version: 0.12.1+e1631f8  (Tag cli-0.12.1-e1631f8)
SHA-256: c9b67ee18ae892045dc55266cc9285f9b9e8b5d9e1827d5fdb89c87773057a7d
```

---

**Ende des Dokuments.** Erzeugt 2026-09-01T232218+02:00. Streng lesende Analyse; das einzige erzeugte Artefakt ist diese Datei.
