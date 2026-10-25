# RadiWorks: Hostprofil v0.1 zur späteren Abstimmung

**Aktualisierung 30.09.2026:** Der aktuelle Kandidat ist `a242d247`; die hier zuerst gegen `48f48db` und `920b507` geprüften Python-/Hostaussagen blieben auf diesem Nachfolger unverändert. `Modul_Templates` enthält jetzt [RadiWorks-spezifische Referenzen und ein lokales Profil v1.1 als Entwurf](../../../Modul_Templates/standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md); der gemeinsame normative API-Vertrag, Hostcode und Freigaben sind nicht umgestellt. [Prüfvermerk](RADIWORKS_TEMPLATE_SYNC_2026-09-30.md).

Stand: 30.09.2026; Quellenabgleich auf Kandidat `48f48db` (Host-/Python-Vertrag unverändert gegenüber `920b507`). **Vertragskandidat, keine implementierte Hostfunktion, keine S4-/M4- oder Aurelia-Freigabe.** Der lokale RadiWorks-Prototyp bleibt im Modus `local`. `enforced` wird beim Start abgewiesen. Dieser Entwurf beschreibt, was vor einer eigenen Hostimplementierung mit `Modul_Templates` und Aurelia zu entscheiden und danach zu testen ist. Das in Aurelias aktueller Projektverfassung freigegebene Produktionsziel ist **Ubuntu Server 24.04.4 LTS amd64**; ältere Debian-Verweise sind historisch. Die Version des tatsächlich laufenden Servers wurde in diesem Abgleich nicht neu festgestellt.

## Quellen und nachgewiesene Grenze

- RadiWorks: `scope.py`, `main.py`, `api/routes.py`, `manifest.py`, `tests/test_scope.py`, `tests/test_api.py` und `tests/test_catalog_release.py` im getrennten Kandidaten-Branch `codex/radiworks-s46-candidate` (`48f48db`); der ursprüngliche Arbeitsbranch enthält weiterhin uncommittete Änderungen.
- Gemeinsames Template: `Modul_Templates/standards/API_CONTRACT.md` v1 und `REIFEGRADE.md`; Aurelia: `AGENTS.project.md`, `docs/07-identity.md`, `docs/18-clipboard.md` (D18 noch „zur Bestätigung“).
- Am 29.09. liefen die gezielten Scope-/Katalog-/Manifesttests isoliert: **25 bestanden, 1 Windows-Symlink-Test übersprungen**. Der erste Sandbox-Lauf scheiterte bereits am temporären Schreibort; der wiederholte Lauf mit zulässigem Testzugriff war grün. Die Tests belegen den lokalen Negativfall, keinen parallelen produktiven Host.
- Der aktuelle [kanonische Kandidat](RADIWORKS_RELEASE_BOUNDARY_2026-09-29.md) bestand den isolierten 19/19-Browser-Smoke mit synthetischen Daten; die vollständige Engine-Suite bestand auf dem produktbytegleichen Vorgänger `0ac9bb5` (ein bekannter Windows-Symlink-Skip). Die [lokale Routenprobe](tools/radiworks_local_scope_probe.py) prüfte auf der Basis `30a9c91` 61 HTTP-Routen und einen WebSocket mit insgesamt 66 gefälschten Scope-Header-Anfragen: alle abgewiesen, virtuelle Queue leer. Das beweist nur die gemeinsame **lokale** Headergrenze, keine Host-Autorisierung.
- Ergänzung vom 30.09.: Kandidat `920b507` bestand eine frische Installation und die vollständige Engine-Suite auch unter Ubuntu WSL2 **26.04/Python 3.14** ohne sichtbaren Symlink-Skip. Das ist ein lokaler Linux-Nachweis, aber weder ein Test auf dem vorgesehenen Ubuntu Server **24.04.4** noch eine Host-Autorisierungsprobe.

## Vorgeschlagenes Profil: `radiworks.host-scope.v0.1`

| Grenze | Soll-Vertrag vor Aktivierung | Vorliegender Beleg / Lücke |
| --- | --- | --- |
| Autorität | Aurelia bildet aus verifizierter Sitzung, aktueller Mandantenmitgliedschaft, Klientenberechtigung, Rolle und nötigem Step-up einen unveränderlichen Kontext `(tenant_id, client_id, job_id)` für **einen** Auftrag. Browserwerte in Header, Body, Query oder Cookie erteilen keine Autorität. | Aurelia besitzt Identitätsbausteine, aber keinen gebundenen RadiWorks-Adapter. `ScopeResolver` akzeptiert nur den festen lokalen Kontext und weist `X-Aurelia-*` ab. Kanal, Ablaufzeit, Widerruf und Vertrauensnachweis sind offen. |
| HTTP | Jeder Lese- und Mutationspfad bindet denselben serverseitigen Kontext; ein fehlender, fremder oder abgelaufener Kontext scheitert geschlossen. Ein Auftrag darf seinen Scope nicht während der Ausführung ändern. | Heute ein gemeinsamer `AppState` pro Engine-Prozess. Das lokale Negativtestpaar belegt nur zwei nacheinander gestartete Scopes mit getrennten Fall-/Draft-Dateien und abgewiesenen Browser-Headern. |
| WebSocket | Autorität vor `accept`; Ereignislog, Replay-Cursor und Queue ausschließlich im gebundenen Scope; Widerruf schließt den Kanal und verhindert Reconnect mit altem Recht. `server.replay_gap` ist ebenfalls scoped. | Lokale Header-Spoofing-Verbindung wird mit 1008 geschlossen. Parallele Scopes, Widerruf und Replay-Isolation sind ungeprüft. |
| Zustand und Wiederanlauf | Fall, Session, AnalysisDraft, Promotion-ID, Passport, Stick-Pad, GV, Entropie-Journal, Settings, Auto-Modus, virtuelle Queue und Recovery-Marker sind atomar einem Scope zugeordnet. Gleichnamige Fälle/IDs in zwei Scopes dürfen sich nie überlagern. | `WorkflowRegistry` partitioniert nur Teilbereiche; die laufende App nutzt sie nicht als parallelen Hostmanager. Prozesslokale Sperren sind kein Mehrprozessnachweis. |
| Freigabe/Wirkpfade | Aurelias HarmonizationLane nimmt nur einen autorisierten Draft-Promote an. Direkte lokale `/broadcast`, `/images/broadcast`, `/auto-mode/on`, Legacy-Mix und globale Stop-Kommandos bleiben im Host geschlossen, bis ein eigener Rechte-, Einwilligungs-, Audit- und Abbruchvertrag verabschiedet und negativ getestet ist. | Die lokalen Direktwege existieren und bleiben für Original-/Prototypvergleich erhalten; `isHardwareActivatable=false`. Sie sind nicht als Hostoperationen im Manifest registriert. Siehe `RADIWORKS_LOCAL_DIRECT_PATHS_V1_2026-09-29.md`. |
| Katalog/Passport | Analyse bindet eine unveränderliche veröffentlichte Katalogversion, Quellenhash und `ScopeContext`; historische Releases bleiben für die vereinbarte Replay-/Aufbewahrungsdauer abrufbar. Eine spätere Host-Bindung muss `(tenant_id, client_id, job_id)` autoritativ belegen. | Lokale Katalog-Release-Tests sind grün. `manifest.INPUT_SCHEMA` nennt nur `database`, `seed`, `mode`, `max_hits` und verbietet zusätzliche Properties; `AnalysisRequest` weist fremde Body-Felder ab. Der Passport trägt Tenant/Client aus `state.scope`, aber keinen `job_id`; der Draft enthält `job_id` und einen Scope mit allen drei Werten. Das gemeinsame `API_CONTRACT.md` führt dagegen noch nullable Tenant/Client im Analyse-Body. Diese Template-/Host-Differenz benötigt eine versionierte Entscheidung, keine Übernahme von Browserfeldern. |

## Inventar der 62 gemounteten API-Einstiege

Die Gruppen stammen aus den aktuellen `@router`-Definitionen in `api/routes.py`. **Vorgeschlagene Hostpolitik:** grundsätzlich keine Route exponieren, bis ihre Autorisierung und Scope-Wirkung einzeln festgelegt sind. Die Tabelle ist eine Zuordnung für spätere Vertragstests, keine aktive Zugriffsliste.

| Gruppe | Anzahl | Zusätzliche Hostgrenze |
| --- | ---: | --- |
| `/ping`, `/manifest` | 2 | Interne Betriebs-/Registry-Abfrage; keine allgemeine Nutzerfreigabe aus der lokalen Erreichbarkeit ableiten. |
| `/entropy/*` | 3 | Feed, Quelle und `acquire` pro Auftrag begrenzen; keine reale Hardware dadurch aktivieren. |
| `/analysis*`, `/gv`, `/essential-questions`, `/search-anomaly`, `/databases`, `/rates` | 13 | Katalog, Analyse, GV-Runde und Sessionwechsel scope- und quota-gebunden; sichtbare Texte durch Host-CopyGuard. |
| `/stickpad/*` | 5 | Positionen und Ergebnis an Fall/Auftrag binden; Reset darf keinen fremden Zustand löschen. |
| `/cases/*`, `/case` | 12 | Falllisten, zuletzt geladen, Namen/Referenzen, Metadaten, Session und Statistik nur mit Klientenrecht. |
| `/drafts/*` | 5 | Rollenabhängige Feldsicht; Transition/Promote mit geprüftem Auftrag, Step-up und Wiederanlauf-ID. |
| `/broadcast/*`, `/auto-mode/*` | 8 | Direkte Wirkpfade im Host zunächst geschlossen; Queue-Lesen und Stop nur für autorisierten eigenen Auftrag. |
| `/images/*` | 2 | Analyse-Metadaten und Bildrechte/Witness separat; Bild-Broadcast zunächst geschlossen. |
| `/script/execute`, `/scripts/*` | 3 | Skriptquellen und -ausführung erst nach eigenem Rechte-, Ressourcen- und Ausgabeaudit exponieren. |
| `/training/*` | 4 | Start, Uncover und Löschen separat autorisieren und auf den eigenen Zustand beschränken. |
| `/settings` | 2 | Lesen scope-gebunden; `PUT` nur mit explizitem Administrationsvertrag. |
| `/materia/clarke-compare`, `/materiaMedicaSearch` | 2 | Korpus-/Vergleichsausgaben und Fallbezug scoped und CopyGuard-geprüft. |
| `/ws` | 1 | Verifizierter Kontext vor Annahme; eigene Events, Replay, Reconnect und Widerruf. |

Der gemeinsame Template-Satz „jede zustandsändernde Operation ist über `/cases/current` + `/analysis/current` introspektierbar“ ist für Settings, Training, Auto-Modus und Queue zu pauschal. Das spätere Template sollte pro Zustandsfamilie den tatsächlichen Beobachtungs- und Audit-Endpunkt angeben; daraus folgt noch keine Hostfreigabe.

## Vor Hostaktivierung erforderliche Negativmatrix

Alle Fälle mit ausschließlich synthetischen Daten, zwei gleichzeitig existierenden Mandanten/Klienten und getrennten Aufträgen. `A`/`B` stehen für verschiedene berechtigte Kontexte; eine bloße nacheinander gestartete lokale Engine genügt nicht.

| Probe | Erwartung | Stand |
| --- | --- | --- |
| Kein Recht, fremde/gefälschte Header, Body-/Query-Scope, abgelaufene oder widerrufene Sitzung auf **jedem** HTTP-Pfad | Ablehnung vor Lesen/Mutation; keine Fremd-Existenzinformation und kein Event | Lokale Header-/Payload-Proben teilweise grün; Host offen |
| A/B parallel: gleiche Fallnamen, Draft-IDs, Promotion-Retry-IDs, Katalogwahl und Recovery-Marker | Daten, Retry und Audit nur im eigenen Scope; keine Doppel-Promotion | Offen |
| A/B parallel: Analyse, Stick-Pad, GV, Settings, Auto, Direkt-/Bild-Broadcast, Stop-all | Keine fremde Queue-, Laufzeit- oder Settings-Wirkung; nicht freigegebene Hostwege geschlossen | Offen |
| A/B parallel: WebSocket-Replay, Cursor-Lücke, Reconnect, Widerruf und Scope-Wechsel | Nur eigene Events; alte Verbindung/Replays sofort unbrauchbar | Lokales Header-1008 grün; Host offen |
| Absturz vor/nach Promote und Neustart; zwei Prozesse mit identischer Auftrags-ID | Genau eine gebundene Wirkung oder expliziter sicherer Konflikt; kein automatisches Neu-Einreihen | Lokaler Wiederanlauf teilweise geprüft; Host offen |
| Katalog-Release/Manifest während eines Auftrags ändern oder entfernen | Gebundene Version erhalten oder fail-closed; keine stille Quellenersetzung | Lokale Release-Tests grün; Host offen |

## Entscheidungspunkte für S4.8 und spätere Implementierung

1. Aurelia muss zuerst `G0-SRV-GROUND-ZERO` und `AUDIT-02` gemäß eigener Verfassung erfüllen. Erst dann Autorität, Vertrauenskanal, Widerruf und Rechte konkretisieren; weder Tokenformat noch Proxy-Vertrag werden hier erfunden.
2. Template `API_CONTRACT.md` und RadiWorks-Manifest brauchen eine **versionierte** Abstimmung: Der lokale Analyse-Body führt keinen frei wählbaren Scope; `job_id` steht im Draft, aber noch nicht in einem autorisierten Host-Passport/-Auftragsvertrag. Der direkte Ergebniszeilen-Broadcast ist als lokale Abweichung kenntlich zu machen; D18-Host-Exposition ist separat zu entscheiden.
3. Vor Umsetzung ist zu entscheiden, ob eine Engine je autorisiertem Scope oder ein nachweislich partitionierter gemeinsamer Host die Runtime trägt. Ein fixer lokaler `AppState` darf nicht stillschweigend zum Multi-Tenant-Host erklärt werden.
4. Dieser Entwurf und lokale Tests schließen S4.7 nicht ab. Die kumulative S4.8-Gesamtentscheidung bleibt ausdrücklich beim Betreiber nach vollständiger S3-/S4-Evidenz und Host-/Template-Abstimmung.

Die einzelnen Formulierungs- und Schemaänderungen für die spätere gemeinsame Abstimmung sind im [Template-Delta v0.1](RADIWORKS_TEMPLATE_DELTA_V01_2026-09-29.md) als Vorschlag festgehalten; der gemeinsame Standard wurde nicht geändert.
