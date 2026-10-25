# Aurelia P1 Rechteprüfung und Klientenbindungen

Die begrenzte lokale SQL-Charakterisierung ist abgeschlossen. **363 Aktionen: 317 erfüllen den vorgeschlagenen Sollvertrag, 46 zeigen Zielabweichungen.** Die 46 bestehen aus 32 widersprüchlichen Klientenverknüpfungen und 14 erlaubten tabellenweiten Leerungen. Das ist keine bestandene Gesamt-Rechteprüfung und keine Cloud-/Produktionsfreigabe. Die bestehenden Module und ihre Algorithmen wurden nicht geändert.

## Gebundener Prüfumfang

| Gegenstand | Nachweis und Grenze |
|---|---|
| Umgebung | Eigene PostgreSQL-17.6-Instanz auf 127.0.0.1:15437, getrennte leere Thom-/Explorer-Testdatenbanken; anschließend kontrolliert beendet. Keine Windows-Daueraufgabe oder Live-Instanz verändert |
| Thom | 5 Tabellen, 66 Spalten, 21 Constraints, 19 Policies, 3 Funktionen, 1 Trigger |
| Explorer | 9 Tabellen, 131 Spalten, 16 Constraints, 42 Policies, 3 Funktionen, 8 Trigger; v1/v2 getrennt |
| Definitionen | Nur ausdrücklich freigegebene Funktionen und Metadaten lesend aus beiden Cloudprojekten; keine Nutzerdatensätze, Authkonten, Medien oder Schlüssel abgerufen |
| Katalogvergleich | Keine Abweichungen im ausgewählten, normalisierten Prüfumfang. Funktionskörper/MD5, Besitzer/search_path, Spalten/Defaults, Constraints, Policies, Trigger und effektive Grants verglichen; Grantor-Zuordnung nicht als Endnutzerrecht abgenommen |
| Nutzerkontext | authenticated/anon ohne Superuser, BYPASSRLS, Login oder Rollenmitgliedschaften. Kontext bei Aktionen geprüft; postgres nur Loader und administrative Rücklesung. SET LOCAL ROLE und Claims simulieren DB-Kontext, keine echte Anmeldung/JWT-Prüfung |
| Authgrenze | Originale auth.uid-Funktion übernommen; auth.users ausschließlich als ID-Fixturestub. Nicht getestete Service-/Sandbox-/Adminrollen sind inaktive NOLOGIN-Platzhalter, kein vollständiger Cloud-Rollenklon |
| Daten | Neu erzeugte künstliche Nutzer, Klienten, Vektoren, Protokolle, Aufträge, Archive und Vorlagen. Kein Exportdatensatz übernommen |
| Quellen | Explorer c69d5aa224018b0484efd90ae456a10aecc78a77; Thom 18e6c12c238985da698f9a46743d893b30d61ba7. Aktiver API-/Worker-Build folgt daraus nicht |

Damit wird ein ausgewählter SQL-Vertrag charakterisiert, kein exakter Cloud-Klon. Nicht abgedeckt: echte Tokens, Gateway/RPC/API, Storage, Realtime, Worker/Hardware, Rollen-/Tenant-/Abovertrag, nicht vorhandene IDs/Timing/Side-Channels, Last und parallele Claims sowie nicht constraintgebundene Indizes. Getrennte Cloud-Snapshotzeitpunkte bleiben getrennt.

## Ergebnisse nach Fallgruppen

| Fallgruppe | Ausgeführte Aktionen | Soll erfüllt | Zielabweichung |
|---|---:|---:|---:|
| R01 Klienten | 63 | 63 | 0 |
| R02 Thom-Aufträge und abhängige Bezüge | 75 | 67 | 8 |
| R03 Thom NULL-Eigentümer zusammen mit clients-RLS | 24 | 24 | 0 |
| R04 Explorer Archive, Sitzungen und Vorlagen v1/v2 | 162 | 138 | 24 |
| R09 Selbstprivilegierung und Admin-Gegenfälle | 25 | 25 | 0 |
| Ergänzende R09 SQL-TRUNCATE-Proben | 14 | 0 | 14 |
| **Summe** | **363** | **317** | **46** |

Die 349 Hauptaktionen und 14 zusätzlichen Utility-Proben sind getrennte Nachweise. Die drei Stufen der Detektor-Kontrollprobe zählen nicht zusätzlich zu diesen 363. Thom: 137 Aktionen, 124 erfüllt/13 Abweichungen. Explorer: 226 Aktionen, 193 erfüllt/33 Abweichungen. Keine unerwarteten Testfehler im vollständigen korrigierten Lauf; frühere fehlgeschlagene Aufbauversuche bleiben separat dokumentiert.

## Bedeutung der Befunde

| Befund | Was tatsächlich beobachtet wurde | Folgerung für die spätere Struktur |
|---|---|---|
| Normale Objektzugriffe | Eigene A/B-CRUD-Gegenfälle gelingen. Bekannte fremde Zeilen bleiben bei SELECT leer und UPDATE/DELETE unverändert; fremde Inserts und Ownerwechsel werden abgewiesen. Anonyme Gegenfälle ebenfalls gesperrt | Diese begrenzten SQL-Gegenfälle erhalten; echte Nutzertransporte separat prüfen |
| Thom Querreferenzen | Auftrag für eigenen Klienten akzeptiert bei INSERT und UPDATE einen Vektor bzw. ein Protokoll eines anderen eigenen oder fremden Klienten | Gültiger FK ersetzt keine konsistente Klientenbindung. Späteren Auftrag-/Vektor-/Protokollvertrag und passende Constraints/Checks festlegen; keine Produktkorrektur hier vorgenommen |
| Explorer Querreferenzen | Eigene user_id mit anderem eigenen oder fremden patient_id wird bei Archiven, Sitzungen und Vorlagen in beiden Familien angenommen | Eigentümer des Hauptobjekts und Klientenbezug gemeinsam validieren. Nachgewiesen ist eine widersprüchliche Verknüpfung, kein hierdurch erlangter Lesezugriff auf fremde Inhalte |
| NULL-Eigentümer Thom | 24 geprüfte Kombinationen bleiben unter der gemeinsamen Policywirkung geschützt; positive eigene Gegenfälle bestehen | Die Jobs-NULL-Policy nicht isoliert bewerten. Keine pauschale Mandanten- oder Delegationsgarantie daraus ableiten |
| Rollen | A/B können sich weder per INSERT noch per UPDATE Adminrechte geben; has_role bleibt false. X-Gegenfälle folgen dem jeweiligen heutigen Schema | SELF-Admin hier nicht nachgewiesen; RPC/Gateway-/Triggerwege und reale Rollenmitgliedschaften bleiben separate Grenzen |
| Tabellenweites Leeren | authenticated kann im simulierten direkten SQL-Rollenkontext TRUNCATE CASCADE auf allen 14 ausgewählten Tabellen ausführen; vor ROLLBACK verschwinden auch fremde Fixtures | RLS gilt nicht für TRUNCATE. Least-Privilege-Vertrag muss auch tabellenweite Grants berücksichtigen. Keine Aussage, dass eine erreichbare Cloud-API dies anbietet oder dass Produktionsdaten gelöscht wurden |

Die vollständigen Fixture-Tabellen wurden nach jeder Aktion administrativ **vor ROLLBACK** rückgelesen; dadurch sind Trigger-/Cascade-Nebenwirkungen im ausgewählten Tabellenumfang sichtbar. Jede nächste Aktion begann wieder mit dem unveränderten Ausgangsbestand. Abschließende Fixture-Hashes stimmen überein. Referentielle Integritätsprüfungen und TRUNCATE fallen nicht unter denselben RLS-Schutz wie normale Zeilenzugriffe; siehe [PostgreSQL 17 Row Security](https://www.postgresql.org/docs/17/ddl-rowsecurity.html).

## Kontrollprobe und fehlgeschlagene Vorversuche

Eine eigene Harness-Tabelle prüfte denselben invokerbasierten SELECT-/Nullzeilendetektor: geschlossene Policy liefert 0 fremde Zeilen, absichtlich permissive Policy liefert 1 und wird erkannt, nach ROLLBACK wieder 0. Das prüft Detektorempfindlichkeit, keine Vollständigkeit aller Modulgrenzen.

PGlite/WASM scheiterte vor Testausführung an Speichermangel. Der native PostgreSQL-Start wurde unabhängig per Identitätsabfrage nachgewiesen; der Bootstrap lief trotz betriebsbereiter Instanz in einen separaten Capture-Timeout. Vererbte Ausgabehandles sind eine dazu passende Arbeitshypothese, nicht unabhängig nachgewiesen. Lebenszyklusbefehle schreiben anschließend direkt in eine geschützte Logdatei. Ein erster anonymer Fixture-Claim enthielt einen leeren statt fehlenden sub-Wert und löste SQLSTATE 22P02 aus; nur der Testaufbau wurde korrigiert, nicht auth.uid oder ein Modulalgorithmus. Diese Versuche zählen nicht als bestandene Rechteprüfungen.

Die PostgreSQL-Binaries stammen aus dem offiziellen EDB-HTTPS-Archiv. Lokaler SHA-256 und CRC/SHA der selektiv entpackten Dateien wurden gebunden; keine unabhängige Hersteller-Checksum-Attestierung. Kein Installer, globaler PATH, Windowsservice oder Daueraufgabe. Abhängigkeiten sind kein neuer Bestandteil des Governor-Produktdienstes.

## Status und nächster Schritt

| Ebene | Stand |
|---|---|
| P0 Quellen-/Strukturkonsolidierung | Erledigt im dokumentierten Umfang |
| P1 SQL-Charakterisierung | Begrenzter ausgewählter Lauf abgeschlossen; Zielabweichungen offen, keine Gesamtabnahme |
| P2 reale Nutzer-/API-/Storage-/Workerprüfung | Separate Staging-Umgebung und Build-/Authbindung noch erforderlich; keine Writes gegen Produktion |
| P3 Aurelia-Vertrag | Tenant/Mitgliedschaft/Delegation/Abo, konsistente Kontext-/Sitzungsbindungen, Medien-/Archiv-/Trigger-/Restoregrenzen vor Implementierung gemeinsam entscheiden |

Als Nächstes P2-Isolation und die noch fehlenden Modulpfade vorbereiten, verbleibende Quellen-/Lizenz-/Asset-/Restoregrenzen erfassen und erst danach die gemeinsame Strukturentscheidung treffen. Referenzkorrekturen, zentrale Migrationen, normative Modul_Templates und S4.8 bleiben eigene Freigabeschritte. Kein fremder Fall wird durch Namen/Geburtsdaten automatisch vereinigt.

## Belege und Sicherung

Private Nachweise: runtime/aurelia-three-modules-20261009/reference-plan/rights-execution-20261009-231423. ENVIRONMENT, SCHEMA_VERIFICATION, FIXTURES, RESULTS, UTILITY_RESULTS, NEGATIVE_CONTROL, STOPPED, UNCHANGED_SOURCES, REVIEW und Fehlerreceipts binden Aufbau, Ergebnisse und Grenzen. Rohdefinitionen, Fixture-SQL, Passwörter und Datenbankdateien bleiben lokal geschützt und werden nicht an Review-Agenten weitergegeben.

Vorherkopien der fünf geänderten Status-/Planungsdateien und ein abschließender manifestierter Dokument-/Testsicherungspunkt sichern diesen Block. Private Passwortdateien, gestoppte Clusterdateien und große Dependencytrees/-archive werden nicht in den kleinen Abschlusscheckpoint kopiert; deren Bindungen bleiben im geschützten Belegordner. Das ist keine vollständige F:-, Cloud-, Storage- oder Projektgesamtsicherung.

Tatsächliche Helfer: Luna6/max für die begrenzte Quell-/Abhängigkeitsprüfung; Astra6/medium für Methodik und bereinigte Ergebnisbeurteilung. Astra hat keine Rohbelege unabhängig nachgerechnet. Parent baute die SQL-Nachbildung, führte Prüfungen/Rücklesung aus und konsolidierte den Bericht. Leitungsroute gemäß Betreiberwahl Sol6.1/high, effektive Desktopauswahl nicht aus Defaults abgeleitet; keine Tokenersparnisbehauptung.
