# Aurelia – Mandanten, Modulabos und Kapazitätsnachweise

**Maßgebliche Betreiberpräzisierung16.10.2026:** Der Test-VPS nimmt Module, Modul_Templates und Aurelia schrittweise für Entwicklung, Funktions-/Integrationsprüfungen und begrenzte Teil-Lastprüfungen auf. Er muss die vollständige Plattformlast nicht tragen. Die abschließende Gesamtlast-/Kapazitätsabnahme einschließlich25-Nutzer- und Modulkombinationsszenarien erfolgt auf dem geplanten Hauptserver unter der späteren Betriebskonfiguration. VPS-Teilergebnisse sind Grundlagen für die Planung, keine Produktionskapazitätszusage.

Betreiberergänzung 16.10.2026, konsolidierte Anforderung und Prüfplanung. Keine neue Datenbankentscheidung, implementierte Mandantenfähigkeit, Tarif-/Leistungszusage oder Freigabe eines Mehrbenutzerbetriebs. Originalalgorithmen, persönliche Heuristik, laufende Instanzen und Serverlimits bleiben unverändert.

## 1. Verbindlicher Umfang und Identitäten

Die Plattform muss mehrere Mandanten sowie abonnierbare Einzelmodule und Modulkombinationen unterstützen. Das Lastszenario „25 Nutzer verwenden RadiWorks gleichzeitig“ gehört zur Kapazitätsplanung. Es ist keine bereits nachgewiesene Hostkapazität.

Mandant/Praxis, angemeldeter Nutzer, Therapeut, fachlicher Klient/Fall und Abonnent/Vertragsinhaber sind getrennte Identitäten. Ein Klientendatensatz bedeutet nicht automatisch einen eigenen Login. Klientenbezogene Abos beziehungsweise direkte Klientenzugänge müssen im Rollen-/Vertragsmodell ausdrücklich abbildbar sein; die konkrete Vertragsinhaberschaft wird vor ihrer Umsetzung festgelegt. Keine Person anhand gleicher Namen zusammenführen und keine vermeintliche Mandantenidentität aus vom Browser gelieferten IDs vertrauen.

| Gegenstand | Verbindlich zu berücksichtigen |
|---|---|
| Modulabo / Kombination | Versionierter Tarif, erlaubte Module/Fähigkeiten, Gültigkeit, Suspendierung/Widerruf, Kontingente und definierte Regel für bereits angenommene/laufende Aufträge. Eine Kombination macht Modulkennzahlen nicht fachlich austauschbar. |
| Zugriff | Anmeldung, aktuelle Mitgliedschaft/Rolle, konkretes Klienten-/Objektrecht und Modulberechtigung getrennt serverseitig prüfen. Abonnement allein verleiht kein Leserecht auf Klientendaten. |
| Auftrag | Tenant, berechtigter Operator, Klient/Fall, Modul-/Verfahrens-/Katalog-/Kontextrevision und bei Annahme maßgebliche Tarif-/Quotarevision nachweisbar binden. Der Snapshot ersetzt keine aktuelle Rechteprüfung. |
| Ressourcen | Hierarchische Budgets: Plattform → Mandant → berechtigter Nutzer bzw. Klientenzuordnung → Modul → Auftrag; gemeinsame Dienste zusätzlich global begrenzen. Abrechnung, Datenschutzzuordnung und technische Belegung getrennt führen. |
| Konkurrenz | Faire Zulassung und begrenzte Warteschlangen; ein Mandant darf andere nicht dauerhaft verdrängen. Kontingentprüfung/Reservierung muss bei konkurrierenden Starts konsistent sein, auch nach Abbruch/Neustart. |
| Lebenszyklus | Stop, Frist und Wiederherstellung wirken nur auf den erlaubten Lauf. Abolaufzeit, Widerruf und Sicherheitsstopp ausdrücklich regeln; keine stille automatische Wiederholung unklarer Sendungen. |
| Speicher / Medien | Originale, Referenzen, Layer, Audios, Berichte und Historien samt Quotas/Aufbewahrung berücksichtigen. Bei Limitüberschreitung neue Arbeit kontrolliert ablehnen; keine pauschale Löschung bestehender Belege. Physischer Hash-Gleichstand begründet keine Sichtbarkeit über Tenantgrenzen. |
| Prüfung / Audit | Abo-/Rechte-/Quotenänderung, Annahme/Ablehnung und Ressourcenverbrauch protokollierbar machen. Negative Mandanten-, Objekt-, API-, WebSocket- und Assetzugriffstests gehören zur Abnahme. |

## 2. Bestätigter Host gegenüber ungeprüfter Leistungsfähigkeit

Frische reine Leseinventur des **Testhosts vm2565 / 193.142.40.36**: [Kapazitätsbaseline](verification/AURELIA_CAPACITY_BASELINE_2026-10-16.json), Zeitpunkt 20:52:34 UTC. Die Angaben gelten für diesen Testhost; sie belegen weder die Ausstattung eines neu aufzubauenden Produktionsroots noch dessen spätere Leistung.

| Ebene | Tatsächlich gelesen | Grenze der Aussage |
|---|---|---|
| Betriebssystem / CPU | Ubuntu24.04.5 LTS, 12 logische vCPUs; virtueller CPU-Modellname | Keine 12 dedizierten physischen Kerne nachgewiesen; reale CPU-Leistung und Providerkonkurrenz nicht gemessen. |
| RAM | MemTotal24607084KiB, etwa23,47GiB | Verfügbarer RAM ist eine Momentaufnahme, keine garantierte Reserve. |
| Dateisystem | 253003403264Byte gesamt, etwa235,63GiB; rund216,31GiB verfügbar bei Inventur | Keine IOPS-/Latenz-/Durchsatzmessung oder Disk-Quota daraus ableiten. |
| Aurelia-Projektbudget | CPUQuota5CPU, MemoryHigh8GiB, MemoryMax10GiB, SwapMax1GiB, Tasks1024 | Gilt gemeinsam für den Projektnutzer einschließlich zugeordneter Prozesse/Container, nicht je Nutzer/Klient/Modul. |
| Website-Projektbudget | CPUQuota1CPU, MemoryHigh2GiB, MemoryMax4GiB, SwapMax256MiB, Tasks512 | Paralleles fremdes Projekt; dessen Budget und laufende Arbeit erhalten. |
| Aktueller RadiWorks-Container | Zuletzt geprüft2CPU/2GiB/256PIDs, netzlos, private Unix-Socket-Vorschau | Obergrenze der bestehenden Einzeloperator-Vorschau, keine Verbrauchsmessung pro Klient und keine Multitenant-Abnahme. |

10GiB plus4GiB sind maximale Projektgrenzen, keine exklusiv reservierten Speicherbereiche. Betriebssystem, Proxy, Datenbank, Worker, Backups, Monitoring und Builds müssen im zukünftigen Host-/Dienstbudget berücksichtigt werden. Quelle des Containerstandes: [Security-Laufzeitprüfung](verification/AURELIA_RW_SECURITY_RUNTIME_REVIEW_2026-10-16.json).

Der bestehende RadiWorks-Kern begrenzt aktive Broadcasts mit `MAX_ACTIVE=8` (`engine/src/radiworks/core/broadcast.py:39,597–603` im Pilotstand b4c4a12). Das ist eine Instanzgrenze, keine Angabe „8 Nutzer“. Nicht zur Erfüllung der25-Nutzer-Anforderung pauschal auf25 erhöhen. Ein eigener Vollcontainer pro Nutzer oder Klient wird durch die Anforderung ebenfalls nicht vorgegeben.

## 3. Messprofile statt pauschaler Nutzerzahl

### Getrennte Prüfaufgaben und Hauptserverherkunft

| Umgebung | Aufgabe | Aussagegrenze |
|---|---|---|
| Test-VPS vm2565 | Module nacheinander aufnehmen; Modul_Templates und Aurelia-Kern entwickeln/prüfen; passende Teilintegrationen und einzelne Modulbereiche innerhalb der Projektbudgets belasten. | Kein Zwang, sämtliche Stacks oder die vollständige25-Nutzer-/Mehrmodullast gleichzeitig auszuführen. Ein VPS-Grenzwert ist kein nachgewiesener Hauptserver-Grenzwert. |
| Geplanter Hauptserver | Zielstack und passende Dienst-/Workerbudgets prüfen; vollständige Mandanten-, Mischlast-, Langlauf-, Kapazitäts- und Betriebsabnahme unter der vorgesehenen Betriebskonfiguration. | Erst nach Bereitstellung, Hostinventur, Absicherung und freigegebenem Prüfaufbau. Kontrollierte Testdaten/Prüfläufe; keine unkontrollierte Belastung echter laufender Klientenaufträge. |

Quelle der folgenden Hardware: Nutzeranhang `Linux_Root_Server_Hardware.jpg`,16.10.2026. Anbieteransicht „GPU Server M G1“; RAM/Datenträger stehen im Bild unter „for example, with“. Daher als geplante/beispielhafte Zielkonfiguration erfassen, nicht als bereits installierte/verifizierte Ausstattung.

| Bestandteil | Im Anhang genannt | Vor Zielabnahme zu prüfen |
|---|---|---|
| CPU | AMD Ryzen5 9600X,6 Kerne/12 Threads | Tatsächlich bereitgestellte CPU und gemessene modulbezogene Leistung. Nicht mit12 VPS-vCPUs gleichsetzen. |
| GPU | NVIDIA RTX4000 SFF Ada,20GB Grafikspeicher | Verfügbarkeit, Treiber, Containerzugriff und tatsächlich unterstützte freigegebene Softwarepfade. Die GPU beschleunigt RadiWorks oder Browser-3D nicht automatisch; keine algorithmische/GPU-Umstellung hier genehmigt. |
| Arbeitsspeicher | Beispielkonfiguration128GB DDR5 | Installierter nutzbarer RAM, System-/DB-/Worker-/Cache-/Backupbudgets und Sicherheitsreserve. |
| Datenträger | Beispielkonfiguration2×1TB NVMe SSD | Tatsächliche Datenträger, Verschlüsselung/RAID/Dateisystem, nutzbare Kapazität, I/O und Restore. Nicht pauschal2TB nutzbar oder Spiegelung als Backup annehmen. |
| Netzwerk / Wartung | 2×1Gbit/s, IPMI, redundantes Netzteil | Tatsächliche Anbindung/Redundanz und abgeschirmter Wartungszugang; keine automatische2-Gbit/s-Einzelverbindung ableiten. |

Anbieter-Benchmark-/LLM-Werte im Bild sind keine Messwerte unseres Stacks und ersetzen keine Kapazitätsabnahme. Ein Rechenfaktor zwischen VPS und Hauptserver wird aus RAM-/Threadzahlen nicht abgeleitet.

**Prüfort der folgenden Lastprofile:** Einzelreferenzen und begrenzte Teilprofile zunächst auf dem VPS, mit explizit reduzierter Parallelität. Die vollständigen25-Nutzer-/Burst-/Modulkombinations- und Gesamtlanglaufprofile gehören zur Hauptserverabnahme. Auch ein gelungenes25-Sitzungen-Teilprofil auf dem VPS ersetzt diese nicht. Die Reihenfolge verlangt keine vollständige Plattform-Lastprüfung als Voraussetzung dafür, das nächste Modul auf dem VPS aufzunehmen.

Alle Lastprofile sind geplant, nicht ausgeführt. Erst nach Ressourcen-/Speicherplatzschutz und für echte Mehrbenutzerproben zusätzlich nach tragfähiger Identitäts-/Mandantentrennung freischalten. Bestehende Einzeloperator-Scopekonstanten niemals als25 unabhängige Mandanten ausgeben. Vorher sind nur kleine getrennte synthetische Kostenmessungen zulässig.

| Profil | Zu unterscheidende Arbeit | Nachweisziel |
|---|---|---|
| Einzelreferenz | Original/persönlich × seeded/stochastisch, mehrere gebundene synthetische Kataloggrößen, Standard105/Erweiterung soweit vorhanden | CPU-Zeit, Laufzeit, Spitzen-RAM, temporäre/dauerhafte Bytes und unveränderte Ergebnisse/Entropiereihenfolge bestimmen. |
| 25 angemeldete Sitzungen | Lesen, Suchen, Seitenwechsel, erlaubte WebSocket-Verbindungen, geringe Mutationsrate | Grundlast, Antwortzeiten, Verbindungslimits und Isolation; kein Nachweis25 gleichzeitiger Analysen. |
| 25 Broadcast-Anforderungen | Gleichzeitige Annahmeversuche, begrenzte aktive Ausführung und sichtbare Warteschlange | Zulassung/Fairness, Beleg-/Eventwachstum, Stop/Frist und Last; nicht voraussetzen, dass25 Broadcasts gleichzeitig laufen dürfen. |
| 25 Analyse-Anforderungen | Gleichzeitiger Startburst für beide Verfahren, definierte Kataloggrößen und Ergebnisumfänge | Messbar sichere Workerzahl, Wartezeit und begrenzte Ablehnung; keine25 unkontrollierten CPU-Jobs. |
| Realistischer Mischbetrieb | Lesen, gestaffelte Analysen, Broadcasts, bis5 Layer, Audio und begrenzte Importe | Nutzungsrate und Häufigkeiten aus Messung/vereinbartem Profil angeben. Serverseitige Arbeit von Browser-Audio-/Bildrenderkosten trennen. |
| Modulabos / Kombinationen | RadiWorks zusammen mit freigegebenen Copen-/Bohm-/Thom-/weiteren Modulwegen und gemeinsamen Diensten | Gemeinsame DB-/Asset-/Jobbudgets, keine doppelte Ressourcenreservierung; Fachsemantik jedes Moduls erhalten. |
| Überlast / Langlauf | Begrenzte Burst-/Ausfall-/Abolaufzeit-/Widerruf-/Restart- und Archivwachstumsproben | Andere Mandanten bleiben bedienbar; keine Historienverluste, Überbuchung oder unklare Wiederholung. Erst nach Schutzmechanismen. |

Pro Messlauf festhalten: Image-/Source-/Schema-/Konfigurationsrevision, Hardware-/Hostbudget, Anzahl aktiver Nutzer/Tenants/Klienten, Modulmix, Katalog-/Mediengrößen, Ankunftsrate und Dauer; CPU-Sekunden, Spitzen-/Dauer-RAM, Queue-Wartezeit, p50/p95/p99-Latenz mit Stichprobenzahl, Durchsatz, Fehler/Ablehnung, Dateiwachstum, I/O und WebSocket-/DB-Verbindungen. Kleine Stichproben nicht als belastbare p99-Abnahme ausgeben. Browserkosten auf repräsentativen Endgeräten separat nachweisen.

Die endgültige Kapazität ergibt sich aus dem engsten nachgewiesenen Budget: CPU/Worker, RAM, Diskwachstum/I/O, Verbindungen und vereinbarte Antwort-/Wartezeiten. Nutzerzahl allein genügt nicht. Pro-Klient-/Modulkosten sind gemessene Nutzungsprofile mit Obergrenzen und Nebenlasten, keine pauschale Multiplikation des2GiB-Containerlimits. Konkrete Latenzziele, Wachstum/Aufbewahrung und Abokontingente vor finaler Tarif-/Kapazitätszusage gemeinsam festlegen; sie blockieren die heutige Aufnahme und kleine Referenzmessungen nicht.

## 4. Einordnung in die bestehende Reihenfolge

1. **Jetzt, RadiWorks-Sicherheitsblock:** vorhandene Grenzen/Writer inventarisieren, history-erhaltende Speicherplatz- und Gesamtbudgets konkretisieren; Anforderungen an späteren Tenant-/Modulbezug aufnehmen. Keine ungeprüfte zentrale DB vorwegnehmen, keine bestehenden Algorithmen ersetzen.
2. **Danach, funktionaler Pilot/CI:** persönliche CPU-/Viermodireferenz und kleine Ressourcenmessungen mit festen Versionen ergänzen. Sicherheit, normale gültige Abläufe und Überlastablehnung nachweisen, bevor größere Lasten laufen.
3. **P3/P4:** Aufwand und Daten-/Job-/Assetpfade aller sieben Module samt Aurelia/Modul_Templates zusammenführen. Bekannte Original-/Access-/Hardwaregrenzen sichtbar behalten. P4 erhält ausdrücklich25-Nutzer-, Burst- und Modulkombinationsprofile.
4. **P5:** zentrale Daten-/Rechte-/Jobstruktur, Abo-/Quotaverträge, Speicherwachstum und Betriebs-/Antwortziele mit Betreiber beschließen. Nicht aus dem jetzigen lokalen Scope eine öffentliche Multitenant-Plattform ableiten.
5. **P6/P7:** zentrale Identität, Rechte/Abo-Prüfung, Ressourcensteuerung, Audit und versionierte Moduladapter implementieren und isoliert prüfen; passende Verträge in Modul_Templates aufnehmen. Verbindliche Rechteprüfung am Server und an Zugriffen auf Objekte/Ereignisse erhalten.
6. **P8 / Hauptserver- und Produktionsvorbereitung:** Die vollständigen25-Nutzer-, Mischlast- und Mehrmodulprofile auf dem bereitgestellten/geprüften Hauptserver unter tatsächlicher Mandantentrennung und der vorgesehenen Betriebskonfiguration stufenweise abnehmen. Davor auf dem VPS nur begrenzte Modul-/Teilintegrationslasten messen. Daraus konkrete CPU-/RAM-/Speicher-/Worker- und Ausbauempfehlung ableiten; gesonderte Hauptserver-/Restore-/Betriebsfreigabe. Weitere Skalierung nur durch gemessene Engpässe begründen.

Aktueller Fortsetzungspunkt bleibt der Schutz vor Ressourcenerschöpfung aus [Security-Review](verification/AURELIA_RW_SECURITY_REVIEW_2026-10-16.md). Größere Lastproben, öffentliche Zugänge, Abo-Implementierung oder Serverbudgetänderungen wurden durch diese Konsolidierung nicht durchgeführt.
