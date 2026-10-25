# RadiWorks – praktischer Vergleich Codex Cloud und Linux-Pilotserver

**Neue Betreiberentscheidung25.10.2026:** Cloudvergleich zurueckgestellt; HauptwegCLI/Desktop + GitHubCI + LinuxPilotserver freigegeben. Die frueherePflicht eines fertigenCloudvergleichs vorStrategieentscheidung ist ausdruecklich ueberholt. CP1 erfolgreich; weiter mit `2026-10-25-radiworks-ci-cp2a.md`. Keine neueMaterial-/Kostenfreigabe aus der Strategiewahl ableiten.

> **For agentic workers:** Use superpowers:executing-plans for the approved preparation. Execution, network access and costs remain subject to the explicit gates below.

**Goal:** Nach dem erfolgreichen CP1 dieselben synthetischen RadiWorks-Prüfungen in einer tatsächlich verfügbaren Codex-Cloud-Umgebung erproben und die reale Kopplung zum IPv4-Pilotserver nachweisen. Erst dann entscheidet der Betreiber über die Strategie.

**Architecture:** CI, Cloud-Entwicklung und dauerhafter Pilotbetrieb erfüllen unterschiedliche Aufgaben. GitHub als Quellverwaltung ist von GitHub Actions als Ausführungsdienst zu unterscheiden. Keine neue Build-VM, kein Ersatz stabiler Produktalgorithmen und keine automatische Weiterführung des zurückgestellten Imports I.

**Tech Stack:** Bestehender RadiWorks-Quellstand, festes Python-Basisimage, 34 hashgebundene Wheels, vorhandene Python-Tests und JavaScript-Syntaxprüfung; Cloud-/Docker-/Netzfähigkeiten sind vor ihrer Verwendung nativ zu belegen.

## Feste Vergleichsbasis

- Produktquelle: `d1eb34260179a499e2b0362bf609ce96957b78aa`, 204 kanonische Dateien.
- Geprüfte CI-Steuerung: `946193f3cb86ee7a1719543d61e63b64c5b3919a`. **Main enthält einen älteren Produktstand:** Cloud darf die Produktdateien aus Main nicht versehentlich als Vergleichsquelle verwenden. Steuerung und Produkt müssen getrennt an ihre jeweiligen Commits gebunden werden.
- Basisimage: `python@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258`; Dockerfile, Lockfile und Wheelhashes bleiben unverändert.
- Testdateien: `test_analysis.py`, `test_rates.py`, `test_gold_parity.py`, `test_bootstrap.py`; CP1:33 Tests,0 Fehler/Fehlschläge/Skips,55 JS-Syntaxprüfungen,34 Wheels,204 Quellen vor/nachher.
- Gemessene CI-Referenz: Run40173688749,39 Sekunden Jobzeit,13,02 Sekunden pytest; dies ist ein einzelner Lauf, kein allgemeiner Geschwindigkeits- oder Lastbenchmark.
- Eigene Cloud-Builds müssen Quell-/Abhängigkeitsidentität belegen. Gleiche Eingaben garantieren keine bytegleiche Image-ID. Bei Übertragung eines fertigen Images ist dagegen genau dessen tatsächlicher Digest zu verifizieren.

## B0 – Konto, Kosten und Startfähigkeit klären

- [x] Aktuelle offizielle Dokumentation und vorhandene lokale CLI-Hilfe lesen; keinen Cloud-Auftrag starten.
- [x] Cloud in Chrome öffnen; fehlende OpenAI-Anmeldung feststellen und Betreiber um Anmeldung mit demselben Konto bitten. GitHub-Anmeldung allein genügt nicht.
- [x] Nach Anmeldung Tarif/Kontingent/Cloud-Bestand lesend geprüft: Pro100,98%Wochenkontingent,1000Credits,neue Cloud verfügbar,0gespeicherteUmgebungen. Zahlungshinweis erkannt; keine Zahlungsdaten gespeichert/Änderung oder Einrichtung gestartet.
- [x] Genau eine private Umgebung nur für `redshift-three67/radiworks-pilot` planen. Vor `Get started`/Setup/Publish konkrete automatische Installationen, Umfang und Kosten vorlegen; bereits Setup kann Nutzung verbrauchen.
- [x] Erst nach dieser Freigabe eine begrenzte Fähigkeitsprobe: OS/Architektur, Versionen, freier Arbeitsbereich und nutzbare Docker-/Netzfunktionen. Keine generelle Umgebungsvariablen-/Schlüsselausgabe und kein automatischer Docker-Daemonstart.

B0 ist ein vorbereitendes Gate und erfüllt den verlangten praktischen Vergleich noch nicht.

## B1 – tatsächlicher synthetischer Cloud-Lauf

- [x] An die belegten Fähigkeiten angepassten Runner vorbereiten, lokal testen und unabhängig prüfen; nicht ungeprüft das an GitHub-Variablen gebundene CI-Skript als Cloud-Runner verwenden.
- [x] Kosten und Ausführungsgrenzen vorlegen. Kein zusätzlicher Securityscan, keine anderen Repositories, Klienten, Datenbanken, Medien oder geschützten lokalen Definitionen.
- [ ] Nach eigener Ausführungsfreigabe genau ein nativer Cloud-Lauf mit denselben Quellen, Wheelhashes und seriellen Tests. Containergrenzen nach Möglichkeit unverändert; jede technisch erforderliche Abweichung vorher ausweisen.
- [ ] Quellen vor/nachher, tatsächliche Versionen, Build-/Imageidentität, Testergebnis, Dauer, Abbruch und Abschluss sowie tatsächlichen Kontingentverbrauch speichern. Fehlende Docker- oder Browserfähigkeit als Grenze ausweisen; keine stillen Ersatzprüfungen.

## B2 – reale Kopplung zum Pilotserver

- [ ] Vor Zugangseinrichtung den tatsächlich unterstützten Transport prüfen. Bestehendes WireGuard bedeutet keine automatische Cloud-Erreichbarkeit; dokumentierte Tailscale-/HTTP(S)-Funktionen beweisen keinen SSH-Zugang.
- [ ] Nur den bestehenden IPv4-Pilotserver und das Aurelia-Projektbudget verwenden. Das parallele Website-Projekt bleibt getrennt. Keine alten privaten SSH-Schlüssel in Cloud kopieren, keine allgemeine Root-Freigabe, keine Firewallöffnung oder neue Bridge aus der Direktive ableiten.
- [ ] Wenn ein direkter begrenzter Weg unterstützt wird: konkrete Authentisierung, Zielpfade, Befehlsumfang, Laufzeit-/Speichergrenzen und Rücknahme vorbereiten, testen/reviewen und zur eigenen Freigabe vorlegen.
- [ ] Danach realen, begrenzten Übergabe-/Steuerungsnachweis mit verifizierter Artefaktidentität, synthetischer Ausführung und kontrolliertem Abschluss durchführen. Ein reines Ping-, Versions- oder Metadatenergebnis genügt nicht.
- [ ] Wird die direkte Kopplung nicht unterstützt, das Ergebnis als technische Grenze dokumentieren. Kein neues aufwendiges Gateway-Projekt beginnen; eine lokale SSH-Übergabe wäre ein gesonderter Workflow und kein Beweis direkter Cloud-Steuerung.

## Vergleich und Entscheidung

Die drei Wege werden anhand tatsächlich erreichter Funktionen, Reproduzierbarkeit, Bedienbarkeit/Livezugang, Sicherheit/Mandantentrennung, Abbruch/Recovery, Hardware-/Datenbanknähe, Kosten und manueller Pflege gegenübergestellt. Offene oder nur dokumentierte Fähigkeiten bleiben entsprechend gekennzeichnet. Für weitere Module die gemeinsamen Prüfbausteine wiederverwenden; modulbezogene DB-, Geräte- und Workflow-Abnahmen bleiben eigenständig.

Vorläufige Empfehlung: CI für standardisierte wiederholbare Prüfungen, Pilotserver für dauerhafte Live-/Integrations-/Recoverytests; Codex Cloud als mögliche entfernte Entwicklungsumgebung nach praktischem Nachweis. Nicht alle Prüfungen müssen in derselben Umgebung stattfinden. Vollständige Regression, SQLite-Fix, Browser-/Geräteabnahme, zentrale DB-Verträge und Aurelia-Integration bleiben nach der Strategieentscheidung erforderlich.

## Aktuelle offizielle Grundlagen, gelesen am25.10.2026

- [Cloud-Umgebungen](https://learn.chatgpt.com/docs/environments/cloud-environments): isolierte Task-VMs, wiederverwendbare Einrichtung, veröffentlichte Umgebungen und Netzsteuerung. Kontoabhängige Freigaben sind erst zu prüfen.
- Dort dokumentiert: Plus2vCPU/8GiB/8GiB; Pro/Business/Enterprise4vCPU/16GiB/32GiB. Das sind Standardangaben, keine Messung unseres Kontos.
- Dort dokumentiert: begrenzte Wiederherstellungszeit des Taskzustands, aktuell keine Computer-/Browsersteuerung, private IPv4-Netze über unterstützte Tailscale-HTTP(S)-Wege. Headless-Testprogramme und raw SSH sind damit nicht für unser Konto nachgewiesen.
- [Preis-/Nutzungsregeln](https://learn.chatgpt.com/docs/pricing): lokale und Cloud-Aufträge teilen Nutzungskontingente; Modell-/Auftragskosten variieren. Kein belastbarer Dollarpreis pro Cloud-Auftrag aus dem API-Preis oder der GitHub-Minute ableitbar.

Dieser Plan ist Vorbereitung. Keine Cloud-Umgebung, kostenpflichtige Aufgabe, Zugangserweiterung oder Serverausführung ist hierdurch gestartet oder freigegeben.

## Ergänzung nach authentifizierter Kontoabfrage

B0 ist konkret in `runtime/rw-cloud-pilot-comparison-prep-20261025/B0_PROMPT.txt` und `APPROVAL_SCOPE_B0.json` vorbereitet. Die bestehende hashgebundene `cloud-audit`-Funktion wurde lokal mit ihrer Regression erneut geprüft: kein Subprozess-/Produktstart, keine Umgebungs-/Schlüsselwerte. Zusätzlich ist ein einzelner20Sekunden-Docker-Versionsaufruf ausschließlich auf dem lokalen Cloud-Unixsocket vorgesehen; seine native Fähigkeit bleibt offen. Keine Serververbindung in B0. B1/B2 bleiben abhängig von den realen Ergebnissen und separat ausführbar vorzubereiten.

Die Kontoseite zeigt einen möglichen Zahlungsfehler. Vor verbrauchender Einrichtung erst Betreiberklärung und konkrete B0-Freigabe; keinen Rechnungs-/Zahlungszustand aus sichtbarem Kontingent ableiten. Preisrechenbeispiel für Standard-Sol6.1:50000ungecachteEingabetokens und5000Ausgabetokens entsprechen3,75Credits bei Creditabrechnung. Das ist keine Prognose oder Obergrenze und kein Dollarpreis; bei gültigem Inklusivkontingent werden voraussichtlich keine Zusatzkosten fällig.20Minuten operative Betreuung begrenzen die Tokenrechnung nicht technisch. Keine Aufladung/Planänderung/API-Abrechnung oder Securityscan vorsehen.

## Nativer B0-Abschluss25.10.2026

Die ursprüngliche Abweichung im Automatiksetup wurde gesondert einmalig freigegeben. Genau1 Einrichtung und1 B0-Folgeprobe im selben Chat/VM abgeschlossen; danach private Umgebung mit B0-only-Startregel veröffentlicht, kein weiterer Task. Setup UI Sol6.1/Gering, Probe auf Betreiberwunsch Sol6.1/Mittel; Hauptchat unverändert/unverifiziert. HEAD946193…, Guardhash20f513… und beide Exitcodes0 nativ belegt. Linux/x86_64, Python3.12.14, Docker-Version28.4.0/28.4.0 am lokalen Unixsocket. Zählwert5 ist keine garantierte CPU-Quote. B0 enthält keine Netzfähigkeitsprüfung; Paketmanager-Voreinstellung an ist keine totale Netzsperre. Einrichtung meldete33Tests/55JS/HTTP-Neustart auf Main, nicht auf der Vergleichsquelle d1; vollständige rohe Setup-Prüfbelege nicht alle unabhängig verifiziert. Kein B1-Nachweis daraus.

Frisches Kontingent vorher97%,danach96%;1000Credits unverändert und keineCreditnutzung angezeigt. Gemeinsame gerundete Nutzung, keine exakte B0-Kostenmessung. Astra/medium bestätigt native Belege und gespeicherte Konfiguration ohne offene materielle Findings. Siehe `runtime/rw-cloud-b0-execution-20261025/B0_COMPLETION.json`. Frühere Aussagen zu nicht gestarteter Cloud/Zahlungshinweis oben dokumentieren den damaligen Vorbereitungsstand und sind hiermit überholt. B1/B2-Ausführung weiter nicht freigegeben; ImportI bleibt zurückgestellt.


B1-Vorbereitung abgeschlossen25.10.2026: `runtime/rw-cloud-b1-prep-20261025/RESULT.json`.27lokale Runner-Tests/55lokale JS-Syntaxprüfungen und unabhängiger Review; konkrete B1-Ausführung mit1neuemCloudauftrag und2privatenKonfigurationsveröffentlichungen einschließlich Rückstellung vorgeschlagen, noch nicht freigegeben.204Quellen unverändert, Lizenzhinweis erhalten. NativeDocker/Cloud/Netz/B2weiteroffen.
