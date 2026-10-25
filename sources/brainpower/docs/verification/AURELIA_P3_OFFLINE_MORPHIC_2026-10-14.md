# P3: serverunabhängige Morphic-Referenzprüfungen, 14.10.2026

## Ergebnis und Geltungsbereich

Die zusätzlichen Owner-/Lease-/Recovery-Proben liefern in zwei lokalen Läufen je 19 bestandene Fälle mit identischen Details. Die Berichtsfunktionen W2 liefern in zwei weiteren Läufen je 16 bestandene Fälle und vollständig gleiche Ergebnisdaten. Das sind 35 unterschiedliche Charakterisierungsfälle, jeweils zweimal ausgeführt; zusätzlich 21 unterschiedliche Werkzeugtests bestanden. Das ist keine vollständige Worker-, Autorisierungs-, Persistenz- oder Wiederherstellungsabnahme.

Quellenreferenz: `C:/morphic_v1/.worktrees/operator-workbench-phase1`, HEAD `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4`. Der getrackte Status war bei den Kontrollen leer. Das legt diesen Worktree nicht als führende Produktquelle fest. Keine Produktinitialisierer, echten Worker oder Liveinstanzen wurden durch diese Proben gestartet.

## Owner, Lease und Recovery

| Prüfgruppe | Umfang | Tatsächlicher Befund |
|---|---:|---|
| Ownerbindung | 5 Fälle | Anderer Operator und unterschiedliche Tupel bleiben verschieden; Unicode-Repräsentation und Leerzeichen bleiben Teil der Hashbindung; acht ungültige Feldkombinationen werden abgelehnt. |
| Lease | 8 Fälle | Exakte Grenze ist noch nicht abgelaufen, eine Mikrosekunde darüber schon. Offset- und naive Zeitpfade, Zukunftsheartbeat, fehlender Heartbeat sowie direkte ungültige Eingaben charakterisiert. |
| Recovery | 6 Fälle | Simulierte aktive Zustände werden nicht als beendet eingetragen; `forced_status` wird weitergereicht, terminaler Zustand vor Zeitprüfung übersprungen. Fehler des simulierten Reconciler/Ereignisschreibers werden weitergegeben. |
| Prüfwerkzeug | 11 Unit-Tests | Hashdrift, Definitionsauswahl, Imports/Dekoratoren/Defaults, reservierte Globals, aufgeschobene Annotationen, Datei-/Socket-/Prozesssperren und Rücksetzen der Prüfphase geprüft. |

Zwei Ergebnisse: `root-first-20261014-125536z` und `root-second-20261014-130020z`; beide Exitcode 0. Namen, Anzahl und Details der 19 Fälle stimmen genau überein. Die zwei Produktquellen blieben vor/nach gleich. Git nach dem ersten Lauf wurde vor dem zweiten aufgenommen; dessen Vorher-/Nachherstand stimmt ebenfalls überein. Controller und [Wiederholungsvergleich](../../checkpoints/Aurelia-P3-Morphic-Lease-Edges-20261014/REPEAT-COMPARISON.json) halten die tatsächlichen Kontrollzeitpunkte fest.

Harness-SHA256: `9b21ef9e6fd68e0db4142c44ffe238a9f7bb5ccf9a94f2d0e0d2ff0eec520d70`. Die erwarteten Fehlversuche der Guardtests sind von den eigentlichen 19 Funktionsfällen getrennt; in diesen Funktionsfällen wurden keine gesperrten I/O-Aufrufe versucht. Die TDD-Scaffoldfehler, anschließende Rotprobe und Grünbelege bleiben erhalten. Der negative `python -O`-Anlauf verweigert die Produktprüfung vor Quellenzugriff.

**Wesentliche Grenze:** Feste Uhr, synthetische Jobobjekte und Fake-Reconciler/Ereigniswriter ersetzen echte Abhängigkeiten. Die Rohobjekte umgehen den echten Jobloader. Insbesondere beweisen ungültiger Heartbeat, negatives direktes Lease-Limit oder künstlicher `forced_status` keine Erreichbarkeit durch die reguläre API. Der zusätzlich gelesene Originalparser prüft `heartbeat_at` über `_parse_optional_timestamp` und beschränkt `forced_status`; der echte Loader und seine Dateipfade wurden hier nicht ausgeführt (`services/harmonization_worker.py:230-278, 428-436, 458-537, 761-801`). Die Original-Leasefunktion akzeptiert die kontrollierten Zeitrepräsentationen; keine reale Uhrabweichung oder länger laufende Prozessautorität wurde geprüft.

Python-Auditguards und Pfadprüfungen sind begrenzte Schutzmaßnahmen im vertrauenswürdigen lokalen Ablauf. Sie sind keine Betriebssystem-Sandbox und kein racefreier Schutz gegen beliebigen nativen Code.

## W2: Berichtskette und Datenstrukturbedarf

17 Produktquellen wurden gebunden, davon zehn frühere W1-Quellen und sieben zusätzliche Quellen. [W2-Vertrag](../../checkpoints/Aurelia-P3-Morphic-Writer-Report-W2-20261014/W2_CONTRACT.md) und [Quellenbindung](../../checkpoints/Aurelia-P3-Morphic-Writer-Report-W2-20261014/SOURCE_BINDING.json) unterscheiden statische Befunde von noch fehlenden Laufzeitnachweisen.

| Thema | Statischer Befund | Konsequenz für P4/P5 |
|---|---|---|
| Tenant und Owner | Standard-Berichtswurzeln haben Tenant-Suffix; ein expliziter Override kann sie ersetzen. Job-Owner bindet Tenant und Operator separat. | Tenant, Operator, Auftrag und Speicherwurzel als getrennte Vertragsfelder erfassen; Verzeichnisnamen sind kein vollständiger Zugriffsnachweis. |
| Sitzungskennungen | Rohsession, Top-N-Ordnersession und Manifest-/Katalogwerte unterscheiden sich. Remedies kann im Katalog den Klient-Slug als Sitzung ableiten. | Eindeutige zentrale Sitzungs-ID und explizite Zuordnung der Quellenkennungen vorbereiten; vorhandene Quellalgorithmen unverändert erfassen. |
| Report-ID | Hash aus Wurzelidentität und relativen Komponenten, kein Inhalts-/Auftragshash. | Logische Artefakt-ID, Inhaltsrevision und Auftragssnapshot getrennt planen. |
| Scoreexport | Exakt `round((value + 1e-12) * 1000) / 1000` bei Float-Schlüsseln mit `score`; Konsolidierer haben eigene Serializerpfade. | Rohwert, angezeigte Präzision und Exportverfahren versioniert unterscheiden. |
| PDF | Mögliche Importlücke bei fehlendem ReportLab vor geplantem Fallback. | Abhängigkeit und tatsächlichen Fallbacklauf später prüfen; derzeit statischer Hinweis, keine bestätigte Runtimefehlfunktion oder Produktkorrektur. |

Eine anfängliche breite reine Dateinamenssuche des Helfers zeigte einzelne Nichtquell-Archivnamen; diese Dateien wurden nicht geöffnet. Die Namen werden nicht wiederholt oder in den Berichten gespeichert. Es wird deshalb kein Nullkontakt mit Dateinamenmetadaten behauptet. Danach blieb die Aufnahme auf benannte Codequellen beschränkt.

### Tatsächliche W2-Funktionsproben

Vier unveränderte AST-Funktionskörper aus zwei gehashten Quellen wurden mit synthetischen Werten ausgeführt: `round_scores_for_export`, `report_json_dumps`, `_catalog_report_id` und `ReportCatalog._session_id`. Die letzte Methode wurde ohne Klasse oder Klasseninitialisierer als Funktion geladen; ihr unbenutztes `self` ist `None`. Pfade sind reine `PureWindowsPath`-Objekte, keine Dateien. Zwei ausgewählte Konstanten wurden aus genau begrenzten literalen AST-Formen übernommen. Aufgeschobene Annotationen verhindern deren Auswertung.

| Prüfgruppe | Umfang | Tatsächlicher Befund |
|---|---:|---|
| Rundung und JSON | 9 Fälle | Verschachtelte Score-Schlüssel, Listenschlüsselvererbung bis zum nächsten Dictionary, unveränderte Boolean-/Ganzzahl-/Nichtscorewerte, positive/negative Epsilon-Grenzen, gewählte doppelte Transformation und tatsächlicher JSON-Wrapper. Score-NaN/Infinity führen zu erwarteten Exceptions; Nichtscore-NaN wird standardmäßig als `NaN` ausgegeben und bei `allow_nan=False` abgelehnt. |
| Bericht-ID | 2 Fälle | Gleiche Eingaben liefern gleiche Kennung; andere Wurzel, Device, Integer-/Byte-Inode und Pfadkomponenten unterscheiden sich in den ausgewählten Beispielen. Keine allgemeinen Kollisions- oder Inhaltsrevisionsaussagen. |
| Sitzungsableitung | 5 Fälle | Resonanzlayout, älteres dreiteiliges Layout, Timestamp-/Dateistammfallback sowie die konkreten Synergy-/Remedieslayouts liefern die erwarteten pfadabhängigen Werte. |

`root-first-20261014-131501z` und `root-second-20261014-131507z`: je 16 erfolgreiche Fälle, Exitcode 0, keine Guardablehnungen in den Funktionsfällen. Vollständige JSON-Ergebnisse gleich. Äußere Controller halten 18 relevante Quellenhashes, HEAD, getrackten Status und drei Werkzeughashes vor/nach fest; unverändert. [W2-Wiederholungsbeleg](../../checkpoints/Aurelia-P3-Morphic-Writer-Pure-Probes-20261014/REPEAT-COMPARISON.json).

Review-Rückmeldung zeigte drei Vorbereitungslücken: fehlende konkrete Fälle, falsch positive Negativfixtures und einen an `False` gebundenen Gatetest. Leitung erhielt die alten Dateien, machte den Fixturefehler mit spezifischen Fehlergründen sichtbar und korrigierte die Fixtures. Zehn Werkzeugtests bestanden danach, ebenso nach der späteren reinen Gateänderung. Die Gateänderung von `False` zu `True` erfolgte erst nach unabhängigem SPEC→QUALITY-PASS; alle übrigen AST-Knoten blieben gleich. `python -O` wird vor Produktquellenzugriff verweigert. Historische Rot-/Grün-/Reviewbelege bleiben erhalten.

Ausgeführte Bindung: Loader `39a09846d97a6cd2e2188cf3b217d26878657ce46cb9a5a51dfb2d9dde16a2e4`, Tests `4f46451da57bf9acb934c95f2d8fc6ad2290cfa3dd7130bb6279bf6b49c4c361`, Runner `c514b5ea92639e4638b314013eb5970a3e22f2cb9eca1bb055ffc8899f21d061`. Der Gatewert betrifft ausschließlich das eigene Referenzwerkzeug, keine Produktkonfiguration.

Die in zwei Sessionfällen genannten Manifestwerte sind vorgegebene synthetische Vergleichswerte. Kein Manifestwriter wurde aufgerufen. Insbesondere sind weder echte Berichtbytes noch Tenant-/Jobautorisierung, Klasseninitialisierung, PDF-Erzeugung oder Dateisystemkatalogisierung durch diese W2-Proben belegt. Die Idempotenz gilt nur für das geprüfte Beispiel. Zwei Wiederholungen ersetzen keinen Langlauf-/Stabilitätsnachweis.

## Offene Voraussetzungen und nächste Gates

| Punkt | Stand | Voraussetzung |
|---|---|---|
| Zusätzliche W2-Funktionsproben | Begrenzter Teilnachweis abgeschlossen | 16 Fälle, zwei gleiche Läufe; komplette Writer-/Readerkette weiterhin offen. |
| Echter Writer/Registry/Job-Gesamtweg | Offen | Geklärte führende Quelle und kontrollierte vollständige Referenzumgebung. |
| Linux/POSIX, Auth/RLS, Storage, Realtime | Offen | Verfügbare isolierte Linux-/Backendumgebung; aktueller Rootserver nicht erreichbar. |
| RadiFarben RF-E1 / aktuelle RMF-Laufzeit | Offen | Geeigneter Access-Automationsweg; geschützte Rohreferenzen waren in diesem Paket nicht lesbar. Keine ACL-Lockerung oder Access-Originalöffnung. |
| P4 und P5 | Teilnachweise ergänzen die Matrix | Vollständige siebenmodulige Matrix vor zentraler Datenstrukturentscheidung. |

Die endgültige normative Synchronisierung von Aurelia und Modul_Templates sowie Integrationen bleiben P6–P8/S4.8. Diese Referenzarbeit ändert weder die Originalalgorithmen noch RadiWorks-Livebestand, Governors-/Chatrouting oder Produktfreigaben. Die abgelaufene Server-Wartungsberechtigung wird nicht verlängert.

## Review und Sicherung

Luna/max: begrenzte W2-Quellenaufnahme und separates Prüfwerkzeug. Astra/medium: unabhängiger SPEC→QUALITY-Review beider Werkzeuge einschließlich Nachprüfung der Korrekturen und tatsächlichen Ergebnisbelege; Prüfung nur lesend, keine Produktfreigabe. Leitung: 16er-Ergänzung, Testkorrekturen, tatsächliche Proben, Nachrechnung und Dokumentation.

Lokaler Vorher-/Nachherpunkt: `checkpoints/Aurelia-P3-Offline-Status-20261014-130301Z`. Vier vorherige Dokumente und 41 ausgewählte Nachherdateien wurden kopiert und rückgeprüft; der vollständige historische Wiederaufnahme-Bytesuffix blieb erhalten. `SNAPSHOT-VERIFICATION.json` bestätigt diesen ersten Stand. Die anschließend präzisierten Abschlussdokumente werden zusätzlich durch `FINAL-MANIFEST.json` und `FINAL-VERIFICATION.json` gebunden; für deren Abschluss gilt ausschließlich der tatsächliche erfolgreiche Rücklesebeleg. Gesichert sind diese benannten Dokumente, Werkzeuge und Prüfergebnisse. Keine F:-Gesamtprojekt-/Server-Sicherung, geschützte Access-Rohdaten oder private Schlüsselkopie in diesem Paket.
