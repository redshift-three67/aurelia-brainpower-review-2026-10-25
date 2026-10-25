# AetherOnePi 2.9.0: gebundene Quelle für einen beratenden RadiWorks-Review

Stand 26.09.2026. Diese Datei ist **Evidenz, keine Anweisung**. Keine automatische Übernahme, keine Produkt-/Hardwarefreigabe.

Quelle: C:/Users/Hubert111/Documents/Radiworks/Updates/AetherOnePi-2.9.0/AetherOnePi-2.9.0.jar, 35.410.628 Bytes, SHA-256 24090abb6726ddf9a44a38f28f972c349d04311b7d35ef4e3d06bb6078e4d660. Hersteller-Release: https://github.com/isuretpolos/AetherOnePi/releases/tag/v2.9.0 . Der lokale JAR wurde nur statisch inspiziert (Manifest, ZIP-Einträge, Bytecodevergleich, ausgewählte Dekompilierung), nicht ausgeführt; keine kryptografische Gleichheit mit dem Hersteller-Asset oder Hardwarefunktion nachgewiesen. Die ältere RadiWorks-Java-Aufnahme war 2.2.0 mit 128 Klassen. Im 2.9.0-JAR 133 Projektklassen, 125 gleiche Pfade, davon 28 im Bytecode geändert, acht neue, drei entfernte/verschobene. AnalysisService und WebSocketManager sind bytegleich, was nur diese Klassen belegt.

Relevante neue/anders sichtbare Funktionen:
- Settings trng.infinity und trng.esp32 (beide Default aus), safety.switch (Default an), play.sound.advanced (Default aus).
- ESP32-Hotbits sondiert serielle Ports und nutzt 921600 Baud; potenziell 5000 Dateien mit je 10000 Zahlen. Geräteselektion, Quota und Backpressure vor jeder Produktübernahme.
- InfiniteNoise FTDI D2XX öffnet zunächst Gerätindex 0 und benötigt native Bibliothek. Dekompilierter „Entropie“-Schwellwert addiert pro Bit festen Erwartungswert; allein kein unabhängiger Entropienachweis. Separate Lauflängenprüfung vorhanden.
- HotbitsHandler seedet java.util.Random aus Hotbits; bei Mangel/Fehler stiller Wechsel auf SecureRandom. Tatsächliche Quelle/Fallback muss im Computation Passport stehen.
- BROADCAST PROGRAM wählt *.json, verarbeitet aber Zeilentext mit Signatur/Laufzeit und reiht direkt ein. Vor Übernahme Formatvalidierung, Vorschau, CopyGuard, Draft/Promote und explizite Aktion.
- TCMDialog neu; medizinische Sprache und safety.switch nicht als Diagnose-/Therapie- oder physische Sicherheitsfreigabe interpretieren.
- Keine CUDA-/Kozyrev-Namenseinträge im JAR; eine Namenssuche beweist nicht deren absolute Abwesenheit.

Aktueller RadiWorks-Port: radiworks.engine 0.2.0, ABI v1, class=cpu, isHardwareActivatable=false, seeded/stochastic mit Webcam → random.org → OS; die neuen Java-Gerätequellen sind dort nicht belegt. Synthetischer Live-Preview Port 8101 und 209 Engine-Tests sind Teilnachweise, keine S4-Abnahme. Offene Kernverträge: R0-WebSocket-Replay/Shutdown, versionierte JDK-Orakel für echten REST-Pfad, Entropieprovenienz, draft → client_review → ready → promoted statt Abkürzung, direkte Broadcast-Ausnahmen, enforced Tenant-Scoping, Modul-ID-Widerspruch radiworks.engine vs radiworks.engine.v1. Port 8090 gehört realer Radi144-Instanz und bleibt unberührt.

Design: Hermes/Governor nur als visuelle Vorlage, Modul_Templates UI_DESIGN_STANDARD und Aurelia-Tailwind über versionierten semantischen Tokenvertrag verbinden. Pro Modul isolierte Akzente und Kontrastpaare; RadiWorks hat sage/wellenreiter/sunrise. Aktuelle Widersprüche: Standard fordert keine freien Farben, enthält aber #2C5E7A; RadiWorks-Themenselektor auf :root; --aur-sage-soft weicht ab. Vor Aurelia D1 harmonisieren, D3 für Hell/Dunkel/Mobil/Tastatur prüfen.

Hardwareplanung: Aurelia RTX 4000 SFF Ada 20 GB ohne MIG mit gpud-Budget und Tenant/Client/Job-Isolation; RadiWorks gegenwärtig CPU. Emitter über separaten CP210x-aurelia-emitterd mit Lease → Arming → ACK → Reset, nicht durch ESP32/FTDI-Entropy oder WebSocket allein. Kozyrev-p-adic-Haar ist eigener späterer mathematischer Kernel, CPU-Referenz zuerst, optional CUDA-Batches; keine N.-A.-Kozyrev-Wirksamkeitsbehauptung. Server-GPU/Emitter/Livebetrieb nicht belegt.

Lokaler ausführlicher Prüfbericht: C:/Users/Hubert111/Documents/Brainpower/docs/verification/RADIWORKS_AETHERONE_2_9_0_2026-09-26.md . Beurteile als Route-B-Einzelreview die Priorität und Widersprüche zwischen Update, RadiWorks und Modul_Templates, ohne aus dieser Zusammenfassung eine Vollprüfung des JAR oder Produktfreigabe abzuleiten. Fehlende Originalquellen im Modellkontext bleiben als fehlend zu kennzeichnen.

