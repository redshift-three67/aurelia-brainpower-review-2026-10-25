# RadiWorks Engine (Prototyp, Stufe 2)

Python-Port der AetherOnePi-Kernlogik als Kernel-ABI-v1-konformer FastAPI-Dienst.
**Wellbeing-Dokumentationssoftware — kein Medizinprodukt, keine Diagnose, keine Therapie.**

## Installieren & Starten

```bash
cd engine
py -3 -m venv .venv
.venv/Scripts/pip install -e ".[dev]"      # Windows/Git-Bash
.venv/Scripts/pytest                        # Testlauf

.venv/Scripts/python.exe run.py             # Server auf 127.0.0.1:8090
# optional: RADIOWORKS_HOME ausserhalb des Projektbaums festlegen
# alternativ (ohne Startskript):
.venv/Scripts/uvicorn "radiworks.main:create_app" --factory --port 8090
```

- REST-Basis: `http://127.0.0.1:8090/` (Endpunkte: `docs/../../Modul_Templates/standards/API_CONTRACT.md`)
- WebSocket-Fachkanal: `ws://127.0.0.1:8090/ws` (Umschlag `{v:1, id, boot, type, payload, ts}`; Kontroll-ID `0`, Fachereignisse mit positiver ID)
- Lokaler Browserzugriff: HTTP und WebSocket akzeptieren nur Loopback-Hosts (localhost, 127.0.0.1, ::1) und vorhandene Browser-Origins mit Loopback-Host. Das begrenzt fremde Origins und DNS-Rebinding im lokalen Preview, ersetzt aber weder Authentisierung noch den späteren Aurelia-Hostvertrag. Die Engine weiterhin nur an Loopback binden.
- Selbstbeschreibung: `GET /manifest` (Kernel-ABI v1, Aurelia docs/06-kernel-abi.md)
- Laufzeitdaten (Daten/Cases/Drafts): standardmaessig `~/.radiworks`, alternativ
  über `RADIOWORKS_HOME` oder `create_app(base_dir=...)`. Sie gehören nicht in
  den ausgecheckten Projektbaum.
- Case-/Draft-Mehrdateioperationen erhalten vor dem ersten Schreiben einen
  privaten Recovery-Marker unter `${RADIOWORKS_HOME}/recovery`. Nach einem
  Abbruch stellt der nächste Start den vollständigen Endzustand wieder her; bei einem
  Fremdedit- oder Marker-Konflikt startet die Engine fail-closed. Pro
  `RADIOWORKS_HOME` ist genau eine laufende Engine zulässig. Eine OS-Dateisperre in
  `.engine.lock` erzwingt dies während des gesamten App-Lebenszyklus. Die Datei
  bleibt bestehen; die Sperre wird bei normalem Ende und Prozessabbruch
  freigegeben. Der Windows-Pfad ist prozessübergreifend getestet; der
  Linux-Pfad benötigt vor Deployment einen eigenen Integrationslauf.
- Broadcast-Queue, aktive Broadcasts, Auto-Modus und WebSocket-History bleiben
  bewusst flüchtig und werden durch Recovery nicht wiederhergestellt.
- Rate-Katalog: `RADIOWORKS_DATA_DIR` verweist optional auf einen separaten,
  read-only `.txt`-Katalog. Ohne Variable gilt `${RADIOWORKS_HOME}/data`.
  Beispiel für einen lokalen Preview: nur `RADIOWORKS_DATA_DIR` auf den
  freigegebenen Katalog setzen; Cases, Drafts und Journale werden nicht kopiert.
- Opt-in für unveränderliche Katalogstände: `publish_catalog_release(source_dir,
  releases_dir)` aus `radiworks.core.catalog_release` kopiert eine **zuvor
  stillgelegte** Quelle in `<releases_dir>/<32-hex-id>/data` und veröffentlicht
  sie nach Manifest-/SHA-256-Prüfung durch atomare Verzeichnisumbenennung.
  Beispiel (Python, nach `from pathlib import Path` und
  `from radiworks.core.catalog_release import publish_catalog_release`):
  `release = publish_catalog_release(Path("frozen-data"), Path("catalog-versions"))`.
  Danach vor dem **nächsten** Engine-Start `RADIOWORKS_DATA_DIR` auf
  `release / "data"` setzen. Jede Engine bindet
  genau diese Version bis zum Ende ihrer Laufzeit. Es gibt keinen automatischen
  Versionswechsel, keine Aufbewahrungs-/Löschautomatik und keine Änderung am
  vorhandenen Preview- oder Echtdatenkatalog.
- Im Release-Modus werden Manifest, Dateiliste und SHA-256 beim Start geprüft;
  verwendete Raten und benannte Skripte werden vor der Verarbeitung gegen das
  Manifest geprüft. Abweichende Bytes führen bei den betroffenen API-Pfaden zu
  HTTP 409. Stick-Pad-Belege tragen die Release-ID; normale Analysen verwenden
  `analysis-request-catalog-v1` und binden Release-ID sowie die geordneten
  analysierten Raten in den Input-Hash ein. Im bisherigen Katalogmodus bleibt
  `analysis-request-v2` unverändert. Die Release-ID ist eine Referenz, keine
  Signatur oder Garantie, dass der Stand später noch aufbewahrt wird.
- Die Quelle muss während der Veröffentlichung vom Betreiber schreibgeschützt
  oder anderweitig stillgelegt sein. Ein extern veränderbarer Quellbaum kann
  trotz Nachprüfung ABA-/Mischstände erzeugen; der Publisher ist keine
  Schreibersperre. Veröffentlichte Verzeichnisse dürfen nicht bearbeitet oder
  umgeleitet werden. Manipulationen werden beim Lesen geprüft, aber kein
  Schutz vor einem absichtlich schreibenden Angreifer zugesagt. Der
  Veröffentlichungs- und Sperrpfad wurden zusätzlich in lokalem Ubuntu-WSL
  mit künstlichen Daten und echtem POSIX-Symlink geprüft. Der vorgesehene
  Debian-/Aurelia-Host und reale Kataloge sind vor Produktfreigabe gesondert
  abzunehmen.
- Clean Checkout: `run.py --bootstrap-synthetic-catalog` legt einmalig einen
  rein synthetischen Preview-Katalog unter `${RADIOWORKS_HOME}/data` an. Der
  Schalter überschreibt nie vorhandene Kataloge und ist bei gesetztem
  `RADIOWORKS_DATA_DIR` gesperrt. Er enthält keine Betreiber-, Fall-, Clarke-
  oder externen Rate-Daten und ist keine fachliche oder Java-Paritätsevidenz.
- S4.3-Ausgabegrenze: HTTP-JSON-Antworten und WebSocket-Fachereignisse ersetzen
  vom lokalen CopyGuard-Lexikon gesperrte Texte durch
  `[CopyGuard: Text zurückgehalten]`. Interne Analyse-, Draft-, Fall- und
  Passportdaten bleiben unverändert; Queue- und Promote-Sperren prüfen weiter
  das Original. Bei der Fallbearbeitung verwendet die Webapp
  `POST /cases/current/metadata` für Name, Beschreibung und letzte Absicht.
  Ein vollständiges Zurückspeichern eines geschwärzten Falls über `POST /cases`
  wird mit 409 abgelehnt, damit Rohdaten nicht unbemerkt ersetzt werden.
  Die lokale Lexikon-Stufe und der [isolierte Browser-Smoke](tools/browser_smoke/README.md)
  sind keine Abnahme aller Textflächen oder der späteren Aurelia-Stufe.
- S4.6-Fallauswahl: `GET /cases` und `/cases/recent` liefern zusätzlich
  `entries` mit `name` und opakem `ref`; `/cases/ref/{ref}/activate`,
  `/cases/ref/{ref}/statistics` und `/cases/current/ref` trennen die
  Fallidentität vom projizierten Anzeigenamen. Die bisherigen Namens-Endpunkte
  bleiben vorhanden. Referenzen gelten nur für den aktuellen Engine-Lauf;
  nach Neustart muss die UI einen frischen Verweis aus der Liste wählen.
  Persistierte Falldateien werden dafür weder geändert noch gelöscht.

## Architektur-Entscheidungen (abweichend vom Java-Original, aurelia-begründet)

| Entscheidung | Grund |
|---|---|
| Entropie **seeded** als Default; `stochastic` explizit per Request | Aurelia Hard Rule 7: strikte Reproduzierbarkeit ist Default |
| Analyse erzeugt **AnalysisDraft** (Status `draft → client_review → ready → promoted`) | D18: Harmonisierung startet nur nach Promote aus der Zwischenablage |
| **Computation Passport** je Lauf (`run_id`, `kernel_hash`, `input_hash`, `seed`, `dauer_ms`, Quellen) | docs/04-compute.md — Verträge leben länger als Libraries |
| WebSocket-Umschlag `v:1` mit Boot-ID, monotoner Fachereignis-ID + bootbewusstem Reconnect | docs/15-live.md |
| Broadcast rein ereignisbasiert (`isHardwareActivatable: false`) | Hard Rule 4/10: Server ist die Uhr, keine USB-/GPIO-Aktivierung |
| LED-Gruppen des Pi nur als Datenstruktur (`BROADCAST_LED_GROUPS`) | späterer `aurelia-emitterd`-Anschluss (Lease → Arming → ACK) |
| CopyGuard-Lexikon fail-closed im Kernel (LLM-Stufe bleibt Plattform) | docs/16-wellbeing.md — Klartext nie in fremde Systeme |
| Draft/Case-Schemas mit `tenant_id`/`client_id` (nullable) | Hard Rule 8: Scoping-Pflicht vorbereitet |

### Entropie und Reproduzierbarkeit

- Java-Orakelparität ist ausschließlich für den seeded `POST /analysis`-Pfad mit
  300 synthetischen Raten (`R0000`–`R0299`) belegt: Seed 42 bei `max_hits=100`,
  Seed 20260829 bei `max_hits=100` und Seed 42 bei `max_hits=1000` (JDK 24.0.1).
  Verglichen werden `generalVitality`, `numberOfTrials` und `rateObjects`.
- `stochastic` priorisiert Webcam-/Hotbits-Seeds (FIFO), danach die explizit
  freigegebene random.org-Quelle und zuletzt den OS-CSPRNG. Netzverkehr findet
  nur in diesem Modus statt; Ausfälle fallen ohne Abbruch auf OS-Entropie zurück.
- Passports führen den wirksamen `seed`, `replayable` und `seed_scheme`.
  Stochastic-Läufe sind bewusst nicht replaybar (`seed: null`). Historische
  Passports ohne diese Felder verwenden die frühere abgeleitete Seed-Semantik.
- `entropy.defaultMode` akzeptiert ausschließlich `seeded` oder `stochastic`.
  Ungültige Werte werden als HTTP 422 abgewiesen und nicht stillschweigend
  normalisiert.
- Für eine persistierte stochastic Fall-/GV-Historie muss das Deployment einen
  Fernet-Schlüssel in `RADIOWORKS_JOURNAL_KEY` bereitstellen. Der Schlüssel und
  Roh-Seeds gehören weder in den Projektbaum noch in Cases, Drafts, Passports,
  Logs oder WebSocket-Ereignisse; verschlüsselte Journale bleiben bis zur
  expliziten Falllöschung im externen Runtime-Home.


- Der Auto-Regler läuft nur bei leerer **wartender** Queue. Bereits aktive Broadcasts bleiben zulässig und bestimmen den Cooldown `aktiv² × 111 ms`.
- Die Ratenauswahl folgt dem verifizierten Original-Bytecode: Übersprungen wird `Raten-GV <= 1400 UND Raten-GV <= Fall-GV + 700`; die erste Rate außerhalb dieser beiden Grenzen wird gesendet.
- Sicherheitsabweichung vor dem Auto-Einreihen: Blockiert CopyGuard die gewählte Signatur, stoppt der Auto-Modus mit `auto.error`/`auto.mode`; die Queue bleibt unverändert. Die Auswahl wird nicht heimlich auf eine andere Rate verschoben.
- Jede Broadcast-Instanz besitzt eine unveränderliche `broadcastId`; dadurch bleiben auch gleichzeitig laufende identische Signaturen getrennt steuer- und darstellbar. „Alle stoppen“ leert aktive und wartende Einträge, der Auto-Modus bleibt separat über AUTO OFF steuerbar.
- Jede WebSocket-Verbindung beginnt mit dem nicht historisierten Kontrollereignis `server.hello` (`id: 0`); dessen `cursor` markiert die bereits übersprungene/zugestellte Replay-Untergrenze. Fachereignisse besitzen positive IDs und werden für Reconnects vorgehalten.
- Neue Clients senden `last_event_id` und `last_boot`. Bei gleicher Boot-ID wird ab der letzten ID replayt; nach einem Engine-Neustart wird die History des neuen Boots von vorn geliefert. Ist der Cursor älter als die begrenzte History oder unplausibel zukünftig, fordert `server.replay_gap` einen REST-Zustandsabgleich an.

### REST-ABI und Computation Passport

- Der verbindliche Kernel-ABI ist die versionierte REST-Operation `POST /analysis`; `GET /manifest` beschreibt deren Request- und Response-Umschlag mit camelCase-Ergebnisfeldern und Draft-Zusammenfassung.
- Der bisherige Callable-Eintrag bleibt nur als `deprecated-compatibility`-Metadatum für eine Minor-Release-Übergangszeit bestehen. Neue Integrationen verwenden den REST-Operationseintrag.
- Neue Passports tragen `passport_schema_version: 2`. Der bisherige Modus
  verwendet `input_hash_scheme: analysis-request-v2` und bindet Datenbank,
  wirksamen Seed, aufgelösten Entropie-Modus und `max_hits`. Der opt-in
  Release-Modus verwendet `analysis-request-catalog-v1` und bindet zusätzlich
  Release-ID und Digest der geordneten Raten. `GET /manifest` erlaubt beide
  tatsächlichen Schemata. Historische Passports ohne diese Felder bleiben
  Legacy-v1-Artefakte.
- `signatur` ist eine deterministische, **unsigned** Provenienz-Prüfsumme (`signatur_status: "unsigned"`), keine kryptografische Signatur, Attestierung oder Autorisierung.
- Seeded Kernalgorithmen werden nur für separat nachgewiesene, versionierte Java-Orakelpfade als paritätsfähig beansprucht. Stochastic bleibt bewusst nicht replaybar und außerhalb der Java-Paritätsbehauptung.

## Verhältnis zum Java-Original

Die explizit referenzierten Kernalgorithmen werden in `tests/` gegen die in
`Radiworks/docs/FUNKTIONSANALYSE.md` dokumentierte Bytecode-Logik geprüft
(Seed-Determinismus ersetzt die Hotbit-Abhängigkeit in Tests). Eine pauschale
Bitidentität des gesamten Python-Produktionspfads mit der Java-Laufzeit ist
noch nicht behauptet; Java-PRNG, HashMap-Reihenfolge und REST-Pfad werden in
der [Roadmap](../ROADMAP.md) getrennt als Paritätsvertrag abgeschlossen. Die
konkreten Belege und offenen Grenzen stehen in der
[Java-/Python-Paritätsmatrix](PARITY_MATRIX.md).
Bewusste, dokumentierte Bereinigungen: Regex-Injection im Such-Highlighting,
toter Nitrite-Datenbankpfad, Doppelimplementierung HotbitsClient/HotbitsHandler.

## Grenzen des Prototyps

- Materia-Medica-Suche: gewichtete Token-Suche (Lucene-Ersatz minimal); FTS-Upgrade offen.
- Broadcast-Visualisierung (Fibonacci-Ästhetik) liegt in der Webapp (P3), nicht hier.
- Kopie der Rate-Datenbanken und Clarke-Korpora: beim Start in `radiworks_home/` einzuspielen
  (Quellordner: `Radiworks/materiaMedica/Clarke`, `data/` aus radionics-rates).
