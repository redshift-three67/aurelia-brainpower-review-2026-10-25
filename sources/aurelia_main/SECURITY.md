# Sicherheit

Dieses Repository darf **keine** Zeugen, Klientenakten, Schlüssel oder
Produktionsdumps enthalten.

Art.-9-Daten gehören ausschließlich auf den Betreiber-Server
(Ubuntu Server 24.04.4 LTS, EU), envelope-verschlüsselt.

ChatGPT/Codex auf diesem Host darf ausschließlich Quellcode und synthetische
Testdaten im unprivilegierten Entwicklungsprofil sehen. Produktionssecrets,
Klientendaten und Datenbankzugänge sind technisch zu trennen.

Verdacht auf Leak: Repository sperren, Keys rotieren, betroffene Mandanten
informieren. Produktspezifikation: `docs/03-security-dsgvo.md`.
