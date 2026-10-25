# Erstes REST-Testpaket und Wiederverwendung

Stand 19.09.2026. Planung nach gezielter Quellprüfung; **keine Implementierung und keine ausgeführten REST-Tests**. Ergänzt [Betriebsvertrag](AURELIA_REST_BETRIEBSVERTRAG_2026-09-19.md) und [25 Fallfamilien](AURELIA_REST_TESTMATRIX_2026-09-19.md). Externe Produktrepositories wurden ausschließlich gelesen. Kein Erstmodul gewählt.

## Befund: vorhandene Bausteine

| Quelle | Tatsächlich beobachtet | Wiederverwendung / Grenze |
|---|---|---|
| Brainpower `governor_workbench/runtime_profiles.py` | Expliziter local_probe, Quellenfingerprint, begrenzte Readiness-Antwort, NoRedirect, Instanzkennung; Konstruktor schreibt Journal und startet Watcher | Entwurfsmuster für Nachweise und begrenzte Kommunikation. Nicht als harmlose Hilfsbibliothek gegen das echte Governor-Journal importieren. Keine REST-/mTLS-Abnahme daraus ableiten. |
| Brainpower `governor_workbench/process_tree.py` | WindowsJob über kernel32; Start erst nach Prozesszuordnung, Kill-on-close | Windows-Prozessbesitz vorhanden; nicht auf Ubuntu übertragbar. Eigener Linux-Prozess-/Abbruchnachweis bleibt nötig. |
| Aurelia `src/lib/auth/server.ts`, `verify.server.ts` | Better Auth, Broker-/Previewpfade, serverseitige Sitzungsauswertung; bei ausgeschalteter Auth und ohne Datenbank unter Bedingungen Dev-User-Fallback, mit Datenbank Sperre; zusätzlicher gateIdentity-Pfad referenziert | Verifizierte Sitzung ist ein möglicher späterer Anschluss, aber kein Nachweis vollständiger Mandanten-/Dienstdelegation. Keine Preview-Credentials oder Brokeraufrufe für das synthetische Paket übernehmen. Gate-Identity-Unterpfad hier nicht vollständig geprüft. |
| Aurelia `scripts/check-auth-invariant.mjs` | Vergleicht Auth-Schalter zwischen Dev und Build; unbeobachtbarer Zustand separat | Nützliche Konfigurationsprüfung, keine Berechtigungs- oder mTLS-Prüfung. |
| RadiWorks `engine/src/radiworks/scope.py` | Nur lokaler Scope zugelassen; enforced wird abgewiesen; eingehende Aurelia-Scope-Header im lokalen Betrieb verboten | Positiver Schutz vor vorgetäuschter Delegation. Noch kein produktiver Mehrmandantenadapter; diesen Schutz nicht für einen Test deaktivieren. |
| RadiWorks `engine/src/radiworks/main.py` | FastAPI-App-Fabrik, Fehlerhülle error/code/message; 422 für Validierungsfehler; Initialisierung weiterer Komponenten | Nur Formatreferenz. Nicht als synthetischen Dienst starten/importieren: Initialisierung kann Laufzeitdaten berühren. Vorgeschlagene 400-Adapterantwort braucht ausdrückliche Übersetzung von 422. |

Die gezielte Suche in Brainpower-Pythonquellen und Tests hat keinen passenden mTLS-/Zertifikatsadapter nachgewiesen. Dateinamenssuche in Aurelia ist kein Beweis der Abwesenheit einer CA-Lösung. Keine systemweite Bestandsprüfung, kein Laufzeit- oder vollständiger Auth-Audit. Alte Planungsdokumente (Passkeys/TOTP) und gefundene Broker-/Previewpfade müssen vor Produktintegration zusammengeführt werden; daraus folgt weder ein belegter Defekt noch eine Freigabe des Brokerpfads.

## Begrenztes Paket in drei Stufen

| Stufe | Lieferumfang | Nachweisgrenze / Voraussetzung |
|---|---|---|
| T1 – lokaler Vertragskern | Reiner Validator, synthetische A/B-Identitäten, deterministische Uhr, feste Manifest-/Schemafixtures, Fehlerübersetzung und Zustandsmodell; getrennt von Governor-App und Produktcode | Belegt ausschließlich Logik. Kein TLS-, Linux-Prozess- oder echtes Aurelia-Auth-Ergebnis. Zuerst A02/A03/A05/A08–A11 und B06 als jeweils benannte Teilvarianten. |
| T2 – isolierter Transport | Eigener CPU-Testdienst mit einem deterministischen Analyse-Endpunkt, Test-Autorisierungsdienst und Testzertifikaten; direkter mTLS-Pfad; kontrollierte Fehler-/Verzögerungsinjektion | Tatsächliche Übertragung und Identitätsprüfung; A01/A04/A06/A07/A12 sowie B01–B06. Windows-Ergebnis nicht als Ubuntu-Ergebnis darstellen. |
| T3 – Ubuntu-Lebenszyklus | Dasselbe versiegelte Testpaket im getrennten Testbereich; eigene Dienst-/Prozessidentität, harte Ressourcenbegrenzung, Journal, Abbruch und Wiederanlauf | B07–B09 und gezielte Linux-Wiederholung der relevanten Transportfälle. Erst nach konkreter Testbereich-/Ausführungsfreigabe. Kein Produktserver-Reboot erforderlich. |

Für jede Stufe separater Bericht mit Plattform und Variantenstatus. Familien mit nur Teilnachweisen bleiben offen. C01–C04 (Promote, Mutationen, WS, Jobs) bleiben außerhalb des Erstpakets. Keine automatische Zusammenrechnung zu S4 oder Produktfreigabe.

Der Testdienst verarbeitet nur eigens erzeugte Daten und liefert einen bekannten synthetischen Ergebniswert plus ausdrücklich unsignierten Test-Passport. Er importiert keine Produktmodule, verwendet keine reale Datenbank und aktiviert keine Hardware. Ein simuliertes Erfolgsresultat ersetzt keine spätere fachliche Kernelprüfung.

## Technikentscheidungen vor Code oder Serverausführung

| Entscheidung | Empfehlung für dieses Paket | Noch zu klären |
|---|---|---|
| Lokale Ablage | Eigenständiges Testverzeichnis unter Brainpower, unabhängig von live journal.db; ausschließlich temporäre Testdaten | Konkreter Implementierungsplan und Freigabe des abgegrenzten Pakets |
| Sprache / Abhängigkeiten | Python-Standardbibliothek für den begrenzten Testkern; keine zusätzliche Governor-Produktabhängigkeit | Unterstützte Python-/TLS-Laufzeit prüfen; begrenzte Schemafixtures ausdrücklich nicht als allgemeinen JSON-Schema-Validator ausgeben |
| Zertifikate | Ausschließlich separate kurzlebige Testidentitäten; benötigte Ausgabe-/TLS-Werkzeuge vor Nutzung prüfen | Werkzeugversionen/-verfügbarkeit und genaue Parameter; keine neue produktive CA nur für Tests einführen |
| Authentifizierung | Deterministische Test-Autorität für synthetische Rollen und Entzug; echte Aurelia-Auth später separat anbinden | Live-Auth-Konzept samt gateIdentity gezielt prüfen, bevor echte Sitzungskontexte verwendet werden |
| Linux-Isolation | Eigener nachweisbarer Ausführungskontext und Ressourcenlimits; WindowsJob nicht kopieren | Verfügbare Linux-Mechanik und minimale Rechte lesend feststellen, danach konkret entscheiden |
| Ports / Netzwerk | T1 ohne Netzwerk; T2/T3 ausschließlich lokale Testverbindungen, kein öffentlicher Listener oder Firewallwechsel | Freie Testports erst vor Start ermitteln, bestehende Dienste bei Belegung unberührt lassen |
| Cleanup | Nur eigene temporäre Dateien/Prozesse anhand Lauf- und Eigentumsbeleg entfernen; Ergebnisse ohne Geheimnisse behalten | Berichtsscope und sichere Aufbewahrung; Testschlüssel nicht in Git oder generelle Logs |

## Konkrete nächste Reihenfolge

1. T1 als erstes kleines Implementierungspaket mit festen Schnittstellen und Prüfvarianten planen. Keine Kopplung an den laufenden Governor, keine Produktänderung nötig.
2. Vor T2 nur benötigte lokale Python-/TLS-/Zertifikatswerkzeuge lesend prüfen; daraus konkrete Transportimplementierung ableiten. Keine Installation aus dieser Dokumententscheidung.
3. T3 erst nach T1/T2 und gesonderter Festlegung des Ubuntu-Testbereichs vorbereiten. Vorhandene Server-/Recoverygates bleiben unverändert.

Diese Fassung beendet die allgemeine Paketabgrenzung. Weitere Arbeit soll konkrete Implementierungsentscheidungen und überprüfbare Tests liefern, keine neue allgemeine Konzeptschicht.

## Beobachtete Quellstände

SHA256 der vollständig gehashten Dateien; gelesen wurden gezielte Abschnitte, keine Vollprüfung des gesamten Codes:

| Datei | SHA256 |
|---|---|
| Brainpower/governor_workbench/process_tree.py | `985ac4929017c0366034624c6cdd3cb43f0a9523f729b77562830803f4d02bff` |
| Brainpower/governor_workbench/runtime_profiles.py | `43008dfd9697d5aa10e4e35a2c6d33b8f88d67a50079e2c91566574e490d2730` |
| RadiWorks/engine/src/radiworks/scope.py | `5eb666ed32c359863f3f69d23850397f828685aa2c454718d1a6eeebe7b03242` |
| RadiWorks/engine/src/radiworks/main.py | `b94643bfa4ff6456cd9bbcd4d1c3f6eb6bb99632616c2491e8bcd5b2ab29f62a` |
| Aurelia/src/lib/auth/server.ts | `9c685989463821b0180121e905d44a0558ba19d37cd509b5e164fb912447557d` |
jects.de:9443/cgi/url_redirect.cgi?url_name=man_ikvm_html5_bootstrap
RadiWorks-Pfade relativ zu radiworks_port; Aurelia relativ zu Documents/ChatGPT/Aurelia. Keine Konfigurationswerte aus .env, Schlüsseldateien oder Preview-Secrets gelesen.
