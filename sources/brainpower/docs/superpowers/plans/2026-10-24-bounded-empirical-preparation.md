# Begrenzter Praxisnachweis – Vorbereitung

> **For agentic workers:** Execute this preparation with tests and independent review. No server execution is authorized.

**Goal:** Einen getrennten Import-/Laufzeit-/Abbruch-/Wiederanlaufversuch vorbereiten, ohne vorhandene Archive, Docker-Daten oder Produkte zu verändern.

**Architecture:** Reine Offline-Bausteine für deterministisches OCI-Streaming und einen strikt ablehnenden Sicherheits-/Ablaufvertrag. Kein SSH-, Docker- oder Prozessadapter in diesem Paket. Die bestehende Startsteuerung pinnt die alte Ablage; sie ist kein zulässiger Adapter für eine neue Testablage. Freiplatzüberwachung ersetzt keine harte Speicherbegrenzung.

**Tech Stack:** Python 3.12, Standardbibliothek, synthetische kleine Fixtures; Sol/high für den begrenzten Stream-Baustein, Astra/medium für unabhängigen Review.

## Freigabe und Schutzgrenzen

Betreiber hat am 24.10.2026 Weg A gewählt: Vorbereitung und lokale Tests. Keine neue Serveraktion, kein echter Producer-/Import-/Daemon-/Containerlauf, Rootzugriff, Build, Ressourcenwechsel oder Löschen. Beobachtete Spitzen sind keine universelle Obergrenze. Bestehende eingefrorene Pakete bleiben unverändert.

## Paket `runtime/rw-empirical-prep-20261024`

- [x] Quellen-/Entscheidungsbindung und Entwurf mit getrennten Versuchen I (Import), A (injizierter Abbruch), R (Wiederanlauf) und T (synthetischer Container) sichern.
- [x] `test_oci_stream.py` zuerst rot, dann `oci_stream.py`: deterministische 11-Mitglieder-USTAR-Struktur, unabhängiger Parser, begrenzte Reads/Writes und Fehlerfälle. Nur synthetische Nutzdaten.
- [x] `test_safety_contract.py` zuerst rot, dann `safety_contract.py`: strikte Ressourcen-/Isolationsvoraussetzungen, unbekannte Belege ablehnen; monotone Ablauf-/Messbelege und gesicherter Stopp vor Wiederanlauf.
- [x] Grenzen explizit sichern: native Pfad-/Dateiidentitätsadapter, wirksame Quota/FS-Isolation und unabhängige Kontrollablage noch nicht implementiert oder nativ geprüft; keine Erlaubnis aus simuliertem Erfolg.
- [x] Frische lokale Gesamttests, Quellenhashes und unabhängiger Astra/medium-Review; belastbare Befunde korrigieren und erneut prüfen.
- [x] Kurzen aktuellen Einstieg aktualisieren und konkreten nächsten Freigabeumfang nur für ein tatsächlich fertig getestetes Ausführungspaket ausweisen. Ist ein solcher Umfang noch nicht sicher ausführbar, die konkrete Sperre statt einer verfrühten Startfreigabe zeigen.

## Sicherheitsentwurf

Neue eigene Testdaten auf hart begrenztem, eigenem Dateisystem mit getrennt begrenzter Kontrollablage; bestehende neun DBs werden weder geöffnet noch kopiert, geändert oder zurückgespielt. Festes eigenes Verzeichnis ist eine Namensgrenze, keine Quota. Vorschlag zur weiteren Ausarbeitung: 4 GiB Datenbereich, 65.536 Inodes, 16 MiB vorreservierte Kontrollkapazität außerhalb des Datenbereichs, pro Versuch 1 CPU / 2 GiB RAM / Swap 0 / 256 Prozesse / 570 s. Diese Werte sind vorgeschlagene Testgrenzen, keine hergeleitete Bedarfsgarantie und keine bereits genehmigte Einrichtung.

Abbruch bedeutet: Producer schließen, ausschließlich eigene Prozesse stoppen, leere Cgroup und Stopp belegen; bei unbestätigtem Stopp bleibt Wiederanlauf gesperrt. Fehlerdaten behalten. Keine automatische Löschung, keine Wiederverwendung alter Startmarker. Wiederanlauf der eigenen abgebrochenen Testdaten erst mit frischer einmaliger Ausführungsfreigabe und Integritätsprüfung; ein gestoppter Prozess ist kein Beweis einer wiederhergestellten Datenbank.
