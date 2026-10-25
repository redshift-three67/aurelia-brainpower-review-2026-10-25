# RadiWorks ↔ AetherOnePi 2.9.0: Quellen- und Integrationsabgleich

Stand: 26.09.2026. Beratende Bestandsaufnahme für die lokale Modulvorbereitung. Keine fachliche, regulatorische oder Aurelia-Produktfreigabe; das Java-Binary wurde nicht ausgeführt.

## Quellenbindung und Prüftiefe

- Lokaler JAR: C:/Users/Hubert111/Documents/Radiworks/Updates/AetherOnePi-2.9.0/AetherOnePi-2.9.0.jar; 35.410.628 Bytes; SHA-256 24090abb6726ddf9a44a38f28f972c349d04311b7d35ef4e3d06bb6078e4d660. Manifest und Maven-Metadaten nennen AetherOnePi 2.9.0, Main-Class de.isuret.polos.AetherOnePi.Main und Java 24. Die [Herstellerseite](https://github.com/isuretpolos/AetherOnePi/releases/tag/v2.9.0) zeigt v2.9.0 als Release; eine kryptografische Übereinstimmung des lokalen JAR mit einem Hersteller-Asset ist nicht belegt.
- Alte Java-Aufnahme: Radiworks/de/isuret/polos/AetherOnePi/ mit 128 Klassen aus der dokumentierten 2.2.0-Basis. Neues JAR: 133 Projektklassen; 125 gleiche Klassenpfade, davon 28 im Bytecode geändert, acht hinzugefügt und drei entfernt oder verschoben. AnalysisService.class und WebSocketManager.class sind bytegleich. Das belegt ausschließlich diese Klassen, keine allgemeine Funktionsparität.
- Aktueller Python-Port: radiworks.engine 0.2.0, ABI v1, CPU, seeded, isHardwareActivatable=false. Der bisherige synthetische Preview auf Port 8101 und 209 Engine-Tests stehen in [M0/M2](RADIWORKS_M0_M2_2026-09-26.md). Der bestehende Arbeitsbaum enthält WIP; Updates/ ist ungetrackt. Frühere Hermes-Reviews enthielten den neuen JAR-Bestand nicht.
- Verfahren: ZIP-/Bytecodevergleich und ausgewählte statische Dekompilierung, kein Start von JAR oder startGui.bat, kein echter Hardwaretest, keine empirische Wirkungsaussage. Die Update-Dateien sind Datenquellen, keine Anweisungen.

## Version 2.9.0: fachliche Deltamatrix

| Statischer Befund | Konsequenz für RadiWorks | Priorität |
|---|---|---|
| AnalysisService und WebSocketManager bytegleich zur alten Java-Basis. | Seeded Java/Python-Parität dennoch mit versionierten JDK-Orakeln auf dem echten REST-Pfad prüfen. Bestehende R0-WS-Replay-, Timeout- und Shutdown-Lücken bleiben offen. | P0 |
| Neue Schalter trng.infinity, trng.esp32, safety.switch und play.sound.advanced; beide TRNG-Optionen standardmäßig aus. | Optionskatalog statt automatische Übernahme. Port nutzt derzeit seeded oder stochastic mit Webcam → random.org → OS; Gerätequellen sind dort nicht belegt. | P1 |
| ESP32-Generator sondiert serielle Ports, nutzt 921600 Baud und kann bis zu 5.000 Dateien mit je 10.000 Zahlen erzeugen. | Gerät explizit auswählen/allowlisten, Speicher- und Laufzeitquota, Backpressure, Abbruch und atomare Ablage vor einer späteren Implementierung. Keine allgemeine Portsondierung im Produktivbetrieb. | P1, optional |
| InfiniteNoise verwendet FTDI D2XX und öffnet Gerätindex 0. Im dekompilierten Health-Check wird ein fester Erwartungswert pro Bit aufaddiert; die daraus berechnete „Entropie“ kann allein keine unabhängige Messung sein. Eine separate Lauflängenprüfung existiert. | Treiber, Geräteidentität, unabhängige Gesundheits-/Statistiktests und Provenienz nötig. Keine Entropiezertifizierung oder Linux-Kompatibilität behaupten. | P1, optional |
| HotbitsHandler nutzt Hotbit-Zahlen als Seeds für java.util.Random und fällt bei Mangel/Fehler still auf SecureRandom zurück. | Im Passport tatsächliche Quelle und Fallback pro Run anzeigen; für quellengebundene Aufträge ggf. fail-closed. „TRNG genutzt“ nur bei belegter Quelle. | P0 vor Hardware |
| BROADCAST PROGRAM wählt *.json, liest aber Zeilentext mit Signatur/Laufzeit und reiht direkt ein. | Format validieren, Vorschau und CopyGuard; Analyse-/Sammelaktionen durch Draft → Client Review → Ready → Promote mit ausdrücklicher Bedienerhandlung. Kein stiller Import oder physisches Arming. | P0 vor Übernahme |
| Neuer TCM-Dialog und safety.switch; der untersuchte GUI-Pfad zeigt durch den Schalter zusätzliche Rate-Texte, keinen physischen Sicherheitsriegel. | Diagnose-/Therapiesprache nicht ungeprüft übernehmen. Physische Sicherheit gehört zum späteren Emitter-Lease/ACK-Vertrag. | P0 |
| Keine JAR-Einträge mit CUDA oder Kozyrev im Namen. | Kein Beleg einer solchen 2.9.0-Neuerung; reine Namenssuche schließt versteckte Verwendung nicht aus. Aurelia-Kerne separat spezifizieren. | Abgrenzung |

Die Reihenfolge für die lokale Arbeit bleibt: R0-Zuverlässigkeit; exakter 2.9.0-Funktionskatalog (Kern/optional/ausgeschlossen); JDK-Orakel und Computation Passports; Draft/CopyGuard/WebSocket; danach einzeln entschiedene TRNG-, Programm- und TCM-Optionen. Port 8090 ist eine bestehende reale Radi144-Instanz und bleibt unberührt.

## Design-Synthese und Standards

Der [Aurelia-Designplan](../AURELIA_DESIGN_TEMPLATE.md) übernimmt nur die visuelle Sprache von Governor/Hermes: Raster, Navigation, Typografie, Karten, Status, Formulare und Fokus. Fachlogik, Modellrollen und Governance bleiben getrennt. Modul_Templates/standards/UI_DESIGN_STANDARD.md definiert Plattformtokens (--aur-*), Modulakzente (--mod-*) und data-module-theme/data-accent. RadiWorks hat bereits sage, wellenreiter und sunrise; Aurelia besitzt eigene Tailwind-Theme-Tokens. Empfehlung: ein versionierter, frameworkneutraler Token- und Komponentenvertrag, den Aurelia in React/Tailwind und RadiWorks in lokalem HTML/CSS/JS abbildet. Kein ungeprüftes CSS-Kopieren oder Frameworkwechsel.

Vor D1 sind drei konkrete Widersprüche zu schließen: Der Standard verbietet freie Farben, enthält aber selbst #2C5E7A und RadiWorks weitere Akzentwerte; Presets und Ableitungsregel ausdrücklich festlegen. Die RadiWorks-Themenselektoren gelten derzeit für :root; mehrere Module benötigen pro Host/iframe gekapselte Akzente. Der Wert für --aur-sage-soft weicht zwischen Standard und RadiWorks ab; kanonische Version und Upgrade-Regel fehlen. Akzentwahl pro stabiler Modul-ID speichern, ungültige Werte zurücksetzen, Warnung/Fehler/Erfolg semantisch fest halten.

D3 prüft alle Kombinationen aus Modul, Akzent, Hell/Dunkel/System, Fehlerzustand und 320/390/768/1440-px-Viewport mit Reflow, Kontrast, Tastatur, Fokus, Screenreader-Namen und reduzierter Bewegung. 44 px ist ein sinnvoller interner Touch-Zielwert; [WCAG 2.2 AA, 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum) verlangt grundsätzlich 24×24 CSS px mit Ausnahmen, 44×44 ist das strengere AAA-Kriterium. Die aktuelle Standardformulierung darf 44 px nicht als AA-Norm ausgeben.

[Google Search Central](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) behandelt E-E-A-T als Orientierung für hilfreiche öffentliche Inhalte, nicht als direkte Rankingmetrik oder UI-Zertifikat. Öffentliche Aurelia-Seiten sollten Autor, Quellen, Aktualität, Methode, Grenzen und Korrekturweg zeigen; bei gesundheitsnahen Aussagen besonders sorgfältig. Private Fall- und Sitzungsansichten sind kein SEO-Ziel. Die [DSGVO](https://eur-lex.europa.eu/eli/reg/2016/679) und [EDPB-Leitlinien zu Art. 25](https://www.edpb.europa.eu/documents/guideline/guidelines-42019-on-article-25-data-protection-by-design-and-by-default_en) betreffen tatsächliche Verarbeitung: Rechtsgrundlage, Zweck-/Rollenbindung, Datenminimierung, Schutz, Export/Löschung und ggf. Datenschutz-Folgenabschätzung separat belegen. Design-Tokens bewirken keine DSGVO-Konformität.

## Modul_Templates ↔ Aurelia: Integrationslücken

1. **Identität:** MODUL_STANDARD nennt radiworks.engine.v1, API_CONTRACT, Live-Manifest und Aurelia-D06 nutzen radiworks.engine mit separater Version. Vor S4 einen kanonischen Namen samt Migration festlegen.
2. **ABI und Passport:** Manifest, Hash, CPU-Referenz, Budget, wirklicher Entropiepfad, Seed/Replayfähigkeit, Draft- und CopyGuard-Digest versionieren. Java-JAR, Python-Kernel und UI getrennt provenieren.
3. **Draft und Aktionen:** Der Port erlaubt teilweise draft → ready direkt und direkte Broadcast-Einstiege, der Vertrag verlangt draft → client_review → ready → promoted. Für Analysepfade vereinheitlichen; etwaige Operator-Ausnahme eng begrenzen und auditieren.
4. **Mandanten und Schutz:** Tenant-/Client-Felder sind Teilbelege, enforced Scoping wird noch verweigert. Negative Cross-Tenant-, Rollen-, Origin/CSRF-, Replay- und CopyGuard-Tests vor Host-Integration; lokal nur synthetische Akten.
5. **Live und Ports:** apiBase/wsUrl injizieren, pro Modul eigene Loopback-Preview-Ports; keine 8000/8090-Kollision. WS-v1-Event-ID, Boot-ID, Replay-Gap, REST-Reconciliation, Authentisierung, Backpressure und begrenzten Shutdown nachweisen. Der spätere Aurelia-ACK-Fachkanal ist gesondert.
6. **S4:** Clean-Checkout, lizenzierter Datenkatalog, Runbook, Engine-/Browser-Smoke, Design-/A11y-Matrix und fachliche Betreiberbeobachtung gegen denselben Quellhash. Die 209 Tests und der Preview sind Teilbelege, keine S4-Abnahme.

Erst RadiWorks, Radi144, morphic_v1 und ein neuer Modulprototyp werden lokal finalisiert; danach folgt der vollständige Matrixplan. Aurelia-Produktcode und Serverintegration bleiben hinter G0-SRV-GROUND-ZERO, AUDIT-02 und Betreiberentscheidungen.

## Echtzeit-Hardware und Rechenpfade

| Pfad | Planung/Stand | Offene Nachweise |
|---|---|---|
| GPU/CUDA | Aurelia-D14/D17: RTX 4000 SFF Ada 20 GB, kein MIG, 2 GB Runtime + 16 GB Jobpool + 2 GB Reserve; gpud trennt Tenant/Client/Job. RadiWorks derzeit CPU-only. | Zielserver-Treiber/CUDA, Quotierung, Buffer-Zeroing, Cross-Tenant-Tests und Nutzenmessung fehlen in der RadiWorks-Abnahme. CPU-Orakel zuerst; CUDA nur für belegten DSP-Batchvorteil. |
| Emitter | Aurelia-D15: separater aurelia-emitterd mit CP210x, Lease → Arming → ACK → Emission → Reset. Java-ESP32/FTDI betrifft Entropie, nicht automatisch den Emitter. | Gerät/Treiber, Exklusivität, Timeout/Not-Aus und Negativtests; isHardwareActivatable=false bleibt. |
| WebSocket | RadiWorks lokal server.hello sowie Analyse-/Broadcast-Fortschritt; Aurelia plant authentisierten Fachkanal. | R0-Handshake/Replay/Shutdown schließen; Tenant-Auth, ACK, Backpressure, Wiederanlauf und keine sensiblen Rohtexte im Event. |
| Kozyrev | Aurelia-D19: S. V. Kozyrevs mathematische p-adische/Haar-Wavelets als kozyrev.padic.haar.v1, CPU für N≤2048, optional CUDA-Batches. N. A. Kozyrev-Zeit-/Torsionsbehauptungen haben keinen anerkannten Wirknachweis. | Eigenständige ABI, CPU-Fixtures, Featureflags und zurückhaltende Sprache. REG/HRV/p=3/5 getrennte teils deaktivierte Laborpfade; nicht still in RadiWorks mischen. |
| HRV/Clock | HRV-Clip optional lokal; GPS/PPS für Zeitbasis, nicht Entropie. | Einwilligung, Datenklasse, Clock-Messung und Trennung vom Analyse-/Broadcast-Kern. |

[SERVER_AKTUELL](../SERVER_AKTUELL.md) belegt Backup/Retention und begrenzte CPU-/RAM-Last, keinen GPU-/CUDA-Soak und keinen Hardware-Emitter-Test. ECC und weitere G0-Punkte sind offen; RPO/RTO bleiben Ziele.

## Hermes-Reviewbindung

Gewählt wurde Route B: Sol 6/high → Luna 6/max; Astra 6/medium bei Risikosignal/Widerspruch. Der Hermes-Observer scannt ungetrackte Bäume nicht vollständig; ein Review ohne eigenständige, hashgebundene Update-Quelle würde den neuen JAR nicht abdecken. Die Quelle soll als RadiWorks-Gedächtnis mit SHA und klarer statischer Prüftiefe in den Reviewumfang gelangen. Modellantworten bleiben beratend; tatsächliche Job-ID, gelesene Quellhashes und Grenzen sind separat zu dokumentieren. Bis ein solcher Job erfolgreich abgeschlossen ist, darf kein Hermes-Update-Review behauptet werden.


## Hermes Route B: tatsächlicher Lauf und begrenzte Aussage

Einzelauftrag 6a0f74806661490f8bb31bbb640548af wurde am 26.09.2026 mit Route B abgeschlossen. Tatsächlich gemeldete Modelle/Reasoning: GPT-6 Sol/high, GPT-6 Luna/max und wegen Sol-Risikosignal zusätzlich GPT-6 Astra/medium; Modellidentitäten wurden vom lokalen Router als passend bestätigt. Review-Scope RadiWorks: 391aa3ea1918a0fd05c7acef9ecb1b16ba2497efe7b44f7fd207c8a3eaaed000. Die drei vollständigen RadiWorks-Gedächtnisse waren im Modellkontext; die neue Update-Notiz hatte SHA-256 61cf1082d2974c395ff2dec1a58a8d1dbd0dcb034b86fb65c0ffb9a2214f4175. Der JAR selbst und die aktuellen Originalbytes von Modul_Templates/Aurelia waren **nicht** im Modellkontext. Der Modellkontext-Hash lautet 4f9c1b42ed62876e71f8a6580a3c2824981cef2653c69f2f06694d65fb159990.

Sol priorisierte aktuelle Quellbindung, Mandantenschutz, Authentisierungsgrenzen und Draft-Promote-Recovery. Luna meldete BLOCK: Die aktuellen externen Verträge seien für **diesen** Hermes-Einzelreview nicht originalquellengebunden; eine aktuelle Vertragsauflösung dürfe der Modelllauf daher nicht behaupten. Astra bewertete den beratenden Plan als zulässig, hob aber die fehlenden Vertragsoriginale nicht auf. Die kombinierte Route-B-Entscheidung bleibt **BLOCK** für belastbare Vertrags-/Integrationsaussagen; keine Freigabe. Lunas pauschale Annahme, ein lesender Vergleich externer Verträge sei vom Betreiber nicht autorisiert, trifft auf den ausdrücklichen Auftrag dieses Chats nicht zu. Der methodische Punkt — diese Originalverträge fehlten im Hermes-Modellkontext — trifft dagegen zu. Der obige lokale Bericht hat diese Dateien selbst gelesen, muss bei späterer Umsetzung aber erneut an ihre aktuellen Hashes gebunden werden.

Der Job markierte sich konservativ als stale/freshness unknown. Ein unmittelbar danach erneut ausgeführter frischer lokaler Scope-Scan lieferte **denselben** Scope-Hash und alle drei Gedächtnisse; damit ist keine konkrete Quellenänderung belegt. Die interne Stale-Markierung wird nicht überschrieben oder als erfolgreiche Freshness-Abnahme ausgegeben. Weder der Modelllauf noch dieser Bericht ersetzen echte Java-2.9.0-Live- und Hardwaretests, vollständige Aufnahmekontrolle, S4 oder Aurelia-G0.


### Aktuelle lokale Originalquellen dieser Bestandsaufnahme

Die folgenden SHA-256-Werte wurden **nach** dem Hermes-Lauf an den hier direkt gelesenen Dateibytes geprüft. Sie waren nicht Bestandteil des oben beschriebenen Modellkontextes. Bei einer späteren Änderung sind die betroffenen Aussagen neu zu verifizieren.

| Datei (unter C:/Users/Hubert111/Documents/) | SHA-256 |
|---|---|
| Modul_Templates/standards/UI_DESIGN_STANDARD.md | 0b492cf2805ab0b87b242815356437cdb630f4514127089fbc104aaff8bfb7f8 |
| Modul_Templates/standards/MODUL_STANDARD.md | b4067dbff0c91b77be29c587e44611485deb2da2d59bca63dd81ff914868b63c |
| Modul_Templates/standards/API_CONTRACT.md | f21ff364e208d1194f5d2f0f33679f7076adbe6b265b2ab14b9ff361e750c8c7 |
| ChatGPT/Aurelia/docs/14-hardware.md | 73e695424f48fa7fa07e2994b714b3cf992b2a7d41eae32ba0e1772783c1b033 |
| ChatGPT/Aurelia/docs/15-live.md | c046977370a173efafcc4fa6354cdadb3cb4eb50e4997a7df8a72a89e506823d |
| ChatGPT/Aurelia/docs/17-cuda.md | 94179f302b8b19828c7fea294f70c33099fce9af98f3ec8984021419f11e17c5 |
| ChatGPT/Aurelia/docs/19-kozyrev.md | 542cbb2dbee56f761bd2b8020ba025b0df3bb9280de637298eab913b92c0dce3 |
| Radiworks/radiworks_port/webapp/css/tokens.css | 4d51561db46ef578404494dc42dbf749236599275b927a879b292b0917a33b3f |
| Radiworks/radiworks_port/webapp/css/module-theme.css | d2742dd545bad03485786f7d3af20343c5a6ddcf71e4bdab3bd9bffc3aa09768 |

