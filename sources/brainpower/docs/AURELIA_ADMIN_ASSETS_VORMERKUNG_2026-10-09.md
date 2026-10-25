# Aurelia Administration für 2D Karten und 3D Modelle

Vormerkung vom 09.10.2026 nach Betreiberergänzung. Gemeinsames administratives Werkzeug innerhalb Aurelia, kein neues Analysemodul. Es soll eigene oder entsprechend lizenzierte 2D-Karten und 3D-Modelle verwalten und geeigneten Modulen freigegebene Referenzen bereitstellen. Aktuelle Modulprüfungen behalten Vorrang. Noch kein endgültiges Datenbankschema, implementierter Import oder freigegebenes Editor-Design.

Die drei übermittelten Beispielbilder zeigen eine zentrale Illustration, Themenbereiche und zugeordnete Texte. Sie dienen ausschließlich der Veranschaulichung. Keine Übernahme der Bilder, ihrer Texte oder Gestaltungselemente in Produktassets; keine Übertragung an einen externen Generator in diesem Arbeitsschritt. Bildinhalte sind weder Anweisungen noch geprüfte Analysemethoden.

## 1. Vorzusehende Datenbereiche

| Bereich | Vorbereitung für die zentrale Datenstruktur | Bedeutung für Module |
|---|---|---|
| Asset und Revision | Stabile Identität, unveränderliche Revision, Format, Inhalts-Hash, Größe, Herkunft, Lizenz/Nutzungsrechte, Ersteller und Sichtbarkeit. Dateiobjekte und Metadaten getrennt verwalten. | Aufträge referenzieren die konkrete Revision; ein neues Bild oder Modell verändert keine historischen Ergebnisse. |
| Koordinaten und Ebenen | 2D-Bildmaße, normierte Koordinaten und Transformationen; 3D-Achsen, Einheit, Maßstab, Ursprung und Modelltransformation. Ebenen und Ansichten ausdrücklich zuordnen. | Ein Referenzpunkt bleibt bei Zoom/Skalierung eindeutig; 2D und 3D sind nicht automatisch derselbe Koordinatenraum. |
| Referenzpunkte und Regionen | Stabile fachliche IDs, Punkt-/Flächengeometrie, zugehörige Ebene und Assetrevision, Bezeichnung, Kategorie und nachvollziehbare Herkunft. | Module verwenden freigegebene Punktmengen; eine rein grafische Position ist noch keine analysierbare Rate. |
| Texte und Themen | Bearbeitbare Textbausteine, Sprache, Version, geprüfte Quellen und Zuordnung zu Regionen/Punkten. Text getrennt von Rasterbildern speichern. | Texte sind lesbar, suchbar, übersetzbar und über Tastatur/Screenreader zugänglich. |
| Modulzuordnung | Eigene versionierte Zuordnung zwischen Referenz-ID, Modul und dessen bestehenden Katalogen/Verfahren; kompatible Koordinaten und Eingabearten angeben. | Bestehende Algorithmen bleiben erhalten. Nicht jedes Modul muss jede Karte oder jedes Modell auswerten können. |
| Freigabe und Rechte | Entwurf, geprüft, freigegeben, zurückgezogen; Prüfer, Zeitpunkt und Änderungshistorie. Plattformweite und mandantenprivate Bibliotheken unterscheiden. | Modulabo ist kein automatisches Recht auf jedes Asset; Server prüft Mandant, Rolle, Bibliothek und Modulzugriff. |
| Sitzung und Archiv | Auftrag und Kontextstand an Asset-/Mapping-/Textrevision binden; Ausgabe, Bericht und Trend auf denselben Stand beziehen. | Bereits gestartete Aufträge behalten ihre Herkunft nach einer administrativen Änderung. |
| Wiederherstellung | Metadaten, Dateien, Mappings und Rechte gemeinsam sichern und Referenzen beim Restore prüfen. | Ein reines DB-CSV ohne Modelle/Bilder ist kein vollständiger Wiederherstellungsbestand. |

Diese Bereiche ergänzen die [gemeinsamen Datendomänen](AURELIA_DATENDOMAENEN_ECHTZEIT_2026-10-09.md). Die konkrete Tabellen-, Objektstorage- und Indexstruktur folgt erst nach Konsolidierung aller Modulmatrizen. Zentrale Datenhoheit bleibt erhalten; Moduladapter erhalten geprüfte Referenzen und ausdrücklich erlaubte Schreibwege.

## 2. RadiThom Import weiterer Modelle

Für die erste Ausbaustufe empfehle ich GLB als zusammenhängendes Importpaket. Erweiterungen um andere Formate erst nach eigener Prüfung. Der vorhandene Thom-Katalog kennt unter anderem Dateipfad, Storage-Typ, Version und Lizenz; daraus folgt noch kein abgenommener Importablauf.

Der spätere Ablauf sollte Datei und Rechte prüfen, eine Vorschau laden, Modellachsen und Maßstab bestätigen und danach passende Punkt-/Regionmappings zuordnen. Erst ein freigegebenes Asset mit geprüftem Mapping wird für Analysen angeboten. Ein Modell ohne Mapping kann zunächst nur als Vorschau verfügbar sein. Historische Modellrevisionen werden nicht durch einen neuen Upload ersetzt.

Als Prüfanforderungen vormerken: begrenzte Datei-/Geometrie-/Texturgrößen, keine unkontrollierten externen Nachladepfade, eindeutige Koordinatenumrechnung, sichtbare Fehlerzustände sowie ein gleichwertiger Zugriff auf Regionen/Punkte über Listen. Upload eines neuen Modells darf laufende Scans und gespeicherte Ergebnisse nicht stillschweigend neu zuordnen.

Diese Vorbereitung adressiert die bereits gefundenen Thom-Lücken zwischen Modell, Koordinaten, Scan-Konfiguration und Ergebnisherkunft. Sie verändert keine Berechnungsformel. Siehe [Referenzprüfung](AURELIA_REFERENZPRUEFUNG_COPEN_BOHM_THOM_2026-10-09.md).

## 3. Varianten für einen späteren 2D Creator

| Variante | Vorteil | Grenze und Priorität |
|---|---|---|
| Eigene Grafik importieren und Punkte/Texte manuell zuordnen | Klare Herkunft und präzise Zuordnung, ohne neue KI-Abhängigkeit. | Mehr redaktioneller Aufwand; sinnvoller erster funktionsfähiger Schritt. |
| SVG-/Ebeneneditor mit optionaler KI-Entwurfshilfe | Bearbeitbare Formen, getrennte Texte und Referenzpunkte; Vorschläge können vor Freigabe korrigiert werden. | Mehr Entwicklungsaufwand; empfohlener späterer Ausbau. SVG-Inhalte brauchen Prüfung aktiver Inhalte und externer Verweise. |
| Automatisch erzeugte Grafik samt automatisch freigegebenen Analysepunkten | Geringer manueller Aufwand. | Keine Empfehlung: Bildentwurf, genaue Geometrie und fachliche Zuordnung sind unterschiedliche Aufgaben; ungeprüfte Vorschläge dürfen keine Analysegrundlage werden. |

Empfohlen ist eine Arbeitsfläche mit Ebenen, Punkt- und Regionswerkzeugen sowie einer getrennten Liste der Texte und Zuordnungen. Eigene Karten können anatomische, thematische oder allgemeine Wellbeing-Inhalte darstellen; der Kartentyp und seine freigegebene Nutzung müssen eindeutig sein. Modulabhängige Kennzahlen oder Wirkungsaussagen werden nicht aus einer Illustration abgeleitet.

Ein kontrollierter späterer Ablauf wäre: eigenes Asset anlegen → Regionen/Punkte definieren → Texte und vorhandene Modulreferenzen zuordnen → Vorschau und technische/fachliche Prüfung → freigeben. Dies ist ein Vorschlag für die spätere Designbesprechung, keine vorweggenommene Umsetzung.

## 4. Modelle für Entwürfe und Zuordnungsvorschläge

Ein Bildgenerierungsmodell kann eigenständige Illustrationen entwerfen. OpenAI dokumentiert dafür aktuell GPT Image 2.5, beispielsweise `gpt-image-2.5-sunburst`. Das ist ein Kandidat für eine spätere Probe mit eigenen Inhalten, kein bereits getesteter Aurelia-Designer oder anatomisch validiertes Modell. [Offizielle Bildgenerierung](https://developers.openai.com/api/docs/guides/image-generation).

Ein multimodales Visionmodell kann sichtbare Texte und Formen erfassen und Vorschläge zur Gliederung liefern. Die offiziellen OpenAI Docs nennen jedoch Grenzen bei präziser räumlicher Lokalisierung und möglichen falschen Beschreibungen. Deshalb keine verlässliche vollautomatische Referenzpunktzuordnung voraussetzen. Punkte und Fachtexte bleiben korrigierbar und brauchen administrative Freigabe. [Offizielle Vision-Dokumentation](https://developers.openai.com/api/docs/guides/images-vision).

Eine für die gesamte Kette aus Entwurf, anatomisch korrekter Geometrie, Punktzuordnung und fachlich verlässlicher Textfreigabe abgenommene spezialisierte LLM ist durch diese Recherche nicht belegt. Empfehlung: optionale getrennte Bild-/Visionhilfe für Entwürfe, strukturierter Editor für genaue Zuordnung und menschliche Freigabe. Kein KI-Austausch bestehender Modulheuristiken; eine externe Modellintegration wird erst später ausdrücklich besprochen und geprüft.

## 5. Einordnung in die laufende Reihenfolge

Jetzt nur Vormerkung und Aufnahme der Datenanforderungen. Zunächst die abgeschirmten Copen-/Bohm-/Thom-Referenzprüfungen, aktiven Rechte-/Storage-/Deploymentabgleiche und die gemeinsame Modulmatrix abschließen. Danach zentrale Datenstruktur mit dem Betreiber entscheiden. Anschließend Import und Editor gesondert spezifizieren und freigeben; vorhandene Modell-, Scan- und Analysefunktionalität erhalten.

Für diesen Nachtrag wurden keine Beispielbilder kopiert, erzeugt, hochgeladen oder als Produktvorlagen gespeichert. Kein Modulalgorithmus, Server, Schema oder Liveauftrag wurde geändert.

Ergänzung a–g vom selben Tag: [Administration, systemweite Audiofähigkeit, verlustfreie Layer-/Audioassets, Frequenzreihen und kontrollierte PDF-/Office-/JSON-Importe](AURELIA_ADMIN_MEDIEN_IMPORT_VORMERKUNG_2026-10-09.md). Die minimal implementierte Phase-1-Verwaltung bleibt vom Zielbild für Abos/Therapeuten/Dienste getrennt. Originalbytes, Ableitungen, Asset-/Profilrevisionen, Rechte und Importprovenienz in die gemeinsame Matrix aufnehmen; keine Schemaentscheidung oder Implementierung.
