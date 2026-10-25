# RadiWorks B1 – Quellenidentischer Cloud-Vergleich

**Ausführungsstand25.10.2026:** Vorbereitung unverändert eingefroren.4/4genehmigte Profilveröffentlichungen umgesetzt, B0 wiederhergestellt.1B1-Cloudchat stoppte nach3Sekunden vor jedem Werkzeug wegen interner Modell-Selbstprüfung;0Runnerstarts/0Hash-/Build-/Testausführung. Minimale Übergabeklarstellung mit außen bestätigter Modellwahl vorbereitet. Nächste konkrete Entscheidung:1zusätzlicherModellturn im vorhandenen B1-Chat,0weitereVeröffentlichungen/0neueVM-Anforderungen, erstmals1unveränderterRunner. Siehe `runtime/rw-cloud-b1-execution-20261025/FOLLOWUP_APPROVAL_SCOPE.json`; noch nicht gesendet/freigegeben.

**Goal:** Einen einmaligen synthetischen Cloud-Lauf auf denselben 204 kanonischen Dateien wie CI40173688749 ausführbar vorbereiten, lokal testen und unabhängig prüfen; noch keine Ausführung.

**Architecture:** Eigenes lokales Vorbereitungspaket unter `runtime/rw-cloud-b1-prep-20261025`. Der vorhandene geprüfte Export `runtime/rw-pilot-session-fix-20261016` wird vollständig gegen den CI-Lock geprüft und als begrenztes ZIP mit unverändertem CI-Guard/Lock gebunden. Ein Python-Standardbibliothek-Runner entpackt ausschließlich das gebundene Paket in eine neue eigene Cloud-Ablage, verwendet den lokalen Docker-Unixsocket und das ursprüngliche Dockerfile. Keine Änderung am Produkt oder Governor. Während der Vorbereitung bleibt der bestehende Cloud-Snapshot unverändert. Der vorgeschlagene spätere Materialumfang enthält1private B1-Konfigurationsveröffentlichung ohne automatische Installation/Starts und mit exakt5Downloadhosts,1neuen Cloud-Auftrag und danach1Wiederherstellung/Veröffentlichung der ursprünglichen B0-Konfiguration. Frischer Taskstart bleibt damit selbst Teil der nativen Prüfung; fehlende Funktionen stoppen ohne Setup/Fallback.

**Tech Stack:** Python3.12, vorhandener Docker-Daemon, festes Python-Basisimage, 34 festgelegte Wheels, vorhandenes Node. Keine lokalen Installationen, kein Docker-/Cloud-/Serverstart während der Vorbereitung.

- [x] Quellen/Guard/Lock und CI-Referenz erneut hashprüfen; Bundle deterministisch erzeugen.
- [x] Zuerst Tests für sichere Bundle-Übernahme, Quellenmutation, Ergebniszählung, Befehlsgrenzen und Containerabschluss schreiben und erwarteten Rotlauf beobachten.
- [x] Runner für feste Befehle, getrennte Quellen/Buildkontext/Ergebnisse und zwei eindeutig markierte Container implementieren. Netzwerk nur für öffentliches Basisimage und PyPI-Wheels; Build und Tests ohne Netzwerk. CLI-Fristen/Abbruch von laufenden Prozessen, Abschlussmeldungen und Quellenprüfung auch bei Fehlern erhalten.
- [x] Lokal ohne Docker/Netzwerk testen: echte Dateien/ZIP/Guard, simulierte Docker-Steuerantworten und reale kurze Kindprozesse. Native Linux-Rechte, Docker/Build/Netz und Cloud-Fähigkeit ausdrücklich ungeprüft lassen.
- [x] Bekannte Abweichungen festhalten: Export statt Git-Checkout, Node-Syntax über ES-Modul-stdin für Node24, keine bytegleiche Image-ID voraussetzen. Build-Clientfrist ist keine Garantie für serverseitigen Buildabbruch oder gesamte VM-Ressourcengrenze.
- [x] Einmaligen Umfang, benötigte Download-Domains, Kostenbasis und Stopbedingungen speichern; unabhängigen Astra/medium-Review durchführen und konkrete Befunde schließen.
- [x] Aktuellen Einstieg und Hashindex aktualisieren und den Materialumfang zur Betreiberfreigabe vorlegen. Die Freigabe bleibt offen. Kein B1/B2-Start, keine Umgebungs-/Netzänderung oder kostenpflichtige Aktion aus Vorbereitung ableiten.


Abgeschlossen als reine Vorbereitung:27Runner-Tests und55lokale JS-Syntaxprüfungen, unabhängig Astra/medium ohne offene materielle Befunde. Keine Materialfreigabe/-ausführung. Siehe `runtime/rw-cloud-b1-prep-20261025/RESULT.json`.
