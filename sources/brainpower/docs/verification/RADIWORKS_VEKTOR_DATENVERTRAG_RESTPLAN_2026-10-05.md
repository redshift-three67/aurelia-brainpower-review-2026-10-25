# RadiWorks: Vektor, Einstellungen, Datenverträge und lokaler Abschluss
Begonnen: 05.10.2026; Prüfabschluss der Nachweise: 06.10.2026. Quellengebundener Abgleich des gepinnten C23-Releases. Keine Aurelia-Integrationsfreigabe und keine neue algorithmische oder Host-Datenbank-Implementierung.

## Betreiberentscheidungen dieser Fortsetzung
- Portable5 0.3.0-rc1 funktioniert nach Vorgabe: neue persönliche Bestätigung im Chat. Dies ersetzt keine pauschale EXP-/Host-/Hardwareabnahme.
- Ego Cleaner bleibt ausgeschlossen. Vorbereitet ist nur ein späterer, gesondert freizugebender Audio-Erweiterungspunkt im Plan: eigener Feature-Identifier, Start/Stop, Inhaltsrechte und keine Kopplung an Analyse/GV. Kein Audio-Asset, keine aktive Funktion oder vorgetäuschte Codefähigkeit.
- Windows-Komfortpaket zurückgestellt. Neue GPU/CUDA-, Kozyrev- und Hardwareanbindungen bleiben optional. Der bereits funktionale separate EXP1-CPU-Vergleich wird dadurch nicht entfernt.
- TXT-Nutzerimport erst nach geklärtem modulbezogenen Daten-/Rechtevertrag. Keine stille Vereinheitlichung der Ratenformate aller Module.
- Bestehende bestätigte Funktionen und ursprüngliche Algorithmen bleiben erhalten; keine semantische KI-Suche oder neuen Analyseverfahren.

## A. Welche Fallfelder wirken tatsächlich?
| Eingabe | Originalanalyse | Lokale Katalogvorschläge VF3 | Numerischer Vergleich EXP1 |
|---|---|---|---|
| Fallbezeichnung, Beschreibung | eingefrorener Kontext; keine Zahlengewichtung | nicht verwendet | keine mathematische Gewichtung |
| Vorname, Nachname | Kontext; keine Zahlengewichtung | nicht verwendet | vorhandene Radi144-Namensformel; Vorname zusätzlich Teil des Matrix-RNG-Seeds |
| Geburtsdatum | Kontext; keine Zahlengewichtung | nicht verwendet | Geburtsformel und zusätzlich Matrix-RNG-Seed |
| Ort mit Typ Geburtsort | Kontext; keine Zahlengewichtung | nicht verwendet | ergänzt Geburtsformel nur mit vorhandenem Geburtsdatum |
| Wohn-/Aufenthaltsort oder untypisierter Altort | Kontext; keine Zahlengewichtung | nicht verwendet | keine numerische Ortswirkung |
| Gespeicherter Fokus | Kontext; keine Zahlengewichtung | Worttreffer für Vorschläge | literal-substring-lower-v1: wortwörtlicher Fund im gebundenen Katalog; numerische Ergänzung nur bei berechneter Frequenz > 0 |
| Zusätzliche Suchthemen | keine automatische Analyseänderung | Worttreffer für Vorschläge | kein persönlicher Signaturparameter |
| Optionales Fokusbild | eingefrorene Referenz; keine Pixelgewichtung | nicht verwendet | Kontext-only, keine numerische Bildsignatur |
| Gewählte Rate / Katalog | tatsächliche Originaleingabe | Suchgrundlage | gebundener Katalog und Ratentext wirken in der bestehenden Vergleichsheuristik |

Die Originalanalyse nutzt Katalog, Entropiemodus/Seed und Analyseparameter. Ein Kontext-Digest bindet Daten und erleichtert Nachvollzug; er beweist keine mathematische oder physikalische Personalisierung. Bei gleichem Seed und Katalog sind gleiche Originalraten trotz verschiedener Personenfelder erwartetes Verhalten. Stochastic-Unterschiede sind nicht allein ein Nachweis von Personenbezug.

EXP1 ist ein ausdrücklich wählbarer Vergleich für bis zu 21 gebundene Raten; es verändert weder Original-EW/Potenz/Level/GV noch die bestehende Broadcast-Queue. Name/Geburt werden über verfügbare Komponenten normalisiert (Basisgewichte 0,15/0,20). Das „Fokusgewicht“ des Matrixaufrufs gewichtet den jeweiligen Ratenvektor; es ist nicht gleichbedeutend mit einer freien semantischen Gewichtung des Fallfokustextes. Wohnort/Bild bleiben numerisch inaktiv.

## B. Broadcast-Ziel und Kontext: tatsächlich implementierte Grenze
| Startweg | Kontext-/Zielbindung heute | Berechnung |
|---|---|---|
| Prüfdraft → Prüfen → Freigeben / Promote | immutable ContextReference zu vorhandener Fall-ID, Kontextversion, Snapshot, Scope, Sitzung und Draft; vollständiger Snapshot bleibt im Draft/Sitzungsbestand | Signature der Rate + EW + Potenz; Laufzeit/Multiplier/Delay/Repeat und eigener Entropieablauf |
| Direkter Broadcast | Signatur und Laufzeitparameter; kein automatisch hinzugefügter vollständiger Fallkontext | keine persönliche numerische Vektorgewichtung |
| Auto-Broadcast | auto-seitig gewählte Ratensignatur und Parameter; Enqueue übergibt derzeit keine ContextReference | keine persönliche numerische Vektorgewichtung |
| Bild-Broadcast | IMAGE:<Hash> als Signatur; nicht der vollständige persönliche Kontext | keine Bild-/Personenberechnung im Resonanzablauf |

Broadcast ist virtuell; Hardware ist gesperrt. Resonanzen sind als simulated gekennzeichnet. Die persönliche Kontextreferenz im Promote-Weg ist Auftragszuordnung, keine belegte physische Zielübertragung oder Behandlung.
**Neu präzisierter Restpunkt BC-1:** gemeinsamer unveränderlicher Zielkontext für alle neuen fallbezogenen Broadcast-Startwege. Direkte Aufträge dürfen keine erfundenen Draft-/Sitzungs-IDs erhalten. Auto muss den Kontext seiner Ursprungsanalyse verwenden, nicht den später gerade aktiven Fall. Bildsignatur und persönliches Fokusbild sind getrennte Funktionen. Bestehende laufende Aufträge nicht rückwirkend umbinden; Originalzahlen/Signaturen bleiben erhalten. Ein eigener Entwurf und gezielte Bindungs-/Fallwechsel-/Wiederanlauftests sind vor Umsetzung erforderlich.

### BC-1: konkret vorbereiteter Entwurf, noch nicht implementiert
Ein gemeinsamer Zielverweis bindet eine unveränderliche Fall-ID, Kontextversion, Snapshot-ID/Digest und den vertrauenswürdig gesetzten Scope. Ein eigener Broadcast-Auftrag erhält eine eigene ID und einen Startgrund (Promote/Direct/Auto/Image). Draft- und Analyse-Sitzungs-IDs sind nur dort vorhanden, wo diese Objekte tatsächlich existieren; der bisherige Promote-Verweis bleibt rückwärtskompatibel. Zielbindung und Beobachtungsbindung sind getrennt: ohne passende gebundene Analyse-Rate darf GV2 nicht durch erfundene Verweise aktivierbar werden.

Für Auto wird der eingefrorene Kontext der Ursprungsanalyse übernommen. Fallwechsel oder spätere Metadatenänderung binden keinen laufenden Auftrag um. Bei direkten fallbezogenen Starts muss die Oberfläche vor Start den tatsächlichen Zielkontext anzeigen; ungebundene lokale Starts bleiben ausdrücklich als solche erkennbar. Image-Signatur und optionales Fall-Fokusbild bleiben getrennt. Alle tatsächlichen Originalsignaturen/Ziehungen und bereits laufenden Aufträge bleiben unverändert. Der Verweis bewirkt keine zusätzliche persönliche Zahlenformel oder belegte physische Zielwirkung.

Abnahme vor Liveübernahme: alle vier Startwege, fehlender/ungültiger Scope, Fallwechsel während Start, veraltete Kontextversion, Bildwechsel, doppelte Anfrage-ID, aktive historische Queueeinträge und Prozesswiederanlauf. Gemeinsam mit dem Adaptervertrag prüfen; weder Body-Mandantenfelder noch ein lokaler Prozessname gewähren Hostrechte. Dieser Entwurf ist kein implementierter Hostvertrag und keine neue Integrationsfreigabe.

## C. Originaleinstellungen: ehrliche Umsetzungsempfehlung
Aktiv sind u.a. Entropie-Standardmodus, Binaural-Schalter im Browser und der getrennt erklärte Legacy-Mix-Aufruf. Direkte Auswahl 100/1000 Treffer funktioniert unabhängig vom historischen High-Hit-Schalter.
| Einstellung | Heute | Empfehlung |
|---|---|---|
| notification.after.broadcast | gespeichert, Default True; keine aktive Abschlussbenachrichtigung | erster kleiner Zusatz: zugängliche lokale Fertigmeldung, kein E-Mail-/Netzversand; keine still neue Wirkung gespeicherter Altwerte |
| broadcast.single.rates.only | gespeichert; MAX_ACTIVE derzeit fest 8 | danach prüfen: Originalsemantik gegen JAR belegen; max. 1 aktiver Queue-Auftrag als eigene explizite Option, wartende Aufträge behalten; nicht als „nur eine Rate insgesamt“ missdeuten |
| analysis.very.high.max.hit | gespeichert; Auswahl im Analyseformular wirkt bereits | höchstens nachvollziehbare Vorbelegung neuer Aufträge, kein Überschreiben ausdrücklicher Auswahl oder Altauftrag |
| broadcast.delta.time | gespeichert, keine Laufzeitwirkung | getrennte Vorbereitung: Formel/Entropiequelle, Grenzen und einmal berechnete unveränderliche Laufzeit vor Freigabe zeigen |
| broadcast.embedded / use.overlay | gespeichert, keine bestätigte Enginewirkung | Darstellung und Wirksemantik erst getrennt klären; bestehendes Area-Overlay ist eine andere Funktion |
| dynamic.adjustments | gespeichert, keine aktive Original-Adjustments-Logik | eigener größerer Schritt, weil Abschluss-GV und ggf. Folge-Broadcasts betroffen; keine Verwechslung mit GV2 und keine stille automatische Aktivierung |
| watchlist.activate | gespeichert | Datenrechte, Aktualisierung, Quotas und Ausführung separat definieren |
| power.switch | gespeichert; Hardware gesperrt | zurückgestellt |
| Ego Cleaner | ausgeschlossen | Plan-Erweiterungspunkt im Plan; keine aktive Funktion |

Dies ist eine Priorisierung, keine bereits implementierte Wirkung oder Freigabe aller Einstellungen. Besonders Abschlussmeldung: gespeicherter True-Default darf nicht unbemerkt als neue aktive Einwilligung interpretiert werden. Keine tatsächliche Original-Einzelqueue-/Delta-Zeit-Parität aus den Namen allein ableiten.

## D. Aurelia-Datenhaltung: geplant, nicht als produktiv nachgewiesen
Der vorhandene Datenplan sagt ausdrücklich **ein PostgreSQL**. Geplant sind zentrale Mandanten/Nutzer/Gruppen/Einwilligungen/Quotas, versionierte Drafts/Scores, Timescale für Zeitdaten, ltree für Hierarchie, MinIO für Medien und ein lesendes Analysewarehouse. Das ist Sollplanung; kein Nachweis aktuell laufender PostgreSQL/RLS/MinIO-Dienste. Historische pgvector-Erwähnungen erlauben keine semantische Suche.

Empfohlene Trennung:
1. **Aurelia-Plattform:** autoritative Anmeldung, Mandant, Nutzer, Abo-/Modul-/Aktionsberechtigung, Objektfreigaben, Quotas, Audit und Katalogveröffentlichung.
2. **Modul-Domänen:** eigene Fachschemas/logische Tabellen und versionierte Ein-/Ausgabeformate. Keine ungeprüften Cross-Modul-Joins oder beliebigen globalen Schreibrechte. Physische separate Datenbanken je Modul sind nicht im gelesenen Plan festgelegt.
3. **Moduladapter:** autorisierten Auftrag/Scope übernehmen, erlaubte Katalogversion als read-only Snapshot liefern, Ergebnisse über geprüfte Verträge speichern. Für RadiWorks bleibt zunächst der funktionale TXT-Parser hinter dem Adapter.
4. **Lokale Prototypen:** vorhandene JSON-/SQLite-/Dateispeicher bleiben während Vorbereitung funktionsfähig. Kein vorzeitiger Austausch durch die Plattformdatenbank.

Schema-/Speichertechnik und Datenzuständigkeit sind verschiedene Fragen: zentral betriebener Postgres kann getrennte Modultabellen mit eng begrenzten Rechten enthalten. Falls später ein Modul fachlich einen anderen Speicher braucht, geschieht dies explizit hinter derselben Rechte-/Adaptergrenze.

### Rechte: notwendige Präzisierung
Zugang braucht die Schnittmenge aus Nutzeridentität, Mandantenmitgliedschaft, Modul-/Feature-Abonnement, Aktionsrecht und konkreter Objektfreigabe; Verbrauchsquotas werden getrennt geprüft.
Tenant-RLS allein trennt keine privaten Nutzer- oder Klientenbestände desselben Mandanten. Abo-Rechte gewähren keine Einsicht in fremde Fälle. Hintergrundjobs, Exporte, Bilder und Caches brauchen dieselben Autoritätsprüfungen. Lokaler Prozessscope ersetzt dies nicht.
**Offen:** Abo je Nutzer, Mandant oder kombinierbar; Rollen; gemeinsames vs privates Katalog-Publishing; Widerruf und Behandlung bereits laufender Jobs. Empfehlung als Entscheidungsentwurf: zentrale, kombinierbare Berechtigungsentscheidung; gesicherte Bestandsdaten bleiben bei Tarifwechsel erhalten, neue Starts werden neu geprüft. Sicherheitswiderruf und normale Tarifänderung getrennt behandeln. Noch keine aktivierte Tarif- oder Stop-Policy.
Der gemeinsame Templatevertrag erlaubt teils tenant/client im Body; RadiWorks lokal lehnt solche Body-Scope-Felder ab. Beim Hostadapter muss Aurelia vertrauenswürdigen Scope setzen. Browserangaben sind niemals Autorität.

### Modulübergreifendes Dateninventar vor gemeinsamem TXT-/Katalogvertrag
| Modul | Bereits erfasst | Noch zu erheben |
|---|---|---|
| RadiWorks | TXT-Kataloge/Gruppen; Fälle/Drafts/GV-Journale; separate Vergleichs-SQLite und Bildreferenzen | Katalognamespace/ID/Version, Owner/Sharing, Importvalidierung, Löschung/Export/Referenzschutz und Adaptervertrag |
| Radi144 | frisch quellengebunden: rekursive TXT-Listen in db_import; JsonStore für Klienten/Sitzungen/Artefakte, Audit-JSON; getrennter SQLite-Interchange-Consumer | vollständige aktive Routen-/Formatbelegung, Owner/Sharing, Autorität des geteilten Busses und Abhängigkeiten; TXT-Parsersicht allein ist keine vollständige Modulaufnahme |
| morphic_v1 / RadiMorphic | frisch aus C:/morphic_v1: prozedurale Itemgruppen mit JSON-Cache; Description-/Remedy-SQLite; JSON-HarmonizationJobs | tatsächliche aktive Einstiegspunkte und Nutzer-/Jobpersistenz vollständig erfassen; Quellenpräsenz ist kein Lauf-/Rechte-/Gesamtaufnahmebeweis |
| RadiFarben / neues Modul | neues Projekt noch in Vorbereitung | erst beim Intake Quelle/Pfad/Version und Datenbedarf belegen; keine Tabellen erfinden |
| weitere Registry-Kandidaten | RadiBlohm/RadiThoms/RadiCopen historisch registriert | aktuellen Quell-/Reifestand und reale Datenverträge bestätigen |

Das Inventar wird in der vereinbarten Modulreihenfolge ergänzt. Es muss gemeinsamen **Zuständigkeits-/Versionierungs-/Rechtevertrag** ergeben, nicht zwangsweise ein universelles Ratenformat. Früher begrenzter RadiWorks-Privatimport wäre technisch möglich; nach der aktuellen Betreiberpriorität wird die Strukturklärung vorgezogen.

### TXT-Import: vorbereiteter Zielablauf
Privater Upload → Format/Größe/Encoding/Inhalt/Duplikate/Herkunft prüfen → Vorschau → ausdrückliche neue versionierte Übernahme.
Bindung: module_id + format/schema_version + catalog_id + content_version + content_hash + Reihenfolgehash + Owner/tenant/Sichtbarkeit + Herkunft/Rechte.
Gemeinsame Veröffentlichung ist getrennte Adminentscheidung. Jobs speichern die genaue Version; neue Releases überschreiben weder laufende Jobs noch historische Sitzungen. Alte referenzierte Versionen nicht ungeprüft löschen. Keine Dateipfadwahl/SQL-Ausführung durch Browser. Aktuelle Startindexierung bedeutet keinen Hot-Swap; Snapshot/Worker ist gesondert zu prüfen.

## E. Prüfungen und notwendige nächste Schritte
Belege unter runtime/rw-local-closeout-20261005. Keine laufenden oder kanonischen Produktdateien, echten Fälle, Tasks oder Liveinstanzen geändert. Der isolierte Entropiekandidat enthält die separat geprüfte Providerkorrektur.
- Frisch: **93** Kontext-/Experimentalinput-/Broadcastbindung-/GV2-/Bildtests und **22** Bild-/Script-/CopyGuard-Tests bestanden, keine Skips/Fehler. Bestehende Starlette/httpx-DeprecationWarning unverändert.
- Frisch im Browser auf eigenem Port8111: Bildschichten, 16x10-Zahlenscan, separates Overlay Erzeugen/Verstärken/Zurücksetzen, Peggotty ANALYZE/PRINT und sichtbare Duplikatfehler, 375px ohne Seitenüberlauf und Tastaturfokus. Screenshots geprüft; keine vollständige WCAG-Abnahme oder persönliche Nutzerabnahme.
- Kamera tatsächlich drei Minuten geöffnet/gestoppt; physische USB2.0 FHD UVC ausgewählt. Kein vollständiges 200er-Paket, Feed0. **Kameranachweis nicht bestanden**, keine Entropiequalität attestiert. Frage zum realen Livebild/Bewegung offen; Stochastic-Kameranutzung nicht als bestanden melden. Keine Kamerabilder gespeichert.
- Synthetisch bestätigt: drei unterschiedliche persönliche Kontexte liefern bei Originalseed42 und gleichem Katalog exakt gleiche Ratenbytes (VECTOR_STOCHASTIC_LIMITATION.json). Erster aktiver Stochastic-Falllauf HTTP200 nach6,628s und Sitzung gespeichert. Nach korrigiertem Passport-Auslesefehler des Testharness lief der zweite Stochastic-Auftrag in ein45s-Clienttimeout; finaler Serverausgang unbekannt. Eigener8111-Prüfdienst nach Shutdown-Anforderung kontrolliert beendet. Kein allgemeiner Stochastic-Abschluss behauptet.
- Neu reproduzierter Fehler: RandomOrgSource versucht nach Ausfall bei jeder Ziehung einen neuen Netzwerkabruf. Isolierter Korrekturkandidat runtime/rw-entropy-backoff-20261005; valider RED-Test mit synthetischem OSError zeigt2Abrufe statt1. Korrektur, Regressionen und Providerreview abgeschlossen: 21 gezielte und 667 vollständige Tests bestanden, 19 begründete Skips. Eigene TCP-/Prozessrestartprobe bestanden. Siehe [Korrekturbericht](RADIWORKS_ENTROPY_BACKOFF_2026-10-06.md); weiterhin keine Live-/Quell-/Portableübernahme.
- Sieben produktive Dauerinstanzen8103–8109 frisch lesend mit pong bestätigt (LIVE_READONLY.json).
- Echter GV2-Zweizyklenlauf: drei verschiedene künstliche Fall-/Sitzungsbindungen, unveränderte Produktionsuhr/Worker/OS-Ziehung, kein Port/Livehome. Laufstatus und Abschluss aus STARTED/PROGRESS/TWO_CYCLES/COMPLETE oder FAILED lesen. COMPLETE inzwischen passed:true:3Bindungen/2realeZyklen/6Records,6Originaldateienunverändert,Historie nachApprestarterhalten. Keine pauschaleVollabnahme daraus. App-Neustart im Harness ist kein vollständiger Windows-/Prozess-Recoverytest; Testschlüssel nur im Arbeitsspeicher.

Priorität: Vektor-/Broadcastgrenzen und Datenvertrag klären → echte GV2-Zyklen abschließen → Kamera bei bestätigter realer Umgebung / Stochastic / Wiederherstellung prüfen → BC1-Kontextentwurf und gezielte Bedien-/Experimentalabnahme → ausgewählte Originaleinstellungen als getrennte Erweiterungen → lokalen Prototypstatus dokumentieren/sichern → Radi144-Dateninventar und Vorbereitung. S4.8 bleibt 0% Freigabe; Hostrechte/-DB und spätere Gesamtmatrix separat.

## Quellen und Review
Aktueller Pin: runtime/rw-c23-fixed-release-20261005, PRODUCT_MANIFEST.json. Relevante Klassen: personal_context, experimental_context, experimental_matrix::_score, draft::begin_promotion, broadcast::_resonance_draw, main AutoMode enqueue, api/routes direct/images broadcast.
Aurelia: C:/Users/Hubert111/Documents/ChatGPT/Aurelia/docs/05-data.md.
Templates: standards/API_CONTRACT.md und standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md; MODULE_REGISTRY.md und GEMEINSAME_PUNKTE_AURELIA.md liegen im Projektroot C:/Users/Hubert111/Documents/Modul_Templates. Historische Aussagen sind keine Hostabnahme.
Brainpower: RADIWORKS_AURELIA_KATALOGVERWALTUNG_2026-10-05.md und aktueller C23-/Quell-/Sicherungsbericht.

Luna6/max: begrenzter lesender Datenvertrag-/Registry-Abgleich und anschließend isolierte Entropiefehlerkorrektur mit RED-/GREEN-Regressionsprüfung. Astra6/medium: unabhängiger Review mit Präzisierungen Matrix-RNG, gespeicherter Notification-Default und Nutzerrechte innerhalb eines Mandanten. Root: konkrete Enqueue-Grenzen, aktuelle Testausführung, Browser-/Kamera-/Vektor-/GV2-Nachweise und Konsolidierung. Astra konnte nicht sämtliche Enqueue-Stellen unabhängig nachlesen; die konkreten Stellen wurden von Root geprüft. Keine gemessene Tokenersparnis und keine Änderung des Hermes-Anwendungsroutings.

Frische Inventarquellen: Radi144/app/api/resonance.py::_list_db_files/_read_db_entries, app/services/json_store.py, app/services/client_registry_service.py und app/interchange_bus/consumer_store.py; C:/morphic_v1/core/quantum_synergy/database_manager.py sowie services/description_service.py, remedy_service.py und harmonization_worker.py. Keine Produktmodule importiert/ausgeführt oder geändert; bestehende Datendateien nicht geöffnet. Keine externe Modellübermittlung durch diesen Inventarread.

Prüfabschluss 06.10.2026: Vektor- und Datenfragen quellgebunden beantwortet; BC1 konkret entworfen, noch nicht implementiert. Entropiekorrektur: 100% des abgegrenzten Kandidatenpakets, Liveübernahme 0%. GV2-Zweizyklusnachweis abgeschlossen; Kamera offen; S4.8 weiterhin 0% Freigabe. Keine Gesamt-Reifeprozentzahl aus Testzählern ableiten.

## Abgegrenzter Phasenstand nach den Prüfungen

| Schritt | Fortschritt des bezeichneten Pakets | Grenze |
|---|---|---|
| Vektor-/Datenquellenabgleich | 100% des jetzigen Abgleichs | kein vollständiger Intake aller zukünftigen Module |
| Bild/Area/Peggotty-Prüfpaket | 100% der genannten synthetischen Prüfungen | persönliche Abnahme und Kamera getrennt |
| GV2: zwei reale Zyklen | 100% | drei künstliche Bindungen; App-Neustart, kein Windows-Recovery |
| Stochastic-Fehlerkorrektur | 100% im geprüften Kandidaten | Live-/Quell-/Portableübernahme noch 0% |
| BC1 gemeinsame Zielbindung | Entwurf vorhanden; Umsetzung 0% | Promote-Bindung funktioniert bereits |
| Kamera-Hotbits | Abnahme 0% | Versuch ausgeführt, kein Paket angekommen |
| Modul-/Katalog-Hostvertrag | geprüfter Entwurf und erstes Inventar | Schema-/Rechte-/Aboentscheidungen und Hostumsetzung offen |
| Aurelia S4.8 | 0% Freigabe | eigenständige spätere Abnahme |

Prozentangaben betreffen nur diese Arbeitspakete; keine Gesamt-Reife- oder Integrationsprozentzahl.
