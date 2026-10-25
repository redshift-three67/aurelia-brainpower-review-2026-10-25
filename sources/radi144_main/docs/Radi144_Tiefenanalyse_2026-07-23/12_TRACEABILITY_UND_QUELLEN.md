# 12 - Traceability und Quellen

## 1. Methodik

Die Analyse basiert auf:

1. Repositoryinventar und Gitstatus,
2. vollständiger/gezielter Quelltextlektüre,
3. parallelen Read-only-Analysen nach Fachbereich,
4. Abgleich vorhandener Dokumentation gegen ausführbaren Code,
5. aktuellen Test-, Syntax- und Dependencychecks,
6. Konsolidierung redundanter Befunde,
7. Priorisierung nach Eintritt, Auswirkung und Einsatzszenario.

Vorhandene alte Tiefenanalysen wurden nicht als Wahrheit übernommen. Sie dienten nur dazu, Claims und historische Annahmen zu finden.

## 2. Repositorysnapshot

| Merkmal | Wert |
|---|---|
| Pfad | `C:\Users\Hubert111\Documents\Radi144` |
| Branch | `fix/r144-frontend-synergy` |
| HEAD | `9649e9b` |
| Datum | 23.07.2026 |
| Dirty | ja |
| geändert | `main.py`, `user_workflow.css`, `user_workflow.html`, `user_workflow.js` |
| unversioniert | `tests/test_standalone_ui_serving.py`, zwei `_old`-UI-Dateien |
| Git-Remote | keiner gefunden |

## 3. Kernbefunde mit Quellstellen

| ID | Befund | Primärquelle |
|---|---|---|
| T01 | Direktstart bindet loopback-sicher auf Port 8090 | `main.py:124-142` |
| T02 | API-Key ist bei leer/Placeholder aus | `main.py:87-98` |
| T03 | Gate schützt auch UI-Assets | `main.py:94-107` |
| T04 | Browser sendet keinen API-Key | `user_workflow.js:1042-1046`, `:1543-1547` |
| T05 | WebSockets akzeptieren ohne Auth | `app/api/resonance.py:1072-1138` |
| T06 | globales Engineobjekt | `app/api/resonance.py:27-33` |
| T07 | freie Ausgabeziele | `app/api/resonance.py:128-135`, `:864-874` |
| T08 | freie bestehende Eingabepfade | `app/api/resonance.py:212-228` |
| T09 | DB-Scan liest bis 5.000 Einträge | `app/api/resonance.py:642-693` |
| T10 | PDF-Matrix nur quadratisch, nicht größenbegrenzt | `app/api/resonance.py:696-711` |
| T11 | Client-/Sessionarchivierung nacheinander | `app/api/resonance.py:83-125`, `:441-458` |
| T12 | `client_data` kann Analyse, `client_id` Archiv bestimmen | `app/api/resonance.py:83-102`, `:279-305` |
| T13 | wirkungslose Requestfelder | `app/schemas/resonance.py:12-17`; Enginecall `resonance.py:441-452` |
| T14 | schwache Matrix-/Stringvalidierung | `app/schemas/resonance.py:8-29` |
| T15 | Engineantwort verliert Felder an API-Grenze | `resonance_engine.py:486-516`; `resonance.py:255-276` |
| T16 | Name-/Geburts-/Organuhr-Heuristik | `client_signature.py:29-129`, `:304-436` |
| T17 | Geburtszeit-Typmismatch | `schemas/klienten.py:9-11`; `client_signature.py:329-337` |
| T18 | Organuhr-Mitternachtslücke | `client_signature.py:349-373` |
| T19 | Gruppensignatur ist skalares Mittel | `client_signature.py:131-159` |
| T20 | Bildbasename ist Teil der Signatur | `client_signature.py:233-247` |
| T21 | Base64-Datei hat Zufallsnamen | `app/api/resonance.py:231-252`, `:330-343` |
| T22 | Geo nutzt Absolutwerte | `client_signature.py:250-266` |
| T23 | Planetary ist Jahrestag-Sinus | `client_signature.py:375-400` |
| T24 | DB-Vektorisierung ist Teilstringsuche | `client_signature.py:268-302` |
| T25 | Client-/Fokusvektoren sind hash-seedetes Rauschen | `resonance_engine.py:1157-1187` |
| T26 | Kandidatenzahl hardwareabhängig | `resonance_engine.py:49-97` |
| T27 | Zufallsmatrizen/-projektion und Cosinusscore | `resonance_engine.py:1031-1111` |
| T28 | Symmetrie nach Score ohne Neuberechnung | `resonance_engine.py:415-433` |
| T29 | 5-Elemente-Validierung ist No-op | `resonance_engine.py:566-575` |
| T30 | D-Wave ist Mock | `resonance_engine.py:1113-1155` |
| T31 | Precision nutzt globalen RNG und Erfolgs-Restore | `resonance_engine.py:282-303`, `:481-484` |
| T32 | HRV ist Tageszeit plus NumPy-Zufall | `resonance_engine.py:270-280` |
| T33 | Memory Guard schätzt physischen Speicher | `resonance_engine.py:999-1029` |
| T34 | EMF nutzt Timing, RNG, Last und GPU | `emf_compensator.py:132-355`, `:388-456` |
| T35 | Remote-Sensordaten nur global gespeichert | `resonance.py:1153-1200` |
| T36 | Counter-Frequency-Wirkungslabels | `emf_compensator.py:580-632` |
| T37 | EMF-Hintergrundthread | `emf_compensator.py:707-741` |
| T38 | atomarer Einzeldatei-Replace | `app/services/json_store.py:27-36` |
| T39 | kein Lock/Transaktion im JsonStore | `app/services/json_store.py:19-36` |
| T40 | Sessionmodell ohne Vollresultat | `app/models/session_archive.py:13-27` |
| T41 | Löschfallbacktoken | `app/services/erasure_service.py:30-35` |
| T42 | nicht transaktionale Löschreihenfolge | `app/services/erasure_service.py:178-233` |
| T43 | Safe-View lässt Metadata stehen | `app/services/safety_service.py:49-64` |
| T44 | Safety-Disclaimer und Marker | `app/services/safety_service.py:21-44` |
| T45 | PII in Browser-LocalStorage | `user_workflow.js:1370-1403` |
| T46 | Reset löscht nur einen LocalStorage-Key | `user_workflow.js:1335-1365` |
| T47 | unescaped `innerHTML` | `user_workflow.js:820-862`, `:1207-1238`, `:2323-2340` |
| T48 | Browsersequenz nutzt Einzelrequests | `user_workflow.js:1030-1060` |
| T49 | Browser-PDF ohne Sessionverknüpfung | `user_workflow.js:1529-1547` |
| T50 | „Excel“ ist CSV | `user_workflow.js:1569-1601` |
| T51 | UI lädt Google Fonts | `user_workflow.html:7` |
| T52 | UI nutzt Naturheil-/Heilsam-/KI-Sprache | `user_workflow.html:14-16`, `:53` |
| T53 | PowerShell nutzt Invoke-Expression | `generate_matrix.ps1:420`, `:529`, `:1034` |
| T54 | CLI-Pfade hängen von CWD ab | `dev_cli.py:118-149` |
| T55 | CLI-Logs enthalten Name/Fokus | `dev_cli.py:1332-1341` |
| T56 | Audio wird im RAM verbunden | `dev_cli.py:1458-1460`, `:1608-1627` |
| T57 | Python-Audio ist mono geschichtet | `dev_cli.py:1647-1697` |
| T58 | Busverify ist ungeschützter SHA-Check | `interchange_bus/envelope.py:123-130` |
| T59 | Bus-ACL wird nicht geprüft | `services/bus_consumer_service.py:84-105` |
| T60 | Bus nutzt WAL und JSON-Constraints | `interchange_bus/consumer_store.py:23-105` |
| T61 | Deployment rsynct breite Arbeitskopie | `deploy/setup_server.sh:32-56` |
| T62 | systemd verlangt ignorierte Env-Datei | `.gitignore:29-30`; `resonance-engine.service:10-12` |
| T63 | systemd hat Basis-Härtung | `resonance-engine.service:18-25` |
| T64 | Env-Beispiel enthält tote Settings | `deploy/server.env.example:9-22` plus Codegrep |
| T65 | Requirements sind offen und unvollständig | `requirements.txt:1-19` |
| T66 | Schnellstart empfiehlt Projektroot-http.server | `SCHNELLSTART-ANLEITUNG.md:14-32` |
| T67 | Referenzdatenherkunft/Lizenz ungeklärt | `docs/DATA_REFERENCE_AUDIT_2026-06-06.md:132-160` |
| T68 | historische Restoretools sind kein aktueller Standard | `docs/RESTORE_PACKAGING_AUDIT_2026-06-06.md:39-112` |

## 4. Claim-Traceability

| Claim | Fundstelle | Codegegenbefund |
|---|---|---|
| „KI-gestützt“ | `user_workflow.html:53` | kein trainiertes Modell; hash-seedete Zufallsvektoren |
| „10^144 possibilities“ | `README.md:7` | 80.000 bis 1.000.000 Samples |
| „>90% Akkuranz“ | `client_signature.py:1-4` | keine Ground Truth/Validierung |
| „98,7/99,2%“ | alte Tiefenanalysen | keine statistische Grundlage im Code |
| „D-Wave abgeschlossen“ | Developer Guide | Mock ohne QPU-Aufruf |
| „5-Elemente-Logik“ | `BIO_RESONANCE_DOCS.md:13-16` | No-op |
| „binaural 10 Hz“ | `BIO_RESONANCE_DOCS.md:20-23` | Python-Mono-Mix mit Quinte |
| „EMF-Echtzeitmessung“ | UI/EMF-Texte | Systemtiming, Last, RNG; optionales SDR nicht Standard |
| „bitgenau über Jahre“ | Developer Guide | Zeit-/Hardware-/EMF-/RNG-Abhängigkeiten |
| „44 passed“ | `README.md:148-155` | aktuell 92 gesammelt; Vollsuite nicht grün |
| „Port 8000“ | `README.md:66` | aktueller Direktstart Default 8090 |

## 5. Verifikationsprotokoll

### 5.1 Erfolgreiche Checks

```text
node --check user_workflow.js
```

Ergebnis: Exit 0, keine Syntaxfehler.

```text
PowerShell Language.Parser::ParseFile(generate_matrix.ps1)
```

Ergebnis: `PowerShell syntax: OK`.

```text
.venv\Scripts\python.exe -m pip check
```

Ergebnis: `No broken requirements found.`

Nicht-Engine-Pytest mit temporären BLAS-/OMP-Threadlimits:

```text
83 passed, 30 warnings in 9.83s
```

Vier leichte Engine-Tests:

```text
4 passed in 1.81s
```

Manueller Smoke mit `candidate_count=1000`:

```text
matrix 12 12 score_in_range True
```

### 5.2 Fehlgeschlagene Checks

Pytest ohne Threadlimit:

```text
OpenBLAS error: Memory allocation still failed after 10 retries, giving up.
```

Vollsuite mit Threadlimit:

```text
collected 92 items
...
RuntimeError: DefaultCPUAllocator: not enough memory:
you tried to allocate 85684224 bytes.
...
Windows fatal exception: access violation
```

Eine grüne Vollsuite darf daher nicht behauptet werden.

## 6. Hypothesen und Restunsicherheiten

### H1 - Exposition

Nicht nachgewiesen ist, ob die ignorierte lokale `deploy/server.env` auf einem tatsächlich erreichbaren Server aktiv ist. P0-Einstufungen zur Remoteausnutzung sind an diese Bedingung geknüpft.

### H2 - Externe Schutzschicht

Ein Reverse Proxy, eine Firewall, TLS oder externe Authentisierung kann außerhalb des Repositorys existieren. Im Repository gibt es keinen Nachweis.

### H3 - Datenrealität

Die Runtime enthält reale oder realistisch wirkende Daten. Ob alle Einträge Testdaten sind, wurde nicht inhaltlich bewertet. Aus Datenschutzgründen wurden keine Klarnamen in diese Analyse übernommen.

### H4 - Externe Evidenz

Wissenschaftliche, klinische oder fachliche Evidenz könnte außerhalb des Repositorys existieren. Der untersuchte Code und die Daten enthalten keinen belastbaren technischen Anschluss an solche Nachweise.

### H5 - Zielhardware

CUDA-, Linux-, systemd-, Last- und Langzeitverhalten wurden nicht auf der vorgesehenen Zielhardware ausgeführt.

### H6 - CVEs/Lizenzen

Ohne externen Vulnerability-/Lizenzscan wird keine konkrete CVE oder Rechtsverletzung behauptet. Das Risiko besteht in fehlender Reproduzierbarkeit und ungeklärter Provenienz.

## 7. Dokumentationsstatus

Als vergleichsweise belastbare Kontextquellen wurden genutzt:

- `docs/RADI144_PROJECT_INTENT_2026-06-06.md`
- `docs/DATA_REFERENCE_AUDIT_2026-06-06.md`
- `docs/GIT_BASELINE_AUDIT_2026-06-06.md`
- `docs/RESTORE_PACKAGING_AUDIT_2026-06-06.md`
- `docs/SESSION_CLIENT_REPORT_ARCHITEKTURPLAN_2026-06-03.md`

Claim-lastige oder driftende Dokumente wurden nur als Behauptungsquelle behandelt:

- `DEVELOPER_MASTER_GUIDE.md`
- `FULL_DOCUMENTATION.md`
- `BIO_RESONANCE_DOCS.md`
- `TIEFENANALYSE_CODEGEAU*.md`
- `USER_GUIDE_DE.md`
- `SCHNELLSTART-ANLEITUNG.md`

Die ausführbaren Quellen haben bei Widersprüchen Vorrang.

## 8. Nicht durchgeführte Prüfungen

- kein externer CVE-/OSV-/pip-audit-Scan,
- kein Secret-History-Scan,
- kein Lizenzscanner,
- kein Coverage-Lauf,
- kein Mypy/Ruff/ESLint/PSScriptAnalyzer/ShellCheck,
- kein Browser-E2E,
- kein dynamischer Securitytest,
- kein Last-/Parallelitäts-/Langzeittest,
- kein Linux-/CUDA-Deployment,
- kein Backup-/Restore-Drill,
- keine rechtliche oder medizinische Begutachtung.

Diese Punkte sind keine behaupteten Fehlerfreiheitssignale, sondern offene Prüflücken.
