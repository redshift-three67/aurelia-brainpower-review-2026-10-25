# RadiWorks: Entwurf des Host- und Scope-Vertrags

Stand: 28.09.2026. **Prüfentwurf für M3, keine Host-Aktivierung, M4-Zertifizierung oder Aurelia-Freigabe.** Die Aussagen trennen den geprüften lokalen Prototyp von Anforderungen an eine spätere Integration. Es wurden nur synthetische Daten verwendet.

## Nachgewiesene Ausgangslage

- `Radiworks/radiworks_port/engine/src/radiworks/scope.py`: `ScopeContext` validiert `tenant_id`, `client_id` und `job_id`. `ScopeResolver` erlaubt nur `local`; `enforced` und vom Browser gesetzte `X-Aurelia-*`-Scope-Header werden abgewiesen.
- `Radiworks/radiworks_port/engine/src/radiworks/main.py`: `create_app` bestimmt den Scope beim Start. Fall, Draft, Recovery, Stick-Pad, Entropie-Journal, Settings, Broadcast, Auto-Modus und WebSocket-Ereignisse hängen an einem gemeinsamen `AppState`. Die HTTP-Middleware und der WebSocket-Einstieg prüfen die lokalen Headergrenzen.
- `Radiworks/radiworks_port/engine/src/radiworks/workflow.py`: `WorkflowRegistry` kann Fall-, Draft-, Journal- und Recovery-Verzeichnisse pro `ScopeContext` trennen. `create_app` verwendet diese Registry noch nicht für einen parallelen Hostbetrieb; die übrigen Zustände sind damit ebenfalls nicht automatisch isoliert.
- `Modul_Templates/standards/API_CONTRACT.md` erlaubt im Prototyp nullable Mandantenfelder ausdrücklich ohne Authentifizierungs- oder Query-Scope-Nachweis. `REIFEGRADE.md` markiert RadiWorks S4 als nicht zertifiziert. Der RadiWorks-Releasekatalog und `analysis-request-catalog-v1` sind dort noch nicht als versionierte Erweiterung beschrieben.
- Aurelias `AGENTS.project.md` verlangt für jede Query und jeden CUDA-Puffer die Trennung nach `(tenant_id, client_id, job_id)` und `client` fail-closed. `src/lib/auth/verify.server.ts` löst einen Nutzer aus einer verifizierten Sitzung auf und lehnt eine gemeinsame Entwicklungsidentität bei realer Datenbank ab. `src/lib/auth/isolation.server.ts` begrenzt geskriptete Browseranfragen nach Fetch-Metadaten. `docs/07-identity.md` beschreibt Rollen, Mitgliedschaft und Step-up. Das ist **noch kein implementierter RadiWorks-Host-Scope-Adapter**. Das Gate-Identity-Token in `gate-identity.server.ts` weist eine Nutzeridentität nach; sein hier gelesener Typ liefert keinen vollständigen RadiWorks-`ScopeContext`.

## Kandidatenvertrag für den späteren Hostmodus

| Grenze | Erforderliches Verhalten | Noch zu beweisen |
| --- | --- | --- |
| Identität | Aurelia prüft Sitzung, Mandantenmitgliedschaft, Klientenzugriff, Rolle und ggf. Step-up **serverseitig**. Erst daraus entsteht ein unveränderlicher, für einen Vorgang autorisierter `(tenant_id, client_id, job_id)`-Kontext. Fehlende oder widersprüchliche Werte scheitern geschlossen. | Konkreter Adapter, Vertrauenskanal und Autorisierungsentscheidung nach AUDIT-02; keine freie Übernahme aus Body, Query, Cookie oder `X-Aurelia-*`-Browserheadern. |
| HTTP und WebSocket | Jeder Einstieg verwendet denselben autorisierten Kontext; ein WebSocket wird vor Annahme gebunden und Ereignis- sowie Replay-Puffer bleiben im Scope. Ein Fallwechsel darf keine alte Verbindung oder Queue in den neuen Kontext mitnehmen. | Parallele Verbindungen, Reconnect, Replay-Lücke, Widerruf und Scope-Wechsel mit Fremdmandanten-Negativtests. |
| Daten und Wiederanlauf | Fälle, aktuelle Sitzung, Drafts, Promotion-IDs, Stick-Pad, GV, Entropie-Journal, Recovery-Marker und Ergebnisansichten sind pro Kontext eindeutig zugeordnet. Freigabe und Wiederanlauf bewahren diese Zuordnung atomar. | Tests über Neustart, Absturz, konkurrierende Aufträge und gleiche Namen/IDs in verschiedenen Scopes. `WorkflowRegistry` deckt nur einen Teil ab. |
| Laufzeit und Nebenwirkungen | Settings, Entropie-Feed, Auto-Modus, Broadcast-Queue, Stop-Befehle und Live-Ereignisse dürfen keinen fremden Scope beeinflussen. Direktes `/broadcast`, Bild-Broadcast und Legacy-Mix benötigen eine ausdrücklich spezifizierte Rechte-/Freigabegrenze. | Vollständiger Lese-/Mutations-Endpunkt-Audit und Negativtests; ggf. dedizierte Engine je Scope statt geteilter Globalzustand. Eine solche Architekturentscheidung ist noch offen. |
| Katalog und Passport | Ein Auftrag bindet eine veröffentlichte, unveränderliche Katalogversion und den zugehörigen Passport. `analysis-request-catalog-v1` und Release-Retention werden als additive Vertragserweiterung gegen das Modul-Template abgestimmt. | Hostweites Veröffentlichungs-/Schreibprotokoll, reale stillgelegte Quelle, Aufbewahrung historischer Releases und Integrationslauf auf der freigegebenen Ubuntu-Zielumgebung. |
| Betrieb | Der lokale Modus bleibt fail-closed und separat lauffähig. Hostaktivierung erfordert eigene Migration, Rollback und End-to-End-Abnahme; keine stillschweigende Umschaltung des lokalen Preview. | G0-SRV-GROUND-ZERO, danach AUDIT-02 und die separate M4/S4-Entscheidung. Keine realen Klientendaten oder Hardware in dieser Prüfung. |

Die konkrete Übertragung der verifizierten Aurelia-Identität an RadiWorks ist absichtlich **nicht** festgelegt: Aus den gelesenen Quellen folgt kein fertiger Signatur-, Proxy- oder In-Process-Vertrag. Vor Implementierung sind Autorität, Kanal, Ablaufzeit, Widerruf und Fehlerverhalten in Aurelia zu entscheiden und zu testen. Die Existenz eines verifizierten Nutzer-IDs allein beweist weder Mandantenmitgliedschaft noch Klientenzugriff.

**Geprüfte Mutations-Einstiege für den späteren Rechte-Audit:** `POST /broadcast` reiht nach Text-CopyGuard direkt ein; `POST /images/broadcast` reiht eine Bildsignatur direkt ein; `POST /auto-mode/on` startet einen Regelkreis mit späterer Queue-Wirkung. `PUT /settings` kann `broadcast.legacyMixMode` verändern; dann führt `POST /broadcast/mix` eine abgekürzte Draft-Freigabe aus. `DELETE /broadcast/current` und `/broadcast/all` beeinflussen die Queue. Diese Pfade verwenden heute denselben lokalen `AppState`; aus ihrer Existenz folgt **keine** Berechtigung in einem künftigen Mandanten-Host. Der Hostvertrag muss für jeden Pfad Scope, Rolle, Step-up, Audit und Abbruchwirkung festlegen oder ihn dort deaktivieren. Die lokale Original-/Prototypfunktion bleibt bis zu einer gesonderten Produktentscheidung erhalten. Aurelias aktuelle Projektverfassung nennt **Ubuntu Server 24.04.4 LTS amd64** als späteres Produktionsziel; der Ist-Server wurde hier nicht neu inventarisiert.

## Lokale Prüfmatrix und offene Abnahme

| Probe mit synthetischen Daten | Stand |
| --- | --- |
| Zwei lokale Scopes nacheinander im selben temporären Runtime-Home: fremde Fallliste, `recent`, Fallobjekt und Draft nicht sichtbar | Bestanden; `/cases/recent` war zuvor rot und wurde gefiltert. |
| Fremden Fall aktivieren; fremden Draft ändern oder freigeben; aktuelle Analyse und Queue des fremden Scopes lesen | Gezielter API-Negativtest bestanden. |
| Direkter Broadcast mit gefälschtem `X-Aurelia-Tenant-Id`; Queue unverändert | Gezielter API-Negativtest bestanden. |
| WebSocket-Verbindung mit gefälschtem `X-Aurelia-Tenant-Id` | Gezielter Test bestanden; Schließcode 1008. |
| Parallele authentisierte Host-Scopes, alle Routen/Queues/Ereignisse, Recovery und Rechtewiderruf | **Offen.** Der produktive Hostmodus existiert nicht. |
| Freigegebene Ubuntu-Zielumgebung, reale stillgelegte Katalogquelle, vollständiger UI-/M4-Lauf | **Offen und gategebunden.** |

Die lokalen Negativtests beweisen nur die genannten Pfade und die verweigerte Header-Übernahme. Sie sind kein Beweis einer vollständigen Mandantenisolierung oder eines produktionsreifen Hostmodus.
