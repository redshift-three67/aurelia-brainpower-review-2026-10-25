# Aurelia-/Modul-Templates: Entscheidungsvorlage vor Integration

Status: vorbereitet, keine Vertragsänderung oder Produktfreigabe. Quellen und Hashes: `verification/WIEDERAUFNAHME_2026-09-19.md`.

| Punkt | Beleg / offene Grenze | Empfohlener nächster Abschluss |
|---|---|---|
| Historischer Ground-Zero-Plan | Alte Dokumentation beschreibt Server vor Installation. Ubuntu 24.04, VPN, Firewall, RAID und grafischer Betrieb inzwischen separat belegt. | Bestehende Installation als Iststand bewerten; Gatekriterien einzeln aktuellen Belegen zuordnen. Keine erneute Installation und keine pauschale G0-Freigabe. |
| Sicherung | Konfigurationsarchiv auf SMB zurückgelesen; Schlüsselkopien E:/F: geprüft; Grafikstartlinks separat auf E:/F: nachgesichert. | Als begrenzte Konfigurations-Recovery dokumentieren. Keine Vollserver-/LUKS-/Datenbank-Recovery behaupten. |
| Kernelaufruf | Aurelia ABI v1: Python/WASM-entry; Modulvertrag: versioniertes REST-Profil, entry nur Übergangsmetadatum. | Versioniertes REST-Integrationsprofil als ausdrückliche Aurelia-Vertragsergänzung zur Entscheidung vorlegen. Schemas, Hashbindung, Budgets und CopyGuard bleiben Pflicht; keine stillschweigende Umdeutung bestehender ABI. |
| Identität und Mandanten | Modulprototyp ohne Auth; nullable tenant_id/client_id sind kein Trennungsnachweis. | Vor produktiver Nutzung vertrauenswürdige Identität und durchgängige Mandantenprüfung samt Negativtests verlangen. Bis dahin nur isolierte synthetische Laborprüfung. |
| S4-Nachweis | RadiWorks lokal S0–S3 dokumentiert, S4/S5 nicht zertifiziert. | Tatsächliches Manifest, wiederholbaren Ubuntu-Smoke, WebSocket/Reconnect, CopyGuard und Betriebsanleitung prüfen. Dokumentbeispiele ersetzen keinen Laufzeittest. |
| Erstmodul | Historische Migrationsreihenfolge Morphic zuerst; kein neuer Betreiberentscheid für erstes Modul. | Nach Vertragsklärung Reihenfolge und konkreten Adapterumfang ausdrücklich festlegen; RadiWorks nicht automatisch auswählen. |

Sinnvolle Reihenfolge: Iststand-/Gateabgleich → verbindliche Schnittstellenentscheidung → Modul-/Adapterauswahl → isolierte Linux-Prüfung → gesonderte Integrationsfreigabe. Keine Änderungen in den fünf Produktrepositories durch diesen Bericht. Das gesamte Hermes-Projekt wird damit nicht als abgeschlossen bezeichnet; sein nachgewiesener Umfang bleibt das direkte unabhängige Pilotprofil.
