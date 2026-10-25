# RadiWorks-Ratenbanken: aktueller Stand und Zielverwaltung in Aurelia

05.10.2026. Lesender Abgleich von RadiWorks-Kandidat EXP1-C1, Aurelia-Datenplan und Modul_Templates. **Empfohlener Zielvertrag, keine bereits implementierte Adminverwaltung oder Serverfreigabe.** Ubuntu-Server/Produktiv-DB wurden für diesen Abgleich nicht verändert oder live geprüft.

## In einfachen Worten

Eine Ratenbank ist hier eine Sammlung von Ratenbezeichnungen und zugehörigen Einträgen. RadiWorks liest heute solche Sammlungen aus `.txt`-Katalogen. Aurelias geplante PostgreSQL-Datenbank hält außerdem Benutzer, Mandanten, Gruppen und Aufträge. Das sind verschiedene Aufgaben; RadiWorks benötigt später einen kontrollierten Katalogzugang über den Adapter und keine eigenen globalen Adminrechte in der Plattformdatenbank.

**Empfehlung:** Aurelia verwaltet Rechte, Versionen und Veröffentlichung zentral. RadiWorks bekommt für jeden Auftrag eine freigegebene, unveränderliche Katalogkopie mit Kennung/Version/Prüfsumme. Ein späteres Katalogupdate verändert dadurch keinen laufenden Auftrag und keine gespeicherte Sitzung.

## Nachgewiesen gegenüber vorgesehen

| Bereich | Aktuell belegter Stand | Empfohlene Aurelia-Ergänzung |
| --- | --- | --- |
| Lesen und Auswählen | RadiWorks liest lokale `.txt`-Dateien; `/databases`, `/rates`, Gruppierung, Suchfilter und erklärbare heuristische Vorschläge vorhanden. Auswahl bestätigt der Nutzer | Adapter gibt ausschließlich Kataloge frei, auf die Nutzer und Mandant Zugriff haben |
| Trennung | `RADIOWORKS_DATA_DIR` als eigener Lesekatalog; `RADIOWORKS_HOME` für Fälle, Drafts, Einstellungen und Journale. Kompatibler Home/data-Fallback | Gemeinsame Lesekataloge getrennt von privaten Listen und personenbezogenen Laufzeitdaten |
| Veröffentlichen | Lokaler Core-Helper `publish_catalog_release` erzeugt Releasekopie/Manifest/Hashes; keine nachgewiesene Nutzer-/Admin-Publish-API | Admin prüft und veröffentlicht versionierte gemeinsame Kataloge; keine direkte Bearbeitung laufender Releasebytes |
| Zusätzliche `.txt`-Listen | Lokaler Mergehelper mit Größen-/Hash-/Duplikatprüfung, keine vollständige Benutzer-Importoberfläche oder Autorisierungsverwaltung | Nutzerimport zunächst privat/mandantengebunden: Dateigröße/Format/Inhalte/Duplikate prüfen, Vorschau zeigen, ausdrückliche Übernahme als neue Version |
| Auftragsbindung | Releasehashes und Ergebnisreihenfolgedigests vorhanden; C1 bindet exakten Katalogname/Text/SHA. Keine belegte komplette Hostauswahl/versionierte Katalogrechte pro Job | Job speichert Katalog-ID, Version, Hash, Zugriffsbereich und Reihenfolge; alte referenzierte Versionen erhalten |
| Datenbank auf Ubuntu | Aurelia-Datenplan sieht PostgreSQL16, `ltree` für Rate-Katalog/Gruppen und tenant_id/RLS für personenbezogene Tabellen vor | Konkretes Katalog-/ACL-/Import-/Adaptermodell implementieren und auf Zielhost mit Positiv-/Negativtests prüfen |
| Mehrmandantenrechte | Lokaler Prozess-Scope; autoritativer Aurelia-Hostkontext ausdrücklich offen | Server bestimmt Nutzer/Mandant/Fall/Job und Rechte; Browserangaben oder fremde Header reichen nicht |

Nicht aus dem Datenplan ableiten, dass PostgreSQL/RLS/Katalogverwaltung bereits produktiv laufen. Historische `pgvector`-Planung ist keine Freigabe semantischer Suche: Die aktuelle Betreiberdirektive bleibt bei vorhandenen stabilen Algorithmen/Heuristiken.

## Rollenempfehlung

- **Aurelia-Admin:** gemeinsame Bibliothek, Themen/Gruppen, Herkunft und Versionen verwalten; Imports prüfen/freigeben; gemeinsame Releases veröffentlichen/archivieren; Berechtigungen und Audit prüfen. Mandantenprivate Daten nicht automatisch durch globale Katalogverwaltung zugänglich machen.
- **Mandantenverantwortlicher, falls diese Rolle eingeführt wird:** geprüfte Listen ausschließlich im eigenen Mandantenbereich veröffentlichen. Abgrenzung zur Plattform-Adminrolle noch ausdrücklich im Rechtevertrag festlegen.
- **Nutzer:** erlaubte Kataloge suchen/auswählen, begründete Fokus-/Themenvorschläge bestätigen; eigene `.txt`-Listen kontrolliert importieren, bearbeiten oder archivieren. Änderungen erzeugen neue Versionen, überschreiben keine gemeinsame Bibliothek und greifen nicht auf andere Nutzer/Mandanten zu.
- **RadiWorks-Modul:** mit genehmigtem Auftrag und gebundener Version rechnen. Keine freie SQL-/Dateipfadwahl durch den Browser und kein Schreiben in globale Kataloge aus einem Analyse- oder Broadcastauftrag.

## Adapterablauf

1. Nutzer wählt aus seinem erlaubten Katalogangebot.
2. Aurelia prüft Identität, Mandant, Berechtigungen, Version und Jobgrenzen serverseitig.
3. Der Katalogservice erstellt/liefert einen unveränderlichen Snapshot. Ein geprüfter RadiWorks-Adapter kann daraus eine read-only `.txt`-Releaseansicht erzeugen; RadiWorks braucht zunächst keinen Austausch seiner funktionalen Parser durch SQL.
4. Der Job bindet Snapshot, Reihenfolge, Fall-/Fokuskontext, Engine-/Formelversion und Parameter. Beide Vergleichswege nutzen ausdrücklich passende gleiche Eingangsgrundlagen.
5. Neue Releases werden erst für neue Aufträge gewählt. Originalresultate und historische Sitzungen behalten ihre gebundene Version. Archivierung/Löschung muss noch referenzierte Versionen berücksichtigen.

Das genaue PostgreSQL-Schema, Rollen-/ACL-Modell, Upload-/Importverfahren, Adapterauthentisierung, Cacheinvalidierung und Widerruf bleiben Implementierungs-/Testaufgaben vor Hostfreigabe. Die aktuelle lokale Engine indexiert den Katalog beim Start; ein produktiver Hot-Swap folgt daraus nicht. Für private Listen wäre zunächst ein eigener autorisierter Snapshot/Worker geeignet, statt den globalen laufenden Repositoryzustand zu ersetzen.

## Einordnung im Plan

Jetzt wird diese Lücke als Kataloggovernance-/Adapteranforderung vorgemerkt. EXP1-C2/C3 vervollständigen den lokalen Vergleichsmodus. Danach weitere Restabnahmen, geprüfte RadiWorks-/Modul_Templates-Synchronisierung, Standalonepaket und vollständige Sicherung. Die endgültige gemeinsame Aurelia-Matrix und Hostintegration folgen den vereinbarten Modulreife-/Hostgates; S4.8 bleibt0%Freigabe. Keine bereits funktionale lokale Originalanalyse wird hierfür vorzeitig ersetzt.

## Quellen und Grenzen des Abgleichs

- RadiWorks-Kandidat `runtime/rw-exp1c-20261005/engine/src/radiworks/main.py`: `default_rate_data_dir` und Startindexierung; `core/rates.py`, `api/routes.py`: vorhandene Lesefunktionen; `core/catalog_release.py` und `core/catalog_merge.py`: Corehelper, keine belegte Admin-/Nutzer-Import-API.
- `C:/Users/Hubert111/Documents/ChatGPT/Aurelia/docs/05-data.md`: Datenplan, insbesondere Ratenhierarchie und personenbezogene RLS. Kein alleiniger Implementierungsnachweis.
- `C:/Users/Hubert111/Documents/ChatGPT/Aurelia/docs/project-control/external-analyses/2026-09-05_radiworks-rate-catalog-separation/README.md`: Lesekatalog-/Runtime-Trennung, ausdrücklich kein automatischer Aurelia-Kanon.
- `C:/Users/Hubert111/Documents/Modul_Templates/standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md`: lokale API, Hostidentität/Mandantenbetrieb/Katalogbindung offen; ältere Nachträge jeweils historische Belege.
- `C:/Users/Hubert111/Documents/Modul_Templates/standards/API_CONTRACT.md` und `GEMEINSAME_PUNKTE_AURELIA.md`: gemeinsame künftige Scope-/Registry-/Rechteverträge. Bestehende Vertragsdifferenz lokaler vs gemeinsamer Analysebody nicht stillschweigend übernehmen.

Quellenhashes für die zusätzlich gelesenen gemeinsamen Dokumente: `runtime/rw-exp1c-20261005/CATALOG_CONTRACT_SOURCES.json`. Keine Vollprüfung aller Aurelia-Komponenten, keine Behauptung über unbesichtigte Live-Serverdienste. Chatdelegation: Luna6/max führte den bounded lesenden Vertragsabgleich durch, Root prüfte die maßgeblichen Quellen und konsolidierte; keine Hermes-Liveaufträge.
