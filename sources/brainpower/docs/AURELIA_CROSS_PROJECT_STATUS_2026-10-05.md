# Aurelia — aktueller übergeordneter Projektstatus

Aktuelle Betreiberbestätigung: Portable5 funktioniert auf dem zweiten PC nach Vorgabe. Neue Vektor-/Broadcast-/Datenvertragsgrenzen und frische Prüfungen: [aktueller Restplan](verification/RADIWORKS_VEKTOR_DATENVERTRAG_RESTPLAN_2026-10-05.md). Historische offene Zweit-PC-Angaben unten sind dadurch überholt; weitere C3-/Host-/Kamera-Gates bleiben getrennt. Diese Zusatznotiz ist noch nicht in den abgeschlossenen F:-Archiven.

Stand: 2026-10-05T16:49:30.117232+00:00. Quellen sind eigenständige Projekte; gemeinsames Template/Review integriert sie nicht automatisch. Produktentscheidungen bleiben bei Aurelia/AGENTS.project.md und bestehenden G0-SRV-GROUND-ZERO/AUDIT-02-/Modulgates. Kein neuer Matrixplan, keine Servermigration oder S4.8-Freigabe.

| Bereich | Aktueller gesicherter Bezug | Grenze / nächster Schritt |
|---|---|---|
| Aurelia | C:/Users/Hubert111/Documents/ChatGPT/Aurelia; bestehende Plattformquellen/Pläne, in diesem Block kein Produktcode geändert | Server-/Hostautorität, Mandanten-/Jobrechte/Quotas und Auditgates gesondert. Historische 30.09-Gitstände sind kein aktueller Runtimebeleg. |
| RadiWorks | C:/Users/Hubert111/Documents/Radiworks/radiworks_port jetzt131/131manifestSHA-gleich mit Brainpower/runtime/rw-c23-fixed-release-20261005 | Lokaler integrierbar vorbereiteter Prototyp; keine Integration/S4.8. Fälle/Homes/Venv/Keys/extraneousfiles bewahrt. 8103–8109 weiterhin gepinnter Release. |
| Radi144 | C:/Users/Hubert111/Documents/Radi144; funktionsfähiger eigener Prototyp,8090 unberührt | M0-Bestandsaufnahme historisch; M0–M4/Frontend/Template/Adapter gezielt nach RadiWorks-Abnahme. Eigene Funktionalität/Formeln bewahren. |
| morphic_v1 / RadiMorphic | C:/morphic_v1 einschließlich Git-Objekte und Worktrees; Operatorworkbench separat | Modulreife-/Live-/Template-/Adapterprüfung nachRadi144, keine externe Mehrbenutzerfreigabe. |
| Modul_Templates | C:/Users/Hubert111/Documents/Modul_Templates; drei additive RadiWorks-Nachträge übernommen | Normativer API-Vertrag/Reifegrad v1 nicht geändert; lokales Profil v1.1 bleibt Entwurf. Hostintegration braucht eigene Autorität/Gates. |
| RadiFarben | Documents/Radifarben vorhanden, optional als unregistrierte Entwicklungsquelle gesichert | Noch kein bestätigtes viertes Modul, keine Gleichsetzung mit anderen Quellen. |

## RadiWorks-Wirkmechanismen und Grenzen

Originalalgorithmen bleiben Standard. Stick-Pad-Folgeschritt als neue getrennte Sitzung; originale Treffer unverändert. 21er-GV/gewählte weitere Seiten explizit, GV2 getrennte Beobachtungsentropie und bewusstes1260sIntervall/Historie; numerische Trends sind keine belegte Diagnose/Wirkung. Broadcast-Dock, W-Texthilfe, GV-/Trendhilfen und Zwischenablage unterscheiden Werte/Beobachtung/Freigabe. Fallvektor ist typisiert (Name/Vorname/Geburtsdatum/Ort/Fokus/optionales Bild), pro Auftrag eingefroren; Geburtsort optional exklusiv, Wohnort numerisch inaktiv. Heuristische Katalogvorschläge brauchen Nutzerauswahl; keine semantische KI. Bild derzeit Kontext-only.

CPU80000-Vergleich `radi144-matrix-cpu-v1` ist separat ausdrücklich wählbar, höchstens21Raten pro ausgewählter Seite, eigener Prozess/SQLite/Auftrags-/Sitzungs-ID und Quellen/Kontext/Katalog/Passportbindung. Restart unterbricht offene Jobs, keinReplay; Retry bewusst/neueIDs/gleicherSnapshot. Keine automatische Übernahme nachGV/Broadcast. Parameter/Formelbindung nicht durch freien Text austauschbar.

679CPU/API-Tests bestanden/3bekannteWindowsSkips im gepinnten Release. Lokales Portable5 0.3.0-rc1 (Engine0.2.0) fünf leere isolierte Instanzen ausZIP einschließlich Originalanalyse,21GV,CPUjob,Stop/Restart geprüft. Privater Administratortest aufzweitemWindowsPC noch offen; MicrosoftVC++v14x64 Voraussetzung. Keine bestehenden Fälle/Keys im Paket. Daten-/Clarke-Lizenz vor öffentlicher Weitergabe ungeklärt. USB-Kameratransport 180s/51.232Seeds am04.10 synthetisch belegt; keine physikalische Zufallsqualität/Wirkungsgarantie oder random.org-Langlaufzertifizierung.

[Aktueller C23/Portable5-Abschluss](verification/RADIWORKS_C23_PORTABLE5_ABSCHLUSS_2026-10-05.md), [tatsächlicher Quell-/Templateabgleich](verification/RADIWORKS_SOURCE_TEMPLATE_SYNC_2026-10-05.md), [Katalogverwaltung](verification/RADIWORKS_AURELIA_KATALOGVERWALTUNG_2026-10-05.md), [GV2](verification/RADIWORKS_GV2_ABSCHLUSS_2026-10-04.md), [Vektor/Experimentalplan](verification/RADIWORKS_VEKTOR_EXPERIMENT_V01_2026-10-04.md).

## Einheitliche Oberfläche / künftige Plattform

Hermes/RadiWorks-Design ist nur Template: dunkler Standard, klare Typografie/Fokus/Status, bedienbare lokale Navigation, modulabhängige Farbakzente; keine Fachlogikübertragung und kein Nachweis heilender Farben. Barrierefreiheit/Datenschutz/Claims jeweils mit konkreten Prüfungen, keine pauschale EEAT/WCAG/DSGVO-Zertifizierung. [Designplan](AURELIA_DESIGN_TEMPLATE.md), [Fortress-Prüfstrang](verification/AURELIA_FORTRESS_INTAKE_2026-10-01.md).

Sieben unabhängige lokale RadiWorks-Prozesse mit eigenemHome/Scope sind umgesetzt, ersetzen nicht Aurelia-RLS/Autorisierung. Gemeinsame Core-Kataloge versioniert/Adminfreigabe, eigene Nutzerlisten mandantenisoliert, Import-/Lizenz-/Driftregeln und adapterautorisierte immutableSnapshots vorbereitet, noch keine belegte vollständige ImportAPI/Hostimplementierung. CPUQuotas/Websocket/Persistenz/Recovery jeMandant/Nutzer/Modul/Job müssen imHost geprüft werden. Governors beobachtet Quellen/Reviewfrische/Gates; vollständige aktuelle Produktmatrix erst nachPrototypen.

## Sicherung / Wiederaufnahme

Voller deklarierter Aurelia-Quellumfang inkl. laufender lokaler Daten in RadiWorks/Radi144/morphic_v1/Modul_Templates/Plattform und optionalRadiFarben aufF:, bestehende Git/WIP-Daten bewahrt. Getrenntes Governors-Archiv ergänzt Brainpower/Laufzeit/Artefakte/Portable5/Hermesgedächtnisse und Codex/CCSwitch/SSH/lokaleServer-Recoverykonfigurationen. LiveSQLite konsistent einzeln, keine gemeinsame Atomarität. Keine frische RemoteUbuntu-/Debian-Sicherung. Alle manifestierten Bytes rückgelesen; explizite Auslassungen, Quellenzeitpunkte, ACL und Restoreanleitung imArchiv. Keine blinde Rückkopie über neuereDaten.

Private Quellvorherkopie vorOverlay: `F:\Hauptprojekt\Aurelia\20261005-184437`,18SHA-geprüfteQuell-/Templatedateien,39vorherfehlendeDateien imPlan. Dieser Einzelcheckpoint ist nicht das Gesamtsicherungsarchiv. Die Pausennotiz/Abschlussreceipt nennt die abschließend verifizierten Archivpfade.

Nächste Schritte nachPause: privatePortable5-Zweit-PC-/persönlicheC3-Abnahme und RadiWorks-Restgates besprechen; dannRadi144 → morphic_v1 → neuesModul → vollständigerMatrixplan → gesonderteAurelia-Gates. Nicht automatisch4.8. Bericht [Governors/Gedächtnis/Routen](GOVERNORS_DEVELOPER_STATUS_2026-10-05.md) und WIEDERAUFNAHME.md lesen; historische Angaben nicht als aktuellen Abschluss übernehmen.
