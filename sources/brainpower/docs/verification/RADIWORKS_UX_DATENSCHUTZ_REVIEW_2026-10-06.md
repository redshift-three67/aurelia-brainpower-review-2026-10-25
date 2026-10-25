# RadiWorks: Katalog- und Qualitätsreview

Stand: 2026-10-06. Kandidat: runtime/rw-options-20261006, Port 8112. Produktmanifest: 615ffb32b98951f60ee206449b755071c2414abb82269b941ae0ee80543c22aa, 172 Produktdateien. Begrenzter technischer Review und Korrekturplan, keine Integrationsfreigabe oder rechtliche Zertifizierung.

## 1. Warum nur eine Datenbank angezeigt wird

| Prüfpunkt | Ergebnis | Bedeutung |
| --- | --- | --- |
| Alte Liveinstanz 8103 | 123 Datenbanken, API erreichbar | Bisheriger Bestand verfügbar. |
| Kandidat 8112 | Eine Datenbank: SYNTHETIC_Options | Absichtlich getrennt konfigurierter synthetischer Prüfstand. Strg+F5 ändert dessen Katalog nicht. |
| Veröffentlichter Livekatalog e33ea136d8ea448fada7524757385ee4 | 126 Dateien, 123 Datenbanken; Größen und SHA-256 geprüft | Kein festgestellter Verlust im geprüften Bestand. |
| Älterer Katalog | 76 Datenbanken, Teilmenge des neueren | Kein Rückgang auf den älteren Bestand festgestellt. |
| Namen nach CopyGuard-Projektion | Entsprechen den 123 API-Einträgen von 8103 | Ein Name wird geschützt. |
| Auswahl dieses geschützten Namens | Isoliert: 149 Raten über internen Selektor, 0 über angezeigten Platzhalter | Zusätzlich reproduzierter Auswahlfehler; Vollkatalog allein behebt ihn nicht. |

Die aktive evidence/browser-8112-config.json verweist auf runtime/rw-options-browser-8112/data. Der Livekatalog liegt unter runtime/radiworks-catalog-releases/e33ea136d8ea448fada7524757385ee4/data.

Beim Auswahlfehler liefert /databases Namen (engine/src/radiworks/api/routes.py:1830); die globale JSON-Projektion schützt Strings (engine/src/radiworks/main.py:312). Die UI verwendet den projizierten Namen zugleich als technischen Auswahlwert (webapp/js/views/analyze.js:307,378). Die Repository-Suche bleibt namens-/präfixbasiert (core/rates.py:119). Der Anzeigeplatzhalter kann deshalb nicht auf die ursprüngliche Datei zeigen.

**Empfehlung:** Stabile Katalog-IDs und getrennte sichere Anzeigenamen. Datei-, Präfix-, Gruppen- und Reihenfolgebedeutung sowie gespeicherte Altsitzungen kompatibel erhalten. CopyGuard nicht abschalten; Raten und Algorithmen nicht umschreiben. Published-Kataloge bleiben unveränderlich mit Manifestbindung.

Eine konkrete **inaktive** Vorlage evidence/browser-8112-full-catalog-PROPOSED.json erhält Kandidat, Port, Home, Scope und Schlüsselpfad; nur der Datenpfad zeigt auf den geprüften Release. Aktive Konfiguration unverändert, kein Restart. Vor Aktivierung: Original-/persönliche-/Vergleichs-/Watchlist-/Broadcast-Aufträge und ungespeicherte Formulare prüfen, geordnet wechseln und Wiederanlauf nachweisen. Der persönliche Einzelkatalog behält seine bestehende Kapazitätsgrenze; ein größerer Originalbestand hebt sie nicht auf.

Belege: evidence/catalog-review.json und catalog-selector-review.json.

## 2. Priorisierte Befunde

P1 = vor Weitergabe/Liveübernahme des neuen Kandidaten klären; P2 = wichtiger Bedienungs- oder Integrationsschritt.

| ID | Priorität | Befund | Stabile Korrektur und Abnahme |
| --- | --- | --- | --- |
| UX-01 | P1 | CopyGuard verändert einen technischen Datenbankselektor. | IDs/Labels trennen; alle 123 Auswahlen, Gruppen, Altsitzungen und Schutzprojektion prüfen. |
| UX-02 | P1 | Offenes Broadcast-Dock verdeckt Tastaturfokus vollständig. | Fokus abhängig von tatsächlicher Dockhöhe sichtbar halten. Dockgröße und Aufträge bewahren; Tastaturprobe bei offenem/geschlossenem Dock und Vergrößerung. |
| DS-01 | P1 | API-/WebSocket-Ziele lassen sich über URL/Modulkonfiguration auf fremde Origins setzen. | Lokales Paket auf vorgesehene lokale Ziele begrenzen. Später nur vertrauenswürdige Aurelia-Konfiguration mit expliziter Freigabe. Abgelehnte Ziele dürfen keine Falldaten erhalten. |
| UX-03 | P2 | Tabnavigation überläuft bei 200 % Textvergrößerung. | Navigation unabhängig vom 900-px-Breakpoint intern begrenzen/scrollbar halten; fokussierten Tab sichtbar machen. |
| UX-04 | P2 | Prüfstand und Katalogumfang sind nicht ausreichend erkennbar. | Kandidat/Live, Port, Anzahl und Katalogstand sichtbar erklären. |
| UX-05 | P2 | Startseite beschreibt geplante Aurelia-Zusammenarbeit als aktuelle Pipeline. | Geplante Architektur kennzeichnen, Modul-/Integrationsstatus getrennt von Analysefortschritt. |
| UX-06 | P2 | Viele Fachbegriffe und gleichrangige Aktionen erschweren die Reihenfolge. | Ergänzende nummerierte Hauptfolge, verständliche Aktionen, kurze lokale Hilfen; bestätigte freie Abläufe erhalten. |
| DS-02 | Vor personenbezogenen Echtdaten bewerten | Fall-JSON und Kontextbilder auf Anwendungsebene unverschlüsselt. | Berechtigungen, Geräte-/Backupverschlüsselung und Schlüsselkonzept prüfen. Fernet-Journal nicht als Vollverschlüsselung darstellen. |
| DS-03 | Vor zentralem Aurelia-Betrieb | Vollständiger Fall-/Bild-/Verlaufslösch- und Exportlebenszyklus nicht nachgewiesen. | Aufbewahrung, zulässige Historie, Löschung, Export und Backupablauf gemeinsam planen. |
| DS-04 | Vor S4.8 | Lokale Scope-Grenzen ersetzen keine Mandanten-/Aboautorisierung. | Identität, Tenant, Modulrechte serverseitig und durch Adapter/Storage binden; tenantübergreifende Negativtests. |

### Reproduzierbare Layoutbefunde

Bei 1440 × 1000 liegt das offene Dock zwischen y=550 und y=1000. Echte Tab-Tastendrücke fokussieren watchlist-load und watchlist-preview vollständig hinter dem Dock. Die Datenbanksuche ist nur teilweise verdeckt und wird deshalb nicht als vollständig verdeckt bewertet. Belege: ux-audit.json (activeElement-Verlauf), ux-focus-confirmation.json, playwright-test-rw-focus-confirm.js und maskiertes ux-focus-covered.png; CSS app.css:532.

Bei 1280 × 900 und auf 200 % vergrößertem HTML-/Body-Text steigt die Dokumentbreite auf 1498 px. Nur die Tabs Einstellungen und Über/Quellen stehen über. .tabs ist ein Flexcontainer (app.css:103); interne horizontale Begrenzung greift erst unter 900 px (:615). Gezielt geprüfte Textvergrößerung, keine vollständige Browserzoom-Zertifizierung. Beleg: ux-text-resize-confirmation.json.

### Datenschutzgrenzen genau unterscheiden

webapp/js/api.js:5–10,17–18,53–55 akzeptiert absolute API-/WS-Ziele ohne Originfreigabe. Bei wirksamer Fremdkonfiguration, entsprechender Nutzeraktion und erfolgreichen Browser-/CORS-Prüfungen könnten neu eingegebene Daten an das fremde Ziel gehen. **Kein aktueller Datenabfluss oder fremder Zugriff auf vorhandene lokale Fälle wurde nachgewiesen.** Standard ist die eigene Origin.

Fallakten werden als JSON geschrieben (core/cases.py:337, persistence.py:52), Fokusbilder als PNG (core/context_images.py:80). Unveränderliche Auftragssnapshots erhalten bewusst frühere Angaben (core/personal_context.py:143). Neue automatisch benannte Fälle haben neutrale Datei-IDs; ältere manuelle Namen können im Dateinamen stehen (core/cases.py:60). Geräteverschlüsselung und tatsächliche ACLs wurden nicht bestätigt. Historienerhalt ist funktional wichtig, benötigt aber ein bewusstes Aufbewahrungs-/Löschkonzept.

„Fokusbild entfernen“ entfernt die aktuelle Referenz, nicht die content-addressierte Datei (webapp/js/case-personal.js:88). Im geprüften Routenumfang wurde kein vollständiges Lösch-API oder gebündelter Export samt Bildern/Verlauf gefunden; Fall-JSON ist lesbar abrufbar. Das ist eine Planungslücke, keine Aussage, dass Daten prinzipiell nicht manuell exportierbar seien.

Fernet schützt Seed, Quelle und Segment im Entropie-Journal, nicht sämtliche Akten/Bilder (entropy_journal.py). Kamera-Frames werden im Browser ausgewertet; an die lokale API gehen abgeleitete Ganzzahlen (views/entropy.js:124). Stochastik kann random.org kontaktieren (entropy.py:56): Die geprüfte feste Integer-Abfrage enthält keine Fallfelder, aber der Anbieter sieht Verbindungsmetadaten. Die Zwischenablage sendet nichts automatisch an eine KI; externe Weitergabe bleibt bewusst zu prüfen. Browserberechtigungen und Clipboard-Kurzbefehle zusätzlich manuell prüfen.

Lokaler Scope-Resolver und Host-/Originprüfung sind vorhanden (scope.py:83, main.py:293); sie ersetzen keine Aurelia-Authentifizierung. Ein geplanter Adaptervertrag ist kein Nachweis produktiv abgenommener Multi-Tenant-Speicherung.

## 3. Verständliche Bedienung und Schriften

Die vorhandene ruhige Designsprache bleibt Grundlage. Empfohlene ergänzende Hauptfolge:

| Schritt | Hauptaktion | Kurze Orientierung |
| --- | --- | --- |
| 1 | Fall vorbereiten und speichern | Aktiver Fall, Kontextstand und Speicherbestätigung sichtbar. |
| 2 | Datenbank auswählen | Suche/Fokusvorschläge helfen; Nutzer bestätigt Katalog. |
| 3 | Verfahren und Zufall wählen | Original/Persönliche Heuristik getrennt von reproduzierbar/stochastisch. |
| 4 | Analyse starten | Quelle, Verfahren und Auftragsstatus unmittelbar zeigen. |
| 5 | Ergebnis prüfen | GV-Runde, Seitenprüfung und persönlicher Score unterscheiden. |
| 6 | Virtuellen Broadcast vorbereiten | Zielkontext/Raten prüfen, bewusst starten, Verlauf zugeordnet erhalten. |

Kein erzwungener Assistent: Nummer, Text und Zustand vermitteln die Folge; Farbe ergänzt. Tab-/Moduswechsel verändern keine laufenden Aufträge. Vergleich/EXP1 und Expertenfunktionen bleiben getrennt und erreichbar.

Vorschläge: „Prüfentwurf“ statt „Prüfdraft“, „Prüfung bestätigen“ statt „Prüfen → bereit“, „Für virtuellen Broadcast freigeben“ statt „Promote“. Grounding, Clear und Training brauchen kurze tatsächliche Funktionsbeschreibungen, ohne reale Hardware-/Heilwirkung zu suggerieren. GV/EW/HIT/GV-RE/REC erhalten eine Legende, die Zahlenwert, Vergleich und Trend trennt. Gesperrte Aktionen erklären Grund und nächsten Schritt.

Body: 16 px, Zeilenhöhe 24 px; Kontrolllabels im geprüften Stand 14,08 px. CSS nennt Source Sans 3 Variable/Fraunces mit System-Fallbacks. In der Probe enthielt document.fonts keine geladenen FontFaces; Wunschfonts sind daher nicht als tatsächlich geladen nachgewiesen. Segoe UI/system-ui bleiben stabile lokale Fallbacks. Ein kontrolliertes lokales WOFF2-Paket wäre eine Gestaltungsoption, kein zwingender Funktionsfix. Gut lesbare Hilfen, begrenzte Textbreite und tabellarische Ziffern unterstützen Orientierung; Zeilen-/Spaltenausrichtung auch mit langen Resultaten prüfen. Im statischen Aufbau keine externen Schrift-/Assetreferenzen gefunden.

Dunkle/helle ruhige Paletten und modulare Akzente fortführen. Trends zusätzlich mit Pfeilen/Wörtern anzeigen. Farben/Schriften nicht als wissenschaftlich „heilsam“ bezeichnen; steigende Softwarewerte belegen keine gemessene Gesundheitsverbesserung.

## 4. Aktuelle Kriterien und Vertrauenswürdigkeit

Ziel: WCAG 2.2 AA, besonders Tastatur, unverdeckter sichtbarer Fokus, Namen/Statusmeldungen, Textkontrast, Reflow, Textvergrößerung/-abstände und Farbe als ergänzende Information. Normaltext mindestens 4,5:1, großer Text 3:1. 24 × 24 CSS-Pixel Mindestzielgröße hat Ausnahmen; Checkbox plus klickbares Label nicht pauschal als Verstoß bewerten. Erforderliche zweidimensionale Tabellen dürfen einen eigenen Scrollbereich behalten.

Quellen: [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [unverdeckter Fokus](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html), [Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html), [Textabstände](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html).

E-E-A-T ist keine Schrift-/Farbvorschrift und kein einzelner Rankingfaktor. Öffentliche gesundheitsnahe Inhalte brauchen besonders nachvollziehbare Verantwortliche, Herkunft, Methodik und Grenzen. Über/Quellen sollte zuerst erklären: Wer ist verantwortlich? Welche Original-/Heuristikversion? Wie entstehen Werte? Welche Prüfung und welche Grenzen? Hashes allein genügen nicht. Private Fallseiten nicht öffentlich indexieren; noindex ersetzt keine Zugriffskontrolle. [Google: hilfreiche und vertrauenswürdige Inhalte](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).

Personenbezogene Verarbeitung benötigt Zweck, passende Rechtsgrundlage, transparente Information, Datenminimierung, Betroffenenrechte und technische/organisatorische Schutzmaßnahmen. Tatsächliche Gesundheitsdaten benötigen zusätzlich Art.-9-Bewertung; eine Fotodatei ist nicht automatisch biometrische Identifizierung. Aurelia braucht umsetzbare Löschung/Export/Aufbewahrung und eine risikobezogene Prüfung einer Datenschutz-Folgenabschätzung. Lokales Paket/Fernet allein erfüllt diese Anforderungen nicht. [DSGVO, Art. 5, 6, 9, 13, 17, 20, 25, 32, 35](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng).

Wellbeing-Zweck und gesamte Produktkommunikation müssen konsistent bleiben. GV, Resonanz und Harmonisierung sind hier algorithmische/heuristische Softwarebegriffe, keine Wirksamkeitsnachweise. Zweckbestimmung umfasst Beschriftungen, Gebrauchsanweisung und Werbung; „kein Medizinprodukt“ allein entscheidet keine Einordnung. Keine regulatorische Klassifizierung durch diesen Review. [MDR, Art. 2(12)](https://eur-lex.europa.eu/eli/reg/2017/745/oj/eng).

## 5. Prüfabdeckung und Sicherung

- Hauptaudit: 27 UI-Zustände; zehn Desktop-Tabs, fünf relevante Tabs bei 768/390/320 px; Textresize/Textspacing. Eigene Browser, Schreibzugriffe/WebSockets gesperrt; sensible Lesedaten im Hauptaudit synthetisch ersetzt. Separate Fokusprobe erlaubte GETs; personenbezogene Bildschirmbereiche im Beleg maskiert. Keine Fallinhalte im Bericht.
- 372 näherungsweise Textkontrastproben für Hell/Dunkel × Salbei/Wellenreiter/Sunrise: kleinster Wert 4,87:1, keine Probe unter ihrer Schwelle. Nicht alle Symbole, Zustände, Trends, Bilder oder Fokuskontraste geprüft.
- Keine JS-Fehler; in geprüfter Namensheuristik keine namenlosen aktivierten Standardcontrols. Tab-Pfeiltastennavigation funktionierte. Kleine Checkbox-/verborgene File-Controls nicht pauschal als Zielgrößenfehler bewertet.
- Normale schmale Ansichten ohne gemessenes Dokumentüberlaufen. Vollständige 400-%-Zoom-/Screenreader-/Kamera-/Stochastik-Langlauf-/Warmstart-/Multi-Tenant-Abnahme nicht erbracht; keine axe-/WCAG-Zertifizierung behauptet.
- Vor Review: checkpoints/RadiWorks-UX-Review-20261006-204351, 175 Dateien mit Größen/SHA-256: Produkt, Manifest, aktive Prüfkonfiguration, synthetischer Katalog. Keine Fall-/Schlüsseländerung. Kein neues Komplettarchiv sämtlicher Liveakten/Geheimnisse.
- Keine Produkt-/aktive Konfigurationsänderung, kein Restart, keine Übernahme nach 8103–8109, kanonischem RadiWorks, Modul_Templates oder Start5. Vollkatalogvorlage ausdrücklich inaktiv.

Helfer tatsächlich: GPT-6 Luna/max für begrenzte Speicher-/Datenflussprüfung; GPT-6 Astra/medium für wesentliche Katalog-/Origin-/Dock-Schlussfolgerungen. Root: Integration, Katalogbelege, Browserprobe, Primärquellen, Dokumentation. Betreibergewählte Leitung GPT-6.1 Sol/high; nicht aus Profilwerten als Laufzeitnachweis abgeleitet. Keine gemessene Tokenersparnis; Hermes-App-Routing unverändert.

## 6. Phasenplan

Prozentwerte beziehen sich auf das begrenzte Paket, nicht auf eine gemessene Gesamtproduktreife.

| Phase | Stand | Abschlussnachweis / nächster Schritt |
| --- | --- | --- |
| R1 Katalogbestand und Ausgang sichern | 100 % | 123er Bestand erhalten; 8112-Begrenzung erklärt; Checkpoint geprüft. |
| R2 Begrenzter Qualitätsreview | 100 % | Prioritäten, Belege, Normquellen und Grenzen dokumentiert. |
| R3 Katalog-ID, Zielgrenze, Dock/Resize korrigieren | 0 % – geplant | Kompatibilität, sichere Zielablehnung, sichtbarer Fokus; Algorithmen erhalten. |
| R4 Vollkatalog und verständliche Führung in 8112 | Offen | Kontrollierter Wechsel, alle Kataloge, Fall-/Auftragserhalt und Nutzerprobe. |
| R5 Erneute Funktionsabnahme | Offen | Original/Personal × reproduzierbar/stochastisch, GV/21/Watchlist/Broadcast/History; Kamera separat. |
| R6 Live-/Quell-/Modul_Templates-/Start5-Abgleich und Gesamtsicherung | Offen, nach Abnahme | Versionierter Stand und geprüfter Wiederherstellungseinstieg. |
| S4.8 Aurelia-Integration | 0 % – keine Freigabe | Datenbankbesprechung, Host-/Tenant-/Abo-/Datenschutzverträge, Zielservertests. |

Empfohlen: zuerst P1-Grenzen und Navigation, dann Vollkatalog und Bedienungsverbesserungen abnehmen. Bestehende Liveinstanzen bleiben auf bestätigtem Stand. Keine neue Such-KI, Algorithmusablösung oder ungeprüfte Gesamt-Datenbankarchitektur aus diesem Review ableiten.
