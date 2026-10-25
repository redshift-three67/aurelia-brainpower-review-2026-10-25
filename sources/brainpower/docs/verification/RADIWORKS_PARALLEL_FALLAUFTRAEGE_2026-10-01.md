# RadiWorks: mehrere Aufträge für denselben Fall

Stand: 01.10.2026. Dies ist ein **Vertragsentwurf**, kein aktivierter Parallelbetrieb und keine Aurelia-Hostfreigabe. Gewünschter Zielablauf: Ein berechtigter Nutzer kann mehrere voneinander getrennte Analyse- und gegebenenfalls virtuelle Broadcast-Aufträge zu derselben Fallakte starten, verfolgen und einzeln beenden.

## Tatsächlich vorhandenes Verhalten

`create_app` erzeugt genau einen `AppState` mit einem aktuellen `CaseStore`-Fall, einer `gv_round`, einem Auto-Modus und einem `BroadcastManager` für den lokalen Engine-Prozess. Falländerungen und Analysen werden über die Stick-Pad-Transaktionssperre serialisiert; eine neue Analyse ersetzt den aktuellen GV-Rundenzustand. Fallakten können mehrere gespeicherte Sitzungen enthalten. Die virtuelle Broadcast-Queue kann mehrere Elemente führen und höchstens acht Elemente zugleich aktivieren (`MAX_ACTIVE = 8`), ist aber pro Prozess gemeinsam und nicht pro Fallauftrag autorisiert. `WorkflowRegistry` trennt einige Dateien nach Scope, wird von `create_app` aber nicht als paralleler Hostmanager verwendet. Mehrere Browserfenster derselben lokalen Instanz teilen somit die aktive Fall-/GV-/Queue-Laufzeit. **Weder die Zahl der Sitzungen noch die acht aktiven Queue-Elemente belegen unabhängige parallele Aufträge.**

Die Modul-Templates nennen im gemeinsamen API-Vertrag optionale Tenant-/Client-Felder im Analyse-Body. RadiWorks weist diese lokal ab und bezieht sie aus einem festen lokalen Scope. Das lokale Profil v1.1 ist ein Entwurf; `job_id` steht im Draft-Scope, nicht in einem hostautorisierten vollständigen Auftrag/Passport. Der gemeinsame v1-Vertrag ist damit nicht stillschweigend erfüllt.

## Vorgeschlagene Auftragsgrenze

| Gegenstand | Erforderliche Regel vor Aktivierung |
| --- | --- |
| Identität | Aurelia bindet aus verifizierter Sitzung, Mandant, Klient, Fallberechtigung, Rolle und gegebenenfalls Step-up einen unveränderlichen `(tenant_id, client_id, case_id, job_id)`-Kontext. Ein Browserwert in Body, Header, Query oder Cookie erteilt keine Autorität. `case_id` ist opak und unabhängig vom möglicherweise personenbezogenen Anzeigenamen. |
| Analyse/GV | Jeder Auftrag bindet Katalog-Release, Eingabehash, Entropiemodus, Passport, eigene GV-Runde und Fortschritt. Ein neuer Auftrag ersetzt niemals den GV-Zustand eines anderen. Gleichzeitige Schreibversuche an derselben Fallakte nutzen Revisionserwartung oder append-only Sitzungsereignisse; Konflikte werden sichtbar und nicht automatisch überschrieben. |
| Draft/Freigabe | Draft, CopyGuard-Urteil, Freigabe und Wiederholungskennung sind an exakte Inhaltsbytes, Policy-/Kernel-/Katalogversion und Auftrag gebunden. Ein identischer Retry liefert denselben Beleg oder einen sicheren Konflikt; keine doppelte Promotion. |
| Laufzeit | Entropie-Journal und Schlüssel, Recovery-Marker, Stick-Pad, Auto-Modus, Einstellungen und virtuelle Broadcast-Elemente sind auftrags- bzw. scopegebunden. Stoppbefehle wirken nur auf einen autorisierten Auftrag; ein globaler Stop braucht einen eigenen Administrationsvertrag. Das lokale `MAX_ACTIVE = 8` ist keine Kapazitätszusage für Aurelia. |
| Livekanal | HTTP- und WebSocket-Autorität stammen aus demselben serverseitigen Kontext. Events, Replay-Cursor, Reconnect und Widerruf bleiben im eigenen Auftrag; ein Fall- oder Rechtewechsel macht alte Kanäle unbrauchbar. |
| Betrieb | Quoten, faire Queue-Zuteilung, Abbruch, Neustart und Rollback sind vor Aktivierung spezifiziert. Die Architekturentscheidung „Engine je autorisiertem Scope“ versus „nachweislich partitionierter gemeinsamer Host“ bleibt nach G0-SRV-GROUND-ZERO und AUDIT-02 offen. |

## Erforderliche synthetische Nachweise

1. Zwei Aufträge A/B desselben Falls laufen parallel mit unterschiedlichen Katalogen/Seeds; Analysen, GV-Schritte, Drafts und Passports bleiben getrennt. Ein neuer A-Lauf ändert B nicht.
2. A/B verwenden absichtlich gleiche Fallnamen, Retry-IDs und ähnliche Signaturen; weder Daten noch Queue- oder WebSocket-Ereignisse vermischen sich. Ein Doppel-POST erzeugt keine doppelte Wirkung.
3. Abbruch, „Stop aktuell/alle“, Auto-Modus und Widerruf von A verändern B nicht. Fremde und abgelaufene Berechtigungen werden vor jedem Lesen und jeder Mutation abgewiesen.
4. Prozessabsturz vor/nach Persistenz und Neustart stellen beide Aufträge getrennt wieder her oder melden einen eindeutigen sicheren Konflikt. Historische Katalog-Releases bleiben gebunden.
5. Zielhost Ubuntu Server 24.04.4 LTS: konkurrierende Prozesse, Sperren, WebSocket-Replay, Quoten und Last einschließlich negativer Mandanten-/Klientenfälle werden geprüft. Ein nacheinander gestarteter lokaler Scope-Test genügt nicht.

## Zuständigkeit und nächste Entscheidung

RadiWorks kann das **Daten- und Laufzeitmodell als getrennten Prototyp** vorbereiten. `Modul_Templates` muss dazu ein versioniertes Profil-/API-Delta für Fall- und Auftrags-IDs, erlaubte Direktwege und die Scope-Herkunft erhalten. Aurelia muss die autorisierte Identität, Auftragserzeugung, Rechte, Quoten und den Hostadapter bereitstellen. Eine parallele Ausführung auf der gegenwärtigen lokalen Engine würde den gemeinsamen `AppState` umgehen und ist daher nicht freigegeben. Die laufende 8103-Instanz, bestehende Fälle und die lokale Originalfunktion bleiben unverändert.

Quellen: [Host-/Scope-Vertrag](RADIWORKS_HOST_SCOPE_CONTRACT_2026-09-28.md), [Hostprofil](RADIWORKS_HOST_PROFILE_V01_2026-09-29.md), [Template-Abgleich](RADIWORKS_TEMPLATE_SYNC_2026-09-30.md), [bestätigter UI-Entwurf](../superpowers/specs/2026-10-01-radiworks-broadcast-dock-parallel-orders-design.md).
