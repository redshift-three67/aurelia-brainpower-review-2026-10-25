# RadiWorks: lokaler Abschlussstand vor Aurelia-S4-Entscheidung

Stand: 30.09.2026. **Ergebnis:** Der getrennte RadiWorks-Kandidat `a242d24758d53e86ab290454ae4772f0827acc06` ist als lokaler, einzeln testbarer Modulprototyp vorbereitet. Er ist **nicht** als Aurelia-Hostmodul, S4 oder S5 freigegeben. Der ursprüngliche Arbeitsbranch und die produktiven Instanzen wurden nicht umgestellt.

## Frische Prüfung dieses Blocks

| Prüfung | Ergebnis | Aussagegrenze |
| --- | --- | --- |
| Vollständige Engine-Pytest-Suite | Auf Kandidatenquellen mit vorhandener Entwicklungs-venv und `PYTHONPATH` auf den Kandidaten: Exit 0; ein Windows-Symlink-Fall übersprungen, bekannte Starlette/httpx-Warnung. | Keine frische Installation und kein Ubuntu-24.04.4-Zielhostlauf. Die früheren frischen Installations- und Ubuntu-26.04-Belege bleiben getrennt. |
| Isolierter sichtbarer Chrome-Smoke | Aus separatem Testordner mit `npm ci --offline`: **19/19** Abschnitte bestanden, darunter zehn Ansichten bei 320 px, Tastatur, geschützte Fallnamen, Analyse → Draft → virtuelle Queue → Stop, WebSocket-Reconnect und Fehler-/Retry-Zustände. Browser, Engine und künstliches Runtime-Home wurden vom Test beendet. | Künstliche Daten, keine echte Hardware, keine umfassende WCAG-2.2-AA- oder Screenreader-Zertifizierung. |
| Quelle/Kandidat | Alle **105** im Provenienzverzeichnis bezeichneten Engine-/Webapp-Dateien zwischen aktuellem RadiWorks-Arbeitsbaum und getrenntem Kandidaten bytegleich. Kandidat-HEAD erneut `a242d247` gelesen. | Weitere Dateien des Arbeitsbaums, darunter Updates, Governor-Belege und WIP, sind absichtlich nicht Teil des Release-Kandidaten. |
| Portgrenze | Radi144/8090 blieb erreichbar; 8101, 8102 und Governor/8787 waren nach dem Lauf nicht als Listener gemeldet. | Portstatus ist eine Momentaufnahme. |

Die vorherige gezielte Betreiberprobe bestätigte sichtbare und hörbar unterscheidbare geschützte Fallaktionen sowie sichtbaren Tastaturfokus. Diese reale Bedienbeobachtung gilt nur für die zwei geprüften künstlichen Fälle. [Kandidaten- und Vorbeleggrenze](RADIWORKS_RELEASE_BOUNDARY_2026-09-29.md).

## Vor Aurelia weiterhin zu entscheiden oder zu belegen

1. **Zielumgebung:** Ubuntu Server **24.04.4 LTS amd64** mit tatsächlicher Installations-, Start-, Symlink-/Sperren-, API- und Browser-/Reverse-Proxy-Probe. Ein früherer Ubuntu-26.04-WSL-Test ist kein Ersatz. Auf dem Aurelia-Produktserver beginnt dies erst nach `G0-SRV-GROUND-ZERO` und `AUDIT-02`; dort ist derzeit keine RadiWorks-Hostübertragung autorisiert.
2. **Hostvertrag und Scope:** Der lokale Analyse-Body lässt keinen frei wählbaren Tenant-/Client-Scope zu, `job_id` liegt im Draft, nicht Passport. `enforced` ist absichtlich gesperrt. Der [lokale Profilentwurf](../../../Modul_Templates/standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md), die 62-Einstiegs-/Negativmatrix und Aurelias D18 müssen zu einem versionierten, autoritativen Identitäts-, Rechte-, Widerrufs-, Replay- und Auditvertrag entschieden werden. Direkte Broadcast-/Auto-/Legacy-Wege bleiben im Host geschlossen, solange ihr eigener Vertrag fehlt.
3. **Kumulative Bedien- und Textprüfung:** Weitere WCAG-2.2-AA-Zustände, mehrere Bildschirmleser-/Browserkombinationen, vollständige öffentliche Text-/Fehlerpfade, Kontrast und Reflow über die getesteten Zustände hinaus. Der bestehende Browser-Smoke und die enge Betreiberprobe reduzieren das Risiko, ersetzen aber die Abnahme nicht.
4. **Design und Modulvertrag:** Gemeinsames Hermes/Governor-Design als **visuelle** Aurelia-Vorlage D0/D1 versionieren; RadiWorks-Akzent und Hell/Dunkel in Aurelia isoliert prüfen. `Modul_Templates`-Referenzen sind aktualisiert, der gemeinsame normative API-Vertrag ist noch nicht übernommen. [Template-Abgleich](RADIWORKS_TEMPLATE_SYNC_2026-09-30.md), [Designplan](../AURELIA_DESIGN_TEMPLATE.md).
5. **S4.8/Release:** Erst nach obigen Nachweisen und einer eigenen Betreiberentscheidung einen S4-GO-, Tag-/Release- und späteren M5-/S5-Schritt erwägen. Keine grüne lokale Testzahl löst diese Entscheidung aus.

**Phasenfortschritt:** S4.6 ca. 98 %, S4.7 ca. 88 %, S4.8 0 % der begrenzten lokalen Prüfpakete; die Werte sind **kein** Gesamt-Reifegrad. Die lokale Modulvorbereitung kann für den nächsten Prototyp als dokumentierter Stand pausieren, während die Aurelia-Host-/S4-Abhängigkeiten separat offen bleiben.
