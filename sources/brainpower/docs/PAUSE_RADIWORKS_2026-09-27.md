# Pause und Wiederaufnahme: Hermes/RadiWorks, 27.09.2026

Persönlicher lokaler Wiederherstellungspunkt nach der Quellenanalyse: checkpoints/Hermes-RadiWorks-20260927-Pause. Neuer Wiederherstellungspunkt nach der Betreiberentscheidung zur Fortsetzung: checkpoints/Hermes-RadiWorks-20260927-PlanPause. Diese Notiz ist der kurze Einstieg für die Fortsetzung. Bestehende Produkt- und Server-Gates bleiben unverändert.

## Gesicherter Arbeitsstand

- Aktueller Quellenbericht: docs/verification/RADIWORKS_AETHERONE_2_9_0_2026-09-26.md. Statischer Vergleich der lokalen AetherOnePi-2.9.0-JAR (SHA-256 24090abb6726ddf9a44a38f28f972c349d04311b7d35ef4e3d06bb6078e4d660) mit der alten Java-Basis und dem RadiWorks-Python-Port. JAR nicht ausgeführt; keine Hersteller-Asset-Gleichheit oder Hardwarefunktion bewiesen.
- Für Hermes neu angelegte externe RadiWorks-Gedächtnisquelle: project_memories/AETHERONEPI_2_9_0_SOURCE_2026-09-26.md, SHA-256 61cf1082d2974c395ff2dec1a58a8d1dbd0dcb034b86fb65c0ffb9a2214f4175. Inhalt ist begrenzte, statische Evidenz, nicht der vollständige JAR.
- Echter manueller Hermes-Einzelreview 6a0f74806661490f8bb31bbb640548af auf Scope-Hash 391aa3ea1918a0fd05c7acef9ecb1b16ba2497efe7b44f7fd207c8a3eaaed000: Sol 6/high, Luna 6/max und wegen Risikosignal Astra 6/medium tatsächlich aufgerufen. Kombinierter Status BLOCK für belastbare Integrationsaussagen, weil aktuelle Modul_Templates-/Aurelia-Originalverträge im Modellkontext fehlten. Der Benutzer hatte den lesenden Abgleich dieser Projekte ausdrücklich beauftragt; Lunas gegenteilige Berechtigungsannahme ist nicht maßgeblich. Der lokale Bericht las und hashte die aktuellen Vertragsdateien separat.
- Der Hermes-Job markierte sich vorsorglich stale/unknown. Ein anschließender frischer Scope-Scan lieferte denselben Hash; die interne Markierung wurde nicht übergangen. Keine Produktfreigabe, kein neuer Matrixplan, keine Änderung an Aurelia-Code oder Server.
- Aktueller RadiWorks-Prototyp bleibt in eigenem Repository mit vorhandenem WIP; synthetischer Preview war auf Port 8101, reale Radi144-Instanz auf 8090 bleibt unberührt. Die früheren 209 RadiWorks-Tests sind ein älterer Teilnachweis, heute nicht erneut ausgeführt.
- Vor der Pause geprüft: null aktive Governor-Modellaufträge, automatische Reviews aus, null aktive Governor-Live-Sitzungen. Bestehende Serverrestpunkte aus docs/SERVER_AKTUELL.md bleiben offen; keine Serveraktion heute.

## Betreiberentscheidung und neue Erkenntnisse vor dieser Pause

- Der Betreiber hat den vorgeschlagenen schrittweisen RadiWorks-Weg bestätigt. Der aktuelle Python-/Web-Prototyp ist die Funktionsbasis. Kernalgorithmen und Original-Workflow bleiben als nachvollziehbare Referenz erhalten; neue AetherOnePi-Funktionen werden nur einzeln und nach stabilen Tests ergänzt. Keine pauschale 1:1-Freigabe.
- Die offizielle GitHub-Versionshistorie bezeichnet v2.9.0 als „Ego Cleaner“. Im lokal vorhandenen JAR führt der untersuchte `EGO CLEANER`-Ereignispfad lediglich `sounds/EgoCleaner.wav` über `SoundFile.play()` aus. Das ist ein Kandidat für eine optionale Klangfunktion, kein nachgewiesener neuer Analysekern. Weitere Änderungen seit der 2.2-Basis separat inventarisieren; der JAR wurde auch bei dieser Prüfung nicht gestartet.
- Die vorhandene Paritätsmatrix belegt exakt drei seeded `POST /analysis`-Fälle mit je 300 synthetischen Raten gegen unabhängige Java-Orakel. Andere Kataloge, Kollisions-/Treeify-Fälle, Hilfsalgorithmen, Persistenz und stochastic-Pfade bleiben außerhalb dieser Aussage. Heute wurde keine RadiWorks-Testsuite neu ausgeführt.
- ESP32 und InfiniteNoise können wegen fehlender lokaler Geräteanbindung nicht als physische Quellen am Rootserver genutzt werden. Linux-Systemzufall ist für den optionalen Rechenpfad ein anders zu kennzeichnender Ersatz; GPU-/CUDA-Zufall ist kein TRNG-Nachweis. Ob der Server `/dev/hwrng` oder eine andere geeignete physische Quelle besitzt, ist nicht geprüft. Keine Hardwareänderung oder Freigabe.
- RadiWorks ist CPU-Prototyp. Aurelia beschreibt CUDA-Scheduler und den mathematischen Kozyrev-Wavelet-Kernel in Verträgen und Konzeptoberflächen; auf dem Server ist eine NVIDIA-Karte mit Treiber belegt, aber kein CUDA-/Kozyrev-Produktlauf. Originalanalyse, optionale DSP-Erweiterung und künftige GPU-Batches bleiben getrennte Pfade.

## Morgen genau hier weiter

1. Diesen Text, den Quellenbericht, `radiworks_port/engine/PARITY_MATRIX.md` und den aktuellen RadiWorks-Quellstatus lesen; Checkpoint nur bei tatsächlichem Verlust zurückspielen. Vor Änderungen die vorhandene WIP erhalten.
2. Eine quellgebundene Funktionsmatrix erstellen: aktueller Prototyp ↔ Originalbasis 2.2 ↔ Versionen bis 2.9.0. Analyse/GV, Fälle/Sitzungen, Raten/Stick-Pad, Broadcast, Bild/Area, Peggotty und Entropie einzeln als vorhanden, abweichend, fehlend oder optional markieren. Ego Cleaner als Klangpfad und andere neue Optionen konkret prüfen.
3. Den R0-WebSocket-/Shutdown- und Zustandsabgleich stabilisieren. Begrenzte Java-/Python-Orakel und synthetische Live-Workflow-Tests für die beanspruchten Kernpfade erweitern; dokumentierte Aurelia-Abweichungen ausdrücklich kennzeichnen. Danach Draft/CopyGuard/Promote und enforced Scope schließen.
4. Nur sinnvoll und stabil umsetzbare Update-Funktionen additiv, einzeln abschaltbar und mit Regressionstest ergänzen. Physische Entropiequellen bleiben optional; Systemzufall nicht als ESP32/InfiniteNoise ausgeben. CPU bleibt Referenz; CUDA/Kozyrev erst getrennt nach belegter Aurelia-Laufzeit und eigenen Gates.
5. Den Design-Tokenvertrag mit Modul_Templates/Aurelia vorbereiten. RadiWorks lokal S4 prüfen; danach Radi144, morphic_v1 und neuer Modulprototyp. Vollständiger Aurelia-Matrixplan und eigentliche Integration folgen separat nach G0-SRV-GROUND-ZERO, AUDIT-02 und den Produktgates.

Reasoning-Arbeitsvorgabe: für diese Analyse nicht auf Low wechseln; kein manueller Wechsel offen. Die vom Betreiber gewählte Chatroute Sol/high mit bedarfsweiser Luna/max- und Astra/medium-Delegation bleibt eine Bedienentscheidung, keine aus Dateitext beweisbare aktive App-Einstellung.

