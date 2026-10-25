# Aurelia Referenzprüfung für Copen Bohm und Thom

Stand: 09.10.2026. Ergänzung zum [gebundenen Modulbestand](AURELIA_COPEN_BOHM_THOM_BESTAND_2026-10-09.md). Die lokalen Rechenproben, ausgewählten Exportbezüge und begrenzten synthetischen UI-Lebenszyklen sind geprüft. Vollständige Funktionsabnahme, aktive Rechteprüfung und Entscheidung über die zentrale Datenstruktur bleiben offen. Bestehende Produktquellen und Algorithmen wurden nicht geändert.

## 1. Phasen und aktuelle Ergebnisse

| Phase | Ergebnis | Noch erforderlich |

|---|---|---|

| Q1 Quellen und Exporte binden | Explorer `c69d5aa224018b0484efd90ae456a10aecc78a77`; Thom `18e6c12c238985da698f9a46743d893b30d61ba7`. Quellen und beide ZIPs hashgeprüft. | Veröffentlichten Anwendungen und aktiven DB-/Storage-Ständen ihre konkrete Version zuordnen. |

| Q2 Datenbezüge untersuchen | 20 ausgewählte Beziehungen geprüft: 16 aus Quell-FKs, vier fachliche Explorer-Bezüge. Fehlende V2-Eltern und besitzverschiedene Verknüpfungen eingegrenzt. | Ursache, legitime Delegation, wirksame Nutzerrechte und Exportvollständigkeit klären; aktive Struktur/Policies inzwischen lesend erfasst. |

| Q3 Rechenreferenzen | Thom-Kern, gemeinsame Copen-Funktion und separater V2-Zahlenblock geprüft. Vollständiger Bohm-Klientenrechenweg mit kontrollierter Hardware-Testantwort; Collector separat mit künstlichen Zeit-/Netzantworten geprüft. | Reale Browser-/Hardwarepfade, Eingabevalidierung und UI-/Archiv-Lebenszyklen isoliert prüfen. |

| Q4 Spezialoberflächen und Laufzeiten | Isolierte React-Browserproben: fünf Bohm-Fälle, vier Copen-Fälle sowie Thom-Scan-Lebenszyklus mit drei synthetischen Punkten; ergänzt um drei Copen-Vorlagenfälle und zwei Bohm-Archivfälle. Ergänzt um fünf Thom-Parallel-Lebenszyklen je React-Build, acht kontrollierte Fortsetzungsfälle, Feldachsen-/Nachtestprobe und zwei synthetische GLBs mit Matrixbeobachtung. Ergebnislücke und 3D-Abweichungen bestätigt. | Unabhängiger synthetischer Dreiecksvergleich und sieben Service-/Archivfälle ergänzt; fachliche Oberflächenabnahme, vollständiger Viewer, reale Modell-/Landmarkenkompatibilität, aktive Worker/Realtime und echte Persistenz weiter offen. |

| Q5 Gemeinsame Datenhaltung | Zusätzliche Anforderungen an Eigentümer, Ersteller, unveränderliche Auftragskontexte und 3D-Herkunft erfasst. | Mit allen Modulmatrizen konsolidieren und danach Strukturentscheidung mit dem Betreiber. |

Q2 und Q3 sind begrenzte Prüfungen. Sie belegen weder vollständige Mandantentrennung noch Integrationsreife. RadiWorks R6, Start5, Dauerinstanzen, Modul_Templates und Server wurden in diesem Arbeitsschritt nicht verändert.

## 2. Tatsächlich ausgeführte Rechenproben

| Gegenstand | Eingaben und Ausführung | Ergebnis und Grenze |

|---|---|---|

| Thom `ThomVectorEngine` | Drei erfundene Personen, derselbe Zustandsvektor, ausdrücklich festgelegte Entropiewerte. Unveränderte numerische Engine in eingeschränkter lokaler VM. | Gleiche Eingaben liefern gleiche numerische Ergebnisse; drei unterschiedliche Dimensionssätze; geänderte Entropie verändert Dimensionen. Fünf Dimensionen endlich und im vorgesehenen Bereich; Frequenzen positiv/endlich. IDs und Zeitstempel sind von der Gleichheitsprüfung ausgenommen. |

| Thom Bildbezug | Derselbe synthetische Kontext mit/ohne Bild-Platzhalter. | Kein numerischer Unterschied in diesem Kernpfad. Keine tatsächliche Bildauswertung nachgewiesen. |

| Gemeinsame Copen-Funktion | Drei künstliche Bezeichnungen; Wiederholung; Bildsignatur an/aus; adaptive Fibonacci-Grenzen 4/5, 10/11 und 20/21 Zeichen; Leerwortvalidierung. | Wiederholung gleich; drei verschiedene Raten; deaktivierte Bildsignatur ohne Einfluss, aktivierte im Test mit Einfluss; Grenzpaare wie im Quelltext; Validator lehnt Leerwort ab. **Nicht der separate Inline-Algorithmus der Copen-V2-Oberfläche.** |

| Bohm persönliche Signatur und Zeitkomponente | Drei künstliche Kontexte, lokale Datumseingaben und kontrollierte Testuhr. | Signaturen bei Wiederholung gleich, drei verschiedene Namensequenzen; gleiche Uhr wiederholt Bohm-Komponente, Zeitänderung verändert Phase. Keine allgemeine Determinismuszusage für die Anwendung. |

| Morphic-Basiskern | Gleiche Zustände, Sequenz, Geometrie, Intention und explizite Zeit; Hardwaremodulation ausdrücklich aus. | Wiederholung gleich, geprüfte numerische Ausgaben endlich. Vollständiges `berechneKlientenFeld` aktiviert Hardwaremodulation selbst und wurde in dieser Probe nicht ausgeführt. |

Die Proben charakterisieren vorhandene Softwareformeln. Unterschiede zwischen erfundenen Personen und Zufalls-/Zeitvariationen belegen keine gemessene Klientenreaktion oder medizinische Wirkung. Sie führen keinen neuen Analysemodus ein.

Node 22.22.0 wurde ohne Paketinstallation verwendet. Seine experimentellen TypeScript-/VM-APIs dienten nur dem Prüfskript. Ein im Original nicht ausdrücklich als Typ markierter `HardwareConfig`-Import wurde für den Testloader ausschließlich im Speicher entfernt; Formeln und Quellbytes blieben unverändert. Der erste Loaderlauf scheiterte daran, der korrigierte Loaderlauf bestand. Die VM erhielt keine Datei-, Netzwerk-, Prozess- oder Timer-Schnittstellen. Für den Explorer war `Math.random` gesperrt; die Testuhr war kontrolliert. Das ist eine begrenzte numerische Probe, keine Browser-Sicherheitsfreigabe.

### Ergänzende Referenzproben vom 09.10.2026

Die folgende Fortsetzung erweitert Q3. Die früheren Proben oben behalten ihren damaligen Umfang. Hardware- und Zeitwerte wurden ausdrücklich als Testeingaben kontrolliert; dadurch wird keine reale Hardwareerfassung ersetzt oder abgenommen.

| Gegenstand | Tatsächlich ausgeführt | Ergebnis und Grenze |

|---|---|---|

| Separater Copen-V2-Zahlenblock | Exakte, hashgebundene Quellabschnitte für Normalisierung, Zeichenwerte und Ratenberechnung in einer gesperrten VM. Neun synthetische Bezeichnungen, sieben Potenztypen, Potenzen 0/1/6 und feste/adaptive Fibonacci-Auswahl: 378 Vergleiche. | Keine Abweichung zur gemeinsamen Funktion in diesen Kombinationen. Grenzpaare bei Länge 0/1/4/5/10/11/20/21 gleich. Keine Ausführung der React-Komponente, Sitzungsladung oder UI-Abläufe. |

| Copen-V2-Klientenrate | Separat extrahierte Funktion mit künstlichem persönlichen Kontext und einer achtstelligen vorgegebenen persönlichen Rate. | Wiederholung gleich; berechnete Klientenrate stimmt für die geprüfte Kontextzeichenfolge mit der gemeinsamen Funktion überein. Das Wortenergieargument verändert diese Klientenrate im Test nicht. Zielrate und Ratenbezeichnung sind hier getrennte Größen; allein daraus folgt kein Defekt. |

| Vollständiger Bohm-Klientenrechenweg | Originale `berechneKlientenFeld` und Rechenmodule mit drei erfundenen Kontexten. Zehn gültige Aufrufe einschließlich Wiederholung, Bildreferenz, Geometrie, Intention und Zeitwechsel; Hardware-Collector am Import durch künstliche Werte ersetzt. | Bei gleicher Testuhr/Hardware gleiche Ergebnisse; drei verschiedene Namensequenzen und persönliche Wellenfunktionswerte. Zahlen der drei Basiskontexte endlich. Hardwarewert 0→1 liefert Faktor 1→1,01 und skaliert die geprüften totalen/persönlichen Wellenfunktionswerte entsprechend. Keine Aussage, dass alle übrigen Felder unverändert bleiben. |

| Bohm-Bildbezug | Zwei unterschiedliche nichtleere künstliche Bildsignaturen beim gleichen Kontext. | Beide liefern gleiche Ergebnisse. Dieser Pfad prüft nur Anwesenheit und setzt einen pauschalen Bildbonus von 0,1; keine inhaltliche Bildauswertung. Die persönliche Faktorberechnung steigt im Test um 10 %, das zugrunde liegende Morphic-Feld bleibt gleich. Nicht mit der separaten Copen-Bildziffernverarbeitung gleichsetzen. |

| Direkte ungültige Eingaben | Vollständige Funktion mit leerer Vornamenliste beziehungsweise ungültigem Datum aufgerufen. | Beide erzeugen nicht endliche Zahlen. Das charakterisiert fehlende Absicherung im Rechenkern; vollständige UI-Erreichbarkeit und Validierung bleiben zu prüfen. Im gelesenen UI-Pfad werden Namen nur auf Nichtleerheit geprüft und anschließend per Leerzeichen aufgeteilt. |

| Originaler Hardware-Collector | Originalfunktion mit künstlicher Performance-Uhr und lokaler Testantwort auf `fetch`; GPU/RAM in der Testumgebung nicht verfügbar. Cache bei 0/4.999/5.000 ms und spätere Sammlung geprüft. | Erste Sammlung fünf künstliche HEAD-Aufrufe; innerhalb fünf Sekunden derselbe Cachewert, bei 5.000 ms neue Sammlung. GPU-/RAM-Fallback je 0,5. Alle geprüften Metriken endlich. Kein echtes HTTP, GPU- oder RAM-Messergebnis. |

Der vollständige Bohm-Klientenpfad setzt `useHardwareModulation: true` selbst. Der Collector nimmt keine Aus-Konfiguration entgegen und sammelt auch bei vorhandenem `DEFAULT_HARDWARE_CONFIG` mit ausschließlich `off`. Die Hardware-Testantwort der Hauptprobe und die künstlichen Collector-Requests der separaten Probe sind unterschiedliche Testgrenzen. In der originalen Sammlung sind externe HEAD-Anfragen vorgesehen; sie wurden nicht ausgeführt.

Die als Zeitkohärenz bezeichnete Funktion setzt `expectedDateDelta = perfDelta` und vergleicht danach beide. Die geprüften Aufrufe liefern deshalb 1; dies ist keine unabhängige Zeitmessung. Aussagen über Genauigkeitsgewinne aus den Quellkommentaren sind durch diese Proben nicht belegt. Diese Eigenschaften werden als Bestand festgehalten, ohne die bestätigten Algorithmen zu ändern.

Belege: private `copen-v2-inline-probe-results.json`, `bohm-full-probe-results.json`, `hardware-boundary-probe-results.json`; Quellen `CopenAlgorithmVisualizationV2.tsx:77,106,260`, `clientFieldAlgorithms.ts:177,371,394`, `hardwareAlgorithms.ts:124,192,258`, `ClientFieldCalculator.tsx:444,450`. Originalquellen vor und nach der Ausführung hashgleich. Der unabhängige Astra-Review führte zur präziseren Benennung einer Testassertion; die korrigierte Probe wurde erneut ausgeführt.

### Isolierte UI und Laufzeitprüfung vom 09.10.2026

Die unveränderten ausgewählten React-Komponenten liefen in einer eigenen lokalen Testoberfläche mit erfundenen Klienten. Vor jeder Navigation waren HTTP auf eine feste lokale Lese-Allowlist begrenzt, externe WebSockets gesperrt und Service Worker blockiert. Negative HTTP-/WebSocket-Proben und die lokale CSP-Sperre bestanden; in den aufgezeichneten Seitenrequests wurde kein externes HTTP zugelassen. Das ist kein OS-Netzverkehrsnachweis und keine Abnahme des gesamten veröffentlichten Produkts.

| Ablauf | Beobachtung | Konsequenz für die Integration |

|---|---|---|

| Bohm: berechnen, zwei Wörter testen, archivieren | Erster Speicherpayload enthält den richtigen künstlichen Klienten, dessen Wellenfunktion und zwei Testergebnisse. | Normalpfad im begrenzten UI-Test nachvollzogen. |

| Bohm: Alpha zu Beta ohne neue Berechnung | Archivpayload erhält Beta-ID und -Name, enthält aber unveränderte Alpha-Wellenfunktion und Alpha-Worttestergebnisse. | Klientenwechsel muss bestehenden Ergebnisstand sperren oder ausdrücklich an dessen ursprünglichen Kontext binden. Aktive DB-Annahme dieses Payloads ist nicht geprüft. |

| Bohm: Beta neu berechnen, Wörter nicht erneut testen | Neue Wellenfunktion, aber alte Worttestergebnisse im Archivpayload. Ein bewusst erneuter Worttest erzeugt anschließend andere Ergebnisse für Beta. | Klientenberechnung und Worttest benötigen eigene, miteinander verbundene Ergebnis-/Kontextrevisionen. |

| Bohm: Vorname nur aus Leerzeichen | UI lässt Berechnung zu; nach dem Aufteilen leere Vornamenliste. Sieben erfasste Ergebnisfelder sind nicht endlich. | Vor Berechnung normalisieren/validieren; nicht endliche Resultate vor Ausgabe/Speicherung ablehnen. Keine Formeländerung. |

| Copen V2: gespeicherte Pause laden | Eine künstliche paused-Zeile erscheint in der aktiven Karte als „Läuft“. | Persistierten Auftragszustand erhalten; Laden darf keine Fortsetzung erfinden. Echte Worker-Ausführung nicht ausgelöst. |

| Copen V2: Pause und erneutes Öffnen | Pause ändert Karte, emittiert im geprüften Handler keinen Speicherauftrag; gespeicherte running-Zeile bleibt so. Nach Unmount/Remount wieder „Läuft“. Wechsel zu Beta ohne Sitzungen blendet Alphas Karte aus. | UI-Zustand, bestätigten Workerzustand und persistierten Auftragszustand konsistent führen. Reale Realtime-Updates nicht geprüft. |

| Thom: Start, Pause, Fortsetzen | Drei künstliche Punkte im geprüften Ablauf einmal in Reihenfolge. Pause hält Punktfolge an; Fortsetzen ohne doppelten Punkt. Pausenzeit geht in angezeigte Laufzeit ein. | Verarbeitungslaufzeit und verstrichene Sitzungszeit getrennt definieren. Scores 2/4/6 sind Testeingaben, keine echte Punktebewertung. |

| Thom: Stop, Unmount, Remount, Reload | Stop/Unmount verhindern im geprüften Zeitfenster weitere Punktcallbacks. Remount/Reload liefern leeren, inaktiven Hook; keine stille Fortsetzung. | Reload-Checkpoint oder vollständige Wiederherstellung gespeicherter Scans nicht bewiesen. |

Die Copen-Ladefunktion setzt außerdem den Potenztyp auf D, nutzt parseInt(tested_potency) und kürzt die Dauer auf ganze Minuten. Für den künstlichen Wert C30 liefert die Konvertierung NaN; 121 Sekunden werden zwei Minuten. Dies sind Quellpfadbefunde, keine abgenommenen UI-Potenzfelder oder Aussagen über das Format aller Bestandszeilen. Wort-/Klientenraten dürfen beim Wiederladen nicht still aus anderen Parametern rekonstruiert werden.

Testgrenzen: Anmeldung, Datenbank, Toasts und Bohm-Hardwareantwort sind lokale Testadapter. Der Store prüft keine RLS, Constraints oder dauerhafte Speicherung; Select-Projektionen werden nicht ausgewertet, single/maybeSingle gleich behandelt und upsert wie Insert behandelt. Channels sind inert, externe Funktionen/RPC deaktiviert. Belegt sind die aufgezeichneten UI-/Payloadpfade, keine Backendabnahme. Die reduzierte Testgestaltung ist kein UX-/Barrierefreiheitsreview. Thom prüft den Originalhook in React, nicht die vollständige 3D-Anwendung.

444 Testabhängigkeiten wurden aus dem unveränderten Explorer-Lockfile mit npm ci --ignore-scripts installiert: React/ReactDOM 18.3.1, esbuild 0.21.5. Keine Installation in Produktquellen. Der Explorer-Build bindet 69 verwendete Originaldateien an Quellhashes; ausgelieferte Testbundles vor/nach Browserläufen gegen lokale Bytes geprüft. Erste Testläufe scheiterten an Testauflösung, doppelter React-Kopie, instabiler künstlicher Auth-Identität und ungenauen Testselektoren. Korrigierte Testläufe wurden wiederholt; keine Produktalgorithmen verändert.

Unabhängiger Review bestätigt Bohm-Payload-/Whitespace-Befunde. Eine Lücke in der Unmount-Testbeobachtung wurde geschlossen: Callbackliste wird jetzt frisch gelesen, auch nach Remount ausdrücklich geprüft; korrigierter Thom-Lauf wiederholt. Belege: private bohm-ui-lifecycle-results.json, copen-ui-lifecycle-results.json, thom-nls-browser-probe-results.json, Buildreceipts, Testskripte und Screenshots. Quellen: ClientFieldCalculator.tsx:213,443,1183; WordEnergyTester.tsx:245,790; CopenAlgorithmVisualizationV2.tsx:371,417,422,805; useNLSAutoScan.ts.

### Ergänzende Archiv- und Vorlagenprobe

Frische isolierte Browserkontexte, gleiche gebundene Produktquellen und HTTP-/WebSocket-Sperren vor Navigation. Fünf zusätzliche Fälle wurden tatsächlich ausgeführt; keine reale Datenbank oder Originaldatei geschrieben.

| Fall | Beobachtung | Erforderliche Bindung |

|---|---|---|

| Copen V2: nur eine abgeschlossene V2-Sitzung | Im Vorlagenbereich keine verfügbaren Sitzungen; er liest die alten `harmonization_sessions`/`analysis_archives`. | Alte und V2-Familien explizit behandeln, nicht durch gleichnamige Felder still zusammenführen. |

| Copen: drei Varianten desselben Wortes | Zwei alte Harmonisierungen mit verschiedenen Potenzen, Raten und Dauern sowie ein Archiveintrag liefern genau eine Vorlagenposition. Gespeichert wird der Archiveintrag mit seiner Rate/Potenz und 3600 Sekunden Default in `harmonization_templates`. | Worttext ist kein eindeutiger Variantenschlüssel. Rate, Potenz, Dauer und Herkunft getrennt erhalten. |

| Copen: gespeicherte Vorlage laden | Keine neuen Writes/Toasts oder geänderten Sitzungszeilen. Originalhandler benötigt optionalen Callback; V2-Elternkomponente übergibt ihn nicht. | Sichtbare Vorlage braucht einen gebundenen, ausdrücklich gestarteten Auftragspfad. Das ist kein geprüfter echter Worker. |

| Bohm: ursprüngliches Ergebnis archivieren | Zwei künstliche Wortresultate, gleicher Klient und zugehörige Wellenfunktion im ersten Payload. | Ausgangsarchiv im begrenzten UI-Pfad nachvollzogen. |

| Bohm: Klientenkontext neu berechnen, altes Archiv laden und erneut archivieren | Gleiche Klienten-ID und unveränderte alte Wortresultate, aber neue Wellenfunktion im zweiten Payload. Das Laden restauriert den ursprünglichen Kontext nicht. | Archiv mit seinem Ergebnis-/Kontextstand öffnen; neue Berechnung ist ein neuer Stand, keine Umdeutung des alten Ergebnisses. |

Belege: private `copen-template-results.json`, `bohm-archive-context-results.json`, Testskripte und Screenshots. Bundle vor/nach beiden Browserproben identisch und gegen lokale Bytes geprüft. Kein externer Seiten-HTTP-Request zugelassen; dies ist keine OS-Paketmitschnittaussage. Anmeldung, Store, Toast und Hardwareantwort sind Testadapter, Bohm-Aufrufe instrumentieren den Originalalgorithmus. Mockprojektionen, Constraints/RLS, echte Speicherung und Worker bleiben außerhalb der Probe. Der erste Vorlagenlauf scheiterte an einem mehrdeutigen Testselektor; Fehlreceipt erhalten, auf Vorlagenkarte eingegrenzt und erneut ausgeführt.

Quellen: `HarmonizationTemplates.tsx:82,99,109–119,156,185–192`; `CopenAlgorithmVisualizationV2.tsx:1401`; `WordEnergyTester.tsx:355–382,810,839–845`. Astra6/medium bestätigte die Copen-Quellbefunde und die begrenzten Testaussagen; Bohm-Archivfall vom Parent frisch ausgeführt, kein separater Reviewer-Rerun.

## 3. Exportbeziehungen und Besitzer

Unter 16 ausgewählten, im Quelltext deklarierten FK-Prüfungen fanden sich keine nicht auflösbaren Nichtleerwerte. Sieben Prüfpfade hatten keine Kindzeilen und wurden deshalb nicht mit Datensätzen ausgeübt. Bei fünf Thom-Trajektorie-/Sitzungspaaren stimmte die Klienten-ID überein. Das deckt keine allgemeine Laufzeit- oder Mandantenprüfung ab.

`client_vectors.session_id` ist eine Textkennung ohne FK zur UUID von `treatment_sessions`. `organ_landmarks.point_id` ist eine fachliche Textkennung; sie ist nicht mit der UUID von `organ_scan_points` gleichzusetzen. Die frühere Prüfung nach ähnlichen Feldnamen wird dadurch präzisiert.

Im Explorer bleiben 26 V2-Sitzungszeilen mit einem einzigen, im Export nicht auflösbaren Klientenbezug. Auch die alte `patients`-Tabelle enthält diesen Bezug nicht. Löschung, unvollständiger Export, Migration oder falsche Zuordnung sind mögliche, unbewiesene Ursachen. In den untersuchten V2-Definitionen ist `patient_id` nicht als FK abgesichert.

| Exportierte Tabellenfamilie | Vorhandene Elternpaare mit beiden Benutzerkennungen | Unterschiedliche Benutzerkennungen |

|---|---:|---:|

| Alte Harmonisierung | 91 | 0 |

| V2-Harmonisierung | 3.118 | 206 |

| Morphic-Sitzungen | 11.007 | 630 |

| V2-Vorlage | 1 | 1 |

| Wortenergiearchive | 298 | 15 |

Diese Zahlen zeigen besitzverschiedene Eltern-Kind-Verknüpfungen im Snapshot. Autorisierung und Ursache bleiben ungeklärt. Sie dürfen nicht als unabhängige Vorfälle addiert werden: Die Morphic-Migration kopiert unter anderem Benutzer- und Klientenbezüge aus V2-Sitzungen.

Die deklarierte RLS schützt einzelne Zeilen durch `auth.uid() = user_id`; Admins dürfen zusätzlich fremde Zeilen lesen. Patientenlisten können dadurch fremde Klienten zeigen, während Inserts den aktuellen Benutzer als Zeileneigentümer setzen. Das erklärt einen technisch möglichen Adminpfad, beweist aber keine erlaubte fachliche Delegation. Eine allgemeine Prüfung von Elternbesitzer, Kindbesitzer und Delegationsrecht fehlt in den untersuchten Definitionen. Die isolierte UI-Probe bestätigt einen Archivpayload mit alten Ergebnissen und neuem Klienten nach einem Klientenwechsel; seine Beteiligung an den Exportabweichungen ist unbekannt.

Für die spätere zentrale Struktur müssen mindestens **Mandant, fachlicher Klient, Ersteller, Zugriffsberechtigung, Auftrag und unveränderlicher Kontextstand** getrennt festgehalten werden. Ein Benutzerfilter allein ersetzt diese Beziehungen nicht. Keine automatische Löschung, Eigentümerangleichung oder Umdeutung historischer Daten ausführen.

Quellbelege: V2-Migration `20251022084553_c1629ce0-2fe2-4d79-a268-b2bc8a1c7efb.sql`; Morphic-Migration `20251231115149_9e2a7375-d96a-47e7-a40a-9f9939fff154.sql`; Wortarchiv-Migration `20251228103553_e9d63adb-6912-4989-b744-296d8096e757.sql`. Schreibpfade: `CopenAlgorithmVisualizationV2`, `HarmonizationManager`, `WordEnergyTester`; Klienten-/Ergebniswechsel: `ClientFieldCalculator`.

## 4. Thom 3D und Scan als gemeinsame Datenkette

Die spezialisierte 3D-Bedienung bleibt Bestandteil des Moduls. Gemeinsame RadiWorks-Gestaltungsregeln dürfen Modellwahl, Anatomieebenen, Region-/Punktwahl, Scan und Kamerabedienung nicht durch eine generische Oberfläche ersetzen.

| Bindung | Statischer Befund | Erforderlicher Referenzfall |

|---|---|---|

| Modell und Koordinaten | GLB wird normiert; Punkte werden direkt übernommen oder auf Meshes projiziert. Ein Modell-/Schema-Koordinatenvertrag ist im geprüften Pfad nicht durchgängig weitergereicht. | Zwei bekannte Modellrahmen mit synthetischen Landmarken; Achsen, Maßstab und Projektionsfallback sichtbar prüfen. |

| Modellwechsel und Ebenen | Scan-Konfiguration hält Modell-ID; Startpfad verarbeitet Punkt-IDs. Wechsel/ausgeblendete NLS-Ebene stoppt oder bindet laufenden Scan dort nicht ausdrücklich neu. | Konfiguration und laufenden Scan bei Modellwechsel prüfen; historischen Modellbezug erhalten. |

| Reihenfolge und Optionen | Punktfolge stammt aus der sortierten DB-Liste, nicht Checkbox-Klickfolge. Fokus priorisiert sie nicht; Harmonischen-Schalter im aktiven Scan nicht verarbeitet. | Sichtbare Auswahl-/Reihenfolge mit drei künstlichen Punkten und jeder wirksamen Option vergleichen. |

| Pause und Wiederanlauf | Browser-State/Timer; Pausenzeit zählt in Laufzeit; beim Unmount Timerbereinigung. Kein belegter Reload-Checkpoint. | Pause, Fortsetzen, Abbruch, Hintergrund und Reload ohne stille Fortsetzung oder doppelte Punkte. |

| Ergebnis, Bericht und Auftrag | Aktives Scan-Ergebnis trägt keine durchgängige Modell-/Konfigurationsrevision. Speicher-Hook vorhanden, im untersuchten UI-Pfad kein Aufrufer gefunden; exportierte Ergebnistabelle leer. Bericht/Job bewahren diese Herkunft ebenfalls nicht durchgängig. | Sitzung → Modellrevision/Mapping → Punktfolge → Resultat → Bericht/Trend → Harmonisierung gemeinsam speichern und neu laden. |

| Tastatur und Bewegung | Native Punktlisten als Alternative vorhanden; 3D-Punkte zeigerorientiert, Overlay-Iconnamen/Statusansagen und Bewegungsreduktion lückenhaft. | Gesamter Ablauf ohne Maus, Screenreaderstatus und reduzierte Bewegung. |

| Fehler und Fallback | GLB-Fallback vorhanden, Fehlerursache nicht durchgängig sichtbar. | Fehlendes Modell, ungeeigneter Mesh/Raycast, Katalogfehler und WebGL-Ausfall mit verständlichem Status. |

13 Modellmetadatensätze im CSV-Export ersetzen kein Assetarchiv. Das gebündelte GLB ist strukturell geprüft; die tatsächliche anatomische Darstellung und Koordinatenkompatibilität sind noch nicht abgenommen. Storage-Dateien, Fotos und Katalogmodelle müssen mit Version, Lizenz und Inhalts-Hash separat erfasst werden.

Zusätzlicher Feldvertrag für die nächste Probe: Thom-Kern verwendet die Reihenfolge körperlich, emotional, mental, Energie, Stress. Der KI-Request benennt Position 2 als Stress und Position 4 als mental. Auch die UI-Nachtestung verwendet eine Simulation Richtung 50 mit Bereich 0–100, während der geprüfte Kern Dimensionen im Bereich −1 bis 1 erzeugt. Diese Unterschiede sind zu klären, bevor daraus Trends oder Vergleichsberichte abgeleitet werden. Keine Formel oder Simulation wurde hier geändert.

Belege: `ThomVectorEngine.ts:313`, `useMeridianDiagnosis.ts:398`, `MeridianDiagnosisPanel.tsx:218`; detaillierte 3D-Dateizeilen und acht Prüffälle in der privaten Notiz `reference-plan/thom-graphics.md`.

### Ergänzung: Thom-Parallelität, Feldvertrag und synthetische 3D-Modelle

Diese Fortsetzung verwendet ausschließlich künstliche Punkte, Scores, Personen und GLB-Modelle. Sie erweitert die Referenzcharakterisierung; sie behebt keine Produktfehler und erteilt keine Integrationsfreigabe.

| Gegenstand | Beobachtung | Konsequenz und Grenze |

|---|---|---|

| Zwei gleichzeitig gestartete Scan-Hooks | In Entwicklungs- und Produktionsbuild drei Alpha-Callbacks, aber nach Pause/Fortsetzen nur zwei gespeicherte Alpha-Ergebnisse. Kontrollierte Produktionswiederholung: 4/4 nur mit Alpha gestartete Scans vollständig; 4/4 mit zusätzlich gestarteter Beta fehlen jeweils Punkt 2. In allen Fällen waren beide Hooks gemountet. | Vollständigkeit muss am Auftrag anhand der erwarteten Punktfolge geprüft werden. Verschachtelte State-Updates sind ein Scheduling-abhängiger Quellverdacht, keine nachgewiesene Ursache oder Mandantenvermischung. 1200 ms Pause direkt vergleichbar; 2600 ms nur ohne gestartete Beta, der zweite Dualfall wartet auf Beta-Ende. |

| Pause, Abbruch und geänderte Eingaben | Beta läuft während Alpha-Pause weiter; Beta-Abbruch beendet in der Probe nicht Alpha. Neue Alpha-Scores beeinflussen folgende Punkte. Eine veränderte übergebene Punktliste erscheint nach Fortsetzen im Alpha-Ergebnis. | Der Hook allein friert Eingaben nicht ein. Ein unveränderlicher Auftragssnapshot und Modell-/Punktrevisionen sind erforderlich. Keine Aussage, dass die vollständige UI diesen Änderungsweg zulässt. Reload startet die Fixture leer, kein Persistenznachweis. |

| Mental-/Stressachsen | Der unveränderte Kern verwendet körperlich, emotional, mental, Energie, Stress. Extrahiertes Original-Requestmapping ordnet Index 2 Stress und Index 4 mental zu. Kontrollierte Einzeländerungen bestätigen die Vertauschung; lokaler Imbalance-Code zeigt sie ebenfalls statisch. | Achsen namentlich und versioniert binden. Keine echte Diagnose oder ausgehender Request ausgeführt; keine Datenkorrektur oder Formeländerung. |

| Nachtestbereiche | Die vorhandene extrahierte Simulation verschiebt Dimensionen Richtung 50. Bei künstlichen Eingaben −1 bis 1 ergeben drei kontrollierte Zufallswerte Ausgaben von 6,65 bis knapp 13,25. | Kernbereich −1 bis 1 und simulierten Bereich 0–100 nicht ungeprüft als dieselbe Trendkennzahl behandeln. Kein Beleg einer Klientenreaktion oder Behandlung. |

Die fünf Parallel-Lebenszyklusfälle pro React-Build und acht kontrollierten Fortsetzungsfälle sind **Charakterisierungen mit bestätigter Ergebnislücke**, keine bestandene fachliche Vollständigkeitsabnahme. Der erste fehlgeschlagene Vollständigkeitscheck bleibt erhalten. Der erste VM-Loaderfehler durch eine wiederholte lexikalische Deklaration wurde nur in der Fixture korrigiert.

Die 3D-Probe lädt die originalen React-/Three-Komponenten mit zwei selbst erzeugten GLB-Ellipsoiden und einem 24-Vertex-Testmesh. Normierung auf die Y-Höhe ist belegt: Modell A Skalierung 0,55, Modell B nach Knotenskalierung 2,75 mit halber Z-Tiefe 16,5. Das ist keine automatische Achsenausrichtung. Raycast-No-Hit und Unterschreiten der 100-Vertex-Grenze behalten in den beobachteten Fällen die ursprünglichen Punkte.

**Oberflächenposition nicht abgenommen:** Im ersten Lauf lag A bei z≈0,09870, während die Welt-Bounding-Box nur bis z≈0,05506 reicht und der vorgesehene Offset 0,008 beträgt. Die damaligen Assertions prüften nur Bewegung/Richtung und waren für geometrische Genauigkeit zu schwach. Dieser erste als bestanden ausgegebene Stand ist archiviert und wird nicht als korrekte Projektionsabnahme verwendet. Die ergänzte Probe erfasst A-Matrix zunächst als Identität und B zunächst nur mit Knotenskalierung 2. Ein archivierter Zwischenlauf behielt A-z≈0,09870 und platzierte B bei y≈0,20799; ein späterer Aufruf derselben Utility nach expliziter Weltmatrixaktualisierung lieferte A-z≈−0,06292 und B-y≈0,95979. Die strenge B-Erwartungsprüfung schlug in diesem Zwischenlauf fehl; der Fehlerbeleg bleibt erhalten. Im abschließenden Lauf lagen B-Layer und späterer Utility-Aufruf dagegen beide bei y≈0,96034, A blieb auffällig. Die Läufe nutzen unterschiedlich instrumentierte Harness-Bundles. Der Unterschied isoliert deshalb weder Scheduling noch Weltmatrixaktualisierung als Ursache. Grüne Assertions im Schlusslauf ersetzen angesichts der bekannten A-Abweichung keine Geometrieabnahme.

Diese Unterschiede stützen einen Verdacht auf den Weltmatrix-/Renderzeitpunkt. Der spätere Aufruf derselben Utility ist keine unabhängige geometrische Referenz und beweist die vollständige Ursache nicht. Es fehlen ein Vergleich im selben Frame gegen transformierte Mesh-Dreiecke, reale anatomische Modelle und der vollständige Viewer. Für weitere Modellimporte benötigen die Datenverträge Achsenkonvention, Einheit, lokale/Welttransformation, Modell-/Landmarkenrevision und ausdrücklichen Projektions-/Fallbackstatus. Die bestehende spezialisierte 3D-Oberfläche wird erhalten.

Chromium verwendete ausdrücklich SwiftShader-Software-WebGL. Quell-/Harnesshashes vor und nach dem separaten Build sind unverändert; Buildbefehl, Exitcode und Dist-Bundlehashes sind protokolliert. Im Schlusslauf stimmen die ausgelieferten JavaScript-Bytes mit dem aufgezeichneten Dist-Bundle überein; die Erst- und Fehlerläufe bleiben separat archiviert. Keine Hardware-GPU-, Anatomie-, DB-, RLS-, Persistenz- oder vollständige 3D-Abnahme.

Die Browserproben sperrten fremdes HTTP und alle WebSockets vor Navigation; Sperrproben und CSP wurden ausgeführt. Original-Hook sowie Entwicklungs-/Produktionsbundles sind hashgebunden. Der 3D-Pfad ersetzt nur den Datenbankimport durch einen ausgewiesenen, bei Aufruf werfenden Stub. Kein Auth-, RLS-, Storage-, vollständiger Viewer-, Hardware- oder Deploymentnachweis. Die Rechenprüfung läuft ohne Datei-, Prozess- oder Netzwerkschnittstellen in einer eingeschränkten VM.

Private Nachweise: `reference-plan/thom-parallel/` und `reference-plan/thom-3d/`. Originaldateien bleiben bytegleich; Ergebnisse und Erstfehlschläge werden in einem begrenzten Abschlusscheckpoint erhalten.

### Ergänzung: unabhängiger Dreiecksvergleich

Die neue Probe liest Punktpositionen und transformierte Mesh-Dreiecke unmittelbar nach demselben Renderer-Aufruf aus den vorhandenen Weltmatrizen. Vor diesen Aufnahmen aktualisiert der Test keine Matrizen. Eine eigene Ebenen-/Segmentrechnung bestimmt den kleinsten Abstand; der Original-Raycaster wird dafür nicht wiederverwendet. Vier analytische Referenzfälle bestanden. Die zwei GLBs und alle Koordinaten sind synthetisch; Chromium verwendet nachweislich SwiftShader. Dies prüft keine anatomische Richtigkeit oder allgemeine Skinned-/Morph-Mesh-Kompatibilität.

| Modell | Erster vollständig erfassbarer Frame: Abstand | Zwölf Render-Aufrufe später: Abstand | Bewertung |

|---|---:|---:|---|

| A, Y-aufrechter Ellipsoid | Frame 5: 0,054688411 | Frame 17: 0,008010994 | Früher Punkt noch an der Ausgangsposition; später nahe am vorgesehenen Offset, aber außerhalb der Prüftoleranz. |

| B, Z-langer Ellipsoid mit Knotenskalierung | Frame 7: 0,545366891 | Frame 19: 0,007931278 | Früher Punkt noch an der Ausgangsposition; später nahe am vorgesehenen Offset, aber außerhalb der Prüftoleranz. |

Die Werte sind Modellkoordinaten, keine Millimeter. Der Originalhelfer verwendet einen Offset von 0,008; die hier festgelegte absolute Prüftoleranz beträgt 0,00001 und ist keine fachlich validierte Genauigkeitsanforderung. Bei beiden frühen Aufnahmen liegt der Punkt noch bei [0; 0,4; 0]. Die späteren absoluten Offsetabweichungen betragen ungefähr 0,000011 beziehungsweise 0,000069. Ergebnisstatus: `completed_with_geometry_failures`; keine Geometrieabnahme. Die ursprüngliche Modellanimation läuft unverändert weiter. Deshalb isolieren diese Abstände weder die Projektionsrechnung noch eine Timing- oder Animationsursache. Eine spätere reine Matrixaktualisierung ohne erneute Projektion ist lediglich eine Zustandskontrolle und belegt keine Reparatur.

No-hit und der 24-Vertex-Schwellenfallback erhalten in beiden beobachteten Frames ihre lokalen Ausgangspositionen; vier entsprechende Assertions bestanden. Quelle, Testaufbau, Build und ausgelieferte JS-/CSS-/HTML-/GLB-Dateien sind mit SHA-256 gebunden; sämtliche protokollierten Antworten der erforderlichen Pfade wurden verglichen. Ausgehendes HTTP und WebSocket sind vor Navigation gesperrt und mit Negativproben geprüft; dies ist kein Nachweis durch systemweite Paketaufzeichnung. Eigener Prüfserver auf 8128 und Prüfchromium wurden geschlossen.

Vorherige Testaufbaufehler sind erhalten, einschließlich fehlendem react-dom-Alias, noch nicht bereitgestellter Testexposition und einem fehlerhaften Server-Rückgabewert. Beim ersten Fehler blieb der eigene Listener zunächst offen; Originalbeleg, separate Korrekturannotation und anschließender kontrollierter Abbau sind dokumentiert. Korrekturen erfolgten ausschließlich am Testaufbau. Die ursprünglichen A/B-Beobachtungen bleiben als frühere, anders instrumentierte Läufe erhalten und dürfen nicht als identischer Vergleichslauf interpretiert werden.

Astra6/medium bestätigt den Ergebnis-SHA und 26 aktuelle Quell-/Harness-/Dist-Dateien sowie die Schließung der vier früheren Beleglücken. Der Review bestätigt die begrenzte Charakterisierung, keine fachliche oder produktive Abnahme.

### Ergänzung: Thom-Archiv, Auftragsdienst und Echtzeit

Sieben isolierte Fälle führen die vollständigen Originalklassen beziehungsweise Archivcallbacks aus. Importabhängigkeiten, Browserzustand, Datenbank, Socket und Zeitgeber sind ausdrücklich simuliert. Quellmanifest und Prüfscripthash sind an das Ergebnis gebunden. Dies prüft einzelne Verträge und Lebenszyklen; es ist keine aktive DB-, Gateway-, Worker-, Audio- oder Hardwareabnahme.

| Gegenstand | Beobachtung in der abgegrenzten Probe | Bedeutung und Grenze |

|---|---|---|

| Bewusstes Trennen / Destroy | Nach dem verzögerten Socket-Close erzeugen beide Pfade einen weiteren Verbindungsversuch. | Gewünschter Offline-/Shutdownzustand ist im geprüften Dienst nicht gegen den Reconnect-Pfad geschützt. Kein erfolgreicher Wiederanschluss oder tatsächlicher Netzausfall behauptet. |

| Relay-Verteilung | Vektor- und Sitzungsereignisse gelangen an die andere offene Verbindung derselben simulierten Registry, ohne lokale Empfängerbindung. | Quellbefund zu Filter-/Autorisierungsbedarf; tatsächliches Gateway und Deployment weiterhin unbekannt. Keine Cloud-Mandantenüberschreitung nachgewiesen. |

| Anfragen im selben Millisekundenwert | Zwei unterschiedliche GPU-Anfragen erhalten dieselbe Request-ID; eine Antwort löst beide Promises mit demselben Ergebnis auf. | Eindeutige Korrelation je Auftrag/Anfrage erforderlich. Keine echte GPU-Berechnung oder Audioinitialisierung ausgeführt. |

| Archiv speichern → laden | Übergebener Score 0,37 wird nicht im Insert erhalten; die gespeicherte Zeile mit Fortschritt 100 lädt anschließend als Score 1. | Auftragsfortschritt, ursprünglicher Stabilitätswert und ein begründeter Trend sind getrennte Größen. Die bestehende Bezeichnung „Verbesserung“ darf keinen neuen Messnachweis suggerieren. Fake-State prüft Callback/Payload, keine React-Rerender- oder reale SQL-Abnahme. Die Gesamtdauer der Folge wird gespeichert, die jeweilige Punktdauer fehlt in den gespeicherten Punktobjekten; aus diesem Payload allein lässt sich die zeitliche Folge nicht exakt rekonstruieren. |

| Auftragserstellung | Übergebene sessionId fehlt im Insert; angefragte Priorität 0 wird 1. | Sitzungskontext ist nicht durch diesen Auftragsweg gebunden. Ob Priorität 0 fachlich zulässig ist, bleibt offen. |

| Demo-Simulation nach Abbruch | Nach erfolgreichem cancelJob schreibt simulateHarmonization weiter; permissive Fake-DB endet mit completed/100. | Demo-Methode und fehlende Abbruchprüfung charakterisiert. Kein UI-Aufrufer gefunden; ein realer Worker oder eine tatsächliche DB-Statusüberschreibung sind nicht belegt. |

Die Fake-DB prüft Payloads und Filter, bildet aber weder RLS/Constraints noch Tabellennamensräume, Sortierung oder Limit-Verhalten vollständig ab. Aus den sieben Fällen folgen keine allgemeinen Persistenz-, Nutzer- oder Mandantenrechte. Definitionen und aktive Rechte müssen getrennt geprüft werden: Die frühere Thom-Migration enthält vier benutzerbezogene Einzelpolicies; eine spätere zusätzliche FOR-ALL-Policy erlaubt in ihrer Definition auch nullable Klienteneigentümer und entfernt jene vier nicht. Das ist eine zu vergleichende Quellfolge, kein Nachweis der aktiven Cloud-Rechte.

Private Nachweise: reference-plan/thom-services/probe.mjs, SERVICE_RESULTS.json sowie erhaltener Erstbeleg FIRST_SERVICE_RESULTS.json. Astra6/medium prüfte die sieben eng begrenzten Befunde unabhängig; Parent ergänzte die Script-Hashbindung und führte die Probe nochmals erfolgreich aus. Produktdateien, Algorithmen und laufende Instanzen wurden nicht verändert.

### Ergänzung: aktiver Lovable-Cloud-Strukturabgleich

Nach Verbindung des Lovable-Plugins wurden beide Projekte über ihre angegebenen IDs gelesen. Projekt-API und jeweiliger Quellcommit stimmen mit dem gebundenen lokalen Bestand überein. Direkte Identitätsabfragen bestätigen PostgreSQL 17.6 und current_user/session_user postgres. Strukturkatalog und Bucket-Konfiguration wurden unter READ ONLY mit abschließendem ROLLBACK erfasst; beide Strukturresultate melden transaction_read_only=on. Die anfängliche reine Identitäts-SELECT-Abfrage lief ohne Read-only-Vorbelegung. Keine DML/DDL, Klientendatensätze, Passwörter, Schlüssel oder Storage-Objekte wurden abgefragt; keine Projekt-Agenten beauftragt oder Deployments verändert.

| Gegenstand | Thom | Explorer |
|---|---|---|
| Anwendungstabellen im Schema public | 18 | 13 |
| RLS dieser Tabellen | überall eingeschaltet, nicht erzwungen | überall eingeschaltet, nicht erzwungen |
| Tabellen-Namensabgleich gegen CREATE/DROP im Migrationsbestand | keine Abweichung gefunden | keine Abweichung gefunden |
| Storage-Konfiguration | 3d-models öffentlich, 100 MiB Bucket-Limit; client-photos öffentlich | client-signatures privat |

public bezeichnet hier den PostgreSQL-Schemanamen, keine öffentliche Lesefreigabe. Der CREATE/DROP-Namensabgleich ist eine begrenzte Regex-Auswertung, keine ausgeführte Migration oder vollständige Schemaäquivalenz. Katalogdefinitionen, Indizes, Fremdschlüssel, Policies, Funktionssignaturen/Definitionshashes, Trigger, Rollen-ACLs und Realtime-Publikationen sind privat erfasst. Acht gespeicherte JSON-Dateien stimmen mit SHA-256 der exakt empfangenen API-Ergebnisse überein; Rohdefinitionen wurden nicht an den Review-Agenten weitergegeben.

**Thom-Auftragsvertrag:** harmonization_jobs hat ein erforderliches client_id, aber keine session_id-Spalte. Die fehlende Session-ID im angebotenen Serviceweg ist deshalb auch eine Schema-/Vertragsfrage; allein ein zusätzlicher Insert-Wert würde sie nicht lösen.

**Zusammenspiel der Rechte:** Die vier benutzerbezogenen Jobs-Policies und die zusätzliche permissive ALL-Policy mit NULL-Eigentümerzweig bestehen aktiv nebeneinander. Zugleich hat clients vier benutzerbezogene Policies ohne NULL-Zweig, entsprechend der späteren Quellmigration 20260626065408. Die Jobs-Regel verwendet eine clients-Unterabfrage, deren RLS mitwirkt. Der NULL-Zweig allein beweist deshalb keine wirksame Freigabe eigentümerloser oder fremder Aufträge. Wirksame Regeln müssen im jeweiligen Nutzerkontext zusammen geprüft werden. Die Admin-Katalogabfrage unter postgres ist kein Nutzertest oder Mandantennachweis. [PostgreSQL-RLS](https://www.postgresql.org/docs/17/ddl-rowsecurity.html)

**Explorer-Versionen:** Die vier v1/v2-Tabellenfamilien für Klienten, Analysen, Harmonisierung und Vorlagen bestehen aktiv nebeneinander. Das beweist weder eine abgeschlossene Altdatenmigration noch ihre aktuelle Verwendung. In beiden public-Schemata fehlt eine ausdrücklich so benannte tenant_id-Spalte; daraus folgt keine fehlende Trennung, da Eigentümer- und Mitgliedschaftsbezüge ebenfalls Grenzen bilden können. Die spätere Aurelia-Zuordnung bleibt ausdrücklich zu entscheiden.

**Funktionen:** Die erfassten SECURITY-DEFINER-Helfer haben PUBLIC EXECUTE in ihren ACLs. Das allein belegt keinen Exploit. Funktionstext, Eigentümerrechte, Namensauflösung und Aufrufkontext müssen zusammen geprüft werden; der serverintern berechnete Definitionshash ersetzt diese Prüfung nicht. [PostgreSQL-Funktionsregeln](https://www.postgresql.org/docs/17/sql-createfunction.html)

**Medien:** Der aktive Bucket client-photos ist öffentlich konfiguriert. Für vertrauliche Klientenbilder empfehle ich private Speicherung mit geprüften Regeln und autorisierten Downloads oder kurzlebigen signierten URLs. Öffentlich konfigurierte Dateien sind bei bekannter URL abrufbar; Upload/Löschen bleiben zugriffsgesteuert. Es wurde kein Objekt gelistet oder heruntergeladen; vorhandene sensible Inhalte und tatsächlicher Fremdabruf sind nicht nachgewiesen. public=false bei Explorer-Signaturen ist ebenfalls keine Freigabe ihrer konkreten Policies. NULL bei Bucket-Limit/MIME-Liste bedeutet keine ausdrücklich gesetzte Bucket-Grenze, nicht unbegrenzte Plattformkapazität. Ein Datenbankexport enthält keine Storage-Dateien. [Lovable Storage](https://docs.lovable.dev/features/storage), [Bucket-Zugriffsmodell](https://supabase.com/docs/guides/storage/buckets/fundamentals)

Astra6/medium prüfte die abgeleiteten Fakten und Grenzen unabhängig, ohne Rohinventare oder Medien zu lesen. Effektive Rechte getrennt angemeldeter synthetischer Nutzer, Delegation/Abo/Mandantenkontext, aktive Edge-/Worker-Versionen, Assetbestand/Lizenzen und vollständige Migration bleiben offen. Es erfolgte keine Produktkorrektur oder Mandanten-/Integrationsfreigabe.

Lokale Erfassung: runtime/aurelia-three-modules-20261009/reference-plan/db-metadata/live-20261009-222316. Unterbrochene lokale Speicherversuche sind erhalten: Windows-Kommando-Längengrenze, automatische Ablehnung möglicher Überschreibung, anschließend zunächst nicht fertig abgewartete Prozessstarts. Vollständige Erfassung danach in neuen Dateien, ohne bestehende Belege zu überschreiben; alle API-Ursprungshashes geprüft.

## 5. Grenzen der Thom Liveprüfung

Ein vorhandener Vektor kann in `MeridianDiagnosisPanel` bei fehlendem Diagnoseergebnis automatisch die Berechnung starten. Nach lokalen Heuristiken ruft `useMeridianDiagnosis` einen Edge-Dienst auf, der über den Lovable-Gateway `google/gemini-2.5-flash` anspricht. Gesendet werden abgeleitete Vektordimensionen und Imbalance-Angaben; im untersuchten Request keine ausdrücklich mitgesendeten Namen, Fotos oder Klienten-/Sitzungs-IDs. Dieser bestehende KI-Weg ist kein freigegebener neuer Aurelia-Algorithmus.

Echtzeitdienste verbinden bereits beim Mount. Ein Endpunkt ist fest im Quelltext hinterlegt; allein eine geänderte ENV isoliert ihn nicht. Der untersuchte Relay verteilt Nachrichten an andere Verbindungen derselben Funktionsinstanz ohne gefundenen Nutzer-/Mandanten-/Sitzungsfilter. Die drei deklarierten Edge-Funktionen haben `verify_jwt=false`; weitere Nutzerprüfung wurde in den Handlern nicht gefunden. Aktive Deployments und Gateway-Regeln sind damit nicht bestätigt. Eine Verbindung oder simulierte Hardwaremetrik beweist keine reale GPU-/Hardwareberechnung.

Die nächste synthetische UI-Probe benötigt **vor Navigation** technische Sperren für ausgehendes HTTP und WebSocket, lokale Antworten für notwendige Dienste und einen Nachweis, dass keine externen Requests zugelassen wurden. Erst dann erfundene Klienten, Vektoren, Scans und Aufträge verwenden. Für ausgewählte synthetische Pfade ist inzwischen eine separate Playwright-Umgebung mit geprüften Sperren eingerichtet. Vollständige Thom-Anwendung, externe Dienste und echte Backendpfade sind weiterhin nicht abgenommen. Ein Login allein genügt nicht.

Der Betreiber hat sich im veröffentlichten Explorer angemeldet. Die Copen-V2- und Bohm-Abschnitte wurden im DOM bestätigt, ohne absichtlich neue Berechnungen, Datensätze oder Harmonisierungen auszulösen. Das ist Sichtbarkeit, keine vollständige Funktionsprüfung; Hintergrundaktivität wurde nicht aufgezeichnet. Thom blieb an der Login-Grenze, seine 3D-Scan-Oberfläche wurde nicht live abgenommen.

Belege: `MeridianDiagnosisPanel.tsx:204`, `useMeridianDiagnosis.ts:396,479`, `supabase/functions/meridian-diagnosis/index.ts`, `supabase/config.toml`, `RealtimeSyncService`, `RealtimeHarmonizationService`, `supabase/functions/realtime-sync/index.ts`.

## 6. Nächste Reihenfolge

Aktueller Anschluss: [gemeinsame Modulmatrix](AURELIA_MODULDATEN_BESTAND_2026-10-09.md) und [Datendomänen](AURELIA_DATENDOMAENEN_ECHTZEIT_2026-10-09.md) um die aktiven Cloud-Belege ergänzt. [Isolierter Rechte-/Lebenszyklusplan](superpowers/plans/2026-10-09-aurelia-isolierte-rechtepruefung.md) mit 22 Fallgruppen. Inzwischen [begrenzte P1-SQL-Charakterisierung](verification/AURELIA_P1_RECHTE_2026-10-09.md) abgeschlossen: 363 Aktionen, 317 erfüllt/46 Zielabweichungen. Echte Auth-, API-, Storage- und Worker-Prüfungen bleiben offen. Isolierte Umgebung, Schema-/Rollenbindung und echte künstliche Anmeldungen sind vor Ausführung nachzuweisen; keine Produktionstests mit künstlichen Writes aus diesem Plan ableiten.

Betreiberergänzung: [Aurelia-Administration für eigene 2D-Karten und weitere 3D-Modelle](AURELIA_ADMIN_ASSETS_VORMERKUNG_2026-10-09.md) als nachrangige Vormerkung aufgenommen. RadiThom-Import, Asset-/Mappingrevisionen und späterer 2D-Creator ergänzen die Anforderungen an die zentrale Datenhaltung; kein neues Analysemodul und noch keine Implementierung. Die folgenden Prüfungen behalten Vorrang.

Neue Ergänzung a–g: [Administration, gemeinsamer Generator, verlustfreie Medien/Layer, Frequenzreihen und kontrollierte PDF-/Office-/JSON-Importe](AURELIA_ADMIN_MEDIEN_IMPORT_VORMERKUNG_2026-10-09.md) sind als Bestand/Vormerkung aufgenommen. Noch keine neue Fähigkeit implementiert oder zentrale Struktur entschieden.

Weitere Betreibervorgabe: [modulübergreifende Favoriten, klientenbezogene Trends und optionale Benachrichtigungstrigger](AURELIA_FAVORITEN_TRENDS_TRIGGER_VORMERKUNG_2026-10-09.md). Herkunft und Vergleichbarkeit jeder Kennzahl erhalten; persönliche Favoriten von automatisch erkannten Kandidaten trennen. Trendarchiv, Regelrevisionen und Zustellprotokolle in der gemeinsamen Matrix berücksichtigen. Heute keine neue Auswertung, aktivierte Regel oder Mailzustellung.

1. Die eingerichtete abgeschirmte Testumgebung auf noch fehlende UI-/Workerpfade erweitern; keine Exportdaten an externe Modelle senden.

2. Bestätigte Copen/Bohm-Zuordnungs-/Pausengrenzen in Adapteranforderungen festhalten; Archiv-/Vorlagenfamilien und parallele Aufträge ergänzen. Thom anhand vollständiger 3D-Abnahmefälle und Feldbereiche prüfen.

3. Aktiver Struktur-/Bucket-Stand beider Lovable-Cloud-Projekte ist jetzt lesend erfasst und an Projekt-IDs/Quellcommits gebunden. Nächster Teil: effektive Rechte, legitime Delegation, Abo-/Mandantenkontext und tatsächliche Edge-/Worker-Versionen prüfen. Assetbestand/Lizenzen und Exportvollständigkeit bleiben getrennt offen. Quellstand, aktive Struktur und wirksamer Nutzerzugriff niemals gleichsetzen.

4. Gemeinsame Modulmatrix mit RadiWorks, Radi144, RadiMorphic und RadiFarben konsolidieren: Berichte/Archive, Trends/Archive, klientenbezogene Zwischenablagen, Vorlagen, Harmonisierungen, Trigger, Echtzeitereignisse und versionierte Assets ausdrücklich aufnehmen.

5. Danach zentrale Datenstruktur und Adapterverantwortung mit dem Betreiber entscheiden. Bis dahin keine Datenbankmigration oder Integrationsfreigabe.

Governors kann später bestätigte Erkenntnisse und offene Entscheidungen in der Projektmatrix nachvollziehbar verwalten. In diesem Block erfolgte keine neue Intake-Bestätigung, Routingänderung oder Modellübermittlung der Exporte. Die lokale heuristische Referenz bleibt von bestehenden externen Empfehlungen getrennt.

## 7. Nachweise und Sicherungsumfang

Private, Git-ignorierte Belege: `runtime/aurelia-three-modules-20261009/reference-plan/`. Enthalten Prüfscripte, aggregierte Ergebnisse, geprüfte Quellhashes, Browserabschnittsnachweis und konsolidierte Reviews. Keine Rohdatensatzwerte im öffentlichen Bericht. Vor Änderung der Bestands-/Wiederaufnahmedokumente wurde eine private Vorherkopie erstellt; Abschlussmanifest und Hash-Rücklesung sichern diesen begrenzten Arbeitsschritt. Frühere F:-Archive enthalten die neuen Belege noch nicht. Dies ist keine neue vollständige Governors-/Aurelia-/Server-Gesamtsicherung.

Tatsächliche Helfer: GPT-6 Luna/max für Thom-Grafik-/Scan-Bindungen; GPT-6 Astra/medium für externe Thom-Testgrenzen und die ergänzende Explorer-Eigentümerbewertung. Leitung gemäß Betreiberwahl Sol6.1/high; effektives Desktop-Modell/Reasoning ist durch diese Analyse nicht ausgelesen. Keine Tokenersparnis gemessen.

In der ergänzenden Rechenprüfung: Luna6/max erstellte die Copen-V2-Zahlenprobe; Astra6/medium prüfte die Bohm-/Hardware-Testaussagen und die Favoriten-/Trend-/Trigger-Vormerkung unabhängig. Parent führte die Bohm-/Collector-Proben aus und prüfte die Copen-Probe erneut. Keine rekursive Delegation, externe Exportübermittlung oder neue Produktfreigabe.

UI-Fortsetzung: Luna6/max erstellte und nach Review präzisierte die Thom-React-Probe; Astra6/medium prüfte Abschirmung und wesentliche Testergebnisgrenzen. Parent führte Bohm/Copen aus, wiederholte Thom und konsolidierte Nachweise. Kein Produktfix oder neue Integrationsfreigabe.

Begrenzter UI-Sicherungspunkt mit Zeitstempel: `runtime/aurelia-three-modules-20261009/reference-plan/completion/ui-20261009-182055`. Enthält aktuelle Berichte, Testskripte, Lockfile, Bundles, Receipts und Ergebnisse; Abhängigkeiten sind über das unveränderte Lockfile rekonstruierbar und nicht erneut kopiert. Der eigene Testserver auf 8125 wurde kontrolliert beendet. Keine vollständige Projekt-/DB-/Storage-Sicherung oder F:-Synchronisierung.

Nachtrag-Sicherungspunkt für Admin-/Medienvormerkung und fünf zusätzliche Archiv-/Vorlagenfälle: `runtime/aurelia-three-modules-20261009/reference-plan/completion/admin-media-20261009-190645`. Vorher vier Dokumentdateien gesichert; Abschlussdateien samt Manifest rückgelesen. Alle 562 gebundenen Explorer-/Thom-Quelldateien unverändert. Eigener Testserver8125 gezielt beendet; keine F:-Gesamtsicherung, Produktänderung oder Modulfreigabe. Helfer Luna6/max Verwaltungsbestand, Astra6/medium Architektur-/Copen-Review; Bohm-Archivprobe vom Parent.

Thom-Fortsetzung: Luna6/max führte die synthetischen Original-3D-Komponentenproben aus; Parent führte die parallelen Original-Hook- und Feldvertragsproben aus. Astra6/medium prüfte die wesentlichen Ergebnis- und Koordinatengrenzen unabhängig. Keine Produktkorrektur, Originalformeländerung oder Integrationsfreigabe. Begrenzter Abschlusscheckpoint: `runtime/aurelia-three-modules-20261009/reference-plan/completion/thom-3d-parallel-20261009-195407`; Quellen/Bundlebindungen/Belege manifestiert und rückgelesen, eigene Testports8126/8127 geschlossen. Keine F:-Gesamtsicherung.

Frühere Zugangsprüfung vor Plugin-Verbindung: [Thom](https://lovable.dev/projects/7d414a8e-f393-427d-962d-848204bdd57c?view=more&subview=cloud) und [Explorer](https://lovable.dev/projects/8432eebb-5390-4c07-83e7-bcddaaa60775?view=more&subview=cloud) vom Betreiber angegeben. Die [Lovable-Dokumentation](https://docs.lovable.dev/features/database) beschreibt SQL-Editor und RLS-Ansicht direkt unter More/Cloud. Öffentlicher Webabruf der Projektlinks scheiterte; damit keine Login-/Rechteaussage. Im aktuellen Chrome kein erkennbarer Debug-Steuerungszugang. Lovable-Plugin verfügbar, zum Prüfzeitpunkt nicht installiert/verbunden; dessen Eignung für aktive Metadaten noch ungeprüft. Keine Cloudabfrage ausgeführt, keine Browser-/Backendkonfiguration verändert.

Fortsetzung dieses Blocks: Luna6/max erstellte die unabhängige Geometrieprobe; Parent führte sieben Original-Service-/Archivfälle aus und bereitete den ausschließlich lesenden Lovable-Cloud-Strukturabgleich vor. Astra6/medium prüfte Methodik/Befunde/Metadatenlimits unabhängig. Fixturefehler und Review-Nachkorrekturen erhalten; keine Produktkorrektur oder Integrationsfreigabe. Begrenzter Abschlusscheckpoint: `runtime/aurelia-three-modules-20261009/reference-plan/completion/thom-geometry-services-20261009-221446`; alle kopierten Bytes manifestiert und rückgelesen, eigener8128Listener und Prüfchromium geschlossen. Keine neue F:-Gesamtsicherung.

Historischer Betreibernachtrag vor direkter API-Prüfung 2026-10-09T22:15:51.752251+02:00: PostgreSQL 17.6 für beide Lovable-Cloud-Projekte gemeldet. Betreiber bestätigt anschließend auch die Rolle postgres in beiden Projekten. Aktive Struktur, Rollenrechte und Projektidentität bleiben hier nicht unabhängig ausgelesen. Private Versionsreceipt unter reference-plan/db-metadata/VERSION_CONFIRMATION.json.

Cloud-Abschlusscheckpoint: runtime/aurelia-three-modules-20261009/reference-plan/completion/cloud-structure-20261009-224211. Acht API-Dateien exakt hashgebunden, alle kopierten Bytes rückgelesen; 562 Originaldateien weiterhin unverändert und beide Quellrepositories sauber. Private Metadaten, keine Cloud-/Storage-Vollsicherung; getrennte Projekt-/Bucket-Zeitpunkte, keine gemeinsame Atomarität. Tatsächlicher Helfereinsatz in diesem Anschlussblock: Astra6/medium prüfte abgeleitete Rechte-/Medienbefunde; keine Rohinventare an den Review-Agenten weitergegeben.

Vorbereitungscheckpoint der gemeinsamen Matrix/Rechteplanung: `runtime/aurelia-three-modules-20261009/reference-plan/rights-plan-20261009-225742`. Vier Vorherkopien, Vorreview-Plan und abgeleitete Reviewkorrekturen erhalten; Dokumentverweise, Reviewergänzungen und Resume-Tail geprüft; Abschlussdateien manifestiert und rückgelesen. Keine Rechtefälle ausgeführt oder Produkte geändert. Tatsächliche Helfer Luna6/max Datendomänen-Abdeckung, Astra6/medium Planreview; historische Cloud-/Referenzbelege bleiben separat erhalten.

Aktueller P1-Anschluss: 14 ausgewählte Tabellen an explizite lesend freigegebene Clouddefinitionen gebunden und unter normalen simulierten Rollen geprüft. Thom-Querreferenzen und Explorer-Patientbezüge erlauben widersprüchliche Verknüpfungen; direkte SQL-TRUNCATE-Grants erlauben tabellenweites Leeren trotz RLS. Keine daraus behauptete Fremdinhaltslese oder erreichbare API-Ausnutzung. Normale CRUD-Gegenfälle/NULL-Policywirkung im Umfang bestätigt; eigene Testinstanz beendet. Quellen, Algorithmen, Cloudbestand, Live-Instanzen und S4.8 unverändert. Methoden-/Ergebnisreview nur mit bereinigten Fakten durch Astra6/medium; Luna6/max prüfte Quellabhängigkeiten. Geschützte Rohdefinitionen nicht weitergegeben. Vollständiger Nachweis: docs/verification/AURELIA_P1_RECHTE_2026-10-09.md.
