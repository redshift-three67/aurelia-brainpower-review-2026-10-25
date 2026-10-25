# RadiWorks: Wiederanlauf, Leeren-Aktionen und CPU-Laufzeit, 2026-10-07


## Betreiberhinweis zum Speicherplatz

Waehren der Arbeit meldete der Betreiber, C: sei zuvor voll gewesen und inzwischen bereinigt. Die anschliessende lokale Kontrolle zeigte3,67GiB frei. Dies ist eine moegliche Ursache frueherer Prozess-/Schreibprobleme; ein kausaler Nachweis fuer die historischen Abbrueche fehlt. Der separat reproduzierte SQLite-Lebensdauerfehler besteht im unveraenderten Code unabhaengig davon. Keine Browser-/CPU-Pakete heruntergeladen; fuer die sichtbare UI-Probe wird das installierte Chrome verwendet.

## Gesicherter Wiederanlauf

Lokaler Checkpoint `checkpoints/RadiWorks-Resume-Clear-20261007-202925`: 176 Produktdateien, insgesamt 535 kopierte Dateien; SQLite-Kopien ueber Backup-API und integrity_check. Kein kompletter F:-Projektbackup. Schluesselinhalt nicht dupliziert; bestehender Key-Pfad bleibt im privaten Checkpoint referenziert.

8112 wurde mit unveraendertem Home, Scope und Schluessel durch den gepinnten Release-Service gestartet. GET /ping 200; Service-PID27276, Startmanifest `00f646cfac80eefffdbb23ed06f49807e807a75ed782a95232e1ccaf5180bd00`. 340 Nicht-Datenbankdateien in den geprueften Fall-/Draft-/Journal-/Auftrags-/GV-/Watchlist-Verzeichnissen bytegleich; alle acht abgeschlossenen persoenlichen Auftraege inklusive input_json/record_json bytegleich. Zwei abgebrochene Auftraege bleiben abgebrochen. Keine neuen Nutzerauftraege/automatischen POST-Replays. Kein Nachweis fuer Codex-unabhaengigen Betrieb des Entwicklungsservers. Dauerports8103-8109 nicht umgestellt.

## Neuer Bedienwunsch und belegte Speichergrenzen

Auto AUS deaktiviert nur den Auto-Regelkreis. Die existierende DELETE /broadcast/all beendet aktive und wartende virtuelle Broadcasts, ihre gespeicherten Auftragsbelege bleiben bestehen. Die beiden UI-Listen unterscheiden sich: Broadcast-Tab zeigt maximal25 empfangene Ereignisse, Statusbar/Dock zeigt aggregierte Serverzaehler ab Browserbaseline. Diese Resonanzlisten und Serverzaehler sind bisher nicht dauerhaft gespeichert; Neustart verliert sie. Gespeicherte GV-Beobachtungen und Fall-/Analysesitzungen sind eigenstaendig und bleiben erhalten.

Freigegebenes additives Verhalten: Broadcasts leeren nutzt den vorhandenen Stop-all-Weg; Resonanzanzeige leeren setzt nur beide Anzeigen zurueck. Kein Loeschen von Faellen, Sitzungen oder GV-Historie. Neue Resonanzen koennen danach neu erscheinen. Auto AUS zuerst verhindert neue automatische Auftraege. Eine vollstaendige dauerhafte Resonanzchronik ist eine separate Erweiterung, aktuell nicht vorhanden.

## CPU-Messung ohne Produkt-/Formelaenderung

Evidenz `runtime/rw-performance-20261007/performance-baseline.json` und `profile_personal.py`. Ausschliesslich kuenstlicher Fall/Katalog mit1382Raten; jeder tatsaechlich berechnete Ratenwert nutzt unveraendert80000Kandidaten, CPUfloat32, einen Thread und lokale Generatoren. Kein vollstaendiger neuer1382-Lauf in diesem Paket.

| Messung | Zeit |
|---|---:|
| 100 vollstaendige Inputvalidierungen | 0,256s |
| Neuer Worker mit1Rate | 6,611s |
| Neuer Worker mit21Raten, Probe1 | 7,763s |
| Neuer Worker mit21Raten, Probe2 | 8,901s |
| Torch-Import im bereits vorbereiteten Hauptprozess | 2,220s |
| Geladener Prozess mit21Raten, Probe1 | 2,985s |
| Geladener Prozess mit21Raten, Probe2 | 2,768s |

Beide Cold-21er-Ausgaben und beide Warm-21er-Ausgaben exakt gleich (Score, Intensitaet, Matrix, Index/Rate). Die aktuelle Steuerung startet fuer jeden21erBlock einen neuen Prozess;1382Raten erfordern66Starts. Damit ist der wiederholte Start-/Importaufwand als wesentlicher Laufzeitanteil belegt. Die Messung isoliert nicht saemtliche Start-/Import-/Endanteile und ist keine garantierte Beschleunigung eines ganzen Katalogs. Historischer Vollkataloglauf~597s bleibt der bisherige Vollnachweis.



Wegen des neuen Speicherhinweises wurde die begrenzte CPU-Probe erneut ausgefuehrt. Auch nach Bereinigung blieben Cold/Warm-Ausgaben exakt gleich. Cold1:11,071s; Cold21:12,753s und11,575s; Warm21:3,101s und2,956s;100Validierungen0,265s. Unterschiedliche Systemlast ist nicht isoliert; kein kausaler Vergleich der C:-Bereinigung. Der wiederholte Prozess-/Importaufwand bleibt sichtbar. Erstprobe erhalten in `performance-baseline-before-storage-note.json`; zweiteProbe in `performance-baseline.json`.

## Zusaetzlicher SQLite-Lebensdauerbefund

Isolierter Belegbenchmark mit1382 synthetischen validen Platzhalterzeilen (keine berechneten Analysescores):66 get-Schritte2,272s,66 append-Schritte7,235s. Der eigentliche Abschlussdatensatz war completed1382; automatische Temp-Bereinigung scheiterte danach mit WindowsDateisperre, also kein fehlerfreier Gesamtlauf. Das exakt eigene Temp-Verzeichnis wurde nach Prozessende kontrolliert entfernt.

PersonalJobStore._transaction verwendete den SQLite-Verbindungskontext ohne ausdrueckliches close(). Dieser Kontext commit/rollbackt, schliesst aber nicht. Nachweis: zwei neue Tests halten echte Verbindungen absichtlich fest; Commit- und Rollbackfall scheiterten im Bestand, weil SELECT weiterhin moeglich war. In `runtime/rw-personal-ledger-20261007` bewirkt aeusseres contextlib.closing mit innerem unveraendertem Transaktionskontext zuverlaessige Freigabe. Beide Tests pruefen Commit/Rollback sowie Windows-Loeschbarkeit ohne GC oder Retry. Insgesamt31 Personal-/Store-/Controller-/Analysepruefungen inklusive echterCPU-Proben bestanden. Bericht `evidence/personal-ledger-tests.xml`. Die minimale closing-Korrektur und die zwei Lebensdauertests wurden nach bestaetigtem Leerlauf und sauberem Dienstende in den Kandidaten8112 uebernommen. Dort bestanden erneut alle31 gezielten Personal-/Store-/Controller-/Analysepruefungen. Dauerinstanzen unveraendert. Keine Behebung aller bisher ungeklärten Prozessabbrueche behauptet.

## Naechster getrennter Performance-Schritt

Ein eigener CPU-Prozess pro Auftrag statt proBlock ist aussichtsreich; keine Wiederverwendung zwischen Auftraegen. Der unabhaengige Astra-Review beurteilt den Ansatz als tragfaehig, aber noch nicht als sicher implementiert. Vor einer Uebernahme erforderlich:

- Zeitgrenze umfasst auch das Schreiben des maximal12MiB-Eingangs; blockiertes Kind muss abbrechbar bleiben.
- Genau ein stdout-Leser; der bestehende communicate-basierte Reaper darf nicht gleichzeitig lesen. Kind und Reader muessen nach Cancel/Timeout/Shutdown bestaetigt beendet sein, bevor CPU-Budget freigegeben wird.
- Begrenzte Byteprotokolle/Queue; Teilzeilen, ungueltiges UTF-8, Ueberlaengen, doppelte Antworten und EOF sicher behandeln.
- Drift vor jedem Block und vor Speicherung kontrollieren; Codeaenderung waehrend des letzten Blocks darf nicht unbemerkt bleiben.
- Sauberes finales Prozessende vor endgueltiger Fertigmeldung, keine automatischen Neustarts oder Wiederholungen.
- Echte Mehrblock-Ergebnisgleichheit bei80000Kandidaten fuerSeed0, anderenSeed und eingefrorene Stochastik; Abbruch-/Fehler-/Driftproben sowie laengerer Speicherlauf.

Diese Performance-Aenderung ist in diesem Paket nicht umgesetzt. Original/EXP1, Formeln, Ratenbestand, Kandidatenanzahl, Threads und RNG bleiben unveraendert.

## Verifikation vor UI-Abschluss

116 gezielte Backendtests bestanden,1 bestehende Probe uebersprungen (117 gesammelt): test_broadcast.py, test_automode.py, test_gv_observations.py, test_broadcast_targets.py. Zusaetzliche Testprobe test_clear_contract.py bestanden: Auto AUS laesst vorhandene aktive/wartende Queue unveraendert; anschliessendes stop_all leert sie. Bestehende Starlette/httpx-Abkuendigungswarnung; keine Dependency-Aenderung.

UI-Abschluss:48Tests aus10UI-Testdateien bestanden,28JS-Dateien syntaxgueltig. Der finale sichtbare Chrome-Lauf pruefte beide Einstiegspunkte, Anzeigeleeren/neue Resonanzen, Stop-Meldungen, Tastaturfokus, Escape und390px-Ansicht ohne Seitenueberlauf oder JS-Fehler. Saemtliche Schreibanfragen wurden synthetisch abgefangen; keine echten Nutzerauftraege im Browser beendet. Node-Warnung zur ESM-Paketerkennung unveraendert, keine globale package.json-Aenderung.

178Produktdateien, Manifest bae4872ad61ac533b19cf596e3a8c670bec1ce0efa6ff038b2e96a9eda1973f4. Eigener alter8112Prozess sauber exitClean=true; neuerPID 61864. Gleiches Home, Schluesselpfad, Scope und123Datenbanken; alle10Auftragsdatensaetze (8completed/2cancelled) inklusive input_json/record_json bytegleich,343ausgewaehlte Fall-/Draft-/Auftrags-/Journal-/Watchlistdateien bytegleich, SQLite integrity_check=ok.8103-8109ping200, unveraendert. Evidenz runtime/rw-performance-20261007/promotion.json, candidate-personal-tests.xml und clear-browser.json. Betreiberabnahme vor R6-/Start5-Uebernahme; S4.8=0% Integrationsfreigabe. Audio/Puls und Bildlayer bleiben unabgeschlossen.

Tatsaechliche Helfer: Luna6/max fuer Quellen-/Historienabgleich und begrenzte Frontend-Umsetzung; Astra6/medium fuer unabhängigen Review der CPU-Prozesswiederverwendung. Hermes-App-Routen unveraendert; keine gemessene Tokenersparnisbehauptung.


## Speicherhinweis und Abschlussgrenze

Betreiber meldet bereinigtes zuvor vollesC:. Erste nachfolgende Messung3,67GiBfrei, spaetereMessung8,82GiBfrei; Momentaufnahmen. Keine Behauptung, damit seien historische Prozessabbrueche kausal geklaert. Keine Formel-/Kandidaten-/RNG-/Ratenkuerzung. Prozesswiederverwendung bleibt ein separater unimplementierter Performance-Schritt. Clear-UI ist technisch100%; Betreiberprobe offen. GV-Beobachtungshistorie und Auftragsbelege bleiben erhalten; vollstaendige Resonanzanzeige ist bislang fluechtig, keine permanente Ereignischronik. AutoAUS stoppt nur Auto, nicht vorhandene Broadcasts.

Abschlusscheckpoint: `checkpoints/RadiWorks-Clear-Abschluss-20261007-212228`; 534Dateien perSHA256verifiziert, beide SQLite-Kopien integritaetsgeprueft. Vorhandener Schluessel nicht kopiert; Wiederherstellung braucht den bestehenden gesicherten Schluesselpfad. KeinF:-Gesamtbackup.

Final schreibfrei: HTML und beide geaendertenJS-Views werden bytegleich ausgeliefert. Nach Neustart kein aktiver Fall; Faelle bleiben gespeichert und muessen bewusst erneut geladen werden. current/ref409 ohne aktiven Fall ist die bestehende Schutzsperre, kein Datenverlust. Die eigene erste Historienprobe ohne erforderlichen case_ref antwortete422; nach Referenzabfrage zeigte409 den ungeladenen Fall. Kein automatisches Fallladen oder POST-Replay.
