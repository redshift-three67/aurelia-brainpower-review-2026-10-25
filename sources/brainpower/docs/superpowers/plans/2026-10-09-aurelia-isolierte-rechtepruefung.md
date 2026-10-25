# Aurelia: isolierte Rechteprüfung und Datenbindung – Prüfplan

> **Für die Ausführung:** Aufgaben einzeln mit Prüfnachweisen und Review abarbeiten. Dieser Plan bereitet Tests vor; er ermächtigt weder Änderungen an den produktiven Cloud-Projekten noch Datenmigrationen oder eine S4.8-Freigabe.

**Ziel:** Wirksame Nutzerrechte, Klienten-/Sitzungsbindungen und Mediengrenzen vor der gemeinsamen Strukturentscheidung nachweisen.

**Architektur:** Zunächst den heutigen Modulbestand unverändert in einer isolierten Testumgebung charakterisieren. Anschließend die noch zu beschließenden Aurelia-Regeln getrennt testen. Datenbankrechte, Anmeldung/API, Storage und privilegierte Worker sind eigenständige Prüfgrenzen; ein bestandener Teil ersetzt keinen anderen.

**Technik:** Gebundene Explorer-/Thom-Quellen, PostgreSQL 17.6 als beobachtete Cloud-Version, vorhandene Lovable-Cloud-APIs und Storage. Konkrete Testdienste werden erst nach Nachweis einer isolierten Zielumgebung aktiviert.

Stand 09.10.2026. **P1-Teilausführung abgeschlossen: 363 SQL-Aktionen, 317 erfüllen den Sollvertrag, 46 Zielabweichungen.** Die übrigen P2/P3-Grenzen bleiben offen; [Ergebnis und Grenzen](../../verification/AURELIA_P1_RECHTE_2026-10-09.md). Es wurden keine synthetischen Nutzer in der Cloud angelegt, Testdaten importiert oder produktive Policies geändert. Lokale Dokumentprüfung ist keine Rechte-Abnahme.

## 1. Verbindliche Ausgangsbelege

| Quelle | Gebundener Stand | Aussagegrenze |
|---|---|---|
| Explorer, Copen/Bohm | `c69d5aa224018b0484efd90ae456a10aecc78a77`; Projekt `8432eebb-5390-4c07-83e7-bcddaaa60775` | Quellcommit, kein Nachweis des aktiven Edge-/Worker-Builds |
| Thom | `18e6c12c238985da698f9a46743d893b30d61ba7`; Projekt `7d414a8e-f393-427d-962d-848204bdd57c` | Quellcommit, kein vollständiger 3D-/Runtime-Nachweis |
| Cloud-Metadaten | PG17.6; acht hashgeprüfte API-Dateien unter `runtime/aurelia-three-modules-20261009/reference-plan/db-metadata/live-20261009-222316` | Lesende Admin-Abfragen; getrennte Snapshotzeitpunkte, keine Nutzerdaten-/Storage-Sicherung |
| Gemeinsamer Bestand | [Modulmatrix](../../AURELIA_MODULDATEN_BESTAND_2026-10-09.md), [Datendomänen](../../AURELIA_DATENDOMAENEN_ECHTZEIT_2026-10-09.md), [Referenzbefunde](../../AURELIA_REFERENZPRUEFUNG_COPEN_BOHM_THOM_2026-10-09.md) | Statische und begrenzte synthetische Belege; offene Quellen/Abnahmen bleiben offen |

Rohinventare, Exportdatensätze, Funktions-/Policy-Literale, Schlüssel und Medien werden nicht an Review-Agenten oder externe Modelle weitergegeben. Sie bleiben lokal geschützt. Review erhält nur abgeleitete Fakten und Testaussagen.

## 2. Umgebungen und Freigabegrenze

| Ebene | Umgebung und Methode | Darf was belegen? |
|---|---|---|
| P0 | Vorhandene Quellen/Metadaten lesend vergleichen | Struktur und offene Voraussetzungen; keine Endnutzerrechte |
| P1 | Leere, ausdrücklich isolierte PostgreSQL-Testinstanz mit notwendigen Auth-Funktionen, Rollen, Grants, Policies und Constraints des gebundenen Stands | SQL-Rechte im konkret nachgebildeten Stand; keine echte Anmeldung, Gateway- oder Storage-Abnahme |
| P2 | Separates Staging-Projekt mit echten künstlichen Konten und bekannten API-/Storage-/Worker-Versionen | Wirksame authentifizierte Endpunkte in diesem Staging, keine automatische Übertragung auf die Produktion |
| P3 | Später beschlossener Aurelia-Adapter mit Tenant, Mitgliedschaft, Modulrecht und Objektberechtigung | Plattformvertrag erst nach Implementierung und eigener Abnahme |

P1 ist als begrenzte eigene PostgreSQL-17.6-Instanz eingerichtet, im ausgewählten Umfang geprüft und wieder beendet. Das ist keine Gesamtabnahme. P2 ist **nicht eingerichtet oder abgenommen**. Kein Test gegen die beiden oben genannten Produktions-IDs. Vor Ausführung isolierte Ziel-ID/Host, Schemafassung, Auth-/Storage-Konfiguration, erlaubte Endpunkte und administrativen Einrichtungszugriff ausdrücklich binden. Eine Kopie nur der Quellmigrationen darf nicht als exakter Cloud-Klon bezeichnet werden: Funktionskörper, Grants, Rollenmitgliedschaften, Trigger und Constraints müssen für den Testumfang übereinstimmen oder als Abweichung ausgewiesen werden. Definitionshashes allein liefern keine nachbaubaren Funktionskörper.

In P1 werden Rechteaktionen unter nicht privilegierten Rollen ausgeführt. Ein administrativer Fixture-Loader ist getrennt; er führt keine Nutzerassertionen aus. `SET LOCAL ROLE`/Claims in P1 simulieren DB-Kontext und sind kein Beleg für gültige JWTs. In P2 stammen Tokens aus echten Testanmeldungen; keine selbst erfundenen Produktions-Claims. Tokens bleiben im flüchtigen Testprozess, nicht in Belegen oder Chat.

Netzwerk-Allowlist umfasst nur das isolierte Ziel. KI-Dienste, externe Hardware, E-Mail und produktive Relay-/Worker-Endpunkte bleiben gesperrt. Fest eingebaute URLs vor Start überprüfen; eine andere ENV allein genügt bei Thom nicht. Keine unbeabsichtigten Berechnungen aus Mount-/Realtime-Nebeneffekten zulassen. Fehlende Isolation führt zum Halt vor Ausführung.

## 3. Künstliche Fixtures und Testregeln

| Alias | Bedeutung |
|---|---|
| A, B | Zwei gewöhnliche Testnutzer ohne Admin-/Service-Rolle; verschiedene Eigentümer |
| D | Testnutzer für später ausdrücklich geregelte Delegation; zunächst ohne Freigabe |
| X | Administratives Testkonto für separate Admin-Regeln; niemals Ersatz für A/B |
| CA, CA2, CB, C0 | Zwei verschiedene künstliche Klienten von A, ein Klient von B sowie Eigentümer-NULL nur dort, wo das aktuelle Schema dies erlaubt |
| SA1, SA2, SB1 | Zwei Sitzungen von CA und eine von CB, mit unterscheidbaren künstlichen Ergebnissen |
| JA1, JA2, JB1 | Aufträge mit eindeutigem Klienten-/Kontext-/Sitzungsbezug, soweit der Ist-Vertrag dies ausdrücken kann |
| MA, MB | Selbst erzeugte Testbilder ohne Personen, getrennte Eigentümer-/Pfadbezüge |
| TA, TB | Späterer Aurelia-Mandantenkontext; heute keine aus `user_id` erfundene Mandantenspalte |

Alias-IDs je Testlauf neu erzeugen und in einem lokalen Fixture-Manifest auflösen; keine Identifikatoren aus Exporten übernehmen. Der Loader verwendet die tatsächlichen Pflichtfelder/Enums/Constraints des geprüften Schemas und bricht bei Abweichung ab. NULL-Eigentümer nur in zulässigen Tabellen erzeugen; `patients_v2.user_id` nicht künstlich nullable machen. Fixtures zunächst administrativ rücklesen, damit negative Tests nicht wegen fehlender Testdaten scheinbar bestehen.

Pro Nutzerkontrollfall: eigenes Objekt positiv lesen/ändern, fremdes bekanntes Objekt direkt über ID lesen/ändern; nach verbotenen Writes administrativ bestätigen, dass nichts verändert wurde. Ein HTTP-200 oder SQL-UPDATE mit null betroffenen Zeilen ist kein erfolgreicher positiver Write. Eine SQL-Constraintverletzung ist kein nachgewiesener RLS-Deny. SELECT kann durch RLS leer ausfallen, INSERT kann Fehler liefern: Entscheidung, Rückgabe und Nebenwirkung jeweils erfassen.

Nur vorab erzeugte Fixture-IDs auslesen; keine Geschäftsobjekte suchen. Fehlermeldungen in Kategorien/SQLSTATE zerlegen und sensible Inhalte entfernen. REST-Antworten, Realtime und Fehlermetadaten ebenfalls auf fremde Fixture-IDs/Inhalte prüfen. Ein FK erzwingt Existenz, nicht automatisch Eigentümergleichheit; referentielle Checks können RLS umgehen. [PostgreSQL 17 RLS](https://www.postgresql.org/docs/17/ddl-rowsecurity.html).

## 4. Konkrete Testfälle, nach Priorität

R01–R04/R09 wurden im ausgewählten P1-Umfang charakterisiert; P2/P3 und weitere Varianten bleiben **nicht ausgeführt**. Die Tabelle beschreibt weiterhin den Sollvertrag; [Ist-Ergebnisse](../../verification/AURELIA_P1_RECHTE_2026-10-09.md) sind getrennt dokumentiert. „Soll“ ist der vorgeschlagene Abnahmevertrag, keine Behauptung heutigen Verhaltens. Ist-Ergebnisse werden unabhängig davon gespeichert. Wo Delegation/Adminrechte oder laufende Aboänderungen noch nicht beschlossen sind, zunächst nur Ist-Verhalten erfassen und keine Freigabe vergeben.

| ID / Ebene | Aktion und Kontrollfall | Soll / besondere Grenze |
|---|---|---|
| R01 / P1+P2 | A/B lesen und ändern CA/CB jeweils einzeln über bekannte ID; anon versucht dasselbe | Eigene erlaubte Aktionen gelingen, fremde/anonymous klientenbezogene Daten bleiben unsichtbar und unverändert |
| R02 / P1+P2 | A erzeugt Auftrag für CA; danach Insert/Umhängen auf CB; bekannte JB1 lesen/ändern/löschen. Zusätzlich CA behalten und vorhandene Vektor-/Protokoll-/Sitzungsfelder mit CB-Referenzen befüllen; INSERT und UPDATE getrennt | Fremder Klient darf nicht durch eigene Auftrags-`user_id` oder gültigen FK zugänglich werden. Haupt- und abhängige Objekte rücklesen; gültige eigene Referenz als Gegenfall, widersprüchliche CA/CA2-Referenzen separat prüfen |
| R03 / P1+P2 | Thom A/B greifen auf C0 und dessen Fixture-Auftrag zu; positiver CA/JA1-Kontrollfall | NULL-Zweig der Jobs-ALL-Policy zusammen mit clients-RLS bewerten. Kein NULL-Fremdzugriff allein aus Policytext behaupten |
| R04 / P1+P2 | Explorer v1/v2 jeweils R01/R02 für Klient, Analysearchiv, Harmonisierung und Vorlage ausführen; eigene Haupt-ID mit fremden vorhandenen Patienten-/Archiv-/Sitzungsreferenzen bei INSERT/UPDATE kombinieren | Beide Familien getrennt, einschließlich abhängiger Owner-/Patientbezüge und widersprüchlicher eigener Klientenreferenzen; kein pauschaler v2-Erfolg für v1 oder umgekehrt. Fehlende Bindungsfelder als Vertragslücke dokumentieren |
| R05 / P2 | Bohm CA berechnen/testen, auf CB wechseln, archivieren; dann CB neu berechnen ohne neuen Worttest | Ergebnis bleibt ursprünglichem Kontext zugeordnet oder Speichern wird gesperrt. Nicht fremde/alte Werte still neu etikettieren; gebundener Quellpfad zeigt bereits ein Risiko |
| R06 / P2 | Thom JA1/JA2 für SA1/SA2 erstellen und laden; Quellen-/Payload-/Schemafeld vergleichen | Unveränderlicher Sitzungsbezug eindeutig. Aktuell fehlt `harmonization_jobs.session_id`; Fall ist Vertragslücke, kein durch zusätzlichen Insertwert gelöster Fehler |
| R07 / P2 | Copen paused-Sitzung neu laden und remounten; Start/Pause/Resume/Cancel kontrolliert ausführen | Anzeige und bestätigter gespeicherter Zustand zusammenpassen; Laden/Wiederholung startet nichts eigenmächtig |
| R08 / P2 | Zwei künstliche Queues desselben Nutzers mit getrenntem Klient/Modul/Batch; zwei kontrollierte Worker-Claims | Keine fremde Queueübernahme oder doppelte Ausführung; fehlende Claim-/Lease-Grenze gesondert protokollieren, keine Production-Worker starten |
| R09 / P1+P2 | A versucht eigene Adminrolle bzw. Ownerbezug per Write/aufrufbarem Helfer zu ändern; X-Kontrollfall gemäß definierter Adminregel | Keine Selbstprivilegierung; SECURITY DEFINER inklusive search_path, dynamischem SQL, Trigger-/RPC-Kontext prüfen. PUBLIC EXECUTE allein ist kein Exploitnachweis |
| R10 / P2 | Gültiges eigenes Token als Gegenfall; Anfrage ohne Token, mit B-Token auf A-Fixture, ungültiger/manipulierter Signatur und abgelaufenem Testtoken an privilegierte Edge-/Worker-Funktion | Authentifizierung und Objektberechtigung serverseitig, Identität aus verifizierter Sitzung statt Requestfeld. Servicekonto darf kein beliebiges Client-/Sessionziel übernehmen. Ablauf nach dokumentierter Uhr-/Skew-Grenze prüfen; nur isolierte Deployments, Nebenwirkungen trotz Fehlerantwort prüfen |
| R11 / P2 | MA/MB hochladen, listen, bekannte Objekt-URL ohne Anmeldung abrufen; A greift auf MB zu | Vertrauliche Medien privat. Öffentliche Thom-`client-photos`-Konfiguration als erwartete Zielabweichung festhalten, nicht still während Charakterisierung ändern |
| R12 / P2 | Signierte Fixture-URL erstellen, vor/nach Ablauf abrufen, anderen Nutzer testen; A versucht MB zu signieren | Nur berechtigter Aussteller, definierte TTL; Kopie der gültigen URL bleibt bis Ablauf nutzbarer Bearerzugriff. Sofortiger Widerruf dadurch nicht automatisch garantiert |
| R13 / P2 | Zwei getrennte Realtime-Anmeldungen; A aktualisiert JA1/CA und B SB1/CB; reconnect/replay prüfen | Keine fremden Inhalte/IDs, kein erneutes Auslösen von Befehlen. Publikationsmitgliedschaft allein beweist weder Zustellung noch Empfängerrechte |
| R14 / P3 | A in TA liest/schreibt TA; fremdes TB-Ziel und unbestätigte gemeinsame Klienten-ID anfragen | Tenantzugehörigkeit UND Objektberechtigung; keine Vereinigung nach Name/Geburtsdatum. Heute noch kein implementierter Plattform-Testpfad |
| R15 / P3 | D ohne Delegation, mit begrenzter read-Delegation, nach Widerruf dieselbe CA-Operation; write separat | Rechte nicht aus Rolle/Therapeutenstatus ableiten. Umfang, Modul, Klient und Widerruf ausdrücklich festlegen; ohne Regel keine Annahme legitimer Fremdnutzung |
| R16 / P3 | Modul-Abo aus/an/abgelaufen für gleichen eigenen Fall; Start/Export/Download getrennt prüfen | Abo ersetzt keine Objektberechtigung. Umgang mit laufenden Jobs und historischen Exporten vor Abnahme entscheiden |
| R17 / P3 | Gleicher Auftragsstart zweimal und zeitgleich; Wiederanlauf nach Annahme/Start/Abschluss | Idempotenz, Versuch-ID, Rechtebindung und Ergebnisveröffentlichung ohne Doppeljob; archiviertes Ergebnis löst keinen neuen Auftrag aus |
| R18 / P3 | Private vs. freigegebene Kataloge/Vorlagen; Autorisierung ändern, alte Auftragsrevision erneut laden | Nutzerimport nicht automatisch global; Quelle/Revision/Dubletten erhalten; Lizenz-/Freigabe nicht aus technischem Zugriff ableiten |
| R19 / P3 | Bericht/Trend/Favorit/Clipboard aus SA1; anderer Nutzer, Tenant, Modul und fehlendes Modulrecht greifen zu | Getrennte Sichtbarkeiten und unveränderte Quellen-/Regelrevision; verschiedene Kennzahlen nicht als identische Messung aggregieren |
| R20 / P3 | Einen Trigger doppelt/replayed zustellen, Rechte widerrufen, Reconnect durchführen | Genau definierte Deduplizierung und aktuelle Autorisierung; nur lokaler Zustellstub, keine Mail oder externe Nachricht |
| R21 / P3 | Fünf Layer plus Audioprofil/3D-Modell revisionieren; Fall ändern, alten Auftrag wieder laden | Verwendete Asset-/Profil-/Modellrevisionen bleiben eindeutig; unsichtbare Layer und Originalbytes erhalten; Downloadrechte erneut prüfen |
| R22 / P2+P3 | Nur Fixture-DB-/Objektbestand gemeinsam sichern, kontrolliert löschen, isoliert wiederherstellen | Beide Bestände und Referenzen vollständig prüfen; kein Wiederbeleben zuvor gelöscht gesperrter Inhalte. Aufbewahrungs-/Löschvertrag vor Plattformabnahme festlegen |

Für R01–R04 und R11 zusätzlich Variante „vermutlich bekannte fremde ID existiert nicht“ vergleichen: Antwort darf keine unnötigen fremden Details preisgeben. Timing-/Lastgrenzen getrennt beurteilen; kein pauschales Side-Channel-Freiheitsversprechen.

## 5. Ausführungsreihenfolge und verantwortliche Dateien

Dieses Plan-Dokument bleibt der öffentliche Prüfvertrag. Private Fixture-/Ergebnisbelege gehören in einen neuen, zeitgestempelten Ordner unter `runtime/aurelia-three-modules-20261009/reference-plan/rights-execution-*`, niemals in Quellprojekte. Geplante Artefakte: `ENVIRONMENT.json`, `FIXTURES.json`, `RESULTS.json`, `MANIFEST.json`, `COMPLETE.json`. Diese P1-Artefakte liegen nach tatsächlicher Ausführung unter rights-execution-20261009-231423 vor; sie ersetzen keine P2/P3-Ausführung.

- [x] **P0:** Quellen-/Cloud-Belege und gemeinsame Datenbereiche konsolidieren; heutige Ausführungsgrenzen benennen.
- [x] **P1.1 (ausgewählter Umfang; Grenzen im Ergebnisbericht):** Isolierte Zielumgebung binden, ihre Admin-/Nutzerrollen und ausgehenden Endpunkte prüfen. Fixture-Loader darf nur dieses Ziel verwenden; Abweichungen vom aktiven Schemasnapshot zuerst dokumentieren.
- [x] **P1.2 (14 Tabellen/197 Spalten; Auth-ID-Stub und inaktive ungetestete Rollen ausdrücklich ausgewiesen):** Pflichtfelder, Typen, Grants, Funktionsdefinitionen und Trigger lokal erfassen; Fixtures ohne reale Exportdaten anlegen und administrativ rücklesen. Ein Testnutzer darf keine BYPASSRLS-/Ownerrechte besitzen.
- [x] **P1.3 (349 Hauptaktionen plus 14 TRUNCATE-Proben; keine Gesamtfreigabe):** R01–R04/R09 unter nicht privilegierten Kontexten ausführen. Jeder Negativfall benötigt positiven Gegenfall und administrative Nebenwirkungsprüfung. Je Mutation eigener Transaktions-/Savepointrahmen; Fehler verursachen ROLLBACK, nicht Folgetests in defekter Transaktion.
- [ ] **P2.1:** Echte künstliche Anmeldungen und bekannte isolierte API-/Storage-/Worker-Builds binden. R01–R04 und R09 ausdrücklich über den echten Nutzertransport wiederholen, einschließlich der Querreferenzfälle. Negative Token-/Objekt-/Workerfälle aus R10 ausführen; privilegierten Loader nicht als Nutzertransport verwenden.
- [ ] **P2.2:** R05–R13 und Fixture-Restoreteil von R22 prüfen. Cross-Client-/Archiv-/Pausen-/Realtime-Resultate getrennt von Berechnungsformeln dokumentieren.
- [ ] **P2.3:** Eigene Fixtures/Konten/Storage-Objekte über Manifest bereinigen, Restbestand prüfen; isoliertes Testziel erst danach entfernen. ROLLBACK einer DB-Transaktion bereinigt keine HTTP-/Storage-/Worker-Nebenwirkungen. Niemals glob-/bucketweite Production-Löschung.
- [ ] **Entscheidung:** Ist-Befunde mit offener Delegation, Abo-/Widerrufsregeln und Quellenständen besprechen. Vor Produktkorrektur Ursachen isolieren und Änderung gesondert freigeben; keine Formeln ersetzen.
- [ ] **P3:** Beschlossene Adapter-/Tenant-/Abo-/Archiv-/Assetverträge implementieren und R14–R22 separat abnehmen. Erst danach normative Modul_Templates und produktive Integrationsgates aktualisieren.

## 6. Prüfnachweis und Abnahme

Pro Fall: Test-ID, Zeitpunkt, isolierte Umgebung/Version, Quellen- und Schemafingerprint, Fixturealias, echte bzw. simulierte Rolle, Operation, erwartetes/erhaltenes Ergebnis, betroffene Zeilen, Fehlerkategorie, vor/nach Nebenwirkungen und Ergebnisstatus. Zulässige Stati: **bestanden, Zielabweichung, Testfehler, nicht ausführbar, nicht ausgeführt**. Nicht ausführbare oder fehlgeschlagene Tests zählen nicht als bestanden; bekannte Ist-Lücken bleiben auch bei erfolgreicher Reproduktion Zielabweichungen.

Ein DB-Test als postgres, ein UI-Mock oder ein öffentliches Bucketflag ist keine Rechte-Abnahme. P1 belegt nur die nachgebildete DB; P2 die gebundenen Staging-Endpunkte. Produktion benötigt später einen eigenen, genehmigten Nachweis gleicher Konfiguration/Version und geeignete Regression. RLS wird für die Prüfung nicht abgeschaltet. [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Storage-Zugriffsmodell](https://supabase.com/docs/guides/storage/buckets/fundamentals).

Ergebnisreview anhand bereinigter Fakten; keine Rohdaten-/Schlüsselweitergabe. Abschluss umfasst manifestierte Rückleseprüfung der Dokument-/Testbelege, unveränderte Originalquellen und geschlossene eigene Testdienste. Dieser Sicherungspunkt ist keine neue F:-Vollsicherung, kein Cloudbackup und kein Gesamt-Restore.

Vorbereitungsreview: Luna6/max prüfte die Abdeckung der gemeinsamen Datendomänen. Astra6/medium prüfte nur den Plan und die neuen Matrixabschnitte, keine Rohinventare. Seine Ergänzungen zu abhängigen Quer-FKs, P2-Wiederholung sowie manipulierten/abgelaufenen Tokens sind übernommen. Review ersetzt weder Testausführung noch Betreiberfreigabe.

## 7. Ergebnis des begrenzten P1-Laufs

[Prüfbericht](../../verification/AURELIA_P1_RECHTE_2026-10-09.md): 317 erfüllte Sollaktionen, 32 angenommene widersprüchliche Klientenreferenzen, 14 erlaubte SQL-TRUNCATE-Leerungen. Vollständige ausgewählte Fixture-Tabellen vor ROLLBACK rückgelesen, abschließender Ausgangsbestand unverändert; eigene Testinstanz beendet. P2-Wiederholung, echte Anmeldungen/Token, Storage, Worker, Realtime, fehlende IDs/Side-Channels, Delegation/Abo und P3 bleiben offen. Nicht behaupten, alle 22 Fallgruppen seien abgenommen.


## 8. P2-Vorbereitung nach der Pause, 10.10.2026

**Status: vorbereitender Quellen-/Einrichtungsabgleich, keine P2-Ausführung.** Die zwei Quellcommits sind frisch bestätigt, alle 562 lokalen Quelldateien hashgleich. Sechs ausgewählte Funktionsfingerprints stimmen mit P1 überein; dies umfasst vier Anwendungsfunktionen und zweimal die providerverwaltete `auth.uid`. Auth-Systemtabellen und Auth-Funktionen werden für P2 nicht durch die P1-Stubs ersetzt.

Begrenzte READ-ONLY-Abfragen prüfen Trigger an den ausgewählten Anwendungstabellen und `auth.users`/`auth.identities`: ein Thom- und acht Explorer-Anwendungstrigger, keine nichtinternen Auth-Trigger im geprüften Umfang. Das ist kein Nachweis ausgeschlossener externer Auth-Hooks oder transitiver Ausgänge. Im Explorer sind `pg_cron` und `pg_net` vorhanden; zwei aktive Zeitpläne enthalten HTTP-/Funktionsendpunktindikatoren. Keine Command-Literale, Header, Schlüssel, Funktionskörper oder Geschäfts-/Auth-Datensätze wurden in diesem P2-Abgleich abgefragt. Eine erste Explorer-Abfrage verwendete zwei falsche singuläre Archivtabellennamen; sie wurde korrigiert und wiederholt. Ausschließlich das korrigierte Ergebnis ist maßgeblich.

Die Thom-Analyse verbindet beim Mount ein Widget mit einer festen bisherigen Backend-WebSocketadresse (`RealtimeSyncService.ts:53–55`, `RealtimeStatusWidget.tsx:20–29`, `Analyse.tsx:253`). Vite-Remapping alleine trennt diesen Pfad nicht. Frontend, CLI-Projektreferenz und privilegierte Deployment-Umgebung sind verschiedene Zielbindungen; automatische Mount-Aufrufe, Editor-Tokenbroker und optionale lokale KI-/Hardwarepfade dürfen keine Test-Isolation umgehen. Dies sind statische Quellenbefunde, kein aktiver Endpunktnachweis.

**Einrichtungsvorschlag:** zwei neue leere, zugriffsbeschränkte und unveröffentlichte Lovable-Cloud-Testprojekte „Aurelia P2 Explorer“ und „Aurelia P2 Thom“. Keine direkte Projektkopie, solange die Übernahme von Zeitplänen/Automationen nicht geklärt ist. Keine Historie, Anhänge, produktiven Datensätze, Secrets, Cronjobs, Webhooks, Edge-Deployments oder Frontendquellen übernehmen. Nur ausgewählte Anwendungstabellen samt geprüften nötigen Abhängigkeiten später administrativ aufbauen. Das ist ein begrenztes Teilstaging, kein vollständiger Cloud-Klon.

Vor der Erstellung fehlen noch die Betreiberfreigabe für die neuen Cloud-Ressourcen und die bestätigte wirksame Europa-Erstellungsregion. Der Connector liefert keinen Regionsparameter. Die Region ist nach Provisionierung unveränderlich; ein vorgeschriebener Business-Workspace-Default kann sie festlegen. Nach Erstellung effektive Region und Identitäten rückprüfen, bevor Anwendungsschema oder Testnutzer geschrieben werden. [Lovable Cloud](https://docs.lovable.dev/features/cloud).

| Reihenfolge | Einrichtung und Aussagegrenze |
|---|---|
| P2.0 | Neue Projekt-/Backendidentität, Region, Zugriffsbeschränkung, unveröffentlichter und leerer Ausgangszustand binden; unbekannte automatische Ausführung sperrt den Start |
| P2.1a | Notwendige Funktions-/Triggerabhängigkeiten, Besitzer/search_path und Zielbindungen lokal prüfen; ausgewählte Anwendungsschemas aufbauen, danach RLS/Grants/Constraints vergleichen; keine vereinfachte Ersatzlogik |
| P2.1b | Provider-Auth-Konfiguration/Hooks prüfen; echte künstliche A/B-Konten ohne Einladungsmail administrativ anlegen, normale Rollen rückprüfen, danach echte Passwort-Anmeldung und REST-Positiv-/Negativfälle |
| P2.1c | Storage-Bucketparameter UND Objektpolicies/Grants vergleichen; bekannte künstliche Medien mit echten Nutzer-JWTs auf Eigen-/Fremd-/Anonzugriff, Nebenwirkungen und signierte URL prüfen |
| P2.2 | Frontend, Realtime und privilegierte Worker separat in quarantänisierten Deployments binden; bestehende produktive Ziele und externe KI/Hardware/Mail bleiben ausgeschlossen |
| P2.3 | Manifestgebundene Fixture-Sicherung/Restore/Bereinigung; keine breite Produktions- oder Bucketlöschung |

Private aktuelle Metadaten/Belege: `runtime/aurelia-three-modules-20261009/reference-plan/p2-preparation-20261010-062156Z`. Keine Cloud-Testprojekte, Testkonten oder Fixtures angelegt; keine produktiven Writes. Die Regions- und Ressourcenfragen sind offen. Ein echter Nutzertransport, Storage- oder Worker-Erfolg wird erst nach Ausführung ausgewiesen.

Luna6/max prüfte aktive Quellpfade lesend; Astra6/medium prüfte die abgeleitete Isolationsmethode unabhängig. Keine Rohdefinitionen, Datensätze oder Schlüssel an Helfer. Review erteilt keine Freigabe. RadiWorks-Dauerinstanzen, Server, bestehende Schemas/Algorithmen, normative Modul_Templates und S4.8 bleiben unverändert.


## 9. Betreiberpriorisierung nach Regionsbild, 10.10.2026

Die Einrichtung aus Abschnitt8 ist **zurückgestellt**, nicht ausgeführt oder abgenommen. „Standard-Region: Nicht festgelegt“ belegt keine effektive Projektregion und keine Europa-Zusage. Für die jetzige Funktionalitäts-/Struktur-/Workflowaufnahme sind neue Cloud-Ressourcen und die Erfassung bestehender Testklienten oder laufender Jobs keine Voraussetzung. Frühere offene Ressourcen-/Regionsfragen blockieren diesen Lesepfad nicht.

Vorrang: [Source-Workflowabdeckung](../../AURELIA_WORKFLOW_ABDECKUNG_2026-10-10.md), eindeutige Objekt-/Ergebnistypen und Writer-/Fehlerpfade, dann modulübergreifender Strukturentscheid. P1-Befunde und P2/P3-Prüfvertrag bleiben erhalten. Reale Auth/API-/Storage-/Worker-/Realtime-/Restore- und gegebenenfalls Regionsnachweise werden vor der jeweiligen Integration/Abnahme benötigt; derzeit keine neuen Konten, Fixtures, Zeitpläne oder Deployments. Keine Übernahme der bestehenden Testklienten vorgesehen.


## 10. Lokale Ist-Portierung als ergänzender Referenzweg, 10.10.2026

Der [neue gemeinsame Phasenplan](2026-10-10-aurelia-module-lokale-referenz-und-datenstruktur.md) empfiehlt lokale strukturtreue Explorer-/Thom-Referenzumgebungen mit eigenen synthetischen Identitäten, Originalbaselines und geprüfter Machbarkeit. Diese technische Ist-Reproduktion liegt vor dem zentralen Strukturentscheid und ist nicht die Implementierung des späteren Aurelia-DB-2-/P3-Vertrags. Neue Cloud-Teilstagings bleiben zurückgestellt.

Vor Einrichtung lokale Ziele und sämtliche festen Cloud-/WS-/Cron-/Workerbindungen prüfen; kein einfaches Umschalten der Frontend-URL und keine Produktions-Secrets/-Klienten übernehmen. Providerkompatible echte Auth/API-/Storage-/Realtimepfade müssen ihren jeweiligen Scope belegen; Mock/Stub nicht als echte Rechteprüfung zählen. Erfolgreiche lokale Tests verleihen weder Produktions-, Migrations-, normative Modul_Templates- noch S4.8-Freigabe. Dieser Empfehlungsplan hat keine Installation oder Laufzeitänderung gestartet.
