# Modulübergang und Betreiberprüfung

Betreiberauftrag vom20.09.2026: Vor Übergang zu einzelnen Modulen ausdrücklich informieren, Überarbeitungsbedarf und Live-Prüfungen gemeinsam einordnen; zusätzliche Module können eigene Vorbereitungsarbeit benötigen. Fortschritt detailliert an den tatsächlichen Phasen und Belegen berichten. Dies ist eine Arbeitsregel dieses Projekts, keine zeitgesteuerte Benachrichtigung.

## Aktuelle Position

Begrenzte synthetische T1–T3-Prüfungen abgeschlossen. Gemeinsamer REST-/Identitätsvertrag als Kandidat konkretisiert. RadiWorks ist als erstes vorzubereitendes Modul benannt; seine konkrete Quellfassung und sein M0-Umfang sind noch festzustellen. Keine externe Produktimplementierung und keine S4-/S5-Freigabe. Aurelia AGENTS.project.md: Produktarbeit pausiert bis G0-SRV-GROUND-ZERO-Abnahme; anschließend AUDIT-02. Diese Reihenfolge ist vor produktiver Adapterarbeit maßgeblich.

## RadiWorks-Fortsetzung, 26.09.2026

Die beiden manuellen Hermes-Einzelreviewwege sind durch den Betreiber für die lokale Modulvorbereitung als Teilabnahme bestätigt. RadiWorks ist mit eindeutigem Repository und HEAD in M0 aufgenommen; ein isolierter synthetischer M2-Live-Test, 205 Engine-Tests und eine responsive Browserprüfung sind belegt. Der Betreiber bestätigte für M1 die empfohlene Reihenfolge Analyse/Fälle → Draft/Freigabe → Broadcast/Live. Fallnamenskollision und Browser-Wiederaufnahme wurden lokal behoben; synthetische Draft-/WebSocket-Livepfade, eine CopyGuard-Sperre für direkten Operator-Broadcast, eine browsergeprüfte sichere Clarke-Darstellung und 209 Engine-Tests sind belegt. Konkrete fachliche Betreiberbeobachtungen sowie M3/M4 und S4 bleiben offen. [Quellen, Testumfang und Restliste](verification/RADIWORKS_M0_M2_2026-09-26.md). Frühere RadiWorks-Modellreviews sind nach der lokalen CSS-Änderung historische Belege; vor neuem Modellentscheid ist frische Quellenbindung nötig.

## Beschlossene Reihenfolge, präzisiert am 25.09.2026

Aktuelle Betreiberpräzisierung vom 01.10.2026: RadiWorks bleibt vor Radi144. Der wiederhergestellte lokale Katalog und eine einzelne erfolgreiche Analyse sind nur Teilnachweise; vor dem Modulwechsel müssen die ursprünglichen RadiWorks-Funktionen und die 2.9.0-Abweichungen mit realem Katalog systematisch abgeglichen und fachlich geprüft sein. [Aktueller Live-Befund](verification/RADIWORKS_LIVE_CATALOG_2026-10-01.md). Der [isolierte Nachtestkandidat](verification/RADIWORKS_KANDIDAT_2026-10-01.md) und die [Fortress-Einordnung](verification/AURELIA_FORTRESS_INTAKE_2026-10-01.md) ergänzen den Plan ohne Modul- oder Modellfreigabe.

1. **Hermes-Modellrollen und Bedienpfade abschließen:** Den bisherigen Terra-/Supervisor-Weg und Route B mit Sol 6/high, unabhängigem Luna 6/max und bedingtem bzw. ausdrücklich gewähltem Astra 6/medium je ausgewähltem Projekt/Modul praktisch prüfen. Der Betreiber wählt **bei jedem Auftrag ausdrücklich** einen der beiden Wege; es gibt keine gespeicherte Standardroute je Projekt oder Modul. Beide Wege müssen in der Oberfläche bewusst wählbar, mit tatsächlicher Modellidentität/Effort, Quellenbindung, Versandfreigabe, Fehler-/Timeoutverhalten und getrenntem Ergebnis belegt sein. Automatische Reviews bleiben aus; kein Weg darf still auf den anderen ausweichen. Die bestehende Route-B-Matrixplanfunktion wird vorläufig nur gegen ihre Sperren und synthetischen Nachweise geprüft: Ein **vollständiger realer Matrixplan** folgt erst nach allen Modul-Prototypen.
2. **Module einzeln zu integrierbaren Prototypen bringen:** RadiWorks → Radi144 → `morphic_v1` (vom Betreiber als „Radimorphic“ bezeichnet) → ein vollständig neues Modul mit eigenem, noch zu bestimmendem Projektpfad. Je Modul M0–M4 mit eigener Quellfassung, Restliste, isolierten Tests, geeignetem lokalen Live-Betrieb, Betreiberbeobachtungen, Anpassungen und erneutem Test bis zur gesonderten fachlichen Finalisierung durchführen. Bei einer Browseroberfläche den lokalen Live-View nutzen; bei Headless-Betrieb den passenden API-/Vertragsweg. Module, Daten, Testprofile und Ports bleiben getrennt. M4 verlangt einen versionierten Schnittstellen- und Datenvertrag, passende Mandanten-/Rechte-Negativtests sowie getrennte technische und fachliche Nachweise; ein Live-Bild allein genügt nicht. Die visuelle Aurelia-Vorlage D0–D3 wird je Modul soweit lokal prüfbar vorbereitet; Aurelia-Code oder Serverbetrieb werden dadurch nicht vorweggenommen.
3. **Dann den vollständigen Matrixplan erstellen:** Erst wenn alle vier vorgesehenen Prototypen mit ihren tatsächlichen Versionen, Verträgen, offenen Grenzen und Live-Nachweisen vorliegen, den Gruppen- und Modulumfang frisch aufnehmen. Abhängigkeiten, Sicherheits-/Betriebsanforderungen und D0–D4 im Plan berücksichtigen; Route und unabhängigen Review bewusst wählen. Ein Plankandidat wird separat geprüft und ausdrücklich übernommen. Weder Review noch Plan sind eine Ausführungsfreigabe.
4. **Danach Aurelia schrittweise implementieren und integrieren:** Das Aurelia-Hauptmodul mit Identität/Mandantenrechten, verbindlichem REST-/bestehendem ABI-Vertrag, CopyGuard, Dienstgrenzen, Daten-/Backup-/Recoverypfad und den benötigten Plattformbereichen stufenweise auf dem tatsächlich verifizierten Linux-Zielsystem aufbauen. Jedes Modul erhält eigene Integrations-, Negativ-, Live-, Rollback- und Freigabebelege. G0-SRV-GROUND-ZERO und AUDIT-02 bleiben vor Aurelia-Produktarbeit maßgeblich; M5/M6 und S5 sind spätere ausdrückliche Entscheidungen.

Diese Reihenfolge ist eine Betreiberpriorität, keine stillschweigende Freigabe von Produktcode, Modellversand oder Serveränderungen. Der neue Prototyp erhält vor M0 eine eindeutige Quelle, einen eigenen Projektpfad und einen bestätigten Umfang. Die bestehende Governor-Gate-Matrix zeigt weiterhin aktuelle Belege und offene Schritte; sie ist **nicht** der spätere vollständige Produkt-Matrixplan. Die historische [Gesamtmatrix vom 20.09.](PROJEKTMATRIX_2026-09-20.md) bleibt ein datierter Ausgangsstand und wird durch diese Entscheidung nicht rückwirkend geändert.

## Verbindliche Mitteilung vor jedem Modulübergang

Vor Bearbeitung eines konkreten Moduls im Chat nennen: Modulname und Quelle, aktueller belegter Stand, noch unbestätigte Angaben, vorgesehener Umfang, benötigte Betreiberüberarbeitung und geplante Live-Prüfung. Die Reihenfolge beginnt nach dem Hermes-Abschluss mit RadiWorks; konkrete Quellfassung, inhaltliche Überarbeitung und tatsächliche Übernahme bleiben je Modul getrennte Entscheidungen. Eine aktuelle Bestätigung des konkreten Umfangs abwarten, wenn Auswahl oder inhaltliche Überarbeitung noch offen sind.

| Schritt | Ergebnis / Beleg | Betreiberbeteiligung |
|---|---|---|
| M0 Aufnahme | Eindeutiges Repository, Version/Quellhash, Funktionsumfang, Abhängigkeiten, bestehender Status und UI-Oberfläche oder Headless-Betrieb | Bestätigt, welches Modul und welche Fassung berücksichtigt werden sollen |
| M1 Überarbeitung | Konkrete fachliche/technische Restliste, getrennt nach vorhanden und neu benötigt | Eigene Anpassungen benennen oder durchführen; veränderte Quellen anschließend erneut abgleichen |
| M2 Einzelbetrieb | Wiederholbarer Start und Tests mit synthetischen Daten; isolierter Funktionsnachweis | Reale Bedienung live prüfen und konkrete Beobachtungen rückmelden |
| M3 Aurelia-Vertrag | Manifest/Schemas/Release, Identität/Mandanten, CopyGuard und angebotene Schnittstellen geprüft; zusätzlich den getrennten [Design-Template-Plan](AURELIA_DESIGN_TEMPLATE.md) D0–D4 für die Aurelia-Oberfläche und dieses Modul zuordnen | Funktionsumfang, Design-Akzentwahl und erforderliche Abweichungen abstimmen |
| M4 S4-Abnahme | Alle zutreffenden kumulativen Reifegradkriterien einzeln belegt | Fachliche Annahme getrennt von technischen Tests festhalten |
| M5 Serverintegration | Freigegebene Übertragung, Dienst-/Limit-/Rollback- und passende Backup-/Restorebelege | Konkrete Integration genehmigen; gemeinsame Live-Abnahme |
| M6 Registrierung/S5 | Tatsächlicher Registry-/Freigabeakt mit Version und Belegen | Eigene Freigabe; niemals automatisch aus grünen Tests |

Live-Prüfung bezeichnet hier tatsächlichen Betrieb des vorgesehenen Testumfangs, nicht automatisch Produktion, reale Klientendaten oder Hardwareaktivierung. Bei Änderungen nach Abnahme nur betroffene Nachweise erneut prüfen, Abhängigkeiten/Hashes dabei berücksichtigen.

## Zusätzliche Module

Neue Module beginnen ebenfalls bei M0. Name, Quelle, Zweck und Abhängigkeiten zuerst eindeutig aufnehmen; keine erfundenen Reifegrade oder automatische Gleichsetzung ähnlich benannter Projekte. Vorhandene Templates und Testadapter wiederverwenden, soweit kompatibel. Ein neues Modul erhält eigene Vertrags-, Test-, Live- und Freigabebelege. Die Zahl zusätzlicher Module wird nicht ohne Betreiberangabe festgeschrieben.

Das gemeinsame Hermes-/Governor-Design ist nur eine **visuelle Vorlage** für Aurelia und die Modulanzeigen. Der D0–D4-Strang gilt auch für später hinzukommende Module und wird in der Matrix als offene Planung getrennt von abgenommenen Produktgates gezeigt. Jede Modulkennung erhält eine eigene wählbare Akzentpalette; bei einem Modul ohne eigene UI betrifft sie dessen Aurelia-Oberfläche. Keine gemeinsame Farbe, kein Fortschritt und keine Freigabe werden von einem anderen Modul übernommen. Siehe [AURELIA_DESIGN_TEMPLATE.md](AURELIA_DESIGN_TEMPLATE.md).

## Fortschrittsmeldung

Bei jedem Phasenwechsel kurz tabellarisch melden: abgeschlossen/belegt, aktuell in Arbeit, offen, nächster Betreiberpunkt. Prozentangaben nur bei festem benanntem Umfang; Testanzahl ist kein Projektfortschrittsprozent. Quellenabgleich, funktionale Implementierung, Live-Abnahme und Freigabe getrennt ausweisen.

## Voraussetzungen vor produktiver Aurelia-Integration (M5/M6)

Aktuelle G0-Belege und offene Kriterien zuordnen → erforderliche Betriebs-/Recoveryentscheidungen und Serverabnahme → AUDIT-02/Identitätsgrundlage → verbindliche Vertragsübernahme → jeweilige M5-/M6-Entscheidung. Nach der Hermes-Funktionsabnahme kann die lokale M0–M4-Modulvorbereitung in der oben festgelegten Reihenfolge und unter den eigenen Modulregeln laufen. Arbeit am Aurelia-Produktcode, produktive Adapter und Serverintegration warten auf G0 und AUDIT-02; lokale Tests oder vorbereitete Verträge erteilen dafür keine Freigabe.
