# Aurelia – lokale Modulreferenzen und zentrale Datenstruktur: konsolidierter Phasenplan

> **Maßgebliche Umgebungszuordnung16.10.2026:** Test-VPS für schrittweise Entwicklung/Funktion/Teilintegration aller Module, Modul_Templates und Aurelia, einschließlich begrenzter Modul-Lastprofile. Vollständige Plattform-/25-Nutzer-/Modulkombinations-/Kapazitätsabnahme später auf dem geplanten und dafür gesondert geprüften Hauptserver unter Zielbetriebskonfiguration. Der VPS muss diese Gesamtlast nicht schaffen; sein Vollastnachweis ist kein Gate zur nächsten Modulaufnahme. [Prüfzuordnung und geplante Hauptserverhardware aus Betreiberanhang](../../AURELIA_MANDANTEN_KAPAZITAET_2026-10-16.md).

> **Betreiberergänzung16.10.2026 – Mandanten/Abos/Kapazität:** [Konsolidierter Vertrag und Prüfplanung](../../AURELIA_MANDANTEN_KAPAZITAET_2026-10-16.md).25 gleichzeitige RadiWorks-Nutzer sowie Einzelmodule/Modulkombinationen in P4/P5 und P8 ausdrücklich berücksichtigen; vorher kleine profilgebundene Kostenmessungen und Schutzmechanismen. Auth-/Objektrecht, Modulabo und hierarchische Ressourcenbudgets getrennt serverseitig durchsetzen. Der aktuelle Pilot ist kein Mehrmandanten-Nachweis. Security-Verbindung/Scan sind inzwischen abgeschlossen; ältere Offenangaben aus43 sind durch [aktuellen Review](../../verification/AURELIA_RW_SECURITY_REVIEW_2026-10-16.md) überholt. Reihenfolge bleibt Ressourcen-/Speicherplatzschutz → gezielte Sicherheits-/Funktionsabnahme → übrige Modulreferenzen/P4/P5 → Kern/Templates/Adapter → echte Mehrmandanten-/Last-/Betriebsabnahme.

> **Maßgebliche Betreiberrevision 15.10.2026:** Remote-Workflow mit Codex Cloud, CI/Docker, Codex Security und eigener Linux-Testinstanz freigegeben; siehe Abschnitt 40. Frühere Anforderungen an lokale Ausführung, zurückgestellte Cloud-Teilstagings und prioritäre Access-Abnahme beschreiben den damaligen Plan. Quellen-/Algorithmusnachweise, P3/P4/P5-Gates und historische Belege bleiben gültig; vorhandene Umgebungen sind nicht als bereits portiert anzusehen.


> Für die spätere Umsetzung: freigegebene Arbeitspakete mit `superpowers:executing-plans` oder begrenzter `superpowers:subagent-driven-development` bearbeiten. Betreiberfreigabe zur Fortsetzung liegt seit 10.10.2026 vor. P0 ist begonnen; lokale Installation/Portierung folgt erst nach belegter Runtime- und Zielisolation. Aktueller Prüfstand: [P0 Referenzen und Ressourcen](../../verification/AURELIA_P0_LOKALE_REFERENZEN_2026-10-10.md).

**Ziel:** Die sechs Module neben RadiWorks quellengebunden und funktional charakterisieren, ihre heutigen Abläufe lokal nachvollziehen und daraus gemeinsam die Aurelia-Datenstruktur entscheiden; erst danach Module und Plattform schrittweise vorbereiten und integrieren.

**Architektur:** Originalreferenzen und lokale Vergleichsumgebungen erhalten zunächst bestehende Modulstrukturen und Algorithmen. Ein später beschlossener zentraler Speichervertrag bestimmt führende Schreibwege, Rechte, Revisionen und Moduladapter. Gemeinsame UX orientiert sich an RadiWorks; fachliche Berechnungen bleiben modulspezifisch.

**Technische Ausgangsbasis:** Explorer und Thom: React/Vite/TypeScript, Supabase-Client und Lovable-Cloud-Dienste. Radi144: vorhandene Python-/API-/Dateiabläufe; RadiMorphic: getrennte Root-/Worktree-Stände; RadiFarben: Access. Aurelia und Modul_Templates bleiben an ihre bestehenden Gates gebunden. Lokale Backendtechnik ist vor Einrichtung zu prüfen, nicht hier endgültig festgelegt.

## 1. Umfang und belegter Stand

Sechs fachliche Module sind **Radi144, RadiMorphic, RadiFarben, Copen, Bohm und Thom**. Mit RadiWorks umfasst die gemeinsame Bedarfsmatrix sieben Module. Copen und Bohm liegen gemeinsam im Resonance Explorer; Thom hat eine eigene Anwendung. Drei Lovable-Module bedeuten derzeit zwei bekannte Quellanwendungen. Weitere App-/Backend-/Servicebeziehungen werden in P0 abgeglichen; eine Aufteilung in drei unabhängige Apps ist nicht vorgesehen.

| Modul | Wiederzuverwendender Bestand | Für vollständigeres Reasoning noch erforderlich |
|---|---|---|
| RadiWorks | R6.2, bestätigte Original-/persönliche Verfahren, Zufallsmodi, Kontext-/Auftragsbindungen, GV-/Watchlist-Verläufe, Medienprofile, Audio und fünf Layer; Start5-Nachweise | Aurelia-Zielrechte, zentrale Speicher-/Katalogverträge, Ubuntu- und Integrationsabnahme. Aktuelle Liveinstanzen bleiben erhalten |
| Radi144 | Lokale Quellen; Klienten/Sitzungen/Artefakte/Audit als JSON, Dateiberichte; vorhandene Berechnungswege | Aktive UI/API/CLI-Abläufe, Fehler-/Abbruchpfade, Ergebnis-/Berichtrevisionen, Archive/Restore und Plattformbezug abschließend verbinden |
| RadiMorphic | Root und registrierter Worktree separat erfasst; Worktree ergänzt Jobpersistenz und Owner-/Lease-Regeln | Autoritativen Quellstand vor dessen Anpassung bestimmen; alle tatsächlichen Router-/Writer-/Rechte-/Event-/Archivpfade und Windows-/Ubuntu-Schlüsselgrenzen erfassen. Nicht mit Bohm gleichsetzen |
| RadiFarben | Aktuelle ACCDB gebunden; 49 lokale/fünf verknüpfte Tabellen, 499 lokale Felder, 47 QueryDefs | Aktuelles VBA, Abfragen, Formulare, externe Quellen und Rechen-/Timer-/Berichtsabläufe kontrolliert lesen; synthetische Originalreferenzen. Metadaten sind keine vollständige Codeversionierung oder Funktionsabnahme |
| Copen | Explorer-Commit gebunden; v1, v2 und separater Generator; begrenzte numerische/UI-/Lebenszyklusproben | Vollständige aktive Pfade, Tabellen-/Vorlagenfamilien, Klienten-ID-Zuordnung, Worker/Queue/Pause/Abbruch/Restart und lokaler Backendbetrieb |
| Bohm | Gleicher Explorer-Commit; Klientenberechnung, Worttest, Bilder, Archive/Sitzungen und begrenzte Referenzproben | Berechnung, Testergebnis und Auftrag eindeutig verbinden; lokale Persistenz-/Rechte-/Worker-/Archivpfade und Grenzfälle prüfen |
| Thom | Eigener Commit; Vektor/Gruppen/Wortsammlungen, Scan/3D/Modelle, Medien/Audio, Berichte/Trends und begrenzte Dienstproben | Vollständige Modell-/Koordinaten-/Referenzpunktbindung, aktive Ergebniswriter, Job-/Sitzungsbindung, lokale Dienste, Audio-/Hardwaregrenzen und Restore |

Quellbindungen und bisherige Grenzen: [Modulbestand](../../AURELIA_MODULDATEN_BESTAND_2026-10-09.md), [Copen/Bohm/Thom-Bestand](../../AURELIA_COPEN_BOHM_THOM_BESTAND_2026-10-09.md), [Referenzprüfungen](../../AURELIA_REFERENZPRUEFUNG_COPEN_BOHM_THOM_2026-10-09.md), [ergänzende Workflowabdeckung](../../AURELIA_WORKFLOW_ABDECKUNG_2026-10-10.md). Die gebundenen Explorer-/Thom-Commits bleiben c69d5aa224018b0484efd90ae456a10aecc78a77 / 18e6c12c238985da698f9a46743d893b30d61ba7; vor Umsetzung frisch rückprüfen.

## 2. Was „vollständig lokal portieren“ bedeutet

Eine lokal geöffnete Oberfläche mit weiterhin aktiver Cloudverbindung ist eine hybride Vorschau. Für eine vollständige lokale Vergleichsumgebung müssen die benötigten Datenbank-, Auth-/Rechte-, Datei-/Storage-, Realtime-, Funktions-, Zeitplan- und Workerpfade tatsächlich lokal laufen. Das Verschieben von PostgreSQL allein übernimmt diese Dienste nicht. Die offiziellen Anbieterunterlagen unterscheiden diese Bestandteile ausdrücklich: [Lovable-Portabilität](https://docs.lovable.dev/tips-tricks/deployment-hosting-ownership), [Supabase-Lokalentwicklung](https://supabase.com/docs/guides/local-development).

Für die erste vergleichbare Reproduktion empfehle ich einen **Supabase-kompatiblen lokalen Dienstumfang**, soweit er die tatsächlich genutzten Schnittstellen abbildet. Die CLI mit einer Docker-kompatiblen Laufzeit ist ein dokumentierter Kandidat, keine bereits eingerichtete oder endgültig beschlossene Aurelia-Produktarchitektur. SQL, Bibliotheken, Renderer und Dienste werden passend versioniert; keine ungeprüfte Aktualisierung auf „latest“.

- [ ] Pro Anwendung ihre heutigen Backendidentitäten, Tabellen, Auth-/Storage-/Realtime-/Funktionsbindungen und gemeinsamen externen Abhängigkeiten erfassen. Getrennte Zielbereiche nach diesem Vertrag bestimmen, nicht allein aus der Anzahl der Oberflächen.
- [ ] Originalschemata, Funktionen, Trigger, Policies und notwendige Referenzkataloge gegen den gebundenen Stand aufbauen; keine späteren Aurelia-Tabellen vorwegnehmen. Providerverwaltete Auth-/Storage-Objekte mit ihrer lokalen Dienstversion abgleichen; keinen P1-Auth-Stub als echte Anmeldung verwenden.
- [ ] Bestehende Klienten, Analysen und laufende Harmonisierungen nicht übernehmen. Frische lokale Testidentitäten und synthetische Fälle verwenden; erforderliche Referenzkataloge/Assets mit Herkunft, Lizenz und Revision aufnehmen.
- [ ] Lokale Secrets neu anlegen, bestehende Deployment-Secrets nicht kopieren. Sämtliche festen Cloud-/WS-/Upload-/CLI-/Workerziele und Cron-/HTTP-Ausgänge vor Start auf erlaubte lokale Ziele binden. Negative Probe muss zeigen, dass die Testkopie bestehende Cloudprojekte nicht beschreibt.
- [ ] Externe KI-, Hardware-, Mail-, Asset- oder sonstige Dienstpfade einzeln klassifizieren. Ein deaktivierter Pfad oder Teststub ist keine vollständig gleichwertige lokale Funktion. Wenn eine Funktion nicht ohne externe Dienste nachbildbar ist, den Umfang ausdrücklich entscheiden; keinen neuen Algorithmus oder lokalen Ersatz als Original ausgeben.
- [ ] Original und lokale technische Anpassung getrennt versionieren. Änderungen an Zielkonfiguration und Infrastruktur von fachlichen Korrekturen unterscheiden; bekannte Fehler zunächst reproduzierbar dokumentieren.

**Machbarkeit vor Einrichtung:** Am 10.10.2026 hatte C: etwa 3,6 GiB frei, F: etwa 381 GiB. `docker`, `podman` und `supabase` wurden im aktuellen PATH nicht gefunden; WSL, Node und npm wurden gefunden. Das beweist weder den vollständigen Installationsstand noch eine funktionsfähige WSL-/Containerumgebung. RAM/Virtualisierung, Laufzeitstatus, reservierte Ports sowie Platz für Images, Builds, Daten, Logs und Rücknahmekopien vor Installation prüfen. Einen separaten Arbeitsbereich auf einem geeigneten Laufwerk planen und von Sicherungsbeständen abgrenzen. RadiWorks 8103–8109 und bestehende Entwickler-/Governors-/Serverdienste bleiben geschützt; neue Ports nach Listenerprüfung reservieren.

## 3. Priorisierte Reihenfolge und Abschlusskriterien

| Phase | Konkrete Arbeit | Ergebnis vor nächster Phase |
|---|---|---|
| **P0 – Referenzen und Machbarkeit** | Pro betroffenem Modul Originalstand, Versionen, Eingaben, Ausgaben, bekannte Fehler und Abhängigkeiten sichern. Speicher/RAM/Laufzeit/Portplanung prüfen; benötigte Schemas/Dienste/Assets und gemeinsame Beziehungen binden | Versionierter Originalbeleg und ausreichende lokale Ressourcen. Unbekannte Original-/Hardwarepfade klar ausgewiesen. Baselines entstehen vor der jeweiligen Portierung, nicht nachträglich |
| **P1 – Lokale Ist-Umgebungen** | Zunächst Explorer einschließlich Copen/Bohm, danach Thom minimal strukturtreu einrichten; zugehörige lokale Backendbereiche nach P0. Erst Readiness/Isolation, dann synthetische Identitäten und Referenzen | UI und tatsächlich benötigte lokale Dienste erreichbar; bestehende Cloud-/RadiWorks-Ziele unberührt; benötigte Ressourcen/Versionen dokumentiert |
| **P2 – Funktion und Parität** | Ein-/Ausgaben, Katalogwahl, Analyse, Klienten-/Sitzungswechsel, Archive/Vorlagen, Jobs/Queue, Pause/Abbruch, Reconnect/Restart, Rechte/Storage/Realtime, Reports/Import/Export, Thom 3D/Audio testen | Jede Funktion: erhalten, bekannte Ist-Abweichung, technische Portabweichung oder noch nicht prüfbar. Keine pauschale Komplettabnahme; Betreiber kann die lokale Fassung prüfen |
| **P3 – Sechs Modul-Reasonings schließen** | Radi144-Abläufe ergänzen, Morphic-Quellstand entscheiden und Pfade prüfen, RadiFarben-VBA/Query/Formular-/Datei-/Timerlogik kontrolliert erfassen; Explorer/Thom-Ergebnisse einordnen | Für jedes Modul vollständige verifizierbare Workflow-/Daten-/Algorithmusmatrix im festgelegten Umfang; Quellen-/Lizenz-/Runtimegrenzen sichtbar. Bestehende Belege wiederverwenden |
| **P4 – Gemeinsame Bedarfsmatrix** | Sechs Module plus RadiWorks, Aurelia-Verwaltung und Modul_Templates zusammenführen; Zuständigkeiten, Datenraten, Aufbewahrung, Parallelität und gemeinsame Fähigkeiten ableiten | Datenstrukturentscheidungsvorlage mit allen Pflichtdomänen, vergleichbaren Alternativen und konkreten offenen Betreiberentscheidungen |
| **P5 – Zentrale Struktur entscheiden** | Führende Systeme, Identitäten, Rechte, Versionen, Transaktionen, Ereignisse, Objekte, Jobs, Archive/Restore, Last-/Betriebsziele und Übergang vereinbaren | Ausdrücklich beschlossener Vertrag; konkrete DB-/Objektspeicher-/Zeitreihentechnik daraus ableiten. Keine Migrations-/Umschaltfreigabe durch bloße Planung |
| **P6 – Aurelia-Kern und Templates vorbereiten** | Beschlossene minimale Speicher-/Auth-/Job-/Asset-/Auditverträge vorbereiten und synthetisch prüfen; normative Modul_Templates vor schreibenden Adaptern abstimmen | Zentraler Kernvertrag und passende Modulfähigkeiten geprüft; eindeutige Grenzen, versionierte Schemas/API und Restore-/Rechtebelege |
| **P7 – Module schrittweise vorbereiten** | Jeweils ein Modul: Originalbaseline → versionierter Adapter/UX → Regression/Parallelität/Rechte/Restore → Betreiberabnahme → Quell-/Modul_Templates-Abgleich | Integrierbarer Prototyp pro Modul; bestätigte Formeln und laufender Bestand erhalten. Reihenfolge nach Abhängigkeiten und Risiko entscheiden, nicht vorzeitig festlegen |
| **P8 – Integration und Gesamtprüfung** | Windows-/Ubuntu-Parität, Tenant-/Abo-/Servicegrenzen, Mehrmodulbetrieb, Fehler/Wiederanlauf und gemeinsame Wiederherstellung testen; Sicherungs-/Freigabepunkte | Einzelne Integrationsfreigaben und gesondertes S4.8-Gate. Keine Freigabe aus einem erfolgreichen lokalen UI-Test ableiten |

P0/P3 können für unabhängige Quellen begrenzt parallel untersucht werden; das fordert keine parallele Mutation oder gleichzeitige große Teststacks. Morphic-Quellentscheidung sperrt dessen Anpassung, nicht die unabhängige Explorer-Vorprüfung. Access-Referenzen laufen zunächst im geschützten Windows-Originalweg; keine Autoexec-, Makro-, Formular- oder externe Linkausführung bei der reinen Inventur. Kontrollierte synthetische Funktionsproben werden gesondert vorbereitet.

Das lokale Ist-Referenzpaket P1/P2 ist vom späteren Aurelia-Zielvertrag DB-2/P3 getrennt. Frühere [P1-SQL-Befunde und P2/P3-Rechteprüfungen](2026-10-09-aurelia-isolierte-rechtepruefung.md) werden nicht in bestandene Gesamtprüfungen umgedeutet. Neue Cloud-Teilstagings bleiben zurückgestellt; ihre noch ungeklärte Hostingregion blockiert die lokale Machbarkeitsaufnahme nicht.

Windows-/Ubuntu-Annahmen bei Packaging, Pfaden, Format-/Dezimalverhalten, Auth und Schlüsselverwaltung früh anhand eines repräsentativen Wegs prüfen; die Gesamtplattformabnahme erfolgt in P8. RadiWorks bleibt die bestätigte Referenz für geeignete Bedien-, Gestaltungs- und Kontextprinzipien, kein universeller Ersatzkernel.

## 4. Prüfkatalog für das vollständige Modul-Reasoning

Jede aktive Funktion erhält eine feste Kennung und diese Felder:

| Prüfbereich | Verlangter Inhalt |
|---|---|
| Einstieg und Rolle | Route/Formular/API/CLI/Timer, Benutzerrolle, Vorbedingungen, Caller und erreichbare Funktion; ungenutzte Helper gesondert |
| Berechnung und Auswahl | Tatsächliche Eingaben/Katalogrevision, Algorithmusversion, Parameter, Reihenfolge, Zufallsquelle und Entscheidungsregeln; unbekannte Regeln sichtbar |
| Zustand und Bindung | Klient/Fall, Sitzung, Kontextrevision, Ergebnis, Auftrag/Versuch und Assetrevision; erlaubte Übergänge und Eigentümer-/Tenantbezug |
| Speicherung und Ausgabe | Führender Writer, Leser, Transaktion, Datei-/DB-/Browser-/externes Ziel, Archiv/Report/Export und tatsächliche Nebenwirkungen |
| Fehler und Wiederherstellung | Ungültige Eingaben, Abbruch/Pause, doppelte Starts, Teilfehler, Rechtewiderruf, Reconnect/Restart, Löschung und Restore |
| Referenzprüfung | Gebundene synthetische Eingabe, erwartete/erhaltene Ausgabe, Grenzfälle, numerische Präzision/Toleranz und Quellhash; keine unbegründete Nulltoleranz bei verschiedenen Renderern |
| Zufallsprüfung | Für Formelparität kontrollierte bzw. aufgezeichnete Zufallseingaben; stochastischen Quellen-/Jobisolationspfad zusätzlich real prüfen. Unterschiedliche Zufallsresultate belegen allein keine Formelabweichung oder Klientenreaktion |
| Abnahme | Beleg, Datum, Ergebnis und Grenze; tatsächliche Originalreferenz, synthetischer Test, Simulation und noch unbekannter Betrieb klar unterscheiden |

Abschluss von P3 bedeutet: Alle vereinbarten aktiven Einstiege sind in dieser Matrix erfasst; fachliche Datenproduzenten/-verbraucher und Zustandswechsel sind zugeordnet, bekannte Abweichungen benannt, wesentliche Berechnungswege mit passenden Referenzen gebunden. Nicht prüfbare Fremddienste/Lizenzen/Hardware verhindern eine Aussage „vollständig gleichwertig lokal“; ihre dokumentierten Anforderungen können trotzdem in P4 eingehen.

## 5. Pflichtdomänen für Aurelia und Modul_Templates

| Bereich | In P4/P5 mitzuführen |
|---|---|
| Administration | Nutzer, Mandanten/Praxen, Mitgliedschaften, Therapeutenprofile/Delegation, Status, Modulabos/Tarifrevisionen, Quotas, Ressourcen-/Serviceversionen/Health, Audit und Widerruf |
| Klient/Fall/Kontext | Stabile Identitäten, bestätigte Modulzuordnung, Vorname/Nachname/Datum/aktiver Ort/Fokus/Bild soweit genutzt; unveränderliche Auftragsrevisionen; keine Zusammenführung allein nach persönlichen Textfeldern |
| Kataloge | Worte/Raten/Remedies/Anatomie/Punkte/Schemata; fachlicher Typ, Inhalt/Reihenfolge/Einheiten, Quelle/Lizenz, Revision, globale/tenant-/nutzerprivate Sicht, Admin-/Nutzerimport und Freigabe |
| Analyse und Ausführung | Native Resultate/Matrixscores/GV getrennt; Sitzung, Job/Versuch, Workerclaim/Lease, Idempotenz, Parallelität, Pause/Abbruch und Wiederanlauf |
| Ereignisse, Trends, Favoriten | Rohbeobachtung, Herkunft/Skala, Zeit-/Sequenz-/Lückengrenzen, Trendregel/-archiv, bestätigte Katalogzuordnungen, persönliche Favoriten gegenüber Kandidaten; verschiedene Modulkennzahlen nicht beliebig mitteln |
| Trigger und Benachrichtigungen | Versionierte Ursache/Entscheidung, Rechteprüfung, Deduplizierung, Empfänger/Kanal, Zustellabsicht/-versuch; standardmäßig aus, externe Nachricht nur ausdrücklich aktiviert |
| Berichte und Arbeitsentwürfe | Ergebnis-/Vorlagen-/Rendererrevision, Reportartefakt und Archiv; dauerhafte klientenbezogene Entwürfe/CopyGuard getrennt von Browser-/System-Clipboard |
| Templates und Presets | Modul- und Plattformvorlagen mit Revision, Rechten, Herkunft, Freigabe; erzeugter Auftrag hält den verwendeten Stand fest |
| Bilder/Layer und 2D/3D | Private Originalbytes, Hash, Ableitungen, Lizenz, Koordinaten/Einheiten/Transformationen, Referenzpunkte/Regionen/Texte/Mappingrevisionen; fünf getrennte Layer samt Reihenfolge und oberster sichtbarer Ebene; administrativer Creator gehört Aurelia |
| Audio und Frequenzreihen | Systemweite versionierte Audiofähigkeit, freigegebener Generator und Profil-/Parameterstand; feste Töne/Solfeggio sowie Phi-/Fibonacci-Pulsrate UND Abschnittsdauer; Sequenzen mit Reihenfolge/Dauer/Einheiten; PCM-/Float-/Original- und Sampleerhalt prüfen |
| Import/Export | PDF/OCR, XLSX/XLS und JSON: Original, Parser-/Templateversion, Herkunft/Position, Unsicherheit, Validierung, Vorschau, Bestätigung, erlaubter Zieladapter, Transaktion/Audit und Exportqualität |
| Schutz und Betrieb | Aktuelle Rechte je Zugriff, vertrauliche Assets, Wellbeing-Kennzeichnung, zugängliche UX/klare Sprache/Dunkeltemplate, Ressourcenlast, Aufbewahrung/Löschung und gemeinsame DB-/Objekt-/Konfigurations-/Schlüssel-Wiederherstellung |

Maßgebliche Detailvorgaben: [Datenbereiche/Echtzeit](../../AURELIA_DATENDOMAENEN_ECHTZEIT_2026-10-09.md), [Administration/Medien/Importe](../../AURELIA_ADMIN_MEDIEN_IMPORT_VORMERKUNG_2026-10-09.md), [2D/3D-Assets](../../AURELIA_ADMIN_ASSETS_VORMERKUNG_2026-10-09.md), [Favoriten/Trends/Trigger](../../AURELIA_FAVORITEN_TRENDS_TRIGGER_VORMERKUNG_2026-10-09.md), [Designvorbereitung](../../AURELIA_DESIGN_TEMPLATE.md). Diese werden als Anforderungen übernommen, nicht als bereits implementierte Fähigkeiten ausgewiesen.

**Zentralhoheit und Übergang:** Pro Objekt führendes System, IDs/Quellzuordnung, Revisionen, Konfliktregel, Kopier-/Übernahmestatus, Löschweitergabe und Rückweg bei Teilfehler vor schreibendem Adapter bestimmen. Referenzdatenbanken sind zeitweilige Originalabbildungen; keine dauerhafte konkurrierende Schreibhoheit einführen. Lokale Tests decken doppelte Starts/Übernahmen, Wiederholungen und Teilfehler ab. DB-Entscheidung, Kernvorbereitung und tatsächliches Umschalten bleiben getrennte Entscheidungen.

PostgreSQL bleibt die bisher dokumentierte Vergleichsbasis. Zeitreihen-/Aggregations- oder zusätzliche Analyticsdienste erst nach konkreten Last-, Isolations-, Lizenz-, Lösch- und Restoreanforderungen entscheiden. Die lokale Supabase-Kompatibilität legt die spätere Produktdatenbank nicht fest. Semantische KI-Suche, Embeddings und neue Universalformeln sind weiterhin nicht freigegeben. Ego Cleaner bleibt inaktiv/vorbereitet; Komfortpaket, CPU/CUDA, Kozyrev und externe Hardware behalten ihren optionalen Status.

## 6. Kontrollpunkte, Zuständigkeit und Abschluss dieses Plans

- [ ] Vor jeder Original-/Portierungsänderung: aktueller Quellen-/Konfigurationssicherungspunkt, geprüfte Rücknahme und keine Übernahme echter/testhistorischer Klienten.
- [ ] Nach P1/P2: lokale Nutzerprüfung je Anwendung, Versions-/Konfigurationsmanifest und reproduzierbare Fehlerliste; keine unbelegte Funktions-/Algorithmusparität.
- [ ] Nach P4/P5: Betreiberentscheidung zur Struktur; Governors-Aufnahmen/Projektmatrix bei Nutzung quellenfrisch und ausdrücklich bestätigen. Vorhandene Intakebelege, RadiFarben-Registrierung und Modellversandgates nicht automatisch ändern.
- [ ] Vor jedem P7-Modul: abgestimmte Modul_Templates-Fähigkeiten/API/Hostvertrag, Aurelia-Abhängigkeiten und bestehende Algorithmusbaseline; zuerst additive Änderungen und eigener Teststand.
- [ ] Nach relevanten technischen Abschlüssen: kurzer Phasen-/Standbericht, reale Modelle und nächste Prüfung nennen; zeitgestempelte geprüfte Sicherung vor Integration oder größerem Umbau.
- [ ] Vor S4.8: produktive Rechte/Hosting/Dienste/Restore und Ubuntu-Abnahme eigens nachweisen. Vorhandene Prüfzahlen sind keine Gesamtfreigabe.

Leitung nach Betreiberroute Sol6.1/high; Luna6/max für unabhängige begrenzte Erfassung/Umsetzung mit klarer Dateiverantwortung; Astra6/medium für Konsequenzen und offene Widersprüche. Keine rekursive Delegation, kein Versand von Cloud-Rohdefinitionen, Datensätzen oder Secrets an Helfer. Tatsächlich in dieser Planrunde: Luna für dokumentierte Anforderungsabdeckung, Astra für lokalen Portierungs-/Reihenfolgereview. Seine Ergänzungen zu vorgezogenen Baselines, Backendbeziehungen, Machbarkeit, Prüfkriterien und Übergangsvertrag sind eingearbeitet.

Zeitangaben sind Orientierung, keine Qualitätsgrenzen. Der aktuelle Planabgleich ist ein begrenztes Lesepaket; belastbare Aufwandsschätzungen für P1/P2 erst nach P0, getrennt nach Oberfläche, Diensten, Assets und externen Abhängigkeiten. Keine Installation oder ungesicherte Speicherreservierung aufgrund einer Schätzung.

Gesicherte Planrunde: `runtime/aurelia-three-modules-20261009/reference-plan/module-roadmap-20261010-073559Z`. Die vier bestehenden Plan-/Statusdokumente wurden vor Änderung kopiert und rückgeprüft. Diese kleine Dokumentensicherung ersetzt keine F:-Gesamtsicherung oder Cloud-/Serverwiederherstellung. Keine Produkt-, Schema-, Algorithmus-, Modul_Templates-, Governors-Routing- oder Liveinstanzänderung in dieser Runde.

## 7. Ausführungsstand P0 vom 10.10.2026

- [x] GitHub-Main-Stände frisch bestätigt; alle 562 Manifestdateien vor/nach Referenzproben unverändert.
- [x] Fünf vorhandene synthetische Rechenproben nach Sicherung erneut ausgeführt; Copen-v2 378 Vergleiche ohne Abweichung. Bestehende Grenzbefunde bestätigt, keine Korrekturfreigabe daraus abgeleitet.
- [x] Paketlockbindung, Quell-Abhängigkeiten, separate Quell-Projektkennungen und geschützte Liveports erfasst; aktive Backendbeziehungen weiter gesondert prüfen.
- [ ] Lokale Runtime-Machbarkeit: C: zuletzt rund 20,35 GiB frei. Drei WSL-Starts einschließlich vorübergehendem 2-GB-Rahmen scheitern; Rahmen vollständig zurückgenommen. Administrator-Leseprobe bestätigt Hyper-V-Partitionfehler 0x800705AA, konkrete Ressource und Stackbudget bleiben offen. Keine dauerhafte Parameter-/Dienständerung.
- [ ] Lokale Zielbindungen, neue Secrets, Auth/Storage/Realtime/Edge/Cron/Worker und ausgehende Sperren tatsächlich aufbauen und negativ prüfen; keine Apps unverändert auf host::/8080 starten.

P0 insgesamt bleibt offen; P1 wurde nicht begonnen. Details und Grenzen: [P0 Prüfbericht](../../verification/AURELIA_P0_LOKALE_REFERENZEN_2026-10-10.md). Sicherungspunkt `runtime/aurelia-three-modules-20261009/reference-plan/p0-preflight-20261010-083915Z`; frühere Originalreferenzen bleiben im before/-Bereich erhalten.

P0-Nachweisberichtigung: Ein ausgelassener historischer Wiederaufnahmeabschnitt (966 Bytes) wurde am 10.10.2026 aus dem verifizierten Vorherbeleg rekonstruiert. Der komplette historische Tail ist wieder bytegleich; alte Nachweise bleiben unveraendert. Details im aktuellen P0-Pruefbericht.

P3 unabhängig fortgesetzt: begrenzte Radi144-Quellaufnahme der aktiven API/UI/CLI-, Archiv- und Templatewege; Konflikt-/Teilfehlerproben noch offen. [Beleg](../../verification/AURELIA_P3_RADI144_EINSTIEGE_2026-10-10.md).

## 8. Betreiberergänzung zu Runtime und RadiWorks vom 10.10.2026

P0–P3 behalten Vorrang. Weitere WSL-Start-/Reparaturversuche vorerst zurückstellen; unabhängige P3-Aufnahme und synthetische Referenzpakete vorziehen. Vollständiger Linux-Dienstumfang für Explorer/Thom bleibt Pflicht vor P1/P2-Abnahme. Ein getrennter Ubuntu-Testrechner ist die bevorzugte Ausweichrichtung, falls WSL nicht tragfähig wird; Zielressourcen, Versionen, Auth/Storage/Realtime/Functions/Worker und Egress-Isolation zuerst belegen. Kein produktiver Host oder neuer Stack in diesem Nachtrag eingerichtet. P0-Runtime bleibt offen, keine Parität aus Stubs oder reiner PostgreSQL-Portierung ableiten.

| Vorgemerkter Block | Platz in der Reihenfolge |
|---|---|
| RW-F1/F2 Auto-/Stochastik-Start und genaue Fehlerursachen | Gesicherter Wartungsblock nach abgeschlossenem P-Prüfpunkt; beide Verfahren betroffen, keine aktuelle Live-Rootcause behauptet |
| RW-U1 Resonanzlistenfläche / RW-U2 Anzeige-Sortierung Lvl/GV | Danach additive Bedienkorrekturen; Originalfolge,21er-Zuordnung, Historie und Broadcast-Ziel erhalten |
| RW-A1 Abschaltgrund / RW-A2 bewusstes Laufzeitbudget | Danach Originalregeln von neuer Zeitsteuerung trennen; Auto zieht10–1000s, leereQueue allein ist kein Auto-AUS-Grund |
| RW-T1/T2 Kamera, R6-/Zweit-PC-/Vier-Modi-Abnahme und Paket | Geräte-/Quellen-/Recoveryprüfung gesondert; nach Korrekturen Betreiberabnahme vor Rollout/Start5-/Quell-/Templatesupdate |
| RW-I1 Integration / RW-O1 optionale Funktionen | Mit P4–P8 und separaten Gates; zurückgestellte oder inaktive Funktionen nicht still aktivieren |
| RadiFarben P3→P8 | Aktuelle Accessfunktionen/VBA/Queries/Timer/Formulare/Berichte und Referenzausgaben vollständig binden; gleiche zentrale Identitäts-/Rechte-/Job-/Archiv-/Adaptergrundbedingungen wie alle Module |

Details, Quellbelege, Laufzeitvarianten und Prüfgrenzen: [Runtime-/RadiWorks-Nachtrag](../../verification/AURELIA_P0_ALTERNATIVEN_RADIWORKS_RESTPUNKTE_2026-10-10.md). Alle200R6Produktdateien frisch manifestgeprüft; keine Produkt-/Live-/Schema-/Schlüssel-/Templatesänderung. Quellenaufnahme durch Luna6/max; kein neuer Astra-Aufruf nötig. Vorher-/Nachher-Dokumentensicherung unter runtime/aurelia-three-modules-20261009/reference-plan/plan-followup-20261010-101737Z, komplette historische Wiederaufnahme bytegleich erhalten; keine neue F:-Vollsicherung.

## 9. P3-Radi144: abgeschlossener Charakterisierungsblock vom 10.10.2026

- [x] Zwölf synthetische Konflikt-/Vorlagen-/Bericht-/Sequenz-/Lösch-/Auditfälle ausgeführt; Leitung wiederholt auf frischen Testpfaden, Quellen13/13 unverändert. Kein Engine-/HTTP-/PDF-Rendering-/Gesamtrestore-Nachweis.
- [x] Unabhängiger Astra-Review; Fixture- und Berichtswidersprüche vor Abschluss korrigiert. Rückgabewert `ok` ausdrücklich von sicherem Gesamtabschluss getrennt.
- [x] P4/P5-Bedarf erweitert: Konfliktregeln, Wiederholungsidentität, Teilveröffentlichung, dauerhafte Löschziele/-fortschritte, Dateieigentum und persistierte Auditnachweise. Keine DB-Technik oder Produktreparatur entschieden.
- [ ] Weitere Radi144-Grenzen: gleiche Namen/geteilte Pfade, alter Writer nach Löschung, Sequenz-Retry, volle Engine-/API-/UI-/CLI-/PowerShell-/Abbruch-/Restore-Verifikation.
- [ ] RadiMorphic-Quell-/Owner-/Lease-Abdeckung und aktuelle RadiFarben-VBA-/Query-/Formular-/Timer-/Berichtsreferenzen vervollständigen; unveränderte Algorithmen erhalten.

[Prüfbericht und Grenzen](../../verification/AURELIA_P3_RADI144_CHARAKTERISIERUNG_2026-10-10.md). P3 insgesamt und P0-Runtime bleiben offen. P1/P2-Linux-Referenzen, P4 gemeinsame Matrix, P5 Betreiberentscheidung sowie P6–P8 Integrationsgates behalten ihre Reihenfolge. RadiWorks-Wartungsblöcke aus Abschnitt8 unverändert vorgemerkt; Liveinstanzen erhalten.

## 10. P0-Wiederaufnahme nach Betreiber-WSL-Reparatur, 10.10.2026

- [x] Neu eingerichtete WSL2-/Ubuntu-24.04-Basis geprüft; frische eigene `Aurelia-Referenz-24.04` auf F: mit signiert geprüftem Ubuntu-Rootfs importiert. Keine eigene Änderung der ursprünglichen Ubuntu-Konfiguration oder globaler WSL-/Windows-Parameter.
- [x] Eigene Docker29.9.0/Compose5.6.0-Grundlage installiert; kleine Warmprobe mit Speicherlimit bestanden. Temporärer Windows→WSL-Loopback→interner-Container-Relay liefert HTTP200; alle Testcontainer/-netze entfernt.
- [ ] Effektive Docker-Portveröffentlichung auf rein internem Netz fehlt; dauerhaften lokalen Zugang gesondert prüfen. Relayprobe ist keine abgenommene Dauerlösung und keine vollständige Egress-Sperre.
- [ ] Erneute äußere WSL-Anlaufaufrufe enden im Timeout; geplanter kontrollierter Neustart nicht durchgeführt. Kaltstart-/I/O-Ursache und vollständiges Supabase-Ressourcenbudget offen. Kein P1/P2-Anwendungsstart.
- [x] Aktive Backend-Caller begrenzt erfasst: Auth/REST/Storage/Realtime/Functions erforderlich; feste Thom-WebSocket-/Storageziele, Explorer-OCR-/Latenz-/optionale Ollama-Pfade vor Lokalstart kontrollieren. Keine Function-/Cron-Parität behauptet; beide Quellen haben20Migrationsdateien.
- [x] Windows-Liveports8103–8109/8787 HTTP200; zeitbegrenzte Keepalives beendet, beide WSL-Distributionen am Abschluss Stopped. Quellen-/Listenervergleich im privaten Abschlussreceipt.

F: enthält die neue Referenzbasis und bestehende Sicherungen, bleibt vorerst verbunden. Betreiberreserve: SD64GB/USB3 separat verfügbar, SSD120GB nur nach Tausch des einzigen F:-Adapters. Kein Datenträgerwechsel oder Formatieren; Nutzdaten/freies Budget/Eignung und gesicherter Stillstand zuerst klären. SSD als mögliche Reserve vormerken, Leistung nicht voraussetzen.

P0-Infrastrukturteilstand sichern; unabhängige P3-Reasoningpunkte können weiterlaufen. Keine neue DB-Entscheidung, Algorithmus-/Produkt-/Live-/normative Templatesänderung. Bericht: [WSL-Referenzbasis und Grenzen](../../verification/AURELIA_P0_WSL_REFERENZBASIS_2026-10-10.md). Sicherung `runtime/aurelia-three-modules-20261009/reference-plan/p0-wsl-reentry-20261010-131856Z`; keine neue F:-Vollsicherung. Tatsächliche Helfer Luna6/max und Astra6/medium.

## 11. P3 – Radi144-Grenzen und Morphic-Quellverträge, 10.10.2026

- [x] Sechs ergänzende Radi144-Proben: gleiche Namen, geteilte Datei, alter Writer nach Löschung, Mehrfokus-Retry, fehlende Sitzung bei Dateiregistrierung und künstlicher Fehler nach Dateiersatz. Nach Guardkorrektur zweimal frisch bestanden; 13/13 Originalquellbytes unverändert. Zusammen mit Abschnitt9 jetzt18 Charakterisierungen, keine vollständige Modulabnahme.
- [x] Astra6/medium prüfte Werkzeuggrenzen und deren Korrekturen. Netzwerk-/Pfad-Negativproben bestanden; Reparse-Negative ist eine Metadatensimulation, keine echte Junction-/Raceprüfung. Zwischenfehler bleiben dokumentiert.
- [x] Luna6/max erfasste Morphic-Root und registrierten Arbeitsstand getrennt: aktive Owner-/Tenant-/Idempotenz-/Lease-/Katalog-/Reportverträge, 18 Quelldateien und zwei Gitstände durch Leitung frisch hashgebunden. Keine Runtime-/Zugriffs-/Restoreabnahme, keine führende Quelle automatisch gewählt.
- [ ] Nächster unabhängiger P3-Block: Morphic synthetische Owner-/Idempotenz-/Lease-/Katalogproben ohne reale CLI-Prozesse; RadiFarben aktuelle Access-VBA-/Query-/Formular-/Timer-/Berichtquellen und Referenzabläufe vervollständigen. Radi144 Engine/API/UI/CLI/PowerShell/Abbruch/Restore bleibt offen.
- [ ] P4 führt Dateieigentum/geteilte Referenzen, Löschrevisionen, Wiederholungsidentität, Teilabschluss/Bestätigung, Tenant-/Operator-/Workspacekontext und führende Writer/Quellen zusammen. Noch keine DB-Technik oder Produktreparatur beschlossen.

Berichte: [Radi144-Grenzen](../../verification/AURELIA_P3_RADI144_GRENZEN_2026-10-10.md), [Morphic-Quellverträge](../../verification/AURELIA_P3_MORPHIC_QUELLVERTRAG_2026-10-10.md). Privater Dokumenten-/Nachweispunkt `runtime/aurelia-three-modules-20261009/reference-plan/p3-boundaries-20261010-140025Z`, ganze vorherige Wiederaufnahme erhalten; keine F:-Vollsicherung. P0/P3 offen, P1/P2 nicht gestartet, P4→P5→P6–P8 und S4.8 unverändert. RadiWorks-Wartung aus Abschnitt8 vorgemerkt; Liveports8103–8109/8787 und Produktquellen bleiben erhalten.

## 12. P3 – Morphic-Charakterisierung / RadiFarben-Workflowquellen, 10.10.2026

- [x] Neun Morphic-Proben durch Luna6/max und Leitung in frischen Scratchpfaden bestanden: Ownerhash, terminales owned Lesen/Stoppen, Startclaim, Replay, Requestkonflikt, Ownertrennung, Leaseklassifikation und Recovery-Dispatch. Elf Quellhashes, Harness, HEAD/getrackter Zustand unabhängig gebunden; keine führende Quelle gewählt.
- [x] Astra6/medium prüfte Methoden, Harness, Ergebnisse und Bericht. Refresh vor Ownerprüfung ist ersetzt, Stop betrifft terminalen RAM-Job; Reconciliation/Ereignispersistenz sind Fakes. Null Sperrtreffer beweisen keine allgemeine Sandbox; API/Auth, echte Prozesse, Konkurrenz, Restart/Restore, Importgraph und Junction-/Race-Negative bleiben offen.
- [x] RadiFarben aktuelle 100 VBA-Dateien / 47 Querytexte frisch hashgeprüft; ergänzter statischer Trace zweimal identisch außer Zeit. Gezielte Start-/Menü-/Bericht-/Paletten-/Symbol-/Timer-/Audiokanten erfasst. Fünf UPDATEs benötigen VBA-Funktionen; SET/WHERE einschließlich NULL-Verhalten unabhängig geprüft. Keine Access-/VBA-/Queryausführung.
- [x] RadiFarben-Trace-Indexbindung nach Review korrigiert: Funktionen direkt aus hashgeprüften Quellen; gleichnamige Definitionen erhalten. Lexerchecks bestanden. Frühfehler und korrigierte Reviewbefunde erhalten; keine Originalalgorithmusänderung.
- [ ] Nächste unabhängige P3-Punkte: Morphic-Katalogrechte/Kontext/Publish/Rollback sowie nachgelagerte Writer-/Artefakt-/Reportkette; RadiFarben gespeicherte Objekt-/Event-/Makrobindungen und kontrollierte Originalreferenzumgebung. 17 Parameterlisten, fünf verknüpfte Quellen und vollständige Laufzeit-/Fehler-/Abbruch-/Restoreparität bleiben offen.
- [ ] P4 führt zusätzlich dynamische Menü-/Reportdefinition, Query-/Funktionsrevision, Symbol-/Stringpräzision, Anzeigeanimation gegenüber Ereignisarchiv sowie Host-/Audiofähigkeiten zusammen. P5 DB-Entscheidung weiterhin erst nach vollständiger siebenmoduliger Matrix.

Berichte: [Morphic-Charakterisierung](../../verification/AURELIA_P3_MORPHIC_CHARAKTERISIERUNG_2026-10-10.md), [RadiFarben-Workflows](../../verification/AURELIA_P3_RADIFARBEN_WORKFLOWS_2026-10-10.md). Privater Punkt `runtime/aurelia-three-modules-20261009/reference-plan/p3-morphic-farben-20261010-142545Z`: vollständige vorherige Wiederaufnahme, private ACCDB-Kopie und getrennte Prüf-/Quell-/Reviewbelege. Abschlussbindung in VERIFY.json/MANIFEST.json; keine F:-Gesamtsicherung. P0/P3 insgesamt offen; kein WSL-Aufruf, P1/P2-Start, Produkt-/Live-/Routing-/Kern-/normative Templatesumbau. RadiWorks-Wartung und P6–P8/S4.8 bleiben getrennte Schritte.

## 13. P3 – Katalog-/Berichtwege und gespeicherte Objektmetadaten, 10.10.2026

- [x] Morphic-Quellvertrag von Adminrouter/Sicherheit/Kontext über SQLite-Draft/Publish/Aktivierung/Rollback und von Scan/CLI über Artefakte/Reports zur Harmonisierung erweitert. 26 Quellen vor/nach gebunden und durch Leitung frisch geprüft. Kein führender Stand gewählt, keine Runtime-/Schlüssel-/DBwerte gelesen oder Dienste gestartet.
- [x] Report-ID bindet Fundort statt Inhaltsrevision; CLI-/Katalog-/Pfad-Sitzungen haben unterschiedliche Herleitungen/Verwendungen, nicht zwingend drei unterschiedliche Werte. Harmonisierung hält Report-ID/Tenant/Operator, keinen Reportbytes-Hash oder direkten Client-/Session-Snapshot im geprüften Vertrag. Crosswalk/Writer-/Inhaltsrevision für P4/P5 vormerken.
- [x] RadiFarben auf privater Masterkopie readonly/statisch untersucht: 105 eindeutige Objekte (45 Forms,3 Reports,54 Module,3 Scripts), Verwaltungs-Propertynamen/-typen und binäre LvProp-Metadaten gebunden. Keine Geschäftszeilen dekodiert/exportiert; vollständige Dateibytes/Seitenköpfe werden gelesen. Kein vollständiger saved-object Decoder.
- [x] Unabhängige DAO-Blobgegenprobe vor erster Zeile unverfügbar; ausdrücklich kein bestandener Gleichheitsnachweis. Vorcheckfehler durch falsche Packagingerwartung erhalten und korrigiert, 694 Bibliotheksdateien unverändert; keine Rechte-/Paket-/Produktänderung.
- [x] Astra6/medium prüfte Werkzeuge, wesentliche Quellpfade, 26 Bindungen und finalen Bericht; Sessionherleitung präzisiert. Keine materiellen Restbefunde im begrenzten statischen Block.
- [ ] Nächster ausführbarer Morphic-P3-Block: synthetische Kontext-/Versions-/Attestproben, danach Admin-API/Pfad/Draft-Publish/Aktivierung-Rollback in isolierter Umgebung. Sechs Prüfpakete definiert, hier nicht ausgeführt; alte neun Charakterisierungen nicht als Katalogtests zählen.
- [ ] RadiFarben: konkrete isolierte Windows-Originalreferenzumgebung zuerst, dann gespeicherte Event-/Record-/Control-/Makrodefinitionen und synthetische Originalausgaben/Fehler-/Abbruch-/Rundungsreferenzen. 17 Parameterlisten, Links, P-Code-/Quellparität und volle Restorewirkung offen; keine unsichere Originalöffnung.

[Bericht und Grenzen](../../verification/AURELIA_P3_KATALOG_BERICHT_OBJEKTBINDUNGEN_2026-10-10.md). Privater Nachweispunkt `runtime/aurelia-three-modules-20261009/reference-plan/p3-morphic-farben-20261010-145604Z`, ganze vorherige Wiederaufnahme erhalten; Quellen-/Produkt-/Listenerabschluss in VERIFY.json/MANIFEST.json, keine neue F:-Gesamtsicherung. P0/P3 insgesamt offen, P1/P2 nicht gestartet, P4-Matrix vor P5 DB-Entscheidung und P6–P8/S4.8 getrennt. Liveinstanzen, Governors, Algorithmen, Kern und normative Modul_Templates bleiben unberührt.

## 14. P3 – synthetische Katalogproben / Access-Alternative und Pause, 10.10.2026

- [x] Neuer begrenzter Katalog-Kernblock durch Luna6/max und Leitung: je acht Fälle bestanden, ein echter Host-Symlinkskip, keine finalen Fehler. Kontextnamespace/Isolation, Draft-/Publish-CAS, Attestbindung, explizite Pfadgrenzen und Aktivierung/Rollback/Audit geprüft. Frühe Fehlerbelege erhalten; getenv ausschließlich im Harness durch geschlossene synthetische Abbildung ersetzt, keine Originalcodeänderung.
- [x] 29 Quellbytes vor/nach gebunden, davon sieben Kernmodule exakt aus gehashten Quellen ausgeführt; HEAD/getrackter Zustand und Harness unverändert. Keine Paketinitialisierer, realen Katalogschlüssel, Klientenzeilen oder API/Authimporte. Ungetrackte Quellen nicht inventarisiert; kein führender Morphic-Stand gewählt.
- [ ] Sechs Katalogpakete weiterhin nur teilweise abgedeckt: API/Auth, Schlüsselzusammenstellung/Recoveryrechte, Importreceipts, Default-Root-Zweige, echte Reparse-/Austauschrennen, Konkurrenz/Restart/Restore und Writer-/Reportkette offen. Symlinkskip nicht als bestandene Negativprobe zählen; eingeschränkte API-Guards sind keine OS-Sandbox.
- [x] RadiFarben-Access-/Windows-/VM-Voraussetzungen rein lesend aufgenommen. Betreiber bestätigt lokale Access-Lauffähigkeit; keine eigene Laufzeitabnahme. VM mangels Windows-/Office-Medien zurückgestellt, keine VM/Installation/Systemreparatur gestartet.
- [ ] Aktueller nächster Access-Kandidat: eigene leere Zieldatenbank, zuerst synthetische Import-/Exportmarker; keine Tabellen/Links/Originalabläufe übernehmen, Importnebenwirkungen/versionierte Herkunft gesondert prüfen. Noch kein Access-Start oder Import; Originalkopie bleibt bis zur belegten Grenze geschlossen. Vollständige Referenzumgebung/gespeicherte Bindungen/Originalausgaben weiterhin offen.

Prüfbericht [Katalogproben](../../verification/AURELIA_P3_MORPHIC_KATALOGPROBEN_2026-10-10.md), [Access-Referenzvorbereitung](../../verification/AURELIA_P3_RADIFARBEN_REFERENZVORBEREITUNG_2026-10-10.md). Unabhängiger Astra6/medium-Review für Harnesskorrekturen und Ergebnisbindung; abschließenden Reviewbeleg mit Sicherung ablegen. Nach diesem Block ausdrückliche Betreiberpause. Wiedereinstieg bei synthetischer Access-Importprobe und weiteren begrenzten P3-Restpaketen, keine automatische Fortsetzung während der Pause.

Privater Sicherungspunkt `runtime/aurelia-three-modules-20261009/reference-plan/p3-morphic-farben-20261010-152120Z`: volle vorherige Wiederaufnahme als bytegleicher Anhang, private ACCDB-Masterkopie, 29 Quellen, Werkzeuge und frühe/finale Prüfbelege. Abschlusssiegel gesondert prüfen; keine neue F:-Gesamtsicherung. P0/P3, P4→P5 und P6–P8/S4.8 bleiben getrennte Gates; RadiWorks-Wartung vorgemerkt, Produkte/Liveinstanzen/Governors/Routing erhalten.

## 15. RadiFarben – führender RMF-Workflow, Betreiberklärung vom 11.10.2026

Der Betreiber bezeichnet **Menüpunkt 1 „Raten-Matrix-Formular“ (RMF)** als zentralen aktuellen Workflow. Grundlage ist seine ausdrückliche Erläuterung und das bereitgestellte Menübild `C:/Users/Hubert111/Pictures/RadiFarben.JPG`. Diese Festlegung steuert die Prüfreihenfolge; sie ist keine bereits ausgeführte Access- oder Funktionsabnahme. Der in Abschnitt14 dokumentierte Pausenstatus wurde durch die Wiederaufnahme am 11.10.2026 beendet; nächster ausführbarer Schritt bleibt die synthetische Access-Import-/Exportprobe.

| Menüpunkt | Betreiberzuordnung | Konsequenz für Aufnahme und Weiterentwicklung |
|---|---|---|
| **1 Raten-Matrix-Formular** | Zentraler aktueller RMF-Workflow | Führender P3-Referenzweg und Grundlage der späteren lokalen Bedien-/Ablaufabnahme. Vollständige Ein-/Ausgaben, Zustände, Berechnungen, Speicherung, Fehler und Wiederherstellung erfassen. |
| **2 Raten-Matrix-Formular manuell (alt)** | Alter RMF-Stand; wird nicht weiterentwickelt | Als historische Referenz erhalten. Keine eigene Weiterentwicklung planen; noch benötigte Abhängigkeiten/Kompatibilität bei der RMF-Aufnahme berücksichtigen. |
| **3 Matrix** | Bereits im zentralen RMF enthalten | Als RMF-Teilfunktion aufnehmen; gemeinsame Berechnungs-/Datenwege eindeutig zuordnen. |
| **4 Test Matrix** | Bereits im zentralen RMF enthalten | Als RMF-Teilfunktion und Referenzprüfweg aufnehmen. |
| **5 Bruce-Copen-Algorithmus** | Bereits im zentralen RMF enthalten | Die bestehende RadiFarben-Berechnung als RMF-Teilfunktion quellengebunden erfassen und unverändert erhalten. |
| **6 Farben** | Bereits im zentralen RMF enthalten | Als RMF-Teilfunktion samt Daten-/Darstellungsbezug erfassen. |
| **7 Farb-Paletten** | Bereits im zentralen RMF enthalten | Als RMF-Teilfunktion samt Auswahl-/Speicher-/Revisionsbezug erfassen. |
| **8 Aufstellungen** | Für den Betreiber unbedeutend | Keine eigene Weiterentwicklungspriorität. Bestehenden Bestand erhalten; mögliche technische RMF-Abhängigkeiten bei der Aufnahme berücksichtigen. |
| **9 Stammdaten / Sonstiges** | Ergänzende Information, soweit noch nicht im RMF enthalten | Prüfen, welche Informationen/Funktionen schon im RMF liegen und welche tatsächlich zusätzlich benötigt werden. Benötigte Stammdaten in P4/P5 vollständig berücksichtigen. |

**P3-Schritte:** Nach RF-E1 zuerst die gespeicherte Menüpunkt1→Formularbindung belegen; dann RMF und seine eingebundenen Teilfunktionen aufnehmen, Punkt9 auf Ergänzungen/Abhängigkeiten prüfen und gezielte synthetische Originalreferenzen vorbereiten. Die vom Betreiber bestätigte Einbettung von3–7 wird als fachliche Vorgabe übernommen; gespeicherte Event-/Control-/Query-/VBA-Aufrufe bleiben technisch zu belegen. Der angezeigte Menütitel allein bestimmt keinen Access-Objektnamen.

**P4–P7-Folgen:** Menüfunktionen dem Modul RadiFarben zuordnen. Datenproduzenten/-verbraucher des RMF mit Algorithmen-/Katalog-/Paletten-/Ergebnis-/Berichtsrevisionen in die gemeinsame Matrix übernehmen. Spätere Moduloberfläche um den führenden RMF-Ablauf entwickeln; vollständiges Quellinventar und bestätigte Berechnungen erhalten. Kein Formular, Algorithmus oder Datensatz wird durch diese Priorisierung gelöscht, verändert oder still aktiviert.

Dokumentensicherung vor/nach dieser Ergänzung: `checkpoints/RadiFarben-RMF-Plan-20261011-074305Z`, einschließlich Betreiberbild und kompletter vorheriger Wiederaufnahme. Kein Access-/WSL-/Produkt-/Live-/Routing-/normativer Templates-Eingriff; keine neue F:-Gesamtsicherung. Diese begrenzte Planpflege erfolgt durch die Leitung ohne Subagenten.

## 16. RMF-Ausgangsversion und weitere Versionsübernahmen, 11.10.2026

Der Betreiber erklärt den zentralen RMF-Stand als **aktuell höchste Version und Basis der Weiterentwicklung**. Das RMF wird weiterhin entwickelt. Zunächst diesen Stand aufnehmen; weitere Versionen bis zur Aurelia-Modulintegration müssen im Projekt kontrolliert berücksichtigbar bleiben.

| Schritt | Verbindliche Behandlung |
|---|---|
| Aktuelle Ausgangsreferenz | Unveränderliche Quellenkopie, Dateihash, Herkunft und Erfassungszeit festhalten. Höchste Version ist eine Betreiberangabe; ohne belegte interne Versionsnummer keinen semantischen Versionswert erfinden. |
| Neue Version aufnehmen | Neue Kopie und eigene Versionsbindung erzeugen, vorherige Belege erhalten. Dateiänderung getrennt von tatsächlichen Änderungen an Formularen, Queries, Algorithmen, Katalogen und Daten prüfen. |
| Unterschiede beurteilen | RMF-Workflow und Teilfunktionen quellenfrisch vergleichen; Auswirkungen auf Eingaben, Speicherung, Ergebnisse, Schnittstellen, Berichte und Datenstruktur bestimmen. |
| Referenzen erneut prüfen | Betroffene und gemeinsam genutzte Wege an synthetischen Fällen prüfen. Frühere Belege behalten ihre ursprünglichen Quellen-/Algorithmusbindungen und werden nicht still für den neuen Stand wiederverwendet. |
| Arbeitsstand übernehmen | Erst nach dokumentiertem Versionsvergleich und nötiger Abnahme die Arbeitsbaseline wechseln. Vorherige Referenz und Rücknahmemöglichkeit erhalten; neue Formular-/Algorithmusänderungen nicht ungeprüft in Adapter/Livefassungen übernehmen. |
| Integration vorbereiten | Bis P7/P8 neue RMF-Versionen über denselben Aufnahmeweg berücksichtigen. Auswirkungen in P4/P5, Aurelia-Verträgen und Modul_Templates ausdrücklich nachführen; bestätigte Abläufe stabil halten. |

Frischer Befund am11.10.: aktuelle ACCDB hat SHA256 `2993247b0b06e84d5897870790a54b0800d8db701e3d1f004c3c26e54675a1c9`, vorherige gebundene Referenz `2b48ce8dec5e0126072e0bc24f07b754b8b64af0651b080d257dcb1b0c8f13bc`. Dateidrift ist kein Nachweis einer Formeländerung. Aktuelle Byte-Referenz separat und stabil während Kopie gesichert unter `runtime/radifarben-source-versions/RF-20261011-080657Z/SOURCE_VERSION.json`; vorherige Masterkopie unverändert. Neuer Quellenordner nur Betreiber/System; keine vorhandenen ACLs geändert. Alte Code-/Objekt-/Prüfbelege bleiben an den alten Hash gebunden, neuer statischer Vergleich noch erforderlich.

Nächstes unabhängiges Paket bleibt **RF-E1** mit ausschließlich selbst erzeugten Accessobjekten, gemäß [Ausführungsplan](2026-10-11-radifarben-access-synthetische-importprobe.md). Kein aktueller oder alter Original-ACCDB-Stand wird in dieser Probe von Access geöffnet oder importiert. Erst danach gesonderte quellenfrische RMF-Aufnahme. Lauf-/Ergebnisstatus im späteren Prüfbericht ausweisen; Vorbereitung allein ist kein bestandener Test. Route für dieses Paket: Luna6/max als begrenzter Worker, Astra6/medium als unabhängiger SPEC→QUALITY-Reviewer; eigene Leitungsausführung nach Vorprüfung.

## 17. RF-E1 – tatsächliche Startgrenze, 11.10.2026

- [x] Aktuelle Quellenkopie, alte Referenz und Originalhash nach Vorbereitung erneut geprüft: unverändert; exakt rückgelesene Owner/SYSTEM-Rechte, kein Original-Lock. Hashbindung ist keine WORM-Schreibsperre.
- [x] Zwei begrenzte COM-Aktivierungsversuche (64-Bit/PowerShell7 und32-Bit/STA) scheiterten mit `80080005`, bevor ein Access-Objekt erworben wurde. Keine Datenbankaktionen aufgerufen; keine Originaldatei als Access-Eingabe. Möglichen kurzzeitigen Serverstart während der Klassenfactory nicht kontinuierlich beobachtet.
- [x] 32-Bit-Probe zunächst durch Skriptrichtlinie gesperrt; danach explizit genehmigtes `RemoteSigned` ausschließlich prozessgebunden verwendet. Keine persistente Richtlinien-, Office-, COM- oder Trustcenteränderung.
- [x] Nachkontrolle: keine Access-Prozesse; alle acht lokalen Listener auf8103–8109/8787 mit unveränderten Adressen und PIDs. Das ist keine neue Broadcast-/HTTP-Funktionsabnahme.
- [ ] Synthetische Form-/Report-/Modul-/Makro-/Queryimporte, Text-Exporte und aktive Positivkontrollen **NOT_RUN**. RF-E1 bleibt offen; Harnesskorrekturen und Host-freie Tests sind davon getrennt im [Prüfbericht](../../verification/AURELIA_P3_RADIFARBEN_SYNTHETISCHE_ACCESSPROBE_2026-10-11.md) zu verfolgen.
- [x] Synthetisches Prüfwerkzeug korrigiert:59 Host-freie Assertions bei Worker und Leitung bestanden, keine Skips/Fehler; begrenzter Astra-Nachreview ohne verbleibende Codebefunde. Vorlagenabdeckung weiterhinUNKNOWN/failclosed, äußerer Vollharnesscontroller vor späterem Hostlauf erforderlich. Keine tatsächliche COM-/Import-/Algorithmusabnahme durch diese Tests.
- [ ] Vor erneutem Hostlauf konkrete Access-Automationsumgebung und Vorlageneinfluss klären. Registrierter Office14-Startpfad und vorhandene neuere Office16-Datei sind ein Diagnoseansatz, keine bewiesene Ursache. Keine pauschale Office-Reparatur oder Neuregistrierung durch diese Fortsetzung.
- [ ] Unabhängig ausführbar: frischer rein statischer Vergleich der neuen RMF-Byteversion; weitere begrenzte P3-Vertragsproben. Aktuelle Objekt-/Algorithmus-/Workflowparität erst nach Quellenvergleich und Referenznachweisen behaupten. P4→P5 und P6–P8/S4.8 bleiben getrennt.

Lokaler Prüfpunkt `checkpoints/RadiFarben-RMF-Plan-20261011-081812Z` bindet tatsächliche Startfehler, Vorher-/Nachhermetadaten, Werkzeuge, Host-freie Tests und Review; Siegel im Manifest gesondert prüfen. Keine neue F:-Gesamtsicherung. Produktalgorithmen, Liveinstanzen, Governors/Routing und normative Modul_Templates durch diesen Prüfblock unverändert.


### Zeitliche Präzisierung der Abschlusskontrolle

Abschlussmetadaten um09:48UTC: ein später gestarteter Access-Prozess (PID37784, Start09:06:20UTC, Office16, Sitzung1) vorhanden. Die unmittelbar nach den COM-Versuchen aufgenommenen Nullbestände bleiben zeitbezogene Befunde. Ursache/Eigentum und eine mögliche Datenbanköffnung dieses späteren Prozesses sind unbekannt; keine Bedienung oder Beendigung vorgenommen. Alle acht Listeneridentitäten unverändert; SOURCE_FINAL.json bestätigt weiterhin die drei Quellenhashes, Rechte und fehlenden Original-Lock. Daraus keine lückenlose Prozess-/Originalöffnungsbeobachtung ableiten.


## 18. RadiWorks CopyGuard und Admin Test-Bypass, 11.10.2026

Betreiberbild meldet „CopyGuard blockt Auto-Broadcast“. Quellpfad bestätigt: gesperrter Name eines ausgewählten Auto-Kandidaten beendet die Generation. Konkrete Rate/Regel/Liveport bleiben anhand des Bilds unbestimmt. P0–P3 behalten Vorrang; nach abgeschlossenem P-Prüfpunkt RW-C1 zusammen mit RW-F1/F2 Ursachen-/Erklärungsprüfung, dann RW-C2 isolierter Admin-Entwicklungstestschalter, RW-C3 Regression/Abnahme. Standard AUS; serverseitige Admin-/Entwicklungs-/Testscopebindung, Befristung/Audit und getrennte Testkennzeichnung. Öffentliche Projektion, Recovery, Kontext-/Tenantgrenzen und reguläre Instanzen unverändert. Kein Schalter in diesem Nachtrag implementiert oder aktiviert. Design-/Prüfgrenzen im [CopyGuard-Nachtrag](../../verification/RADIWORKS_COPYGUARD_ADMIN_TEST_PLAN_2026-10-11.md). P4–P8 berücksichtigen getrennte Admin-/Testrechte, Archiv/Adapter/Templates.

## 19. Access Dateiformat und Startautomation getrennt beurteilen

Betreiber bestätigt aktuelles installiertes Access. ACCDB ist seit Access2007 das Standardformat und wird auch von aktuellen Accessversionen unterstützt; Dateiformatunterstützung allein belegt nicht jede VBA-/Steuerelement-/Referenzfunktion. [Microsoft Dateiformate](https://support.microsoft.com/en-us/access/which-access-file-format-should-i-use), [32-/64-Bit-Kompatibilität](https://learn.microsoft.com/en-us/office/client-developer/shared/compatibility-between-the-32-bit-and-64-bit-versions-of-office). Bestätigte manuelle RadiFarben-Nutzung als Betreiberbeleg erhalten. RF-E1 scheiterte beim COM-Start vor Datenbankaktion; kein RadiFarben-Formatfehler daraus ableiten. Frühere Registryprobe: Office14-Startpfad bei vorhandener Office16-Datei, nur Diagnoseansatz. Erst konkreten Automationsweg/Vorlagen prüfen; keine neue Installation, Neuregistrierung oder Originalöffnung durch diese Ergänzung.


## 20. P3 – frischer RMF-Versions-/Objektvergleich, 11.10.2026

- [x] Beide geschützten Masterkopien neu statisch erfasst und in einem zweiten frischen Lauf wiederholt; vollständige Erfassungsmetadaten außer UTC gleich. 100 kanonische VBA-Quelltexte ohne Änderungen, frische alte Extraktion gegen historischen Manifestbestand bestätigt. 751 Query-Speicherzeilenfingerprints gleich.
- [x] 190 ausgewählte Systemobjekte je Stand:105Form/Modul/Report/Script-Objekte plus85Query-Typ-Objekte. Kein neuer/entfernter Schlüssel; fünf Query-Objekte mit abweichendem binären Lv-Feld. Keine Gleichsetzung der85Systemqueryobjekte mit47früheren DAO-Querydefinitionen.
- [x] Vor Extraktion Werkzeugreview; Windows-Dateinamen- und gemeinsame Quellenabschlussprüfung korrigiert. Leitung14Guardtests; Comparator Worker/Leitung je11bestanden+1Hostsymlinkskip. Astra prüfte Werkzeuge und Beweisgrenzen. Keine Roh-VBA an Helfer.
- [ ] Bedeutung der fünf binären Unterschiede, volle saved-object/Event/Control/Makro-/SQL-Parameter-/Laufzeit-/P-Codeparität bleiben offen. RF-E1/Vorlagen/äußerer Controller weiterhin offen; kein Access-/DAO-/Originalablauf in diesem Paket.
- [ ] Weitere unabhängige P3-Vertrags-/Writer-/Reportprüfungen fortsetzen; vollständige aktuelle RMF-Referenzen vor Modulabnahme. Versionsbindung/Objektrevision/Prüfnachweise in P4 aufnehmen; zentrale Datenbankentscheidung erst P5 nach kompletter siebenmoduliger Matrix.

Quellenbindung/Detailgrenzen im [RMF-Versionsbericht](../../verification/AURELIA_P3_RADIFARBEN_RMF_VERSION_DELTA_2026-10-11.md). Vorher-/Nachherpunkt checkpoints/RadiFarben-RMF-Delta-20261011-121653Z; private Quellbelege im versionsgebundenen Owner/SYSTEM-Ordner. Keine F:-Vollsicherung, WSL-/Cloudaktion oder Produkt-/Live-/Governors-/Routing-/normative Templatesänderung. P0/P1/P2 und P6–P8/S4.8 sowie RadiWorks-Wartungsreihenfolge bleiben erhalten. Abschnitt16/17 bleiben historische Vorbereitung; der dort noch offene statische Versionsvergleich ist durch diesen begrenzten Befund ergänzt.


## 21. P3 – gruppierter Import-Schutz und RMF-Abfragezuordnung, 11.10.2026

- [x] RadiMorphic: bestehende Service-Publish-Sperre bei synthetischem Receipt mit echtem Store; vier explizite Pfadgruppen. Worker und Leitung je5bestanden,0Fehler/Skips. Genau sieben Core-Dateien bytegebunden und unverändert, keine Produktinitialisierer; zusätzliche Leitungskontrolle der exakten Testnamen/Anzahl/Skips.
- [x] RadiFarben: fünf neue Lv-Metadatenänderungen gegen alte Querydefinitionen und100aktuelle manifestgebundene kanonische VBA-Dateien zugeordnet. Drei alte Definitionstreffer, sechs Literalkandidaten bei einem Objekt; zwei~sq_-Präfixnamen. Zwei Läufe außerUTC gleich; öffentlicheAggregatebytegleich. Leitung/Astra je15synthetischeTestsgrün. Kein neuerDAO-/SQL-/VBA-/Runtimebeleg.
- [x] Vorher-/Nachher-Dokumentenpunkt; drei ACCDB-Quellenendpunkte zu ihren jeweiligen Referenzhashes unverändert15:39UTC, keineLockdateien. Technische private Zuordnungsbelege separat manifestiert, keine Rohdefinitionen an Helfer. Frühere Testfehler und synthetische Scratchreste erhalten.
- [ ] Vollregistry-/Importrevalidierung: außerhalb siebenModulen; getrennten Scope vorbereiten, keine Autoritäts-Dummies. RF-E1/Access-Vorlagen/äußererController, aktuelle RMF-Event-/Control-/Makro-/SQL-/Parameter-/Laufzeitparität bleiben offen.
- [ ] Nächste unabhängige P3-Arbeit weitere Writer-/Report-/Archiv-/Restore-Verträge. P0/P1/P2/restlicheP3 weiterhin offen; P4 vollständige siebenmodulige Matrix einschließlichAurelia/Templates, dann P5 zentraleDatenbankentscheidung. P6–P8/S4.8 und RadiWorks-Wartungsreihenfolge unverändert.

Detailgrenzen und tatsächliche Ausführungs-/Reviewrollen im [Prüfbericht](../../verification/AURELIA_P3_IMPORT_RMF_BINDUNGEN_2026-10-11.md). Lokaler Prüfpunkt checkpoints/Aurelia-P3-Import-RMF-20261011-153618Z; keine F:-Vollsicherung, Produkt-/Live-/WSL-/Cloud-/Office-/Governors-/Routing-/normativeTemplatesänderung. Python-Guards sind keineOS-Sandbox; alte SQL-Zuordnung und Literaltexte keine aktuelle Laufzeit-/Algorithmusparität. Astra unabhängig begrenzt, Quellenrohtexte nur Leitung.

## 22. P3 – Backup-Referenzen, 11.10.2026

- [x] Snapshothelper und Manifest-/Completion-Verträge sowie öffentliche Restore-Ablehnungen: zwei Läufe je14 bestanden,0 Fehler/Skips; aktuelle sieben Quellenhashes nachgerechnet.
- [x] Astra Werkzeug-/Ergebnisreview; lokaler Vorher-/Nachher-Prüfpunkt mit Manifest. Keine Produkt-/Liveänderung.
- [ ] Vollständiger positiver Publish/Restore, Registry/Migration und Windows-Bericht-Handleprüfung. Kein vollständiges Writer-/Job-E2E daraus ableiten.

Details: ../../verification/AURELIA_P3_BACKUP_REFERENZEN_2026-10-11.md; Prüfpunkt Aurelia-P3-Backup-Status-20261011-163541Z. P4 vor P5 unverändert.

## 23. P3 – Berichtreferenzen, 11.10.2026

- [x] Zwei synthetische Roots, Standort-ID/Inhaltsrevision, Preview/Download und echter Windows-Handleweg: zwei korrigierte Läufe je12/0/0/0; Erstlauf-Guardfehler erhalten.
- [x] Astra statischer Scope-/Baseline-/Ergebnisreview; Quellenbindung und lokaler manifestierter Vorher-/Nachherpunkt.
- [ ] Writer-/Registry-/Restore-E2E, RF-E1 und übrige P3-Abnahmen; keine Mandanten-/Linux-/Raceabnahme. P4 vor P5 unverändert.

Details: ../../verification/AURELIA_P3_BERICHT_REFERENZEN_2026-10-11.md; Prüfpunkt Aurelia-P3-Report-Status-20261011-171422Z.

## 24. P3 – Writer-/Registryvertrag und lesender Template-Abgleich, 11.10.2026

- [x] Statische Top-N-Writerkette in zehn bytegebundenen Dateien; Job-Owner, Roh-/Katalogsession, Artefaktrevision und Teilpersistenz getrennt. Keine Writer-/Job-Runtime ausgeführt.
- [x] Vier direkte Publish-Abhängigkeiten und drei aktuelle Template-Dateien gebunden. POSIX-Publishguard im geprüften Stand fail-closed; echte Ubuntu-Cleanup-Probe offen. Historische Sechserkarte ohne RadiFarben; keine normative Templateänderung.
- [x] Luna6/max Writeraufnahme, Astra6/medium unabhängige Präzisierung, Leitung Quellen-/HEAD-/tracked-only Nachrechnung und lokaler Dokumentenprüfpunkt. Andere Template-WIP nur als Status, nicht bytegebunden.
- [ ] Nächster Referenzweg: geprüfter realer Loader und nativer Windows-Publish/Restore an synthetischen Schema-v8-Fixtures. POSIX-Negativ-/Cleanup und v7-Migration separat; keine Guardumgehung/Dummy-Registry.
- [ ] RF-E1, übrige P0/P1/P2/P3 offen. P4 vollständige siebenmodulige Matrix einschließlich Aurelia/Templates vor P5 Datenstrukturentscheidung; P6–P8/S4.8 separat.

Details: [Teilbericht](../../verification/AURELIA_P3_WRITER_REGISTRY_TEMPLATE_2026-10-11.md); Prüfpunkt `checkpoints/Aurelia-P3-Writer-Registry-Status-20261011-174307Z`. Liveinstanzen/Originalalgorithmen unverändert; keine neue F:-Vollsicherung.


## 25. P3 – öffentlicher Windows-Schema-v8-Backup-/Restoreweg, 11.10.2026

- [x] Zehn originale Module bytegebunden, öffentliche Erstellung und Restore an synthetischen Katalogen über echte Registry-Funktionen. Zwei frische Läufe je10 bestanden,0 Fehler/Fehlschläge/Skips; zehn exakte Namen und guard-first zusätzlich nachgerechnet.
- [x] Manifest/Completion/Hashes/Schema-v8/Drafts/Kontextabfragen, neue getrennte Zielkopien, Nichtüberschreiben, öffentliches Tamper-/Completion-Reject und direktes Publish-Cleanup. Keine Auth-/Writer-/Job-/Race-/Crash-/Linux-Abnahme.
- [x] Luna6/max statische Quellenbindung, Astra6/medium vor Ausführung und Ergebnis-/Abschlussreview; Quellen/Harness/HEAD/tracked-only unverändert, je29 gespeicherte synthetische Artefakte unabhängig nachgerechnet.
- [x] Frischer Dokumentenprüfpunkt mit separat geprüftem Vorher-Manifest; historische Wiederaufnahme als exakter Bytesuffix. Abschlussmanifest erst durch tatsächlichen Abschlussbeleg bestätigt, kein F:-Gesamtbackup.
- [ ] POSIX-Negativ-/Cleanup, v7-Migration und übrige P3-Vertrags-/Writer-/Registry-/RF-E1-Abnahmen. P0/P1/P2 offen; P4 siebenmodule Matrix mit Aurelia/Templates vor P5 Datenstrukturentscheidung; normative Synchronisierung P6–P8/S4.8 getrennt.

Bericht [öffentlicher Restore-Referenzweg](../../verification/AURELIA_P3_PUBLIC_RESTORE_2026-10-11.md); frischer Prüfpunkt `checkpoints/Aurelia-P3-Public-Restore-Status-20261011-182431Z`. Abschnitte22–24 bleiben ursprüngliche zeitgebundene Befunde; deren offene positive Windows-v8-Referenz ist durch diesen Teilnachweis ergänzt. Live/Originalalgorithmen unverändert.


## 26. P3 – separater Windows-v7→v8-Migrationsnachweis, 11.10.2026

- [x] Elf reale Module bytegebunden, keine Produktinitialisierer; Luna statischer Quellen-/Fixturevertrag und Astra SPEC→QUALITY vor Originalausführung. Zwölf exakte Fälle, Guard zuerst.
- [x] Direkte Migration/idempotentes v8, unsupported schema, drei echte Checkpoint-Rollbacks, öffentlicher v7-Bundle→v8-Bundle→Restore und fünf negative öffentliche Fälle. Zwei leere Drafts/Kontextabfragen/Markerreset, keine historische Vollkatalog-/Auth-/Revalidierungsabnahme.
- [x] V1 Fixture-Snapshotabweichung: 6/0/1/0 (fünf bestanden) erhalten; Testfixture originalnah normalisiert, ursprüngliche Hashprüfung unverändert. Zwei korrigierte frische Läufe je12/0/0/0, je39 Artefakte plus12 alte Fehlerartefakte nachgerechnet. Quellen/Harness/HEAD/tracked-only gleich.
- [x] Unzulässigen historischen63-stelligen Quellenhash erhalten und aktuelle Metadaten v2 programmgeneriert; keine rückwirkende Kontinuitätsbehauptung. Lokaler Dokumentenpunkt mit geprüftem Vorher-Manifest vorbereitet; vollständiger historischer Bytesuffix und final-Manifest werden erst durch den tatsächlichen erfolgreichen Abschlusslauf bestätigt.
- [ ] POSIX-Ablehnungs-/Cleanupweg, volle Registry-/Writer-/Job-/RMF- und übrigeP3-Prüfungen. P0/P1/P2/RF-E1 offen; P4 vollständige siebenmodulige Matrix mit Aurelia/Templates, dann P5 zentrale Datenstrukturentscheidung, P6–P8/S4.8 separat.

[Migrationsbericht](../../verification/AURELIA_P3_V7_MIGRATION_2026-10-11.md); Prüfpunkt `checkpoints/Aurelia-P3-V7-Migration-Status-20261011-191912Z`. Vorherige Abschnitte bleiben historische Nachweise, deren offene v7-Referenz durch diesen begrenzten Nachweis ergänzt ist. Keine Produkt-/Live-/normative Templateänderung oder F:-Gesamtsicherung.


## 27. P3 – POSIX-Prüfaufnahme mit Anlaufblocker, 11.10.2026

- [x] Zehn Originalmodule statisch paarweise gebunden; Luna Vertrag und Astra unabhängiger Review. Frühere 133 Manifestdateien frisch geprüft; keine Produktmodulausführung.
- [x] Referenzanlauf tatsächlich versucht, vor Linux-Python CreateVm/HCS/0x800705aa. Hostzähler separat gelesen, genaue Ursache nicht bewiesen; keine Hostkonfiguration geändert.
- [ ] Tatsächlicher ext4-/Python-/Guard-/FD-/Backup-/Restore-Cleanup-Nachweis und zwei frische negative Prüfläufe; Anlaufvoraussetzung fehlt.
- [x] Begrenzter Iststand/Vorherpunkt vorbereitet; Abschlussmanifest/Nachherstand/historischer Bytesuffix ausschließlich durch tatsächlichen erfolgreichen final-Lauf bestätigt.
- [ ] P0/P1/P2/RF-E1 und übrige P3-Verträge; P4 vollständige Siebenermatrix einschließlich Aurelia/Templates, dann P5 Datenstrukturentscheidung. Eigener Linux-Publishadapter nicht freigegeben oder umgesetzt.

[POSIX-Vorbereitung](../../verification/AURELIA_P3_POSIX_VORBEREITUNG_2026-10-11.md); Prüfpunkt `checkpoints/Aurelia-P3-POSIX-Status-20261011-195451Z`. Vorherige Windowsnachweise bleiben erhalten. Keine normative Template-/Produkt-/Liveänderung oder F:-Gesamtsicherung.

## 28. P3 – serverunabhängige Owner-/Lease- und Writer-/Reportfortsetzung, 14.10.2026

- [x] 17 W2-Codequellen statisch gebunden: Tenant-/Job-/Reportroot, Roh-/Ordner-/Manifest-/Katalogsession, Inhaltsrevision, genaue Score-Rundungsformel und PDF-Abhängigkeiten. Sieben neue Quellen gegenüber W1; anfängliche breite Dateinamensmetadatenaufnahme begrenzt dokumentiert, keine Archivdaten geöffnet.
- [x] Owner/Lease/Recovery: zwei Läufe je19 synthetische Fälle, identische Details; drei extrahierte Originalkörper, feste Uhr und Fake-Jobs/Reconciler/Ereigniswriter. Elf Guardtests; AST-/Quellenbindung und unabhängiger Vorher-/Ergebnisreview. Ungültige Rohobjekte umgehen Loaderprüfung; keine echte Recovery-/Autoritätsabnahme.
- [x] W2: vier ausgewählte Berichtsfunktionen, zwei Läufe je16 Fälle mit gleichen vollständigen Ergebnissen. Rundung/JSON und konkrete Sessionlayouts; reine Pfadobjekte. Zehn Werkzeugtests nach drei Reviewkorrekturen, negative Optimierungsprobe, Gateänderung separat gebunden. Keine Originalmodule oder Klasseninitialisierer, kein PDF oder echter Writerlauf.
- [x] 18 relevante Quellen, HEAD und getrackter Zustand vor/nach unverändert; tatsächliche Helfer Luna/max und Astra/medium. P4-Datenbedarf präzisiert: getrennte Tenant-/Operator-/Auftrags-/Session-/Artefaktidentitäten und Inhalts-/Formel-/Quellrevisionen. Keine neue Heuristik oder Produktimplementierung.
- [ ] Gesamt-Writer-/Registry-/Job-/Readerkette, führende Morphic-Quelle, Linux/POSIX-/Backendnachweise, RF-E1/aktuelle RMF-Parität bleiben offen. Aktueller Rootserver nicht erreichbar; geschützte RF-Rohreferenzen in diesem Paket nicht lesbar. Keine ACL-Änderung, Officeaktivierung, Server-/WSLaktion oder neue SSH-Berechtigung.
- [ ] P4 vollständige Siebenermatrix einschließlich Aurelia und Modul_Templates, dann P5 zentrale Datenstrukturentscheidung. Normative Synchronisierung und Integration erst P6–P8/S4.8. RadiWorks-Wartungsreihenfolge, Dauerinstanzen und Originalalgorithmen erhalten.

Details und tatsächliche Grenzen im [Offline-Prüfbericht](../../verification/AURELIA_P3_OFFLINE_MORPHIC_2026-10-14.md). Lokaler Vorher-/Nachherpunkt `checkpoints/Aurelia-P3-Offline-Status-20261014-130301Z`; Abschluss ausschließlich durch rückgeprüftes Manifest bestätigt. Kein F:-Gesamtprojekt-/Serverbackup oder private Schlüsselkopie. Ältere Abschnitte bleiben zeitbezogene Nachweise; ihre Linux-/Accessgates sind durch diese Offlineproben nicht erfüllt.

## 29. P3 – tatsächliche Auftragsdatenvalidierung, 14.10.2026

- [x] Originalparser und zwölf reine Helper/Authority-Validatoren aus zwei bytegebundenen Quellen; 27-Feld-Dataclass bewusst ohne sechs Originalmethoden. Kein ganzer Modul-/Datei-/Workerpfad oder permissiver Autoritäts-Dummy.
- [x] Zwölf synthetische Werkzeugtests, Reviewkorrekturen vor Ausführung, Astra SPEC→QUALITY und Ergebnisreview. Historische v1-Byte-/Rotprotokolllücke offen dokumentiert, keine vollständige TDD-/v1-Reproduzierbarkeitsbehauptung. Ausgeführte v2 vorab als Bytes gesichert.
- [x] Zwei Läufe je24 Fallgruppen mit gleichen vollständigen Ergebnissen; Format-/Legacy-/ID-/Zahlen-/Hardware-/Zeit-/Status-/Phasen-/Fortschrittsregeln und In-Memory-Aliasing charakterisiert. 19 Quellen, beide Werkzeuge, HEAD und getrackter Stand unverändert.
- [x] P4 ergänzt: Eingangsschema versus normalisierte Darstellung, Default-/Feldpräsenz, Rohzeit versus Vergleichswert, gespeicherte versus neu erzeugte IDs und Snapshothoheit getrennt. Parserannahme ist kein Rechte-/Klientenbezug.
- [ ] Echte Datei-/Speicher-/Lock-/Recovery-/Prozess-/Auth-/Restore-/Linuxpfade sowie führende Morphic-Quelle und RF-E1 bleiben offen. Gesamt-P3 und vollständige Siebenermatrix vor P5; normative Aurelia-/Modul_Template-Abstimmung und P6–P8/S4.8 unverändert.

Details: [Auftragsdaten-Prüfbericht](../../verification/AURELIA_P3_MORPHIC_RECORD_VALIDIERUNG_2026-10-14.md). Lokaler Vorher-/Nachherpunkt `checkpoints/Aurelia-P3-Morphic-Record-Status-20261014-164313Z`, genau gesicherter Umfang durch Abschlussmanifest/Rücklesebeleg. Keine Server-/F:-Vollsicherung, private Datenkopie, Produkt-/Live-/Routing-/normative Templateänderung.

## 30. P3 – Radi144 CPU-Kern und API-Vertrag, 14.10.2026

- [x] Zehn benannte Quellen einschließlich bestehendem vorgemerktem AGENTS.md bytegebunden. Sieben ausgewählte Enginefunktionen und zwei reine API-Amplifier-Helper statisch erfasst; kein Enginekonstruktor, Produktmodul, Wissenskatalog oder echter Klient gestartet. Bestehende 18 Storage-/Fehlercharakterisierungen nicht wiederholt.
- [x] Luna/max begrenzter Harness, Astra/medium unabhängiger Vorreview; äußerer Controller mit bereinigter Umgebung, Quellen-/Werkzeugbindung, eigenem Kindprozess und technischer Zeitgrenze. Gate-/Fehlerbelege erhalten, originale Algorithmen unverändert. Kleine CPU-Kandidatenzahlen sind keine Vollpool-/Hardwareabnahme.
- [x] V7 35 frische synthetische Werkzeugtests erfolgreich. Tatsächlicher Codec-/AST-Auditvertrag und vorbereitende AST-Maße 172945/6098 Byte geprüft; keine numerischen Originalergebnisse daraus ableiten.
- [ ] Zwei erfolgreiche frische CPU-Kernläufe und Ergebnisvergleich. Bisher vier Anläufe, kein Originalfunktionskörper ausgeführt; zunächst Codec-/Alias-/Importsemantikgrenzen, zuletzt NumPy-Umgebungsinitialisierung. Quellen, ausgeführte Werkzeuge und benannter Gitstand gleich; kein Timeout/Ressourcenfehler. CPU-Abnahme offen; vollständige zeitbezogene Historie im Prüfbericht, aktuelle V8-Fortsetzung unten.
- [x] FortsetzungV8 nach Betreiberfreigabe: Importentwurf geprüft und minimal umgesetzt,37/37 synthetische Tests bestanden. Versuch4 überwindet bisherigen Abbruch, erreicht NumPy und stoppt an OPENBLAS_MAIN_FREE-Initialisierung. Neue Quelle-/Werkzeug-/Gitgleichheit, kein Timeout/Ressourcenfehler. Vereinbarter Fehlerstopp eingehalten, Gate geschlossen, keine weitere Patchfolge. Vorbereiten einer konstanten Kindumgebungsvariable statt zusätzlicher Guardausnahme nur als nächster Entwurf; noch keine CPU-Abnahme. Aktueller Punkt `checkpoints/Aurelia-P3-Radi144-Import-Status-20261014-200503Z`, aktueller Prüfbericht erklärt Historie und Grenzen.
- [x] FortsetzungV9 nach erneuter Betreiberfreigabe: genauOPENBLAS_MAIN_FREE=1 nur in Kindumgebung, Controllerprüfung und37Harnessproben grün, Astrareview. Versuch5 überwindet NumPy-Umgebungssperre und stoppt korrekt an installiertem, unfreigegebenem torchgen. Quellen/Werkzeuge/benannter Gitstand gleich;0Originalfallgruppen, keine CPU-Abnahme. Gate geschlossen, kein Versuch6. Deklarierten zusätzlichen Torch-Paketumfang vor nächstem Start konsolidieren; noch keine Paketfreigabe. Lokaler Punkt `checkpoints/Aurelia-P3-Radi144-Env-Status-20261014-202421Z`.
- [ ] Gesamt-Engine-/API-/UI-/CLI-/Parallelitäts-/Linuxabnahme, führende Morphic-Quelle, RF-E1 und übrige P3-Punkte bleiben offen. P4 vollständige Siebenermatrix einschließlich Aurelia/Modul_Templates vor P5-Datenstrukturentscheidung; P6–P8/S4.8 getrennt.

Details: [Radi144-CPU-Prüfbericht](../../verification/AURELIA_P3_RADI144_CPU_KERN_2026-10-14.md). Lokaler Statuspunkt `checkpoints/Aurelia-P3-Radi144-CPU-Status-20261014-174238Z`; Abschluss und gesicherter Umfang erst durch nachgerechnetes Manifest. Kein Server-/F:-Gesamtbackup oder Produkt-/Live-/Routing-/normativer Templateeingriff. Historischer Verlust genau eines zusätzlichen synthetischen Controllerbelegs ausdrücklich ausgewiesen; tatsächliche Fehlversuche und Werkzeugfassungen erhalten.


## 31. P3 – Radi144 CPU-Teilreferenz bestanden, 14.10.2026

- [x] Vier tatsächlich benötigte Torchgen-Module quellen-/RECORD-/Ursprunggebunden;39 Werkzeugtests und Controllerprüfung erfolgreich, Luna/max lesende Vorbereitung und Astra/medium Vor-/Ergebnisreview. Keine zusätzliche Rootwildcard, functorch oder Produktänderung.
- [x] Zwei Läufe6/7 mit je14 Fallgruppen/81 Erwartungen bestanden; vollständige stabile Caseobjekte, Source/AST/Runtime-/Werkzeug-/Bootstrapbindungen gleich. Tensorwerte als vollständige kanonische Digests, Roharrays nicht exportiert. Python3.11.12/Torch2.12.0+cpu/NumPy2.4.6, Threads1/1, CUDA nicht initialisiert; Kandidaten64/96/160. Quellen/Werkzeuge/benannter Gitstand unverändert.
- [x]26 JIT-Overload-Inspektionswarnungen jeLauf erhalten, kein JIT-Nachweis. Originalfehlergrenzen Top-k/kleiner Pool, Precision-RNG bei Fehler und API-Datenreferenzrückgabe charakterisiert, nicht verändert. Kein vollständiger erfolgreicher calculate_resonance-/HTTP-/UI-/Stochastik-/Linuxweg oder Parallelitätsnachweis.
- [x] P4 konkretisiert: unveränderliche Rechenrezepte/Quell-/AST-/Runtimeparameter; Matrixartefakte+Hash/Form/Datentyp, eigene Score-/Intensitätsdefinitionen; Rohfokus versus Suchnormalisierung, Defaultfrequenz, Kandidatenpolitik, RNGhoheit und Inhaltsrevision bei Amplifiern. Keine neue zentrale Datenbank entschieden oder implementiert.
- [ ] Gesamt-P3/führende Morphic-Quelle/RF-E1 und Linux-/Backendreferenzen bleiben offen. P4 vollständige Siebenermatrix mit Aurelia/Modul_Templates vor P5; normative Abstimmung/Integration P6–P8/S4.8 getrennt. Unabhängige belegbare P3/P4-Vorbereitung fortsetzen, keine unverifizierte Runtime-/Produktfreigabe.

[CPU-Prüfbericht](../../verification/AURELIA_P3_RADI144_CPU_KERN_2026-10-14.md); geprüfter lokaler Punkt `checkpoints/Aurelia-P3-Radi144-Torchgen-Status-20261014-205410Z` erst durch finalen Rücklesebeleg abgeschlossen. Historische Fehlerabschnitte bleiben erhalten. Keine Live-/Produkt-/Routing-/Templateänderung oder F:-/Servergesamtsicherung.


## 32. P3 – nachfolgender Radi144-Parameterbefund und vereinbarter Halt, 14.10.2026

- [x] Drei Originalquellen statisch per AST verbunden, danach Hash/HEAD/benannter Status gleich; keine Module/Engine/HTTP gestartet. `calculation_mode` wird weitergereicht. `use_cuda`/`use_quantum` werden als Requestwerte gespeichert, steuern aber den untersuchten Rechenaufruf/Vorbereitungsweg nicht; Gerät aus globaler Engine. `iterations` deklariert, nicht weitergereicht, ohne entsprechenden Engineparameter.
- [x] Astra/medium bestätigt die quelllokale Vertragslücke und Begrenzung. P4 muss angeforderte, wirksam angenommene und tatsächlich beobachtete Parameter trennen. Separate vorhandene Hardware-Ergebnisausgabe bleibt berücksichtigt. Keine Aussage „in der gesamten App ungenutzt“ oder Live-Reproduktion.
- [ ] Wie vom Betreiber verlangt bei erkannter Problematik weitere Ausführung angehalten. Vor neuen API-Referenzen Vertragsentscheidung: Original unverändert als Referenz erhalten; Optionen als Legacy-/Kompatibilitätsfelder oder echte Auftragssteuerung einordnen. Keine stillen Produktkorrekturen, neue Formel oder normative Templateänderung.
- [x] CPU-Teilnachweis aus Abschnitt31 unverändert gesichert; Parameterbericht und eigener Vorher-/Nachherpunkt konsolidiert. Manifest/Rücklesebeleg belegen tatsächlichen Umfang, kein F:-/Servergesamtbackup. Gesamt-P3 und P4/P5-Gates bleiben offen.

[Parameterbericht](../../verification/AURELIA_P3_RADI144_PARAMETER_2026-10-14.md), lokaler Punkt `checkpoints/Aurelia-P3-Radi144-Parameter-20261014-211126Z`. Liveinstanzen und Originalalgorithmen unverändert; kein neuer nativer Lauf.


## 33. P3 – bestätigte Fortsetzung und API-Parameterreferenz, 14.10.2026

- [x] Betreiber folgt Empfehlung zur bekannten Vertragslücke; Original unverändert als Ist-Referenz erhalten. Wunsch-/wirksame/beobachtete Einstellungen getrennt; keine neue Requeststeuerung still verdrahten. Vorherpunkt `checkpoints/Aurelia-P3-Radi144-API-Parameter-20261014-213342Z` mit drei Dokumentkopien/Manifest.
- [x] Begrenzter Entwurf und Ausführungsplan für genau acht API-Funktionskörper, acht synthetische Übergabe-/Fehlerfallgruppen und Standardbibliothek; keine echte Rechenengine, HTTP, Dateistores oder Klienten. Rootcontroller-RED fünf erwartete Fehler, danach fünf Werkzeugtests erfolgreich; kein Original ausgeführt.
- [x] Luna/max Werkzeug+Tests, Astra/medium eingefrorener SPEC→QUALITY-Vorreview, zwei frische Kindläufe und vollständiger Ergebnisvergleich; bekannte CUDA-/Quantum-/Iterationsdiskrepanz bleibt erwarteter Istbefund.
- [x] P4-Provenienz/Teilabschlussbedarf, geprüfter Bericht und manifestierter Vorher-/Nachherpunkt ergänzen. Gesamt-P3, führende Morphic-Quelle/RF-E1/Linuxreferenzen und P4-vor-P5 unverändert; keine Produkt-/Live-/Routing-/normative Templateänderung.

[Teilplan](2026-10-14-radi144-api-parameter-reference.md). Ältere Stoppaussagen in Abschnitt32 sind durch die neue Betreiberentscheidung ergänzt, nicht rückwirkend gelöscht.


## 34. P3 – API-Parameter-Teilreferenz bestanden, 15.10.2026

- [x] Acht Original-AST-Funktionen bei unveränderter Quelle mit synthetischen Rechen-/Session-/Responsegrenzen; sieben Harness-/sechs Controllertests bestanden. Root übernimmt aktuelles Werkzeug nach Luna; Astra Vorreview findet falsche Session-Double-Rückgabe, minimal mit separater Rot-/Grünregression korrigiert vor Originalausführung.
- [x] Zwei frische Läufe je8 Fallgruppen/36 Erwartungen erfolgreich, vollständige Ergebnisobjekte ausschließlich ohne Label gleich. Quellen-/Werkzeug-/benannter Gitstand vor/nach gleich; kein Timeout/Nachprüffehler, stderr leer. Gate nach Verbrauch der Laufkennungen geschlossen. Keine echte Berechnung, Pydantic, HTTP, Stores oder Autorisierung.
- [x] Bekannter Request-/Wirkparameterbefund unverändert erhalten. Für P4 angefordert, weitergereicht, Speicherung versucht/tatsächlich erfolgt und Responsekonstruktorwert getrennt führen. Fall07 besitzt nur Speicherungsversuch ohne Session; Fall08 synthetische Session/Header vor Antwortfehler, keine echte HTTPübertragung. Keine neue Formel-/Produktreparatur.
- [x] Bericht und Vorher-/Nachherpunkt konsolidiert; tatsächlicher Umfang/Abschluss durch finales Manifest/Rücklesen. Historische Loader-/ast.dump-Zwischenbytegrenze ausgewiesen. CPU-Teilnachweis aus Abschnitt31 bleibt unverändert.
- [ ] Gesamt-P3, vollständige Rechen-/API-/UI-/CLI-/Abbruch-/Parallelitäts-/Linuxwege, führende Morphic-Quelle und RF-E1 bleiben offen. P4 vollständige Siebenermatrix mit Aurelia/Modul_Templates vor P5; P6–P8/S4.8 separat. Kein Live-/Routing-/normativer Templateeingriff oder F:-/Servergesamtbackup.

[API-Parameterbericht](../../verification/AURELIA_P3_RADI144_API_PARAMETER_2026-10-14.md), Prüfpunkt `checkpoints/Aurelia-P3-Radi144-API-Parameter-20261014-213342Z`. Neue unabhängige P3-Aufnahmen auf dieser belegten Basis fortsetzen; keine Gesamtfreigabe aus Teilprüfungen ableiten.


## 35. P3 – Radi144-Eingabe-/Signaturaufnahme und neuer Halt, 15.10.2026

- [x] Pausepunkt mit29Manifestdateien/61ZIP-CRC-Einträgen frisch nachgerechnet; vorherige numerische Referenzen nicht wiederholt. Zehn Original-/Abhängigkeitsquellen als Bytes gesichert,22Funktionsdefinitionen AST-/Zeilengebunden, bestehendes AGENTS-WIP erhalten.
- [x] Luna/max liest Caller von UI/Schema über Inline/ID/Gruppe/Geo/Bild/DB zur Signatur; Leitung bindet Quellen und sichert. Keine numerische Originalfunktion oder echte Pydantic-/HTTP-/Datei-/Storegrenze ausgeführt.
- [x] Astra/medium bestätigt SPEC→QUALITY neue materielle Zeittyp-/ID-Inline-Vorranglücken und begrenzte Registry-Projektion. Native date akzeptiert, nur time-Anteil betroffen; geolocation-Auslassung ohne belegten numerischen Effekt. Kein Livevorfall behauptet, keine Produktreparatur.
- [ ] Betreiberentscheidung vor weiteren Originalläufen: Empfehlung Original unverändert erhalten und native/String-/Registry-/Mischfälle getrennt charakterisieren; Reparatur separat. Nicht durch frühere Parameterentscheidung oder Reviewerurteil als bereits freigegeben behandeln.
- [ ] Danach weitere Signatur-/Kontext-/Workflowreferenzen mit expliziter Zeit-/Quell-/Runtimebindung. Echte NumPy-/Pillow-/Pydantic-/Datei-/HTTPgrenzen separat; kein math-Adapter als Originalformelbeleg. Gesamt-P3/führende Morphic-Quelle/RF-E1/Linux-/Backendgates bleiben offen.
- [ ] Vollständige P4-Siebenermatrix einschließlich Aurelia/Modul_Templates vor P5; normative Abstimmung/Integration P6–P8/S4.8 separat. Liveinstanzen/Algorithmen/Routing/Templates unverändert.

[Quellbericht](../../verification/AURELIA_P3_RADI144_EINGABE_SIGNATUR_2026-10-15.md), lokaler Punkt `checkpoints/Aurelia-P3-Radi144-Input-20261015-061349Z`; genauer Umfang und Abschluss erst durch finalen Rücklesebeleg. Kein F:-/Server-/Schlüssel-/Gesamtbackup. Frühere Abschnitte bleiben zeitgebundene Historie.


## 36. P3 – Kontext-/Zeitreferenz nach Betreiberentscheidung, 15.10.2026

- [x] Betreiber erlaubt unveränderte Charakterisierung der neuen Befunde; keine Korrekturfreigabe. Vorpunkt und24Dateien des vorherigen Punkts geprüft, drei Statusdokumente vorher gesichert.
- [x] Enger Entwurf/Plan: sechs API-Helper und zwei originale Geburts-/Julianmethoden, zwölf synthetische Zeit-/Kontext-/Identitätsfälle. Keine echte Pydantic-/HTTP-/Engine-/Storeausführung.
- [x] Rootcontroller RED sieben erwartete fehlende Funktionen, GREEN siebenTests, zehn unveränderte Quellhashes. Neues Gate bis Review geschlossen;0Originalfunktionsaufrufe. Luna/max Harness/Tests, Astra/medium Vorreview, Root besitzt Controller/Ausführung/Status.
- [ ] Eingefrorenen Harness/Controller unabhängig prüfen, zwei frische context-run-1/2, vollständige Ergebnisse ohne Label vergleichen; bei unerwartetem Fehler stoppen.
- [ ] Gate schließen, Ergebnisreview, Quellen-/Werkzeug-/Gitgleichheit, Bericht und final rückgelesenen Prüfpunkt konsolidieren. Nicht als Gesamt-P3 oder Freigabe einer Produktreparatur ausweisen.

[Teilplan](2026-10-15-radi144-context-reference.md), Punkt `checkpoints/Aurelia-P3-Radi144-Context-20261015-062425Z`. P4 vollständige siebenmodulige Matrix mit Aurelia/Modul_Templates vor P5; P6–P8/S4.8 getrennt. Quellen/Liveinstanzen/Routing/Templates unverändert.


## 37. P3 – Kontextreferenz: Werkzeugstand geprüft, Git-Vorprüfung gestoppt, 15.10.2026

- [x] Abschnitt35-Betreiberentscheidung inzwischen ausdrücklich erteilt: Originalbefunde nur charakterisieren, keine Reparatur. Vorbereiteter Acht-AST-/Zwölfgruppenvertrag;20 aktuelle isolierte Werkzeugtests (7 Controller+13 Harness) bestanden,0Skips, vier Werkzeugbytes vor/nach gleich. Astra/medium eingefrorener SPEC→QUALITY-Vorreview ohne materiellen Blocker.
- [x] Erster Versuch `context-run-1` scheitert vor Kindstart (`launch_attempted=false`) an Git dubious ownership: Repository Hubert111, isoliertes Testkonto CodexSandboxOffline. Keine Originalfunktion aufgerufen. Zweiter Lauf nicht gestartet; Gate exakt geschlossen, kein Retry. Zehn Quellhashes/vier Werkzeughashes vor/nach gleich; Git-HEAD-/Statusprüfung fehlgeschlagen, deshalb unbekannt.
- [x] Fehler unabhängig von Astra gelesen, Ursache/Ungewissheit erhalten. Bericht, Wiederaufnahme und lokaler begrenzter Vorher-/Nachherpunkt; Sicherungsabschluss nur gemäß FINAL-READBACK. Historische falsche GREEN-Verzeichnisnamen und Zwischenmanifestlücke sind ausgewiesen; finale20Tests unabhängig belegt. Kein Produkt-/Live-/Server-/Routing-/Templateeingriff.
- [ ] Betreiberentscheidung vor neuer Ausführung: empfohlen ausschließlich prozesslokales `-c safe.directory` für exakt geprüften Radi144-Pfad, keine globale/wilde Ausnahme. Erst neue Controllerfassung, Tests/Review und frischer Prüfpunkt; bestehende Kennung1 bleibt verbraucht. Die Kontextreferenz selbst und der Zweiervergleich sind noch offen.
- [ ] Gesamt-P3, RF-E1/führende Morphic-Quelle/Linux-/Backendnachweise bleiben offen. Vollständige P4-Siebenermatrix mit Aurelia/Modul_Templates vor P5; P6–P8/S4.8 separat. Keine Datenbankentscheidung aus diesem Werkzeugnachweis.

[Kontextbericht](../../verification/AURELIA_P3_RADI144_KONTEXT_REFERENZ_2026-10-15.md), Punkt `checkpoints/Aurelia-P3-Radi144-Context-20261015-062425Z`. Frühere Start-/Erwartungsabschnitte sind zeitgebundene Historie; kein P3-Gesamterfolg oder F:-/Servergesamtbackup.


## 38. P3 – begrenzte Git-Korrektur und Kontextteilreferenz bestanden, 15.10.2026

- [x] Neue Betreiberfreigabe für exakt pfadgebundenes Vertrauen nur im Prüfprozess. Vorpunkt 117 Manifestdateien/116 ZIP-Einträge rückgeprüft; neuer Punkt mit 26 Anfangsdateien. Nur neuer Controller und dessen Tests geändert, keine globale Gitkonfiguration oder Produktdatei.
- [x] Drei neue Regressionen zuerst erwartungsgemäß rot; danach 23 aktuelle Werkzeugtests grün, keine Skips, vier Bytesfassungen vor/nach gleich. Fester gewöhnlicher Pfad vor Hash/Git, leere dann genaue safe.directory, fsmonitor=false und bereinigte Umgebung. Luna/max Tests; Astra/medium eingefrorener SPEC→QUALITY-Vorreview ohne materiellen Blocker.
- [x] Zwei frische Läufe im neuen Punkt mit je12 Gruppen/42 Erwartungen bestanden; vollständige Ergebnisobjekte nur ohne Label identisch. Zehn Quell-/acht AST-/vier Werkzeugbindungen, HEAD und benannter Raw-XY vor/nach gleich. Leeres stderr, keine Timeouts/Nachprüffehler, Gate auf Originalbytes geschlossen. Astra/medium Ergebnisreview bestätigt unabhängig. Alte Fehlversuche bleiben erhalten.
- [x] Bekannte Zeittyp-/Projektions-/ID-Inline-Befunde unverändert charakterisiert. P4 muss Typ/Serialisierung/Fallback sowie Rechenkontext, Fall-ID, Ergebnisname und Sitzungsreferenz getrennt führen. Keine Produktreparatur, echte HTTP-/Store-/Pydantic-/Engine-/Klientenabnahme daraus ableiten.
- [x] Bericht und Wiederaufnahme konsolidiert; lokaler begrenzter Vorher-/Nachherpunkt, tatsächlicher Abschluss/Umfang durch FINAL-READBACK. Dokumentierter LF/CRLF-Wrapper-Vorhalt vor Teststart korrigiert, kein Referenzretry oder Belegüberschreiben.
- [ ] Nächste unabhängige P3-Vorbereitung: übrige reine Signatur-/Aggregationsanteile mit expliziter Prüfuhr; NumPy/Pillow und volle Workflowwege getrennt. Gesamt-P3, führende Morphic-Quelle/RF-E1/Linux offen. Vollständige P4-Siebenermatrix einschließlich Aurelia/Modul_Templates vor P5; P6–P8/S4.8 separat. Keine normative Template-, Live-, Server- oder Routingänderung.

[Neuer Ergebnisbericht](../../verification/AURELIA_P3_RADI144_KONTEXT_GITSCOPE_2026-10-15.md), Punkt `checkpoints/Aurelia-P3-Radi144-Context-GitScope-20261015-072137Z`. Abschnitt37 und alter Kontextbericht beschreiben den versiegelten früheren Halt; die neue Freigabe und erfolgreiche Referenz ergänzen diese Historie. Kein F:-/Server-/Gesamtprojektbackup.


## 39. P3 – Signatur-/Gruppenreferenz vorbereitet, Betreiberpause vor Originalausführung, 15.10.2026

- [x] Begrenzter Vorherpunkt20Dateien; zehn Quellpins/neunAST-Verträge festgehalten, alte Kontextbelege62/61 nachgerechnet. Luna/max Probe/synthetische Tests; Root Controller und Ein-/Ausführungsgrenzen.
- [x] Astra/medium Entwurf und V1 SPEC→QUALITY: fehlende leere Texteingabe erkannt, sonst kein materieller Blocker. Root ergänzt tatsächlichen Leereingabeaufruf/0.0-Orakel/Beobachtung mit separater Regression und verlustfreien ASCII-JSON-Transport. Aktueller V2-Gesamtgrünlauf23Tests,0Skips,Exit0,vierWerkzeugbytes vor/nach identisch. Historische Zwischenbeleggrenzen offen dokumentiert, nicht als Originalbytes rekonstruiert.
- [ ] V2-Astra-Review auf Betreiberpause unterbrochen; danach erst Originalteilreferenz. Gate geschlossen, keine Originalläufe und kein runs-Verzeichnis. Exakter Fortsetzungspunkt `PAUSE-STATUS.json` / `ROOT-FROZEN-TOOLS-v2.json` / `root-green-v2/ROOT-TEST-RECEIPT.json` im Punkt `checkpoints/Aurelia-P3-Radi144-Signature-20261015-075536Z`.
- [ ] Zwei frische Läufe, vollständiger Ergebnisvergleich, unabhängiger Ergebnisreview/P4-Ableitungen und erfolgreicher Abschlussbericht stehen noch aus. Gesamt-P3/P4-vor-P5 und übrige Modul-/Linuxgates unverändert. Keine Produkt-/Live-/Server-/Routing-/normative Templateänderung.

Lokaler begrenzter Pausepunkt mit Manifest/ZIP-Einzelhashes/CRC/Rücklesen; kein Gesamtprojekt-, F:-, Schlüssel- oder Serverbackup.

## 40. Remote-Workflow – Betreiberfreigabe und nächste Schritte, 15.10.2026

### 40.1 Beschlossene Richtung und unveränderte Grenzen

- [x] Betreiber bestätigt die vorgeschlagene Reihenfolge und entfernt ausgeführte Entwicklung/Prüfung als Ziel. Codex Cloud liefert begrenzte Entwicklungsaufträge, CI erzeugt nachvollziehbare Images/Prüfberichte, Codex Security ergänzt Sicherheitsprüfungen, eine eigene Linux-Testinstanz trägt vollständige Abläufe und Langläufe. PC als Steuerung/Nutzerabnahme; neue lokale Builds/WSL-Reparatur sind kein primärer Weg.
- [x] Eigene Linux-Testinstanz wird vom Betreiber nach Ermittlung der Anforderungen vorbereitet. Bisheriger Rootserver soll später neu initialisiert werden; Betriebssystemwahl erst passend zum nachgewiesenen Stack und Betrieb. Keine sofortige destruktive Maßnahme, keine Bereitstellung und keine erreichbare SSH-Verbindung durch diesen Beschluss.
- [x] RadiFarben-Abnahme vorerst im Hintergrund. Access/VBA bleibt eigene Originalreferenz; Windows-Testweg/Lizenz später klären. Ungeprüfte Funktionen nicht als gleichwertig markieren. Ihre Datenanforderungen bleiben Teil der siebenmoduligen P4-Matrix, offene Annahmen vor P5 ausweisen und entscheiden.
- [x] Kamera, Audio und 3D behalten automatisierte Prüfungen plus echte Browser-/Geräteabnahme. Cloud-Entwicklungsruntime ersetzt weder dauerhaften Abnahmeserver noch Access oder physischen Ton-/Kameranachweis.
- [x] Bestehende Algorithmen, Originalquellen, Immutable-Job-Kontexte, Governors-/Hermes-Routen und Freigaben bleiben erhalten. Cloud-Umzug ist keine Freigabe zur öffentlichen Mehrbenutzerbereitstellung des bisherigen Loopback-Governors oder zu neuen Analyseformeln.

### 40.2 Reihenfolge, Ort und überprüfbare Ergebnisse

| Schritt | Ausführungsort / Arbeit | Erforderlicher Nachweis |
|---|---|---|
| RW-C1 Ausgangspunkt | Vorhandene Quellen und Nachweise aufnehmen, vorhandene Sicherung und offenen P3-Stand binden | Revisionen/Hashes, bekannte Lücken und Wiederaufnahme dokumentiert; keine erfundene Gesamtprojektsicherung |
| RW-C2 Quellenfreigabe | Freigegebene Repositories/Verzeichnisumfänge einschließlich Historie, LFS, Unterprojekte, Katalog-/Assetrechte prüfen | Inhalts-/Übertragungsinventar; keine Klienten-/Secret-/Chatarchivübernahme; synthetische Fixtures und notwendige Ziele bestimmt |
| RW-C3 Cloud-Pilot | Begrenzten freigegebenen RadiWorks-Stand in Codex Cloud vorbereiten | Tatsächlicher Zugang, Laufzeiten, Werkzeuge, Ressourcen, Netzgrenzen, Rücklesen und Kostenrahmen geprüft; Docker-Daemon nicht voraussetzen |
| RW-C4 CI und Security | Isolierte Prüfungen, Images, Abhängigkeiten/Secrets/Container und geeigneter Security-Scan | Quellen-/Konfigurations-/Imagebindungen, Prüfberichte; untrusted PR ohne privilegierte Runner/Produktionsgeheimnisse; Veröffentlichung und Deployment getrennte Rechte |
| RW-C5 Linux-Testziel | Betreiberinstanz inventarisieren, begrenzten SSH-/Administrationsweg, HTTPS/VPN-Zugang, Volumes/Logs/Backup einrichten | Hostidentität, Zuständigkeit, Readiness, Ausgänge, Rechte und Wiederherstellung belegt; Zugriff aus Cloud oder getrennter CI/SSH erst praktisch nachweisen |
| RW-C6 vollständiger Pilot | Dasselbe gebaute Image mit synthetischem Fall: speichern/laden, gewählte Analyse, Persistenz/Restart und Browserabnahme | Reproduzierbarer vollständiger Ablauf; ausdrücklich begrenzter Umfang, keine pauschale Vierkombinationen-/Medien-/Gesamtabnahme |
| RW-C7 P3 fortsetzen | Passende Remote-Laufzeiten für die offenen Modulreferenzen; RadiFarben zurückgestellt sichtbar halten | Bestehende Baselines erhalten, echte Runtime-/Numerik-/Workflowreferenzen und ungeprüfte Grenzen getrennt; kein Abschluss durch bloßes Packaging |
| RW-C8 P4/P5 | Sieben Module mit Aurelia und Module_Templates zusammenführen, zentrale Struktur entscheiden | Last-/Daten-/Rechte-/Archivvertrag und ausdrückliche Betreiberentscheidung; Supabase-Referenz ist keine Vorentscheidung der Ziel-DB |
| RW-C9 Zielstack | Beschlossene Kern-/Template-/Adapterverträge schrittweise umsetzen | Regression, Mandantentrennung, Jobs, Migrationen, Langlauf, Restore und Rückweg geprüft; gleicher Digest plus versionierte Konfiguration/Schemas/Volumevertrag |
| RW-C10 Produktion | Passendes Linux auf gesondert abgenommenem Zielserver, Freigabe und kontrollierte Migration | Zielserver-/Betriebsabnahme, Backups/Erreichbarkeit/Observability, bewusst freigegebene Releases; Testabnahme ersetzt keine Produktionsfreigabe |

RW-C1 ist mit diesem begrenzten Planungsstand nicht als gesamtes Quellen-/Backupinventar abgeschlossen. RW-C2 bis RW-C10 sind noch offen. Arbeitspakete werden im kleinstmöglichen sinnvollen Prüfverbund ausgeführt; bei Fehlern, fehlendem Zugang oder nötiger Betreiberentscheidung an sicherer Grenze halten. Kein kostenpflichtiger Scan oder pauschaler Quellenversand durch das bloße Fortschreiben dieses Plans.

### 40.3 Anforderungen an die vom Betreiber vorzubereitende Linux-Testinstanz

Vor Beschaffung ein messbares Pilotprofil ableiten: verfügbare vCPU/RAM und Reserven für Backend/Builds/Berechnungen, SSD-Kapazität/IOPS für Images/Daten/Logs/Restore, Architektur und exakt unterstützte Laufzeiten, Region/Vertrag, Kostenrahmen und Aufbewahrung. Noch keine feste Dimensionierung oder Linux-Version abgenommen. Vollständige Stacks nur bedarfsgesteuert; keine sieben dauerhaften Vollkopien. Ausgangsbasis Compose auf einem getrennten Testhost; Kubernetes/Redis/GPU nur bei nachgewiesenem Bedarf und gesonderter Entscheidung.

Betriebskriterien: nichtprivilegierte Anwendung, minimale Berechtigungen, kein Produktions-Docker-Socket für PR-Code; unabhängige Testvolumes und neue Testsecrets, dienstbezogene Health-/Readinessprüfungen, Ressourcen-/Loggrenzen und klare Wiederanlaufregeln. Keine offenen DB-/Storage-Verwaltungsports; notwendige HTTPS-/VPN-/SSH-Wege erst nach Netzprüfung freigeben. Reale private Verbindung aus Codex Cloud ist unbekannt; alternativ kontrollierter CI-/SSH-Ausführungsweg. Langläufe müssen nach Schließen von Codex/SSH weiterlaufen und aus Protokollen bewertbar sein. Sicherung außerhalb des Testhosts mit realem Restore; Hostingregion/Aufbewahrung vor sensiblen Inhalten entscheiden.

### 40.4 Aktueller Nachweis und Quellen

Nur lesende Dokumentations-/Zugangsprüfung, keine Cloud-Umgebung veröffentlicht, kein GitHub verbunden, kein Scan/Build/Deployment oder Serverbefehl ausgeführt. Security-Bootstrap am 15.10. meldete Zugriff, aber keine GitHub-Verbindung und nicht vollständig konsistente Workspace-Flags; Usage meldete Kontingent. Daraus folgen weder vollständige Einsatzbereitschaft noch garantierte Kostenfreiheit. Verfügbarkeit vor Nutzung erneut prüfen. Die aktuelle Cloud-Dokumentation trennt neue Umgebungen von Legacy; Fähigkeiten nicht zwischen beiden übertragen.

- OpenAI: https://learn.chatgpt.com/docs/environments/cloud-environments
- Codex Security: https://learn.chatgpt.com/docs/security
- Docker Compose Produktion: https://docs.docker.com/compose/how-tos/production/
- GitHub Images/Herkunft: https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images

Voriger P3-Pausepunkt aus Abschnitt 39 bleibt byteunverändert. V2-Review, Originalsignaturläufe und Ergebnisabnahme sind weiter offen; neue Remote-Prüfwerkzeuge getrennt versionieren, keine Windows-Pfade oder Rechenparität unter Linux voraussetzen. Dieser Nachtrag ist ausschließlich eine Planrevision. Normative Modul_Templates, ausführbare Governors-Strategien, Produktquellen und Liveinstanzen sind nicht geändert.


## 41. RW-C1/C2 – Quelleninventar und begrenzter Remote-Pilotvertrag, 15.10.2026

### 41.1 Geprüfter Umfang und Übertragungsgrenze

- [x] Kanonischer `Radiworks/radiworks_port` und angenommener `runtime/rw-r6-release-20261008` bei allen 200 manifestierten Dateien frisch nach Länge/SHA-256 gleich: 1.812.733 Bytes. Gruppen: 3 Engine-Metadaten, 61 Engine-Quellen einschließlich Fixtures, 75 Testdateien, 61 Webdateien. Pfadbestandteile/Eltern auf Symlinks/Reparse-Punkte geprüft. Manifest-SHA-256 `445ece8f8c826e1391fead34c9a4c9b271e3b13b6d59a7654f66f11ab77b6275` unverändert. Keine Aussage über heutigen Laufzustand der Dauerinstanzen.
- [x] Fünf ausdrücklich erfundene Katalogeinträge und vier Gold-JSON-Dateien mit je 105 Ergebnissen, generierten R0000-Namen und ausschließlich null-URLs geprüft. Goldwerte sind gespeicherte historische Java-Referenzen; kein neuer Java-Lauf, keine komplette Originalparität daraus ableiten. Heuristische Textprüfung findet keine privaten Schlüsselmarker, auffälligen Zugangsschlüsselformen oder geprüften Betreiberkennungen. Dies ist keine umfassende Datenschutz-/Geheimniszertifizierung. Token-/Epoch-/Regex-Treffer sind Programmvariablen; Windows-Pfad ist ein Dokumentationsbeispiel.
- [x] Materielle Git-Grenze erkannt: umschließende Git-Wurzel liegt im Benutzerprofil. Weder diesen Bestand noch dessen Historie/Index/LFS/Submodule an Cloud anbinden. Später ausdrücklich ausgewählte aktuelle Dateien in einem tatsächlich unabhängigen privaten Repository erfassen; bloßer Unterordner ohne eigene geprüfte Git-Wurzel reicht nicht. Zielindex, Remote und fertige Export-Dateimenge vor Verbindung prüfen.
- [ ] Herkunft/Rechte je Python-Port/Fixtures/Webasset klären. LGPL-Text im Elternprojekt und dessen Pi4J-spezifische NOTICE sind keine belegte pauschale Lizenzzuordnung für den Port. Ungeklärte Bestandteile zurückhalten; kein rechtliches Freigabeurteil aus Dateivorhandensein.
- [ ] Reales privates GitHub-Ziel, Eigentümer/Zugriffsberechtigte, Cloud-Verbindung sowie nötige Region/Aufbewahrung/Kostenrahmen konkret prüfen. Erst danach Export; beim Export Quelle erneut binden, nur Allowlist übernehmen und Zielverzeichnis auf exakte Dateimenge und gewöhnliche Pfade prüfen. Rohakzeptanzdatei mit privaten Absolutpfaden ausgeschlossen; abgeleitete bereinigte Provenienz ausdrücklich separat kennzeichnen.

Maschineninventar: [AURELIA_RW_CLOUD_SOURCE_INVENTORY_2026-10-15.json](../../verification/AURELIA_RW_CLOUD_SOURCE_INVENTORY_2026-10-15.json). Es ist ein lokaler Kandidatenbestand, KEINE Übertragungsfreigabe. Runtime-Homes/Fälle/Medien/Schlüssel/Logs, echte Kataloge/Clarke, private Archive, Start5-venvs, upstream Java-Binaries und profilweite Git-Historie bleiben ausgeschlossen. Bestehendes Home und server.log liegen außerhalb der 200-Dateienliste; daher keine rekursive Gesamtkopie. Eingefrorene ältere Manifestmetadaten bleiben erhalten; spätere lokale Audioannahme zeitlich getrennt dokumentieren.

### 41.2 Technischer Pilot und Abnahmefolge

| Schritt | Inhalt | Nachweis/Grenze |
|---|---|---|
| C2a | Herkunft/Rechte, unabhängiges privates Quellziel, bereinigte Provenienz und Übertragungspaket | Aktuelle Hashes, genaue Dateimenge, Index/Remote und Zugriff prüfen; keine alte Git-Historie |
| C3a | Kleinster Original-Pilot mit erfundenem Katalog und reproduzierbarer Analyse | Python >=3.12; genaue Linux-Version und vollständige Dependency-Auflösung/Hashes erst festlegen und remote prüfen. Testkandidaten im Inventar, noch nicht ausgeführt |
| C3b/C4a | CI mit Originalregressionen, JS und sauber getrennten Installations-/Testnetzen | Setup nur erforderliche Paketquellen; Anwendung/Test technisch ohne externen Egress. Seed allein ist keine technische Netzsperre. Docker-Fähigkeit von Codex Cloud nicht voraussetzen; Build in geeigneter CI/Test-VM |
| C4b | Persönliche Heuristik als eigenes CPU-Profil | Vorhandener Lock ausdrücklich Windows CPython3.13, kein Linux-Nachweis. Linux-Resolver/Lock, numerische Vergleichbarkeit, große synthetische Kataloge, Laufzeit/Fortschritt/Abbruch separat prüfen; keine Formeln ersetzen |
| C4c | Browser- und Medienprüfungen | Vorhandene Playwright-Hilfe nur Kandidat: feste Chrome-/headed-Annahme und Pfade portieren, separat hashen/reviewen. Browser nicht in der neuen Cloud-Umgebung voraussetzen; echte Audio-/Kamera-/3D-Abnahme zusätzlich |
| C5/C6 | Vollständiger RadiWorks-Lebenszyklus auf isoliertem Testhost | Vier Kombinationen Original/persönlich × seeded/stochastisch, isolierte Fälle/Homes/Zufallsfolgen; eigene synthetische Schlüssel, keine vorhandenen Betreiber-Schlüssel übertragen. Kontext, Abbruch, Parallelität, Wiederanlauf, Historie und Restore prüfen |

Python-Kern verlangt FastAPI/Uvicorn/Websockets/httpx/cryptography mit offenen Versionsuntergrenzen; damit ist der Stand noch nicht reproduzierbar unter Linux installiert. Die persönliche CPU-Abhängigkeit getrennt halten; kein GPU-Zwang. Gespeicherte Einstellungen schreiben beim Zugriff unter das Home; daher separate beschreibbare Laufzeitvolumes. Ein Home zunächst genau einer Instanz zuordnen; Lease-/Linuxverhalten gesondert prüfen. Cloud-Aufgaben und SSH-Sitzungen sind keine Dauerjob-Supervisoren.

**Netz-/Identitätsgrenze:** Vorhandener Scope unterstützt nur `local`; erzwungener Aurelia-Scope wird abgewiesen. Host/Origin sind auf lokale Adressen begrenzt und stellen keine Benutzeranmeldung dar. Route-spezifische Autorisierung ist hier nicht vollständig geprüft. Initialer Testhost deshalb nur Single-Operator: Dienst auf Host-Loopback veröffentlichen, Zugriff über eigenen authentifizierten SSH-Tunnel, Browseradresse localhost. Interner Containerbind allein genügt nicht. Öffentliche Namen, Mehrbenutzer-/Mandantenbetrieb und Reverse-Proxy-Vertragsänderungen sind getrennte spätere Arbeit. Andere lokale Hostnutzer/Prozesse liegen innerhalb dieser Vertrauensgrenze; SSH ersetzt keine Anwendungsidentität. Tatsächliche IPv4-/IPv6-Bindings, Tunnel, Host/Origin und Browserfunktion vor Betrieb nachweisen. Kein Docker-Socket, privilegierter Appcontainer oder Administrator-/Produktionsgeheimnis im App-Prozess.

Stochastik kann beim ersten Zug ohne Webcamwerte `www.random.org:443` kontaktieren; Fehler führen zum OS-Zufall. Kein belegter globaler Egress-Aus-Schalter im Quellstand. Initiale Tests deshalb technische Netzsperre; spätere gezielte Quellenprüfung mit ausdrücklich erlaubtem Ziel und dokumentierter tatsächlicher Quelle. Keine Entsperrung von Wiederherstellungs-/CopyGuard-Gates durch diese Planung. Factory-/Importkonstruktion in main.py und Linux-Lease noch prüfen.

### 41.3 Anforderungen an die neue Linux-Testinstanz – Planung, kein gemessener Bedarf

| Profil | Vorläufige Ausstattung | Nutzung |
|---|---|---|
| Einzelner RadiWorks-Pilot | 4 vCPU, 8 GB RAM, 80 GB SSD/NVMe | CPU-Profil und Browser/Builds zunächst begrenzt nacheinander; reale Spitzen erst messen |
| Empfohlener Ausbau für die folgende Modulprüfung | 8 vCPU, 16 GB RAM, 160 GB SSD/NVMe | Ein vollständiger Lovable-kompatibler Backendstack plus begrenzte Builds/Browser/CPU-Jobs; Projektstacks zunächst nacheinander |
| Mehrere vollständige Backends und Builds gleichzeitig | Noch nicht dimensioniert | Erst Messung; ggf. 32 GB RAM/größerer Speicher oder getrennte kurzlebige Runner. Keine gleichzeitige Siebenmodule-Garantie aus Profil 2 |

Diese Zahlen sind eigene Startschätzungen, keine Anbieteranforderung oder Bestellfreigabe. Supabase selbst nennt für alle Komponenten 4 GB/2 Kerne/40 GB SSD als Minimum und 8 GB+/4 Kerne+/80 GB+ SSD als Empfehlung; unsere Module, Browser, CPU-Pakete, Images und Backups kommen hinzu. Siehe [Supabase-Systemanforderungen](https://supabase.com/docs/guides/self-hosting/docker). Backupziel unabhängig vom Testhost; Aufbewahrung, Restoreumfang und Speicherwachstum anhand echter Testartefakte festlegen, kein Snapshot als alleiniger Restorebeleg.

64-bit amd64 bevorzugen, Architekturwechsel numerisch gesondert prüfen. Debian 13 und Ubuntu 24.04 LTS werden derzeit offiziell von Docker unterstützt; beide sind Kandidaten, finale Wahl nach Paket-/CPU-/Betriebsprüfung, keine Diagnose des früheren LUKS-Fehlers. Siehe [Debian](https://docs.docker.com/engine/install/debian/), [Ubuntu](https://docs.docker.com/engine/install/ubuntu/). Docker Engine/Compose aus geprüftem Repository und gebundenen Versionen; keine blinde Installationspipeline. Provider-Firewall sowie Docker-Portfreigaben tatsächlich prüfen, ufw allein nicht als Abschottungsnachweis werten. Keine administrativen DB-/Studioports öffentlich. Adminzugang, Projektvolumes, Ressourcenbegrenzung, Healthchecks, Logrotation, Wiederanlauf und externe Backups vor vollständigem Pilotbetrieb nachweisen.

### 41.4 Status, Prüfung und exakter Fortsetzungspunkt

RW-C1 ist NUR für diesen RadiWorks-Quellvergleich belegt; Gesamtprojekt-/Governors-/Serverbackup weiterhin nicht erledigt. RW-C2 bleibt bis Rechte-/Ziel-/Exportprüfung offen. C3–C10 nicht gestartet. Nächster Schritt: enge Herkunfts-/Lizenzzuordnung und konkretes privates Pilotziel klären, danach überprüfbares bereinigtes Quellpaket und remote ausführbare Pilotdefinition. Keine Pakete oder Tests lokal gestartet, kein Cloud-/GitHub-Connect, Scan, Build, Deployment oder Serverbefehl. Dauerinstanzen/Algorithmen/Routing/normative Templates unverändert. Tatsächliche Helfer: Luna/max Quellen-/Abhängigkeitsprüfung, Astra/medium unabhängige Übertragungs-/Zugangsgrenzenprüfung; kein aktives Desktopmodell daraus ableiten.

Begrenzter Vorher-/Nachherpunkt `checkpoints/Aurelia-RW-Cloud-Inventar-20261015-185709Z`; Sicherungsabschluss erst durch READBACK.json. Erste in-memory Inventarvalidierung stoppte vor Schreiboperationen wegen der falschen Annahme leerer URL-Strings; tatsächliche null-Werte der vier Goldfixtures gezielt geprüft, Inventar korrigiert, Originalbytes unverändert. Gesamte P3-Referenzen und V2-Review bleiben offen; P4 Siebenermatrix mit Aurelia/Modul_Templates vor P5-Datenstrukturentscheidung, P6–P8/S4.8 getrennt.


## 42. RW – Bedienung, Listen und getrennte Ablaufarten freigegeben, 15.10.2026

Betreiber stimmt der Reihenfolge des Quellenreviews zu und wünscht zusätzlich die optionale vollständige Ausgabe über105 Ergebnisse, unter vorrangigem Erhalt des stabilen Standes. Dies ist eine Entwicklungsfreigabe, kein Nachweis bereits umgesetzter Funktionen, keine Cloud-Übertragungs-, Kosten-, Liveausrollungs- oder Integrationsfreigabe. Nullrisiko kann nicht zugesichert werden; Originalbaseline bleibt separat rücksetzbar und wird durch Regressionen geprüft.

### 42.1 Verbindliche Reihenfolge

- [ ] Zuerst Quellen-/Rechte-/Zielprüfung aus41.1, unabhängige private Git-Wurzel, minimale Remote-Entwicklungsumgebung mit gebundener Quelle und Dependency-Auflösung. Keine Produktbuilds/-tests auf dem Windows-PC. Eine vorbereitete Linux-Testinstanz wird jetzt sinnvoll; Planungs-/Quellfreigabearbeit kann vorher weitergehen. Vollständiger RadiWorks-Pilot erst nach diesen Ergänzungen; die technische Testbasis wird schon während ihrer Entwicklung benötigt.
- [ ] RW-U1: getrennte Vollkatalogsuche und Ergebnissuche über die ganze gespeicherte Sitzung; Filterzählung/Seitenzahl und Rücksetzen anzeigen. Kein Katalogtreffer als gemessenen Analysewert ausgeben. Stabile Ratenidentität auch bei Namensduplikaten, Sortierung und Paging erhalten.
- [ ] RW-U2: Nur Ansichten sortieren: NR ursprünglicher Index; EW/GV/recurringGeneralVitality/recurring numerisch; Rate alphabetisch; Level numerisch; Potenz nach Familie und Zahlenanteil ohne behauptete gemeinsame Stärke. Fehlende Messungen von gemessenen Werten unterscheiden. HIT bleibt Marker der ursprünglichen21er-GV-Gruppe; kein neuer Messwert. Original-21er-Runden dürfen nicht an umsortierte Bildschirmindizes geraten. Persönliche Scores bleiben getrennt von Original-EW/GV.
- [ ] RW-U3: gemeinsames Buttonschema für startbereit/angefordert/läuft/Stopp angefordert/nicht verfügbar/Fehler oder unklaren Annahmestatus. Voraussetzungen sichtbar am Bedienelement erläutern, nicht nur Tooltip/Farbe. Tastaturbedienung, ausreichende Lesbarkeit und bestehende serverseitige Zulassungen erhalten. Kein Wiederholungsstart bei unbestätigtem Auftrag; Statusabgleich getrennt anbieten.
- [ ] RW-U4: Resonated-Rates-Liste mit kurzer Überschrift/kompakten Hilfen, nutzbarer Mindesthöhe und vollständiger zugänglicher Ansicht. Vorhandene Kurzliste schneidet nach8 Einträgen ab. Anzeige leeren bleibt getrennt von Verlauf/Belegen löschen; keine Historienlöschung als Layoutänderung.
- [ ] RW-U5: zusätzliche bereits bewertete EW-Kandidaten ohne neue Zufallsziehungen sichern/anzeigen. Original105 mitsamt Potenz/Level/Fall-GV/Entropiezustand unverändert. Zusätzliche Kandidaten besitzen nicht automatisch Potenz/Level/GV oder bestehende21er-Aktionen. Tatsächlich bewertete Teilmenge kenntlich machen, nicht als vollständigen Katalog ausgeben.
- [ ] RW-E105: optionaler vollständiger Erweiterungsmodus nach42.2; getrennt versionieren und abnehmen, niemals bloß globale RESULT_LIMIT-Konstante überschreiben. Danach gemeinsame Bedienabnahme.
- [ ] RW-L1: ausdrücklich gestartete feste Listenfolge. Reihenfolge, Kontext, Quelle und Medien tatsächlich unveränderlich aufnehmen, genau ein eigener Broadcast gleichzeitig. Sendedauer/Pause in Sekunden; Wiederholungswert bezeichnet Gesamtdurchläufe. Emitter-repeat/delay nicht dafür umdeuten. DynamicAdjustments zunächst ausdrücklich aus. Stop/Frist betrifft nur den eigenen Lauf; Belege erhalten. Original-Auto und neuer Steuerlauf serverseitig gegen gleichzeitigen Start sperren.
- [ ] RW-L2: getrennte Analyserundenschleife, keine Änderung der Original-Auto-GV-Heuristik. Pro abgeschlossener Analyse neue Sitzung, Ergebnisumfang/zu sendende Auswahl vorab anzeigen. Neue Runde erst nach atomar belegtem Ende aller eigenen aktiven/wartenden Jobs und möglicher Kindjobs. Laufzeitgrenze/manueller Stop entwertet auch späte Analyseergebnisse. Leeres Ergebnis/CopyGuard-/Schlüssel-/Persistenzfehler mit Ursache anhalten, keine schnelle Endlosschleife. Neustart zunächst unterbrochen, keine automatische Wiederholung unklarer Sendungen; explizite Wiederaufnahme separat nachweisen.
- [ ] Remote-Regressionspaket mit vier Verfahrens-/Zufallskombinationen, ursprünglichen Goldfixtures, Identität nach Suche/Sortierung/Seitenwechsel, konkurrierenden Starts, Stop/Frist in Analyse/Sendung/Pause, Netzverlust, Uhrsprung, Absturz und Langlauf. Komponentenvertrag/Modul_Template-Verweise abgleichen, normative Änderung nur innerhalb bestehender Gates. Nutzerabnahme vor Liveübernahme; Sicherung/Rollback und anschließendes aktualisiertes Start5 separat prüfen. Vollständiger Cloud-/CI-/Linux-Pilot und P3/P4/P5 folgen weiterhin nach geltenden Phasengrenzen.

### 42.2 Optionaler vollständiger Erweiterungsmodus – ausdrücklich gewünscht

Originalanalyse sortiert und kürzt auf105, danach erfolgen Potenz-/Level-Ziehungen und anschließend API-seitig der Fall-GV. Mehr vollständige Ergebnisse können daher nachfolgende Zufallsziehungen und Fall-GV verändern. Gewünschte Erweiterung ist zulässig, eine Behauptung originalidentischer Werte bei geändertem Umfang nicht. Keine zusätzliche Formel/semantische KI oder algorithmischer Vollkatalogscan genehmigt.

Standard bleibt105. Zusätzliche klare Auswahl „Ergebnisumfang: Standard / Erweitert“ mit serverseitig validiertem Umfang und technischer Obergrenze, tatsächlichem Kandidatenumfang und Aufwandhinweis. Konkrete Grenzwerte im engen Implementierungsvertrag anhand Remote-Messung festlegen; nicht pauschal die persönliche4096-Raten-Grenze oder die Original-Kandidatenauswahl aufheben. Erweiterung verwendet bestehenden Rechenweg in eigener versionierter Auftrags-/Ausgabevariante. Umfang, Profilversion, Katalog, Fallkontext, Verfahren und Zufallsquelle in unveränderlichem Auftrag festhalten. Laufende und alte Aufträge bleiben unverändert.

Nicht vorhandene Kandidaten erfinden und nicht behaupten, jede Katalograte sei analysiert. Persönlicher Weg hat eigene Score-/Ratenverträge. Bisheriger gebundener Auto-Modus akzeptiert nur Originalverfahren; erweiterte Ergebnisse nicht still über einen alten Auto-/GV-/Broadcastvertrag routen. Neue Herkunfts-/Ratenzuordnungen vor Freischaltung mit den jeweiligen Aktionen prüfen; nicht unterstützte Aktionen sichtbar begründen.

Abnahme: Standard105 muss bei gleichen Eingaben/Seeds weiterhin vollständige Originalergebnisse, Entropie-Endzustand und anschließenden Fall-GV reproduzieren. Erweiterter Weg erhält eigene reproduzierbare Referenzen, stochastische Quellen-/Recoveryprüfung sowie Last-/Abbruch-/Historiennachweise. Ansichtssortierung darf keine neuen Ziehungen oder veränderte Auswahl erzeugen. Bedienung von Standard und Erweiterung muss eindeutig sein. Wenn eine Voraussetzung scheitert, Erweiterung gesperrt lassen, Standard weiterhin nutzbar; keine Zusicherung absoluter Fehlerfreiheit.

### 42.3 Infrastruktur und nächster Schritt

Neue getrennte Testinstanz jetzt vorbereitbar, mit vorläufig empfohlenen8vCPU/16GBRAM/160GBSSD oder NVMe; eine vollständige Lovable-Backendumgebung und CPU-/Browserjobs zunächst begrenzt, weitere Projektstacks nacheinander. Kein gemessener Gesamtprojektbedarf/keine Parallelitätsgarantie. Ubuntu24.04LTS amd64 als bevorzugte Testbasis, Debian13 bleibt geeigneter Docker-Kandidat; Paket-/numerische Linuxeignung wird erst im Pilot belegt, Produktions-OS damit nicht festgelegt. Tatsächliche Betriebssysteminstallation/Serverbereitstellung noch nicht erfolgt oder nachgewiesen. EU-Hosting bevorzugt; tatsächliche Region/Rollen/Backups dokumentieren. Zunächst Provider-Konsole und separater SSH-Zugang, keine öffentlichen App-/DB-/Studioports, Loopback/Tunnel-Plan aus41.2 vor Aktivierung prüfen.

Benötigt werden nach Bereitstellung Host/IP, installierte Distribution und ein nichtgeheimer Wartungsbenutzername; Schlüsselzugang separat vorbereiten und prüfen, keine Passwörter/privaten Schlüssel im Chat. Kein Zugriff auf den alten Rootserver und keine LUKS-/Neuinitialisierungsaktion. Unabhängiges privates Pilot-Repository und Quellenrechte bleiben Voraussetzungen einer tatsächlichen Cloudanbindung. Bis dahin Herkunfts-/Transferfreigabe und konkrete Teilentwürfe ausarbeiten, kein Test- oder Umsetzungsabschluss behaupten.

Dieser Nachtrag hält Betreiberfreigabe und Grenzen fest, kein vollständiger ausführbarer Implementierungsplan. Je Teilpaket erst quellengebundenen technischen Plan erstellen, dann remote implementieren und prüfen; schon erteilte Freigaben nicht erneut pauschal erfragen. Voriger Review tatsächlich Luna/max (Listen-/Algorithmusquellen) und Astra/medium (Ablauf-/Erweiterungsgrenzen); für diese Dokumentationsfortschreibung keine neuen Helfer. Kein aktives Desktopmodell geprüft. Lokaler begrenzter Vorher-/Nachherpunkt gemäß READBACK.json, kein Gesamt-/F:-/Serverbackup.

## 43. C3b – Nutzerimport, offene Anforderungen und Security-Status, 16.10.2026

Dieser Stand aktualisiert die historischen Offenangaben aus40–42; er hebt keine Freigabegrenzen auf. Private Quellbaseline und getrennte Linux-Testbasis sind inzwischen eingerichtet. Die Python-Suite hat878 bestandene/19 übersprungene Tests; die neue netzlose JavaScript-Probe100 bestandene Tests ohne Skips/Fehler sowie55 bestandene Syntaxprüfungen. Alle200 Produktdateien weiterhin manifestgleich. Das ist keine vollständige Viermodi-, Medien-, Langlauf- oder Integrationsabnahme.

### 43.1 TXT-/XLSX-Nutzerimport und CopyGuard

TXT-Nutzerimport wurde bereits am05.10. nach Klärung des modulbezogenen Daten-/Rechtevertrags vorgemerkt; XLSX/XLS sind seit09.10. im gemeinsamen Aurelia-Importkonzept enthalten. Der aktuelle RadiWorks-Kern liest vorhandene TXT-Dateien (Zeile NAME oder NAME plus TAB plus URL); ein nutzerbedienbarer TXT-/XLSX-Katalogupload mit Vorschau und kontrollierter Veröffentlichung ist im geprüften Pilotquellstand nicht implementiert. Vorhandenes Lesen/Indizieren von Dateien ist keine Importfreigabe.

Neues zusammengeführtes Arbeitspaket **RW-IMP1 / AURELIA-IMP-CATALOG**: Nutzer kann eigene Ratenkataloge inTXT undXLSX einbringen. Gemeinsamer Importablauf, jeweils ausdrücklich definierter RadiWorks-/Moduladapter; kein universelles Ratenformat und kein direkter Nutzerzugriff auf DB-Tabellen. Der frühe RadiWorks-Pilot darf den späteren zentralen Speicher nicht vorwegnehmen. Vor Implementierung mindestens Katalogeigentümer, Nutzer-/Tenantrechte, Zielablage und versionierte Veröffentlichung verbindlich klären; P4/P5-Gesamtentscheidung bleibt separat.

Vorgesehene Abnahmekette: begrenzter Upload → Format-/Zeichensatz-/Strukturprüfung → Spalten-/Feldzuordnung und Vorschau → strukturelle Fehler, Duplikate und CopyGuard-Treffer sichtbar prüfen → ausdrücklich bestätigte, atomare Katalogrevision → Analyse/Broadcast weiter mit bestehender Textprüfung. Kein stilles Überschreiben oder Umbenennen von Raten; Quellhash, Originaldatei, Parser-/Regelversion, Zeilen-/Zellbezug, Freigabe und Rückweg nachvollziehbar. Bestehende/laufende Aufträge behalten ihre eingefrorene Katalogrevision. Fehler bewirken keine halbe Veröffentlichung.

TXT-Encoding, erlaubte Spalten und das erste XLSX-Zuordnungstemplate sind vor Umsetzung explizit zu spezifizieren, nicht aus beliebigen Dateien zu erraten. Führende Nullen, Signaturen und Dezimaldarstellungen erhalten; keine Formeln, Makros, externen Verknüpfungen oder importierten Anweisungen ausführen. Ressourcen-/Archivgrenzen und sichere Ausgabe/Export prüfen. CopyGuard prüft sichtbare Texte und meldet Regelbefunde; er zertifiziert weder fachliche Richtigkeit noch Lizenzrechte oder Wirkung und darf Signaturen/Algorithmen nicht still verändern. Ein Importbefund darf nicht durch den angefragten Admin-Testmodus allgemein freigegeben werden.

Priorität: nach tragfähiger Pilot-/Fehlerprüfung und dem benötigten Katalog-/Rechtevertrag gemeinsam mit RW-U1/U2 konkretisieren; Umsetzung vor Freigabe der neuen Listensteuerungen, sofern deren Eingabevertrag betroffen ist. Keine zusätzliche Importimplementierung oder neue Datenbankentscheidung in dieser Fortschreibung. Verweise: [bisheriger TXT-Vorbehalt](../../verification/RADIWORKS_VEKTOR_DATENVERTRAG_RESTPLAN_2026-10-05.md), [gemeinsames Importkonzept](../../AURELIA_ADMIN_MEDIEN_IMPORT_VORMERKUNG_2026-10-09.md).

### 43.2 Konsolidierter offener Umfang und Reihenfolge

| Reihenfolge | Anforderung / verbleibende Arbeit | Nachweisgrenze |
|---|---|---|
| 1 – Pilotbasis abschließen | Gespeicherte Sitzungs-Kataloganzeige auf privater Vorschau korrigiert/abgenommen; tatsächliche Codex-Cloud-/CI-/Security-Anbindung, gebundene Prüfungen und sichere Releasewege. | Linux-SSH-Pilot und bestandene Tests sind belegt; Cloud-Anbindung/automatische CI/Security-Scan noch nicht. |
| 2 – Funktion und Laufzeit | Persönliche CPU-/Numerikparität, große Kataloge mit Fortschritt/Abbruch; beide Verfahren in seeded/stochastisch samt dauerhafter Zufallsquelle, Recovery und verständlicher Fehlermeldung. | Original-Seed42-Browserprobe belegt; vollständige Vierkombinationenabnahme offen. Bestehende Formeln und Schutzsperren erhalten. |
| 3 – CopyGuard | Erklärung/konkrete Regelursache und Auto-Abschaltgrund; angefragter serverseitiger Admin-Entwicklungstestmodus mit Isolation, Ablauf/Widerruf und Regressionen. | Lexikon-DE/EN ist vorhanden; kein LLM-Sicherheitsurteil, kein bereits aktivierter allgemeiner Bypass. [RW-C1–C3](../../verification/RADIWORKS_COPYGUARD_ADMIN_TEST_PLAN_2026-10-11.md). |
| 4 – Bedienung und Kataloge | Vollkatalog-/gesamte Ergebnissuche, stabile Sortierung, verständliche Buttonzustände/Voraussetzungen und nutzbare Resonanzliste; TXT/XLSX-Importvertrag aus43.1. | RW-U1–U4 aus42.1 noch nicht umgesetzt; Ansicht/Identität/GV-21er-Zuordnung und Historie erhalten. |
| 5 – Ergebnisumfang | Weitere schon bewertete Kandidaten; optional vollständige Ergebnisse über105 in eigener versionierter Variante. | RW-U5/RW-E105; Standardalgorithmus/Entropiefolge nicht durch globale Limitänderung ersetzen. |
| 6 – Ablaufsteuerung | Feste manuelle Ratenliste mit Sendedauer/Pause/Gesamtdurchläufen; getrennte Analyserundenschleife mit Laufzeitlimit/manuellem Stop. | RW-L1/L2; ursprüngliches Auto-Verhalten bleibt eigenständig. Fehler, unklare Auftragsannahme und Restart nicht still übergehen. |
| 7 – Medien und Betrieb | Bereits vorhandene Einzelton-/Solfeggio-/Rosa-Rauschen-/Phi-Fibonacci-Profile und bis5 Fallbildlayer remote/browserseitig abnehmen; Kamera/Quellenwechsel gesondert; Parallelität, Absturz, Langlauf, Neustart und Off-Host-Restore. | Frühere Windows-Hör-/Bedienbestätigungen bleiben erhalten; neue Linux-/Clientabnahme nicht daraus ableiten. Zwei verständlich erklärte Auswahlachsen und zwei explizite Zufallsmodi erhalten. |
| 8 – Abnahme und Auslieferung | Nutzerabnahme, versionsgebundener Quell-/Adapter-/Modul_Templates-Abgleich, gesicherter Dauerinstanz-Rollout, danach geprüftes aktualisiertes Start5. | Kein neues Start5 und keine Übernahme der Pilotänderungen durch diese Fortschreibung. |
| 9 – übrige Module / P3 | Radi144-Signatur-/Gruppenreferenz und offene Original-/Linuxreferenzen für RadiMorphic, Copen/Bohm/Thom; RadiFarben-RMF-Höchstversion als versionierte, weiter aktualisierbare Originalreferenz, Abnahme zunächst im Hintergrund. Thom-3D-/Import-/Oberflächenweg gesondert. | Quell-/Exportaufnahme und vollständige Workflow-/Runtimeabnahme unterscheiden; keine Klientenmigration oder Algorithmusersetzung. |
| 10 – P4/P5 | Siebenmodulvergleich mit Aurelia/Modul_Templates, danach Betreiberentscheidung zur zentralen Datenstruktur, Rechte/Identitäten und Betrieb. | Keine Modul-Datenbankinseln oder Ziel-DB allein aus der aktuellen Referenzlaufzeit festlegen. |
| 11 – gemeinsame Aurelia-Fähigkeiten | Administration/Therapeuten/Abo/Module/Status/Ressourcen/Services; mandantensichere, pro Klient modulübergreifende Archive/Berichte/Trends/Favoriten/Zwischenablagen/Templates/Harmonisierung/Trigger/Echtzeit; systemweiter Generator/Frequenzreihen; originale Medien und verlustfreie Layer-/Audioverwaltung; 2D/3D-Adminwerkzeug; kontrollierter PDF/OCR-/XLSX/XLS-/JSON-Import/Export. | Anforderungen aus den verlinkten Domänen-/Medien-/Trendkonzepten, nicht bereits fertige Plattformfunktionen. Benachrichtigungen benötigen später eigene Regeln/Zustellung/Rechte; keine Mail jetzt senden. |

Zurückgestellt/unverändert: Ego Cleaner bleibt ausgeschlossen/vorbereitet; Windows-Komfortinstaller, zusätzliche CUDA-/Kozyrev-/Hardwareanbindungen nicht automatisch aktivieren. Optionaler Umfang und endgültige zentrale Datenbankstruktur werden getrennt entschieden. Normative Modul_Templates und Produktalgorithmen hier unverändert. Einzelheiten der Langzeit-/Modulreferenzen bleiben an die jeweiligen Belege gebunden; diese Tabelle behauptet keinen Vollabschluss durch Dokumentation.

### 43.3 Tatsächlicher Codex-Security-Status

Reine Statusprüfung16.10.: Zugang zur Security-App erlaubt, aber `githubConnected=false`, keine Connector-IDs; RadiWorks-Umgebungssuche ohne Treffer. Scan-Historie antwortet403 `no_github_connection`; damit ist kein laufender/erfolgreicher RadiWorks-Scan belegt. `isEligibleWorkspace=false` als weiteres offenes Setupmerkmal erfasst, keine ungeprüfte Lizenz-/Berechtigungsursache daraus ableiten. GitHub-CLI-Anmeldung/privates Repository ist davon unabhängig. Security-App geöffnet; keine Verbindung, Berechtigung, Überwachung oder Scan verändert/gestartet. Nächster Setupschritt über die App: GitHub-Ziel gezielt verbinden und Zugriff auf genau das private Pilotrepository prüfen; erst danach konkreten Scanumfang/Version/Kosten und Ergebnis nachweisen. [Bereinigter Statusbeleg](../../verification/AURELIA_RW_SECURITY_IMPORT_STATUS_2026-10-16.json).

Sitzungsbefund: Beide synthetischen Sitzungen besitzen gespeicherte Ergebnisse sowie passende Draft-IDs; beide Drafts enthalten denselben ursprünglichen Katalogselektor. `view_session` gibt diesen nicht zurück, `stepSession` und `analysis.external` setzen die lokale Kataloganzeige ausdrücklich zurück. Damit ist eine Übergabelücke nachgewiesen, kein Verlust der beiden Testanalysen oder ihrer verknüpften Katalogzuordnung. Korrektur später aus gebundener, autorisierter Herkunft; niemals aus der gerade sichtbaren neuen Katalogauswahl raten. [JS-Nachweis](../../verification/AURELIA_RW_C3B_JAVASCRIPT_2026-10-16.json). Dokumentensicherung vor Änderungen; keine Produktdatei geändert, keine neuen Helfer eingesetzt.


### 43.4 Fortschritt16.10. – gebundene Sitzungsherkunft

Minimaler API-/UI-Fix im getrennten Pilotzweig: Katalog nur aus exakt zugeordnetem, im aktuellen Scope lesbarem Draft mit passender Sitzungs-ID, Revision, Lauf-ID und eingefrorenem Kontext. Fehlende/inkonsistente Herkunft bleibt unbelegt; unlesbare optionale Herkunft verhindert das Ergebnisladen nicht. Kein Raten aus neuer UI-Auswahl, keine Migration oder Schreiboperation beim Sitzungslesen. Fallladen reicht bestehende Draft-ID ebenfalls weiter.

19 neue Regressionen, insgesamt897 Python bestanden/19 übersprungen;100 JS-Tests und55 Syntaxprüfungen grün. Reale private Browserprobe: Fallladen und beide Sitzungsrichtungen zeigen historischen Katalog; Fall-/Draftdateien erhalten. Kaltes synthetisches Archiv, hashgleiche Kopie, getrennte Kandidatenlaufzeit und alte Vorschau als Rückfallstand. Luna-Vertragsprüfung und Astra-Nachreview ohne blockierenden Befund; Grenzen/Fehlversuche im [Abschlussbeleg](../../verification/AURELIA_RW_SESSION_CATALOG_COMPLETION_2026-10-16.json). Keine Windows-/Start5-/normative Templateübernahme.

Security-App zeigt fehlende GitHub-Verbindung; Betreiber um gezielte Verbindung zum privaten Pilotrepository gebeten. Kein Scan gestartet. Als Nächstes Cloud-/CI-Vertrag und versionsgebundener Security-Scan nach tatsächlich vorhandenem Zugang, persönliche CPU-/Numerik- und Viermodiabnahme ohne Ersatz der Formeln. Importvertrag und sämtliche übrigen Punkte aus43.1/43.2 bleiben offen.
