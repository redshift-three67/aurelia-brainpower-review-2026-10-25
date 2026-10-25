# Aurelia: Administration, Medien und kontrollierte Importe

Stand 09.10.2026. Betreiberergänzungen a–g sind als Anforderungen und Architekturvorschläge aufgenommen. **Keine neue zentrale Datenbank, Medienverwaltung, OCR-Pipeline oder Generatorfreigabe wurde implementiert.** Modulcharakterisierung und Referenzprüfungen behalten Vorrang; Strukturwahl und gemeinsame Modul_Templates-Verträge folgen danach mit dem Betreiber. RadiWorks R6, Start5, Dauerinstanzen, Modulalgorithmen und Server bleiben unverändert.

## 1. Verwaltung: belegter Bestand und offene Zuständigkeiten

Gezielter read-only Abgleich von Aurelia-Phase-1-Quellen und Modul_Templates; keine Prüfung produktiver Dienste, Zugangsdaten oder echter Klienten. „Nicht gefunden“ bezieht sich auf die genannten Migrationen, Praxisfunktionen und Architekturunterlagen, nicht auf einen vollständigen Serveraudit.

| Frage a | Lokal vorhanden | Zielbild / noch offen |
|---|---|---|
| Identität und Mandanten | Auth-Tabellen für Nutzer, Sitzungen/Konten; `tenants` und `memberships`. `/praxis` verwaltet eigene Mitgliedschaften und legt begrenzte synthetische Mandanten mit `tenant_admin` an. | Plattformadministration, Einladung, delegierte Praxisverwaltung und differenzierte serverseitige Rechteprüfung. Rollenbezeichnungen allein sind keine nachgewiesene Autorisierung. |
| Therapeuten | Praxiszugehörigkeit als minimale technische Basis. | Therapeutenprofil, fachliche Rolle, Klientenzuordnung/Delegation, Sperre und Historie separat spezifizieren; Nutzer, Praxis und Klient nicht gleichsetzen. |
| Abos / Module | Tarif-/Quota-Zielbild in Dokumenten. Keine Durchsetzung in den geprüften Phase-1-Migrationen und Praxisfunktionen gefunden. | Vertragslaufzeit, Modulberechtigung, Tarifrevision, Suspendierung/Kündigung, Quotas und Rechte bei laufenden Aufträgen bestimmen. Modulabo ersetzt keine Klienten-/Assetberechtigung. |
| Status | Kein allgemeiner Nutzer-/Praxis-/Abo-/Dienst-Lifecycle in den geprüften Phase-1-Tabellen. Einzelne zukünftige Fachzustände sind dokumentiert. | Für Mitgliedschaft, Abo, Auftrag, Asset, Import und Dienst jeweils eigene Zustände, erlaubte Übergänge, zuständige Rolle und Audit festlegen. |
| Ressourcen / Dienste | Control Plane, GPU-/Timer-/Emitter-Dienste und geplante Laufzeiten sind Architekturziele. Kein zentraler Ressourcen-/Service-Admin im geprüften UI-/Lib-Scope. | Diensteinventar, Version/Health, Kapazitäten, Tenantlimits, Warteschlange, Fehler/Wiederanlauf und kontrollierte Freigaben. GPU-/Hardwareleistung nicht aus Anzeige oder Simulation ableiten. |
| Zentraler Speicher | Code nutzt `pg`, wenn `DATABASE_URL` gesetzt ist; sonst flüchtiges PGlite. | Eine beschriebene PostgreSQL-/Objektspeicher-/Zeitreihenumgebung ist noch kein Betriebs- oder Restorebeleg. Produktionsstruktur bleibt Gegenstand der kommenden Entscheidung. |

Quellanker: Aurelia `migrations/0001_auth.sql:19`, `0002_tenants.sql:1`; `src/lib/db.ts:13`; `src/routes/praxis.tsx:74`; `src/lib/praxis/memberships.ts:12,37`; `docs/07-identity.md:3,23`, `02-architecture.md:14,36`, `09-roadmap.md:18`, `18-clipboard.md:7`; Modul_Templates `GEMEINSAME_PUNKTE_AURELIA.md:22`, `MODULE_REGISTRY.md:94`. Phase-1-/Servergrenze: Aurelia `AGENTS.project.md:79,110`. Autoritative Plattform-RLS und Rechte müssen aktiv nachgewiesen werden.

Empfehlung: zentral verwaltete Identitäten, Praxis-/Tenant-Mitgliedschaften, Modulberechtigungen und Dienste. Module erhalten ausschließlich erlaubte Adapterzugriffe. Administrativer Besitzer, Ersteller, fachlicher Klient und Zugriffsrecht werden getrennt geführt. Die Entscheidung über konkrete Tabellen, Dienste und Datenbankaufteilung erfolgt nach der gemeinsamen Modulmatrix.

## 2. Gemeinsame Medienverwaltung und Verlustfreiheit

| Ebene | Was erhalten bleiben muss | Wie der Nachweis erfolgt |
|---|---|---|
| Originaldatei | Exakte hochgeladene Bytes samt Originalformat und vorhandenen Metadaten. | Inhalts-Hash und Rücklesen; Originalrevision unverändert erhalten. Lösch-/Aufbewahrungsregeln gelten weiterhin. |
| Bildpixel | Auflösung, Kanäle, Bittiefe, Alpha und Farbraum; auch unsichtbare RGB-Werte bei transparenten Pixeln, falls pixelidentische Ableitungen versprochen werden. | Dekodierte Werte und relevante Metadaten vor/nach Kompression vergleichen. Keine stille 16→8-Bit-, Farb- oder Größenreduktion. |
| Audiowerte | Sampleformat, Samplezahl, Reihenfolge, Kanalzuordnung und Abtastrate. Container-/Zusatzmetadaten zusätzlich behandeln. | Samplegleichheit und separater Originaldatei-Hash; ein gleiches Audiosignal ist nicht automatisch dieselbe Containerdatei. |
| Struktur / Interpretation | Layerreihenfolge, Transformationen, Profil-/Sequenzparameter, Importmapping und Herkunft. | Versionierte Manifeste, Schema-/Referenzprüfung und Wiederherstellungsprobe. OCR-Text ist eine überprüfbare Ableitung, keine garantierte exakte Interpretation. |

Originale, Arbeitsfassungen und Vorschauen werden getrennt geführt. Ein verkleinertes PNG in RadiWorks ist eine bestehende Anzeige-/Datenschutzableitung, kein nachträglich verlustfreies Originalarchiv. Bereits verlustbehaftete JPEG-/MP3-Dateien erhalten durch Umwandlung keine verlorenen Informationen zurück.

Empfohlene zentrale Verantwortung: Dateiobjekte in privatem Objekt-/Dateispeicher, Metadaten und fachliche Referenzen in der zentral verwalteten DB. Asset-ID, Revision, Hash, Format, Größe, Herkunft/Lizenz, Tenant-/Bibliotheksrecht, Ersteller, Freigabe, Ableitungsbezug und Aufbewahrung/Löschung zusammenführen. Keine öffentlichen Objektpfade oder mandantenübergreifende Sichtbarkeit aus einem gleichen Hash ableiten. Exakte Originale können sensible Metadaten enthalten: restriktiv zugängliches Original und bereinigte veröffentlichbare Ableitung getrennt halten. DB, Objekte, Rechte und Löschstände gemeinsam sichern; technische Inhaltsgleichheit ersetzt weder Datenschutzentscheidung noch Zugriffsprüfung.

## 3. Administratives Layerwerkzeug: Frage c und e

Vorschlag: **bis zu fünf getrennte Bilder/Symbole**, mit wählbarer Reihenfolge und oberster sichtbarer Ebene innerhalb dieser fünf. Kein sechstes Bild still ergänzen; eine zusätzliche Deckbildanforderung vor Umsetzung klären. Verdeckte Ebenen bleiben gespeichert und wieder auswählbar. Die Vorschau ist eine zusammengesetzte Ableitung und ersetzt kein Original.

Eine Layerrevision referenziert konkrete Assetrevisionen und hält Layer-ID, Reihenfolge, Sichtbarkeit, Position/Transformation, Deckkraft und Mischmodus fest. Dokumentmaße, Koordinatensystem und Farb-/Compositingregel gehören dazu. Die Kombination aus fünf Originalen und Manifest ermöglicht Wiederherstellung; ein flaches Gesamtbild allein ermöglicht sie nicht. Grafische Layer ändern keine Modulformel oder Gewichtung ohne gesondert freigegebenen Vertrag.

PNG ist ein verlustfreier Rasterkandidat auch für höhere Bittiefen. Lossless WebP kommt für geeignete 8-Bit-Ableitungen infrage; `-lossless` allein bewahrt nicht zwingend RGB hinter voller Transparenz, dafür ist auch `-exact` relevant. Farbraum-/Metadatenerhalt muss zusätzlich geprüft werden. Kein allgemeiner bester Codec wird ohne Vergleich eigener Dateien festgelegt. [PNG-Spezifikation](https://www.w3.org/TR/png-3/), [offizielles cwebp-Handbuch](https://developers.google.com/speed/webp/docs/cwebp).

Vor Codecfreigabe: Testbilder mit Alpha/unsichtbarem RGB, 8/16 Bit, ICC, Rotation/Metadaten und fünf Ebenen; Hash-/Pixelvergleich, Import→Speichern→Export→Restore, Größe, Laufzeit und Speicherbedarf. Optional allgemein verlustfrei komprimierte Originalbytes nur bei gemessenem Vorteil; bereits komprimierte Dateien nicht blind erneut verpacken. Decoder erhalten Größen-/Speichergrenzen.

HTTPS schützt die Übertragung. Bild-/Audio-Codecs und HTTP-Inhaltskompression sind getrennte Entscheidungen; TLS-Kompression wird nicht aktiviert. Range-/Streaming-/Cacheverhalten, autorisierte Downloads und tatsächliche Bytegleichheit gehören in den späteren Transporttest. TLS 1.3 sieht nur die Null-Kompressionsmethode vor. [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html).

## 4. Gemeinsamer Generator und verlustfreie Audiodateien: Frage b und d

Der vorhandene Generator und die bestätigten RadiWorks-Profile bilden die Ausgangsbasis. Browser-, Native- und Releasekomponenten sind laut [Generatorreview](verification/RADIWORKS_AUDIO_PHI_REVIEW_2026-10-07.md) nicht pauschal dieselbe Version oder Funktionsmenge; native Linux-Abnahme bleibt separat. Die aktuelle RadiWorks-Integration ist durch die neueren R6-Nachweise beschrieben. Keine ungeprüfte Generatorübernahme oder Algorithmusänderung.

Empfehlung: versionierte systemweite **Audiofähigkeit** mit Profil-/Sequenzkatalog und ausdrücklich berechtigten Moduladaptern. Sie kann Browserwiedergabe und später Serverrendering anbieten; nicht jedes Modul braucht einen permanenten Audioprozess. Tenant, Modulrecht, Ressourcenbudget, Profilrevision, Generatorversion und vollständige Parameter werden am Auftrag eingefroren. Benutzeraktivierte Wiedergabe und „Audio stoppen“ bleiben eigenständig; Audiozufall darf weder Analyse-Zufallsfolgen noch parallele Fälle beeinflussen. Eingefrorene Parameter und protokollierte Berechtigungsstände ersetzen keine aktuelle Autorisierung: Download/Start erneut prüfen; Widerrufs- und Sperrverhalten laufender Aufträge vor Umsetzung festlegen. Keine neue freie Umrechnung von EW/GV/Resonanzen in Hz.

| Audioform | Stabile Vorbereitung | Noch erforderlicher Nachweis |
|---|---|---|
| Ganzzahlige PCM-Datei | Original behalten; FLAC als verlustfreie Nutzsignal-Kompression prüfen. | Samplegleichheit, Kanal-/Zeitdaten und gesonderter Metadatenerhalt. |
| Float-Master | Original-WAV unverändert erhalten. WavPack für unterstützte 32-Bit-Float-Master oder allgemeine Bytekompression als Kandidaten prüfen. | Exakter Roundtrip, Tool-/Codecversion und unterstütztes Sampleformat; kein Hybrid-/Lossy-Modus. |
| Streaming / Browser | Autorisierte Audioableitung mit dokumentierter Sample- und Formatkonvertierung. | Tatsächliche Browserabtastrate, Übergänge, Stop, Mehrinstanzverhalten, Arbeitsspeicher und Lautstärke. |
| Ubuntu-Renderer | Gemeinsamen Parametervertrag vorbereiten, vorhandenen Algorithmus erhalten. | Lizenz/Nutzungsrecht, reproduzierbare Linuxausgabe, Profilparität, Abbruch/Wiederanlauf und Ressourcenlimits. |

FLAC unterstützt ganzzahlige PCM-Samples, aber keine Float-Samples. WavPack dokumentiert unter anderem 32-Bit-Float-Unterstützung. Diese Formatfakten ersetzen keinen Aurelia-Roundtriptest. [FLAC FAQ](https://www.xiph.org/flac/faq.html), [WavPack](https://www.wavpack.com/).

## 5. Frequenzreihen in Katalogen: Frage g

**Ja, technisch sinnvoll:** als versionierte, geordnete Datenobjekte. Dafür ist keine neue multidimensionale Spezialdatenbank zwingend. Ein Profil verweist auf eine konkrete Sequenzrevision und einen kompatiblen Generator; die Ausgabe bleibt ein getrenntes Asset mit Rendernachweis.

Vorzusehen: stabile Sequenz-ID, Herkunft/Lizenz, Rechtebereich, Version und geordnete Schritte. Pro Schritt Frequenz und Einheit, Dauer, Träger/Puls/Wellenform, Kanal-/Gain-/Übergangsparameter und Wiederholung explizit festhalten. Doppelte Frequenzen und Reihenfolge dürfen nicht durch Wörter-/Wert-Deduplizierung verschwinden. Kanonische Dezimalwerte erhalten beispielsweise `429,62 Hz` als `429.62` mit Einheit und Originaldarstellung. Geplante Dauer und tatsächlich gerenderte Samplezahl/Abtastrate samt Rundungsregel getrennt dokumentieren.

Phi-/Fibonacci-Profile bewahren Konstante, Index-/Folgenregel und algorithmische Version; in RadiWorks wurden Pulsrate **und** Abschnittsdauer freigegeben. Laufzeitberechnungen bleiben an die tatsächliche numerische Rendererpräzision und Sampleclock gebunden. Mehr Dezimalstellen in der DB beweisen keine entsprechende analoge Ausgabegenauigkeit. Frequenzlisten enthalten Daten, keinen ausführbaren Nutzer-Code. Hardware-/Träger-/Pulsparameter sind verschiedene Größen; keine automatische gegenseitige Interpretation und keine Wirkbehauptung aus einem Profilnamen.

## 6. Kontrollierter PDF-/Office-/JSON-Import und Export: Frage f

Ergänzung16.10.2026: Der gewünschte nutzerbedienbare Ratenkatalogimport für **TXT und XLSX einschließlich CopyGuard** ist als `RW-IMP1 / AURELIA-IMP-CATALOG` konkretisiert. TXT war bereits im RadiWorks-Restplan vorgemerkt, XLSX hier; bestehendes TXT-Lesen ersetzt keine Importoberfläche. Gemeinsamer Ablauf mit erlaubtem Moduladapter, Eigentümer-/Tenantrechten, Vorschau, Herkunft/Revision, struktureller und CopyGuard-Prüfung, ausdrücklicher atomarer Veröffentlichung und Rückweg; keine stille Textkorrektur oder Änderung laufender Aufträge. CopyGuard bleibt zusätzlich bei Analyse-/Broadcastfreigabe wirksam. Noch keine Implementierung oder zentrale DB-Entscheidung. Reihenfolge, offene Formatfestlegungen und Abnahmekriterien: [Hauptplan43.1](superpowers/plans/2026-10-10-aurelia-module-lokale-referenz-und-datenstruktur.md#431-txt-xlsx-nutzerimport-und-copyguard).

Empfehlung: gemeinsame administrative Import-/Exportfähigkeit mit versionierten Templates; Moduladapter bestimmen ausdrücklich erlaubte Zielobjekte. Kein generischer Schreibzugriff auf beliebige DB-Tabellen.

| Format | Vorgesehener Weg | Präzisionsgrenze |
|---|---|---|
| PDF | Text und Struktur zunächst extrahieren; OCR für Bildseiten. Original, Seiten-/Textpositionen, Engine-/Sprachversion, erkannte Werte und Review speichern. Export aus freigegebenem Template mit gebundenen Eingaberevisionen. | OCR kann Zeichen, Dezimalstellen oder Zuordnungen falsch erkennen. Kritische Klienten-IDs/Frequenzen nicht erraten; Unsicherheiten sichtbar zur Bestätigung. |
| XLSX / XLS | Beide Formate explizit unterstützen und separat prüfen. Blatt-/Zellbezug, Formeln, vorhandene Ergebniswerte, Einheiten, Datumsmodell, Dezimallokalisierung und führende Nullen unterscheiden. | Keine stille Neuberechnung oder Ausführung von Makros/external links. Fehlende/veraltete Formelwerte kennzeichnen; keine Layout-Roundtripgarantie aus einem Tabellenimport ableiten. |
| JSON | Rohdatei behalten, Schema-/Versionsprüfung und typisierte Mappings. Dezimal-/ID-Werte ohne stille floatbedingte Rundung übernehmen. | Doppelte Objektschlüssel vor semantischer Übernahme ablehnen; Arrays/Reihenfolge erhalten. Normalisierung ist eine dokumentierte Ableitung, keine exakte Originaldatei. |

Ablauf: Upload mit Format-/Größenprüfung → isolierte Verarbeitung → Template-Mapping → Vorschau mit Herkunft, Validierungsfehlern und Duplikat-/Klientenzuordnung → ausdrückliche Bestätigung → transaktionale Übernahme mit Audit/Idempotenz → nachvollziehbarer Export/Restore. Name/Geburtsdatum allein sind kein automatischer modulübergreifender Klientenschlüssel. Eingebettete Dokumentanweisungen sind Inhalt; niemals Befehle oder neue Importrechte. Formeln/Skripte nicht aus Imports ausführen. Externe OCR-/LLM-Übertragung ist nicht Bestandteil dieses Vorschlags.

OCR kann strukturierte Positionen und Erkennungsscores liefern; diese Werte sind keine Fehlerfreiheitsgarantie. Tesseract dokumentiert unter anderem hOCR/TSV und PDFs mit einer Textebene über dem Scan. [Offizielle OCR-Ausgabeformate](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage).

Exportanforderung: Template-/Rendererrevision, vollständige Eingabebindung, Fonts/Zeichensatz, Einheiten und klare Beschriftung. Suchbarer, zugänglicher PDF-Export und passende Archivformate werden separat validiert; keine pauschale PDF/UA-, PDF/A- oder DSGVO-Abnahme durch bloße Dateierzeugung. Importfehler bleiben korrigierbar, frühere Reports/Assets bleiben an ihrem verwendeten Datenstand gebunden.

## 7. Einordnung in den bestehenden Plan

| Priorität / Phase | Jetzt / nächster Schritt | Abschlussgrenze |
|---|---|---|
| 1 – Q4 Referenzcharakterisierung | Archiv-/Vorlagenfamilien und Kontextbindungen synthetisch prüfen; Thom 3D/Koordinaten/Feldbereiche und Parallelitätsgrenzen ergänzen. | Quellgebundene Ergebnisse; keine Originalalgorithmusänderung. |
| 2 – Q2 Betriebs-/Rechteabgleich | Aktive Deploymentversion, Eltern-/Kindrechte, Rollen/Delegation und Storagebestand nachweisen. | Quellen und DB-Exports allein sind keine aktive Serverabnahme. |
| 3 – MATRIX / ADM / MEDIA / IMP | Alle Modulbedarfe inklusive Administration, Berichte, Trends, Zwischenablagen, Vorlagen, Harmonisierungen, Trigger, Echtzeit, Frequenzreihen und Assetrevisionen gemeinsam erfassen. | Fehlende Quellen/Bedarfe sichtbar lassen; Governors-Intake/Freigaben getrennt. |
| 4 – DB-1 / CONTRACT | Zentrale Struktur, Zuständigkeiten und Lebenszyklen mit Betreiber entscheiden; danach verbindliche Modul_Templates-/Adapterverträge. | Noch kein beschlossenes Gesamtschema und keine Migration. |
| 5 – Umsetzung / Abnahme | Zunächst Isolation/Rechte/Restore und Speichervertrag; dann Katalog-/Medienfähigkeit, Generatorparität, kontrollierte Imports und zuletzt Creator-Komfort. | Jede Fähigkeit braucht eigene synthetische Referenz-, Last-/Fehler-/Restoretests; S4.8 gesondert. |

Priorisierte Abnahmekriterien: unveränderte bestätigte Rechenergebnisse, eingefrorener Auftragskontext, Rechte an jedem Asset/Schreibweg, Varianten-/Reihenfolgeerhalt, byte-/pixel-/samplebezogene Verlustfreiheit und kein stiller Wiederanlauf. Die konkrete Implementierungsreihenfolge innerhalb Phase 5 folgt den später beschlossenen Abhängigkeiten.

Verknüpfungen: [Datendomänen](AURELIA_DATENDOMAENEN_ECHTZEIT_2026-10-09.md), [2D/3D-Werkzeug](AURELIA_ADMIN_ASSETS_VORMERKUNG_2026-10-09.md), [Favoriten/Trends/Trigger](AURELIA_FAVORITEN_TRENDS_TRIGGER_VORMERKUNG_2026-10-09.md), [Copen/Bohm/Thom-Referenzen](AURELIA_REFERENZPRUEFUNG_COPEN_BOHM_THOM_2026-10-09.md).

Helfer dieses Blocks: Luna6/max für den begrenzten read-only Verwaltungsabgleich; Astra6/medium prüfte Verwaltungsbefunde, Medienverlustfreiheit, Rechte-/Widerrufsgrenzen und Copen-Testaussagen unabhängig. Kein blockierender Widerspruch für die Vormerkung; Ergänzung zur aktuellen Autorisierung übernommen. Keine Implementierungsfreigabe durch Review. Betreibergewählte Chatleitung Sol6.1/high; effektive Desktop-Auswahl nicht ausgelesen. Keine Zeitvorgabe als Qualitätsgrenze und keine gemessene Tokenersparnis.
