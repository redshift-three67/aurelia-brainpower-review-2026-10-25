# RadiWorks R2: Speicherzulassung und abgesicherte Schreibpfade

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans task-by-task. Bounded independent work/review follows the operator's route B. Execute only the separately authorized block; checkboxes record evidence, not permission.

**Goal:** Aus R1 einen belegbaren Schutz gegen unkontrolliertes Wachstum ableiten, ohne Analysealgorithmen, Auftragskontexte oder gespeicherte Bestände zu verändern. Der erste ausführbare Block ergänzt die fehlenden nativen SQLite- und Transaktionsabbruchnachweise; er implementiert keinen Produktwächter.

**Architecture:** Zunächst unveränderte Produktquellen im abgeschirmten Linux-Prüfstand. Danach begrenzte Eingangsverträge und eine Rechnung pro beschreibbarem Dateisystem. Erst auf dieser Grundlage ein explizit pro App injizierter Budgetdienst mit Reservierungen vor neuer Arbeit und Prüfungen am tatsächlichen Schreibpfad. Aufnahme neuer Arbeit und Abschluss bereits angenommener Arbeit werden getrennt bilanziert. Eine Reservierung im gemeinsamen Dateisystem garantiert keine freien Blöcke gegenüber fremden Schreibern.

**Tech Stack:** Python-Standardbibliothek für Teststeuerung und Budgetkern; bestehende RadiWorks-Python-/Webarchitektur und SQLite-Konfigurationen; rootloses Docker auf vm2565, IPv4-SSH. Keine lokale Produktausführung, kein Build/Pull, kein kostenpflichtiger Scan.

## 1. Entscheidungs- und Quellenbindung

Status am 17.10.2026: **R2-0 durch Betreiberfortsetzung „dann weiter“ freigegeben und mit 31 Kontrollen sowie sechs Kapazitäts- und vier Crashfällen abgeschlossen.** R1 ist freigegeben und abgeschlossen. R2-0 umfasst ausschließlich die zusätzlichen synthetischen Tests aus Abschnitt 2 mit unveränderten Produktquellen. Die Freigabe gilt nicht für R2-Produktimplementierung oder Schutzaktivierung; R2-1 bis R2-4 bilden die abhängige Reihenfolge und benötigen ihren jeweils vervollständigten Vertrag vor Umsetzung.

| Block | Konkretes Ergebnis | Eintritt / Grenze |
|---|---|---|
| **R2-0 – ergänzende SQLite-Proben** | Native Kapazitätsfehler, Transaktionsabbruch und Wiederöffnung gegen denselben synthetischen Bestand; Ergebnisbericht mit Fehlercodes und Grenzen. | Eigene Freigabe des beschriebenen Testblocks; Produktquellen bleiben unverändert. |
| **R2-1 – Mengen- und Größenvertrag** | Für jeden schreibenden Pfad begrenzte Eingänge, Lebenszyklus, vollständige Spitzenbedarfsrechnung und Umgang mit größeren Altbeständen; vorgeschlagenes numerisches Pilotprofil. | R2-0 ausgewertet; ungeklärte Fehlersichtbarkeit sperrt die betreffende Schutzzusage. Zahlen werden zur Entscheidung vorgelegt, nicht aus R1-Stichproben hochgerechnet. |
| **R2-2 – Budgetkern und Schreiben** | Getrennter Kandidat mit expliziter Reservierung, Schreibpfadprüfung, Rekonstruktion und Fehlerbehandlung; standardmäßig nicht aktiv. | Abgenommener R2-1-Vertrag und separate Implementierungsfreigabe. |
| **R2-3 – Aufnahme und Lebenszyklen** | Sämtliche Analyse-/Job-/Auto-/Recoverypfade an denselben Vertrag gebunden; Ablehnung vor Zufallszug/Jobstart. | Budgetkern geprüft; vollständige Pfadabdeckung. Kein teilweise geschützter Pilot als vollständig geschützt ausweisen. |
| **R2-4 – Pilotabnahme** | Linux-Regression, unabhängiger Review, synthetische Grenz-/Parallel-/Neustarttests; gesicherte kontrollierte Pilotaktivierung mit Rückfallplan. | Gesonderte Aktivierungsentscheidung erst nach konkreten Belegen und vollständiger Sicherung des Pilotbestands. Keine Windows-/Start5-/Template-/Aurelia-Übernahme. |

Maßgebliche Baseline: unabhängiger Gitroot `runtime/rw-storage-r1-20261017`, HEAD `d1eb34260179a499e2b0362bf609ce96957b78aa`. Alle Produktpfade in diesem Plan sind relativ zum unabhängigen Gitroot. Zukünftige Arbeit erhält eine eigene Arbeitskopie `runtime/rw-storage-r2-20261017` auf `codex/rw-storage-r2-20261017`; deren Gitroot muss exakt dieser Arbeitskopie entsprechen. Niemals im umgebenden Benutzerprofil-Repository stagen oder committen. R1-Werkzeuge und vorhandene Belege bleiben historisch unverändert.

Referenzen:

- [R1-Bericht mit Aussagegrenzen](../../verification/AURELIA_RW_STORAGE_R1_2026-10-17.md), [Laufindex](../../verification/AURELIA_RW_STORAGE_R1_2026-10-17_INDEX.json), [letzter R1-Abschlusscheck](../../verification/AURELIA_RW_STORAGE_R1_2026-10-17_FINAL_CHECK_2.json).
- [Schreibpfadabgleich](../../verification/AURELIA_RW_SPEICHERPFAD_ABGLEICH_2026-10-17.md), [59-Dateien-Inventar](../../verification/AURELIA_RW_SPEICHERPFAD_INVENTAR_2026-10-17.json), [Schutzentwurf](../specs/2026-10-17-radiworks-speicherschutz-entwurf.md).
- Offline-Image `sha256:121b7b271d5709c44c1e8ac2a62d6ef21acaed6dcd009514cdcbb6caee664215`; kein austauschbarer Tag als Identität.

R1 belegt 15 Kontrolltests und 27 unterschiedliche Charakterisierungsfälle. Seine SQLite-Fehlerinjektion rollte im Proxy selbst zurück; der Prozesswechsel erfolgte nach bereits bestätigten Transaktionen. Diese beiden R1-Lücken wurden im begrenzten R2-0-Rahmen geprüft; Ergebnis und verbleibende Grenzen siehe Abschlussbericht. Dateigrößen sind Stichproben, keine garantierten Spitzenbedarfe. Ebenso offen bleiben Host-/Datenträger-/Stromausfallfestigkeit, geschluckte Verzeichnis-fsync-Fehler und die Sichtbarkeit unbestätigter Journalbytes nach Flushfehlern. R2-0 schließt nur die unten ausdrücklich geprüften SQLite-Lücken.

## 2. R2-0: erster ausführbarer Block

### 2.1 Eigentum und unveränderbare Grenzen

Neue Dateien ausschließlich unter `pilot/storage_r2/` der unabhängigen Arbeitskopie:

| Datei | Verantwortung |
|---|---|
| `runner.py` | Profil-, Quellen-, Ergebnis-, Ausgabe-, Zeit- und Bereinigungsprüfung; keine Produktimporte. |
| `operator_local.py` | Bestehenden geprüften IPv4-Transport verwenden; genau einen eigenen Prüfcontainer erstellen, inspizieren, überwachen und entfernen; begrenzte Belege speichern. |
| `probe.py` | Seiteneffektfreie Protokollvalidierung; CLI delegiert ausschließlich im Linux-Prüfcontainer. |
| `execution.py` | Getrennter Linux-Treiber: gültige Store-Fixtures, native Fehler, begrenzte Childcapture und Prozessaufsicht gegen synthetische Daten. |
| `test_runner.py` | Positive/negative Kontrollen des Schutzprofils und der Ergebnisvalidierung. |
| `test_probe_protocol.py` | Nachweis, dass falsche Fehlercodes, vorzeitiger Child-Abbruch, fehlendes READY und unvollständige Beobachtungen nicht als Erfolg zählen. |
| `README.md` | Exakte Aufrufe, Profil und Grenzen; kein Produktstart außerhalb des Prüfcontainers. |

Der Transport bleibt auf die bereits freigegebene Aurelia-Rolle beschränkt. Keine SSH-Rechte-/Firewall-/Website-/Budgetänderung. Bestehende Vorschau wird nur nach Identität und Zustand verglichen, nicht neu gestartet. Keine echten Klienten-/Auftrags-/Mediendaten kopieren.

Containerprofil unverändert zu R1: read-only Root und Quellen, Netzwerk aus, keine Privilegien/Capabilities, `no-new-privileges`, UID/GID 65532, genau ein eigener Container; 1 CPU, 512 MiB RAM einschließlich tmpfs, kein zusätzlicher Swap, 64 PIDs. `/test-work` höchstens 32 MiB, `/enospc` höchstens 4 MiB. Kein beschreibbarer Hostmount. HOME/TMPDIR/SQLITE_TMPDIR/XDG_CACHE_HOME liegen unter `/test-work`; Pythonbytecode aus, Docker-Logging aus. Paketaufsicht 180s, innerer Alarm 175s; Childausgabe je Kind höchstens 64 KiB und gesamte Childcapture höchstens 128 KiB, Paket stdout/stderr zusammen höchstens 1 MiB. Gespeicherte eigene Belege höchstens 8 MiB insgesamt für diesen Lauf. Stop-/Abwesenheitsprüfung jeweils begrenzt wie R1 (5s + 5s). Bei Abweichung nicht starten bzw. nur exakt den eigenen Container stoppen.

### 2.2 Vorbereitung und rote Kontrollen

- [x] Gitroot, HEAD und alle 59 Produktdateien plus Pilotentry anhand des bestehenden Inventars prüfen. Bei Drift anhalten; keine Baseline automatisch aktualisieren. Profil und Vorschauidentität frisch lesen, ohne Dienste zu verändern.
- [x] R2-Arbeitskopie erst nach Freigabe erstellen. Additive R1-Treiber als unveränderte Referenz lesen; neue R2-Treiber bekommen eigene Quellenhashes und Protokollversion `radiworks.storage-r2-probe.v1`. Nicht nachträglich R1-Ergebnisse umetikettieren.
- [x] Zuerst Kontrolltests schreiben: falsche Image-ID/UID/Mounts/Limits, zusätzliche Schreibwurzel, Quellenänderung, OOM, Timeout, zu große Ausgabe, fehlende Bereinigung, falscher oder fehlender SQLite-Code, kein aktiver Transaktionszustand vor Kill, identische Child-PIDs, neue leere tmpfs, fehlender Readback und fehlgeschlagenes `integrity_check` müssen den Bericht ablehnen.
- [x] Die Tests vor Implementierung auf Linux rot sehen. Import-/Umgebungsfehler sind Harnessfehler, keine erwarteten Assertionfehler. Danach Runner minimal implementieren und dieselben Kontrollen grün nachweisen. Keine Produktdatei ändern.

Der neue Operator erhält den festen Aufrufvertrag `python pilot/storage_r2/operator_local.py --package controls|capacity|crash`; die Auswahl startet genau ein Paket, keine beliebige Shell. `controls` führt nur die beiden benannten Testdateien im begrenzten Linux-Container aus. Für direkte Ausführung innerhalb dieses Containers gelten:

```text
python -m unittest discover -s pilot/storage_r2 -p test_runner.py -v
python -m unittest discover -s pilot/storage_r2 -p test_probe_protocol.py -v
```

Erwartung: mindestens ein ausgeführter Test pro Suite, null Fehler/Fehlschläge, keine ausschließlich übersprungenen Tests, vollständiger Runnerabschluss und unveränderte Produktquellen. Diese Befehle werden nicht auf Windows gegen das Produkt ausgeführt. Der Operator darf lokal nur Steuerung/SSH und Belegsicherung ausführen.

### 2.3 Paket capacity: native SQLite-Fehler

Die Produkt-Stores mit ihren tatsächlich eingestellten Modi prüfen: Personal DELETE, Vergleich WAL sind R1-Beobachtungen und vor jedem Paket erneut zu lesen. SQLite-Version, Journalmodus, page_size, synchronous, busy_timeout, foreign_keys, freier tmpfs-Platz und tatsächlich vorhandene DB-/Journal-/WAL-/SHM-Dateien vor/nach jedem Schritt protokollieren. Nicht beim Testen still auf einen anderen Journalmodus umstellen.

- [x] Mit denselben bereits gültigen fachlichen Fixtureformen wie R1-C (`pilot/storage_r1/probe.py:986–1070`) je Store einen bekannten bestätigten terminalen Basisauftrag erzeugen. `core/personal_jobs.py::PersonalJobStore(path, scope)` und `core/comparison_store.py::ComparisonStore(path, scope)` verwenden `create(request_id, payload)`, `claim(record['id'])`, `cancel(record['id'])`; Baseline nach bestätigtem cancel wieder öffnen. Rückgabe-ID ist `record['id']`; Vergleichsinput liegt in `record['input']`. Reale Controllerpfade sind `personal_jobs/personal.sqlite3` und `comparisons/comparisons.sqlite3`; die flachen R1-Testpfade sind keine Produktpfade. Keine neuen Feldnamen raten. Die Wiederöffnung muss den vollständigen fachlichen Basiszustand bestätigen.
- [x] **Deterministische native SQLITE_FULL-Kontrolle:** Im ausschließlich synthetischen SQLite-Bestand nach Schemaanlage und Abschluss der Baseline `PRAGMA max_page_count` auf die aktuelle Seitenzahl begrenzen. Ein natives UPDATE von input_json mit zeroblob(1048576) an einer vorhandenen synthetischen Zeile innerhalb einer eigenen, nie bestätigten Kontrolltransaktion muss durch SQLite selbst mit Basiscodierung `SQLITE_FULL` scheitern. Fehlerklasse, `sqlite_errorcode`, `sqlite_errorname` und `connection.in_transaction` festhalten. Dies belegt eine SQLite-Seitenbegrenzung, nicht physisches ENOSPC.
- [x] **Produkt-Transaktionshülle:** Je Store einen transparenten Test-Connectionadapter verwenden, der Produkt-SQL unverändert an die native Connection durchreicht. Ziel ist `PersonalJobStore._transaction` bzw. `ComparisonStore._transaction(write=...)`, nicht eine Ersatz-Transaktionsfunktion. Erst nach dem fachlichen INSERT, noch innerhalb dieser tatsächlichen Store-Transaktion, auf **derselben aktiven nativen Connection** die aktuelle Seitenzahl lesen, das Seitenlimit darauf setzen und dessen Rückgabewert prüfen; dann ausschließlich input_json der gerade neu eingefügten unbestätigten Zeile über deren gebundene ID nativ auf zeroblob(1048576) aktualisieren. Eine Einstellung an einer früher geschlossenen Setup-Connection genügt nicht. Keine zusätzliche Tabelle: ComparisonStore verlangt ein exakt unverändertes Schema. Bei unerwartetem UPDATE-Erfolg vor Rückkehr zum Produkt einen ValueError als Harnessfehler auslösen; niemals als FULL zählen. Kein selbst ausgeführtes Rollback/Commit und keine selbst erzeugte `OperationalError` im Adapter. Die Store-Fehlerbehandlung muss den nativen Fehler sehen. Record- und Adapterbeleg getrennt ausweisen: Dies ist eine native Fehlerauslösung innerhalb der Produkthülle, keine unveränderte fachliche Nutzlastprobe.
- [x] Auf frischer Connection prüfen: vollständige Baseline vorhanden, neuer Auftrag vollständig vorhanden oder vollständig abwesend gemäß eindeutig beobachtetem Commitzustand; niemals ein Erfolg bei nur teilweise gespeichertem Auftrag. Für diese vor Commit ausgelöste FULL-Probe wird Abwesenheit des neuen Auftrags verlangt. Keine unterdrückte Ausnahme oder unbestätigte Erfolgsmeldung. `PRAGMA integrity_check` muss genau `ok` liefern. Eine notwendige Wiederöffnung ist kein Beweis, dass die ursprüngliche Connection weiterverwendbar ist; deren Zustand separat berichten. Hat SQLite selbst die ganze Transaktion zurückgerollt, belegt der Test keinen davon unabhängigen Rollback durch Produktcode; er prüft die tatsächliche native Fehlerreaktion und deren Weiterbehandlung.
- [x] **Physisch begrenzte Fehlerprobe:** Separaten frischen Bestand ausschließlich unter `/enospc` vorbereiten. Nach gültigem Basiscommit eigene Fülldateien begrenzt schreiben; tatsächliches `errno.ENOSPC` des Dateisystems belegen. Im verbleibenden Platz einen weiteren echten Store-Schreibversuch mit gültigem neuem Request durchführen. Maximal 32 Versuche, gemeinsam höchstens 256 KiB fachliche Requestdaten und keine unendliche Suche nach dem gewünschten Fehler. Erfolgreich angelegte Aufträge vor dem nächsten create bestätigbar terminalisieren; scheitert bereits dieses cancel nativ, dessen Phase und letzten bestätigten Zustand separat erfassen. Busy-/Idempotenzfälle zählen nicht als Kapazitätsfehler. Für Vergleich WAL und Personal DELETE separat erfassen, ob Fehler an DB, Journal oder WAL beobachtbar ist.
- [x] Die native SQLite-Reaktion auf physischen Platzmangel exakt klassifizieren (`sqlite_errorcode & 255`, erweiterter Code und Name). `SQLITE_FULL` und ein passender nativer I/O-Fehler sind verschiedene Ergebnisse; OOM, Python-Proxyfehler oder bloßer Childexit erfüllen die Probe nicht. Wenn unter den festen Grenzen kein nativer Storefehler erreicht wird: **nicht nachgewiesen**, Paket nicht als bestanden ausweisen, Belege sichern, keine Ressourcen automatisch erhöhen.
- [x] Eigene Fülldateien entfernen, freie Kapazität messen und gegen dieselben Daten mit neuer Connection `integrity_check`, vollständige Basisrecords und eindeutigen Zustand des neuen Requests prüfen. Keine Nutzdatenreparatur, kein Löschen der Storedateien, kein Neuaufbau einer leeren DB als Recovery.

Prüfplanpräzisierung 17.10.2026: Der unabhängige Astra-Review bestätigte den Schemawiderspruch der ursprünglich vorgesehenen Probetabelle. Der native UPDATE-Auslöser erhält Schema und Produktprüfungen sowie die bereits freigegebenen Ressourcen-/Testgrenzen. Er bleibt eine künstliche native Fehlerauslösung, kein unveränderter fachlicher Nutzlasttest.

SQLite kann bei FULL/IOERR je nach Fehlerstelle nur das Statement oder die gesamte Transaktion zurückrollen. Die tatsächliche Transaktion und der Wiederöffnungszustand entscheiden; der Fehlername allein beweist keinen Rollback. [SQLite: Transaktionsfehler](https://sqlite.org/lang_transaction.html).

### 2.4 Paket crash: Abbruch in offener Produkttransaktion

- [x] Je Store einen eigenen Childprozess gegen einen frisch vorbereiteten synthetischen Bestand starten. Der Supervisor bleibt im selben Container aktiv und hält dessen tmpfs. Child verwendet den echten Store; sein Testadapter führt den fachlichen INSERT nativ aus und meldet dann über eine begrenzte Pipe `READY` mit PID, Fixture-ID und bestätigtem `connection.in_transaction == True`, **vor** Commit oder Contextmanager-Exit. Anschließend bleibt der Adapter innerhalb derselben offenen Transaktion an einer Haltebarriere blockiert, bis SIGKILL das Child beendet. Kein Rücksprung in Produktcode, Commit, Contextmanager-Exit oder Rollback zwischen READY und Kill. Es gibt kein vom Supervisor gesendetes Fortsetzungssignal; Pipe-Abbruch/Barriere-Timeout sind Fehler und dürfen nicht als normaler Commitpfad enden.
- [x] Parent prüft das READY-Protokoll, exakte eigene Child-PID und offenen Transaktionspunkt. READY spätestens nach 10s; andernfalls nur eigenes Child stoppen und Probe als fehlgeschlagen abbrechen. Dann gezielt dieses Child mit SIGKILL beenden, höchstens 5s auf Ende warten und den tatsächlichen Signalexit erfassen. Nicht den Container oder die Produktvorschau töten.
- [x] Ein zweiter Child mit anderer PID öffnet dieselben Pfade und dasselbe gehaltene tmpfs. Baseline muss vollständig erhalten, uncommitteter Auftrag abwesend und `integrity_check == 'ok'` sein. Fachliche DB-Zustände vergleichen, keine Bytegleichheit regenerierter SQLite-Dateien verlangen. Sidecars getrennt beobachten; ihre Existenz allein ist kein Defekt.
- [x] Zusätzlich den schon in R1 belegten Fall **nach Commit** mit separater Fixture-ID als Protokollkontrolle wiederholen: bestätigter queued/running Auftrag bleibt vorhanden und wird durch `interrupt_pending` als interrupted markiert. Keine automatische Wiederaufnahme/Neuanalyse und keine Vermischung mit dem offenen-Transaktion-Fall.
- [x] Fehler-/Timeout-/falsches-READY-Kontrollen müssen zeigen, dass ein Abbruch vor INSERT oder nach Commit niemals als erfolgreicher Test des Abbruchs in offener Transaktion zählt. Eine zusätzliche Negativkontrolle lässt ein fehlerhaftes Child nach READY gezielt weiterlaufen und DONE/Commit bestätigen, bevor der Parent auswertet; dieser Ablauf muss abgewiesen werden. Die echte Haltebarriere muss dagegen nachweislich einen Rücksprung verhindern.

Dieser Test belegt Prozessabbruch/Wiederöffnung im erhaltenen tmpfs. Er belegt weder Container-/Hostneustart noch Datenträger- oder Stromausfallfestigkeit. Ein späterer voller HTTP-App-Wiederanlauf ist ein eigener R2-3-/R2-4-Test mit App-Lifecycle und RuntimeLease.

### 2.5 R2-0 Abschlusskriterien und sichere Fortsetzung

Abschlussbelege: [Bericht](../../verification/AURELIA_RW_STORAGE_R2_0_2026-10-17.md), [Laufindex](../../verification/AURELIA_RW_STORAGE_R2_0_2026-10-17_INDEX.json), [Finalprüfung](../../verification/AURELIA_RW_STORAGE_R2_0_2026-10-17_FINAL_CHECK.json).

- [x] Pro Fall unveränderliches Ergebnis mit Protokollversion, Quelle-/Tool-/Image-/Profilhash, Befehl, PID/Exit/Signal, Dauer, Fehlerstelle/-code, Commit-/Transaktionszustand, begrenzten Dateimesspunkten, vollständigem Readback und Konsistenzurteil speichern. Nicht beobachtete Werte explizit unbekannt, keine Erfolgsvorgaben aus bloßer Prozessrückgabe.
- [x] Bei unerwarteter Inkonsistenz, Quellen-/Vorschaudrift, fehlender Begrenzung oder unklarer Bereinigung **betroffenes Paket stoppen**, nicht mit gelockerten Kriterien wiederholen. Harnessfehler getrennt diagnostizieren; Belege behalten. Kein automatisches Repair an Produktdaten.
- [x] Nach jedem Paket genau eigene Prozesse/Container bereinigen, deren Abwesenheit und Quellenhashes erneut prüfen; vorher/nachher dieselbe Vorschauidentität und ihren Zustand vergleichen. Fehlende Beobachtungsmöglichkeit bleibt ein offener Abschlusscheck.
- [x] Bericht `docs/verification/AURELIA_RW_STORAGE_R2_0_2026-10-17.md` und zugehörigen JSON-Laufindex erzeugen; bei späterem tatsächlichem Datum dieses verwenden. Quellen/Belege hashgebunden sichern. Ein Dokumentcheckpoint ist keine Runtime-/Klientensicherung und noch keine Gitversionierung neuer Werkzeuge.
- [x] Unabhängiger Review bewertet native vs. injizierte Fehler, Transaktionspunkt, Readback, fehlende Beobachtungen und Aussagen. R2-0-Erfolg schließt keinen Security-Befund und genehmigt keine Schutzaktivierung.

## 3. R2-1: Vertrag vor Produktimplementierung

**Stand18.10.2026, v0.4:** Die Betriebsregel ist [freigegeben](../../verification/AURELIA_RW_STORAGE_R2_1_POLICY_APPROVAL_2026-10-18.json), Zahlen/Implementierung/Aktivierung nicht. [Vertrag](../specs/2026-10-18-radiworks-storage-r2-1-contract.md)/[Profil](../../verification/AURELIA_RW_STORAGE_R2_1_PROFILE_DRAFT_2026-10-18.json) behalten alle21 offenen Gruppen. [Paket-/Quellenbeleg](../../verification/AURELIA_RW_STORAGE_R2_1_SQLITE_PATCH_PROOF_2026-10-18.json) bestätigt fehlenden untersuchten WAL-Fix in Debian3.40.1-2+deb12u2, keine aktuelle Korruption nachgewiesen. [Wachstumspfade](../../verification/AURELIA_RW_STORAGE_R2_1_DOCUMENT_ENVELOPES_2026-10-18.json): volle GV-/Sitzungs-/Draftkopien und Original-Katalogtexte benötigen vollständige neue Dokumentobergrenzen. [Separater SQLite-Kandidatenplan](2026-10-18-radiworks-sqlite-candidate.md) nach Review noch nicht ausführungsreif: konkrete harte Buildablage, Builder/Toolchain/Libc und Parserweg zuerst belegen, dann eigene Build-/Regressionsfreigabe. Keine parallelen WAL-Proben auf altem Image oder automatische Umstellung. Bedingte Abschlussrechnung/Entropiezahlen erhalten;8GiB weiterhin Planungsoption, kein Budgetauftrag. Produkt unverändert.

Keine festen Nutzerquoten in dieser Vorlage: Zwei Größenproben und ein 4-MiB-Fehlertest erlauben diese Ableitung nicht. Vor R2-2 muss eine neue versionierte Profilvorlage für **alle** folgenden Klassen konkrete maximale Byte-/Mengenwerte und eine nachvollziehbare Berechnung enthalten. Fehlt eine Obergrenze, darf dieser Pfad nicht unter eine vollständige Schutzzusage fallen; ein optional abgeschalteter Pfad ist eine sichtbare Profilentscheidung, kein stiller Funktionsverlust.

| Pfadklasse / existierende Dateien unter `engine/src/radiworks/` | Vertrag und notwendige Abnahme |
|---|---|
| `persistence.py`, `core/cases.py`, `core/draft.py` | Tatsächliche UTF-8-Größe mit aktuellem Serializer; größter Zustand inklusive Fehler-/Endstatus; vorhandene Datei plus Ersatztempfile, Verzeichnis-/Blockbelegung. Recovery-Marker enthält alle **after**-Dokumente plus Digests/Metadaten, keine vollständigen before-Dokumente. Alle gleichzeitig lebenden Marker-/Zieldateien mitzählen. |
| `core/context_images.py`, `core/presentation_profile.py` | Bestehende Einzelgrenzen erhalten; Gesamtzahl/-bytes je Scope und Namespace definieren; neue eindeutige Datei vs. vorhandener deduplizierter Inhalt unterscheiden. Keine automatische Bildlöschung/Neukompression. |
| `core/broadcast.py`, `core/broadcast_target.py`, `core/auto_jobs.py` | Signaturlänge, Queuegröße, Receiptgröße/-anzahl und größter Abschlusszustand; Aufnahme, Queue und aktive Jobs getrennt. MAX_ACTIVE=8 ist keine Queuegrenze. Langlauf/Auto benötigt begrenzte Arbeitsepochen, Prüfung vor jedem neuen Schritt und eine endliche Abschlussreserve. Keine neue Daueranalyse als Nebenwirkung. |
| `core/stickpad.py`, `core/watchlist.py`, `core/gv_observations.py` | Begrenzte Positions-/Eintragszahl und Dokumentgrößen vor Listenaufbau/-kopie; bestehende GV-Begrenzungen erhalten. Clear/Stop sind selbst schreibend und benötigen begrenzte Reserven. |
| Entropiejournal und persönliche/Vergleichs-Stores | Begrenzter Record-/Resultumfang, Append-/Commit-/Checkpointbedarf, DB-/Journal-/WAL-/SHM-/Tempdateien und Leserlebensdauer. Nicht bestätigte Entropie bleibt unbestätigt; kein neuer Zufallszug nach Persistenzfehler. |
| `config.py`, Katalog-Bootstrap/-Release/-Merge, `runtime_lease.py`, App-Startup | Konfiguration erst nach erfolgreichem Persistieren als gültig behandeln; sämtliche tatsächlich beschreibbaren Wurzeln zuordnen; Direktwrites/Staging/Lockdateien und Startupänderungen erfassen. Read-only Quellen nicht als Schutz bereits bestehender beschreibbarer Bestände missverstehen. |

Für jedes Dateisystem separat bilanzieren: **bereits belegte Blöcke + noch nicht belegter reservierter Nettozuwachs + gleichzeitig benötigte temporäre Zusatzblöcke + noch nicht belegter Abschluss-/Recoverybedarf + Dateisystem-/Metadatenreserve ≤ zugeordnetes Anwendungsbudget**. Bereits belegte Anteile dürfen nicht nochmals als zukünftige Reserven gezählt werden. Hostfreiraum ist eine zusätzliche Beobachtung, kein Ersatz für diese Rechnung. Inodes, Symlinks, fremde Pfade und unerwartete neue Dateien müssen in den Erfassungsvertrag eingehen. Alle Writewurzeln einschließlich abweichendem cases_dir/drafts_dir erhalten eine eindeutige Dateisystemzuordnung.

SQLite `max_page_count` begrenzt DB-Seiten, nicht sämtliche Begleitdateien. `journal_size_limit` wirkt auf zurückbleibende Dateien nach Commit/Reset und ist keine harte Grenze für einen laufenden WAL. Leser können Checkpoints verzögern. Daher Modus, gleichzeitige Transaktionen und Reader-/Checkpointverhalten explizit begrenzen/belegen, bevor eine SQLite-Reserve als vollständig gilt. [DB-Seitenlimit](https://sqlite.org/limits.html), [Journal-/WAL-Restgröße](https://sqlite.org/pragma.html#pragma_journal_size_limit).

Größere Altbestände bleiben vollständig erhalten. Vor Aktivierung deren aktuellen Bedarf und mögliche Abschluss-/Recoveryzustände ohne Klientenexport aufnehmen. Bei unzureichender Reserve keine neue Arbeit annehmen; Lesen und kontrolliertes Stoppen anbieten, notwendige Schreibfehler dabei wahrheitsgemäß zeigen. Keine Historienkürzung, automatische Archivbereinigung oder Algorithmusänderung als Platzbeschaffung. Numerische Grenzwerte sind sichtbare Pilotkonfiguration, keine bereits bestätigte spätere Mandanten-/Aboquote.

## 4. R2-2/R2-3: Implementierungs- und Prüfvertrag

Die folgenden Bausteine sind der verbindliche Zuschnitt für den nach R2-1 zu vervollständigenden Implementierungsplan, noch keine Erlaubnis für Produktänderungen. Neue Datei `engine/src/radiworks/storage_budget.py` hält Budgetprofil, bytegenaue Bedarfsangaben und Reservierungslebenszyklus zusammen. Abhängigkeit explizit von `main.py` in Stores/Controller/Recovery injizieren; keine globale Policy oder automatische Änderung bestehender Standalone-Kernaufrufe. Weitere Produktänderungen nur in den im Schreibpfad-Inventar belegten Pfaden und deren direkten Aufrufern/Tests.

Quellengebundene Anschlussstellen (Zeilen beziehen sich auf die oben genannte Baseline):

| Stelle | Integrationsgrenze |
|---|---|
| `pilot/preview_entry.py:5–8`, `main.py:108–160`, `persistence.py:87–98` | Katalogbootstrap kann vor `create_app` schreiben; Konstruktion von Recovery/anderen Stores kann schon vor Lifespan/Lease Verzeichnisse anlegen. Schutzkonfiguration und Rootzuordnung müssen vor dem ersten Writer vorliegen. Bootstrap separat injizieren/schützen; bloße AppState-Erweiterung deckt ihn nicht ab. |
| `api/routes.py:665–675,951–1088` | Originalanalyse unter Stick-Pad-Lock/Recoveryprüfung; Journalanlage erfolgt vor Draw/Analyse, anschließend Journalcommit und Mehrdatei-Recovery. Reservierung davor, nicht erst unmittelbar vor finalem JSON. |
| `api/personal.py:78–105`, `core/personal_controller.py:87–103,249–300` | Vor Journalanlage/Entropiefrieren reservieren; die Reservierung muss Queueanlage, Workerblöcke und terminales Persistieren begleiten. |
| `api/comparisons.py:102–131`, `core/comparison_controller.py:127–172` | Vor persistenter Queueanlage einschließlich Retry reservieren; claim/Workerstart und finish/fail brauchen denselben begrenzten Lebenszyklus. |
| `api/routes.py:1641–1665`, `main.py:184–203` | Auto-On legt Journal vor start an; jeder nachfolgende Generationsschritt benötigt eine neue begrenzte Aufnahme vor Draw. |
| `main.py:205–230`, `runtime_lease.py:11–48` | Lease umschließt Lifespan-Recovery, Storeöffnung und Controllerstart; queued/running Jobs werden unterbrochen, nicht erneut ausgeführt. Lease gilt für dieselbe base: unterschiedliche Bases mit gemeinsamem cases_dir/drafts_dir müssen im Schutzprofil ausgeschlossen oder ausdrücklich gemeinsam gesperrt werden. |

Diese Source-Anker wurden statisch geprüft; sie sind kein Nachweis einer bereits existierenden Budget-API, eines integrierten Schutzes oder einer getesteten App-Wiederaufnahme.

| Vertrag | Zu beweisendes Verhalten |
|---|---|
| Aufnahme vor Arbeit | Originalanalyse, persönliche Entropiebindung und Jobanlage, Vergleichsenqueue, Auto-Start/-Schritt und Broadcastaufnahme prüfen/beanspruchen **vor** Draw, Analyse oder Workerdispatch. Bei Ablehnung unveränderter Seed/Zufallszustand, kein neu angenommener Auftrag, keine Queue-/Receiptteilzustände. Idempotente Wiederholung erzeugt keine zweite Reservierung. |
| Tatsächlicher Schreibpfad | Atomisches JSON, direkte Writes, Journalappend/-commit, Bilder und SQLite bleiben geschützt, auch bei Hintergrundarbeit oder Kernaufrufen ohne HTTP. Fehlende Rootzuordnung verhindert Aktivierung. Reine GET-Namen sind kein Beleg für Schreibfreiheit: SQLite-Transaktionshilfe/Startup können physisch schreiben. |
| Sperren und Zuständigkeit | Domänenlocks behalten Reihenfolge; Budgetlock ruft keine Stores/Worker/Broadcasts, Analyse oder Netzwerkfunktion auf. Kein Warten auf Workerabschluss unter Budgetlock. Singlewriter-/RuntimeLease-Grenzen erhalten, konkurrierende Reservierungen atomar bilanzieren. Kein neuer App-Prozess neben einer bestehenden schreibenden Runtime. |
| Abschlussreserve | Reservierung an unveränderliche Scope-/Job-/Requestidentität binden; Speicherung der Reservierung selbst endlich budgetieren. Abschlussübernahme/Freigabe idempotent; bei Fehler nicht vor bestätigtem Abschluss freigeben. Critical/Stop/Recovery ist kein unbegrenzter Bypass. Auto reserviert keine unendliche Zukunft. |
| Wiederanlauf | Vor Annahme neuer Arbeit dauerhafte Aufträge und Reservierungen abgleichen. Fehlender/unklarer Ledger oder widersprüchliche Belege sperren neue Arbeit; keine automatische Wiederholung unterbrochener Jobs. Ledgerupdates/-recovery benötigen selbst begrenzten Platz und einen expliziten Bootstrapvertrag. |
| Fehler und UI | Begrenzte stabile Fehlercodes ohne Pfade/Rohdaten/Schlüssel; UI zeigt echte Ablehnung/Recoverybedarf statt Erfolg. Voller Datenträger, fehlendes Verzeichnis, Berechtigungsfehler, I/O-Fehler und Quotenmangel getrennt behandeln. Kein Retry mit neuer Analyse/Zufallsquelle. CopyGuard bleibt eigenständig und wird nicht umgangen. |

Vor Implementierung benötigte Tests, auf dem Linux-Kandidaten auszuführen:

1. Genau passend / ein Byte oder ein belegter Block zu groß; UTF-8-Mehrbytezeichen und eingerücktes JSON; vorhandene Zieldatei plus Ersatztempfile; Recovery-Marker mit mehreren Zielen.
2. Zwei konkurrierende Aufnahmen: nicht beide dieselben freien Bytes beanspruchen; keine negative/vergessene oder doppelt freigegebene Reservierung; dedupliziertes Bild wächst nicht erneut.
3. Jede Pfadklasse der Tabelle mit positiver Aufnahme, Ablehnung vor Nebenwirkung, Fehler am realen Write und wahrheitsgemäßem Endstatus. Begrenzte Spies belegen insbesondere **keinen** Draw/Workerstart bei abgelehnter Aufnahme.
4. Voll-/I/O-/Berechtigungsfehler nach erfolgreicher Aufnahme: vorhandene Dokumente gültig bzw. eindeutiger Recoverybedarf; keine Erfolgsquittung bei fehlendem Commit. Verzeichnis-fsync-Best-effort nicht als garantierte Dauerhaftigkeit ausweisen.
5. Restart mit queued/running/abgeschlossenen Jobs, doppelten Requests, veralteten/fehlenden Reservierungen, gültigem/fehlgeschlagenem Recovery-Marker und größeren Beständen; neue Arbeit erst nach eindeutiger Rekonstruktion.
6. Haupt-App-Lifespan inklusive RuntimeLease, Startup-Bootstrap/-Recovery und kontrolliertem Stop; kein zweiter Schreiber und keine automatische Wiederaufnahme. CPU-, Entropie-, Queue-, WebSocket- und Transportbudgets bleiben getrennte spätere Schutzverträge, soweit hier nicht ausdrücklich zur Speicheraufnahme begrenzt.
7. Bestehende relevante Python-Suiten und JS-Syntax-/Browserprüfungen bei betroffenen UI-Pfaden; Prüfbefehle im folgenden Implementierungsplan an die tatsächlichen Tests binden. Keine aktuelle Anzahl bestandener Tests vor Ausführung behaupten.

## 5. R2-4: Aktivierung, Rückfall und Projektfortsetzung

- [ ] Neue Kandidatenversion mit allen Dateien/Tests/Profilwerten hashbinden und unabhängig prüfen. Kein neuer bezahlter Security-Scan ohne Kostenentscheidung; bestehende Befunde bleiben offen, bis ihr eigener Nachweis erbracht ist.
- [ ] Vor Aktivierungsentscheidung vollständige Sicherungs-/Wiederherstellungsvorlage für die **tatsächlichen** Pilotdatenwurzeln, SQLite samt konsistentem Backup, Journal und Recoverybelegen vorbereiten. Ein Quellcheckpoint ersetzt diese nicht. Live-Schreibarbeit muss kontrolliert ruhen; keine reine Dateikopie einer laufenden WAL-DB als sichere Vollsicherung ausgeben.
- [ ] Zuerst separaten synthetischen Pilotbestand mit aktivem Profil abnehmen. Vorschlag zur Live-Pilotaktivierung enthält konkrete Grenzen, Source-/Imagehash, Sicherungsbeleg, Stopbedingungen und Rückfallkompatibilität; Betreiber entscheidet danach gesondert.
- [ ] Bei Fehlern neue Aufnahme sperren, Diagnose/Belege sichern und nur eigene Arbeit kontrolliert stoppen. Kein automatisches Deaktivieren des Wächters, um volle Datenträger weiterzubeschreiben. Neue Reservedaten müssen alte Versionen gefahrlos ignorieren können oder einen ausdrücklich geprüften Rückfall benötigen; kein Überschreiben neuerer Job-/Entropiestände durch altes Backup.
- [ ] Rückfall zuerst gegen synthetischen Zustand testen: Dienste/Jobbesitz eindeutig, keine parallelen Schreiber, alter Kandidat nicht mit unbekannten laufenden Reservierungen starten. Erst bei verifizierter Kompatibilität und freigegebener Reserve auf vorherigen Kandidaten wechseln. Andernfalls sicher gestoppt lassen und Entscheidung anfordern.
- [ ] Nach Abnahme aktuellen Einstieg knapp aktualisieren; Hashbelege und Einschränkungen beibehalten. Anschließend RadiWorks-Restpunkte in der bestehenden Priorität fortführen. Globale Modulmatrix, Modul_Templates, Aurelia-Mandanten-/Aboverträge und Hauptserverkapazität sind eigene spätere Integrationsabnahmen.

## 6. Definition von fertig für diesen Planungsschritt

Fertig ist diese Vorlage nach Quellen-/Pfadprüfung, unabhängiger Prüfung auf materielle Lücken und lokalem Hashcheckpoint. **Nicht fertig** sind R2-0-Ausführung, Produktimplementierung, neue Grenzwerte, Security-Abschluss oder Schutzaktivierung. Der nächste freigabefähige Arbeitsauftrag ist allein Abschnitt 2 mit unveränderten Produktquellen und dem vorhandenen begrenzten Linux-Testprofil.

Planprüfung: Luna/max hat die Anschlussstellen und tatsächlichen Storeverträge statisch abgeglichen. Astra/medium hat den Plan unabhängig geprüft; der materielle Befund zur Haltebarriere nach READY ist oben eingearbeitet. Dieser Quellen-/Planreview ist keine Testausführung, Sicherheitsabnahme oder Betreiberfreigabe.
