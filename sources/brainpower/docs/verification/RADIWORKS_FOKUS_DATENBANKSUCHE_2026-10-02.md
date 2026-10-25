# RadiWorks: Fallfokus und Datenbanksuche (02.10.2026)

**Stand:** In einer isolierten Kopie geprüft und nach regulärem Auslaufen der virtuellen Broadcasts in RadiWorks-Quelle sowie den lokalen Betreiber-Kandidaten auf Port 8103 übernommen. Keine Aurelia-Integrationsfreigabe.

## Verhalten

- Das neue Suchfeld filtert die bereits geladene Datenbankliste lokal nach Namen und Gruppentitel. Es ändert die gewählte Datenbank nicht und startet keine Analyse. „Suche löschen“ stellt die vollständige Auswahl wieder her.
- Ein optionaler Fallfokus ist von Beschreibung und Sitzungsabsicht getrennt. „Fokus in Suche übernehmen“ setzt ihn nur nach ausdrücklichem Klick als Suchtext ein. Der Fokus wird in einem neuen Prüfdraft als Fall-Snapshot dokumentiert; Analysewerte, Entropie, GV, Passport und Broadcast-Berechnung bleiben unverändert.
- Bei einer Fallbearbeitung verhindert ein erwarteter opaker Fallverweis das Schreiben in einen inzwischen gewechselten aktiven Fall. CopyGuard prüft den eingegebenen Fokus lexikalisch und schreibt einen angezeigten Zurückhaltungsplatzhalter nicht als Originaltext zurück. Das ist keine Anonymisierung; der Fokus soll keine sensiblen Personen- oder Gesundheitsangaben enthalten.
- Fall-Antwort und opaker Verweis werden als eine gebundene Antwort verarbeitet. Ein zweites Browserfenster kann dadurch einen nachträglich gewechselten aktiven Fall nicht stillschweigend als Ziel eines älteren Formulars verwenden. Der Verweis wird für erlaubte lokale UI-Origins als Antwortheader freigegeben; die JSON-Form der bestehenden Fall-API bleibt unverändert.
- Die lokale Engine hat weiterhin einen gemeinsamen aktiven Fall. Mehrere Browserfenster oder gespeicherte Fallsitzungen sind keine unabhängigen parallelen Aufträge; der [Auftragsvertrag](RADIWORKS_PARALLEL_FALLAUFTRAEGE_2026-10-01.md) bleibt offen.

## Nachweise

- Neue gezielte API-Tests: Speicherung ohne Sitzung, unveränderter alter Draft nach Fokuswechsel, gleiche seeded Analysewerte trotz unterschiedlichem Fokus, Konflikt bei Fallwechsel, CopyGuard-Platzhalter sowie Längen-/Typgrenze bestanden. Gebundene Fall-Antwort, lesbarer Header bei erlaubtem Origin sowie Fokus-Snapshots für Stick-Pad-Analyse und getrennte Folgeanalyse sind ebenfalls geprüft.
- Vollständige Engine-Testsuite nach der letzten Testergänzung in der isolierten Kopie: Exit 0, zwei umgebungsabhängige Skips. JavaScript-Syntaxprüfungen und reiner Suchfiltertest bestanden.
- Der aktuelle synthetische Chrome-Gesamttest bestand mit 21 Abschnitten, einschließlich gefilterter Datenbankwahl mit Persistenz und anschließender Analyse, Fallbearbeitung, CopyGuard, 320-px-Ansicht und null Browser-Seitenfehlern. Eine eigene Interleaving-Probe wechselte zwischen dem Speichern von Fall A und dessen Antwort auf Fall B; ein weiterer A-Formularspeicheraufruf wurde sicher abgewiesen und B blieb unverändert. Die ergänzende Chrome-Probe auf 8104 bestand für Suche, Fokusübernahme, seeded Analyse und sichere Fallbearbeitung ebenfalls ohne Seitenfehler.
- Die Suchfunktion wurde lesend mit der Antwort des laufenden 8103-Katalogs geprüft: 123 Namen, eine Suche nach „bach“ fand einen Namen. Es wurde kein Analyseauftrag an 8103 gesendet.
- Nach Auto AUS liefen alle virtuellen Broadcasts regulär aus. Der damalige 8103-Vorschau-Datenordner wurde nach Prozessstopp mit 76 Dateien kopiert und Datei für Datei per SHA-256 geprüft. Die 14 Programmdateien wurden in Quellordner und bisherigen 8103-Kandidaten kopiert; beide Ziel-Hashsätze stimmen mit dem geprüften Kandidaten überein.
- Der erste Neustart verwendete versehentlich die Standard-Scope-Kennungen. Dadurch zeigte die API null Fälle/Drafts an, obwohl die gespeicherten Dateien unverändert vorhanden waren. Die gespeicherten drei Fälle und 51 Drafts hatten einen einheitlichen anderen lokalen Scope. Nach einem zweiten Neustart mit genau diesen Kennungen waren wieder drei Fälle und 51 Drafts sichtbar; die vier geprüften Zustandsbereiche (`cases`, `drafts`, `config`, `stickpad`) blieben gegenüber der Sicherung hashgleich. Keine Datenmigration oder Neuerstellung von Fällen war nötig.
- Die aktuelle 8103-API meldete danach 123 Datenbanken, Auto AUS und eine leere Broadcast-Queue. Eine unabhängige, ausschließlich lesende Chrome-Probe bestätigte die neue Datenbanksuche und das Fokusfeld ohne Seitenfehler. Der zuvor aktive Fall wird durch einen Prozessneustart nicht automatisch wieder ausgewählt; die gespeicherte Fallakte muss unter „Fälle“ erneut geladen werden. Der opake Fallverweis wechselt pro Prozess und ist kein persistenter Wiederherstellungsschlüssel.
- Drei RadiWorks-bezogene Nachträge in `Modul_Templates` wurden aus einer gesicherten Vorlage übernommen und hashgeprüft: `MODULE_REGISTRY.md`, `standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md` und `UEBERGABE_AURELIA.md`. Historische Abschnitte und der gemeinsame API-Vertrag blieben unverändert.

## Übernahmegrenze

Das [Übernahmemanifest](../../runtime/rw-focus-search-20261002/promotion-manifest.json) hält die 14 betroffenen Dateien mit Ausgangs- und Ziel-Hashes fest. Neun vorhandene Quelldateien, neun entsprechende Kandidatendateien und der damalige 8103-Datenordner sind im [Wiederherstellungspunkt](../../checkpoints/radiworks-focus-search-20261002-before) gesichert; die drei ursprünglichen Template-Dateien separat unter `checkpoints/radiworks-template-sync-20261002-before`. Alle Programm- und Template-Ziel-Hashes wurden nach der Übernahme geprüft. Die technische 8103-Probe ist abgeschlossen; eine bewusste Betreiberprobe mit einem bereits gespeicherten, erneut geladenen Fall steht noch aus. Der gemeinsame Host-/Mandantenvertrag und die Aurelia-Freigabe bleiben getrennt.

| Phase | Geschätzter Stand | Nächster Nachweis |
| --- | ---: | --- |
| S4.6 Ergebnis/Bedienung/GV | ca. 98 % | Betreiberprobe der GV-Seitenprüfung und dieser Suche auf 8103 |
| S4.7 Originalnähe/Restfunktionen | ca. 90 % | Area-Ergänzung, Peggotty-Randfälle, reales Kamera-/Recovery-Umfeld |
| Suche/Fokus in Testkopie | 100 % | Synthetische API-, Interleaving- und Browserproben bestanden |
| Suche/Fokus im Betreiberstand | ca. 90 % | Technische 8103-Probe bestanden; gespeicherten Fall laden und Bedienablauf bestätigen |
| Modul_Templates-RadiWorks-Referenzen | 100 % lokal synchronisiert | Host-/ABI-Entscheidung weiterhin offen |
| S4.8 Aurelia-Integration | 0 % | Host-, Scope-, Rechte-, Einwilligungs- und Betreiberentscheidung |

Die Prozentwerte sind Planungsnäherungen, keine Freigabe- oder Testabdeckungsquoten.

**Betreiber-Nachtrag 02.10.2026:** Der Betreiber bestätigte die zuletzt erfragte durchgängige Funktion der neuen Fokus-Funktion mit „Ja“. Damit ist die lokale Bedienprobe für Fokus, Suche und anschließende Analyse bestätigt; der oben dokumentierte frühere 90-%-Zwischenstand ist historisch. Host-/Mandantenverträge und Aurelia-Freigabe bleiben unverändert offen.
