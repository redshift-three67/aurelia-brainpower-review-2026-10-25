# P3: Morphic-Auftragsdaten und Parser, 14.10.2026

## Ergebnis

Zwei lokale Läufe des geprüften Werkzeugs bestanden jeweils dieselben 24 synthetischen Fallgruppen; vollständige Ergebnisdaten sind gleich. Zwölf synthetische Werkzeugtests bestanden bei Helfer und Leitung, auch nach den Reviewkorrekturen. Das ergänzt die früheren Rohobjekt-/Recoveryproben durch den tatsächlichen Datenparser und dessen reine Abhängigkeiten.

Dieser Teilnachweis ist keine vollständige Modul-, Persistenz-, Recovery-, Berechtigungs- oder Plattformabnahme. Gesamtphase P3 bleibt offen. Es wurden keine Originalalgorithmen verändert, echten Aufträge geladen oder Liveinstanzen angesprochen.

## Gebundene Referenz und Modellgrenze

Referenzworktree `C:/morphic_v1/.worktrees/operator-workbench-phase1`, HEAD `151e2bb0a69d49677a0b1e40e0bffd0f172d34c4`, getrackter Zustand leer. Das legt ihn nicht als führende Produktquelle fest.

- `services/harmonization_worker.py`: SHA256 `412c9d8e13acbeb76110462fd14583fee07be0070c7273a7ac82fbbcf891ac38`.
- `apps/web/authority_ids.py`: SHA256 `161108445d603fcc9cfb4f34c8f1df0bf121ea4b49dc5c0bcbd3ef29c012c69f`.

Zehn Worker-Funktionen und drei Authority-ID-Validatoren wurden aus dem Original-AST übernommen. Dazu kommen die originale Exceptionklasse und genau begrenzt ausgewählte Konstanten einschließlich ASCII-Regex. Keine permissiven Autoritäts-Dummies oder ersetzte Parserlogik. Ganze Produktmodule, Runtime-Verzeichnisanlage und Hardware-/Web-/psutil-Imports wurden nicht ausgeführt.

`HarmonizationJob` wurde als angepasstes Dataclass-Feldmodell konstruiert: genau 27 originale Felddeklarationen in derselben Reihenfolge, geprüfte literale Defaults und `@dataclass`, aufgeschobene Annotationen. Alle sechs Originalmethoden `to_dict`, `from_dict`, `save`, `_save_locked`, `load`, `delete` fehlen bewusst. Der kontrollierte Namespace wird nur für die Konstruktion registriert und danach entfernt. Dies ist keine Vollklassenparität; erzeugte Standard-Dataclass-Methoden sind Teil des begrenzten Feldmodells.

## Tatsächliche Befunde

| Gruppe | Fallgruppen | Beobachtetes Verhalten |
|---|---:|---|
| v2-Grundform und Felder | 4 | Vollständiger Datensatz und acht gültige Statusformen angenommen; Boolean-Schema und fehlende/zusätzliche Felder abgelehnt. Baselinewerte stammen vom tatsächlichen Rückgabeobjekt. |
| Legacyformat | 5 | Optionale Felder ergänzt, Schema auf 2 normalisiert; falsche Feldmenge abgelehnt. Aktive Phase bei explizitem terminalem Legacyzustand normalisiert. Fehlt die Phase ganz, kann beim terminalen Status `completed` der Default `pending` erhalten bleiben. |
| Identität und Autorität | 3 | Allgemeine gespeicherte IDs gegenüber strengeren Creation-IDs getrennt; abweichende Autoritäts- oder erwartete Job-ID abgelehnt. Ungültige gespeicherte ID: `RuntimeError` mit `AuthorityIdError` als Ursache. |
| Zahlen und Hardware | 3 | Konkrete Boolean-/NaN-/Infinity-/Bereichs-/Ganzzahlvarianten abgelehnt. Verschachtelte JSON-Grundtypen angenommen; nichtstring Schlüssel, Tuple, fremdes Objekt und nicht endliche Hardwarewerte abgelehnt. |
| JSON-Duplikate | 1 | Originaler `_strict_json_object` als `object_pairs_hook` mit synthetischem JSON-Text lehnt doppelte Schlüssel ab. Kein Dateiladevorgang. |
| Zeitangaben | 2 | Offset-Zeitstempel validiert und als ursprünglicher String erhalten; falscher Typ/Leerstring/Format, Ende vor Start und inkompatible naive/aware Zeitangaben abgelehnt. |
| Zustand, Phase, Fehler und Fortschritt | 5 | Konkrete Phasen-/Status-/Endzeit-/Fehler-/Forced-Status-/Zyklenkonflikte abgelehnt; gültiges Fortschrittsverhältnis und Completion-Ausnahme angenommen. |
| In-Memory-Struktur | 1 | Verschachtelte `hardware_config` bleibt in der geprüften Eingabe aliasiert; Mutation eines geteilten Containers ist am geparsten Objekt sichtbar. Kein unveränderlicher Snapshot dadurch belegt. |

Untervarianten innerhalb einer Gruppe sind ausdrücklich keine weiteren Fallgruppen. Alle negativen Unterassertions prüfen genaue Exceptiontypen und Meldungen; im Persistenz-ID-Fall zusätzlich die Ursache.

Läufe `root-first-20261014-165932z` und `root-second-20261014-165941z`: je24 Gruppen, Exitcode0, keine verweigerten I/O-Versuche während Konstruktion/Funktionsproben. Controller binden 19 relevante Quellhashes, HEAD, getrackten Zustand und beide Werkzeughashes vor/nach; unverändert. [Wiederholungsbeleg](../../checkpoints/Aurelia-P3-Morphic-Record-20261014/REPEAT-COMPARISON.json).

Geprüfte Werkzeugbindung: `source_probe.py` SHA256 `7ce3ca0d78032430b4b110c04b335ff150533825f46ec7c6ea44e6f021db1df7`; `test_source_probe.py` SHA256 `0cf8096ac31c7485bbb917486f8263cefc6e2f470940bf602388dfc25333d5cb`. Das Dateidefault-Gate bleibt `False`; nur der ausdrücklich gesetzte CLI-Schalter öffnete es im jeweiligen geprüften Kindprozess. `python -O` wurde vor Originalquellenlesen abgelehnt.

## Review, Werkzeughistorie und Grenzen

Luna/max bereitete Quellenvertrag und Werkzeug vor, ohne Originaldefinitionen oder Parserfälle auszuführen. Astra/medium prüfte unabhängig zunächst SPEC, dann QUALITY. Drei blockierende Prüferwartungen wurden vor Originalausführung korrigiert: `None` statt numerischem Fortschritt, falscher Exceptiontyp beim Boolean-Schema und Verwechslung von Timestamp-String mit `datetime`. Zusätzlich wurden tatsächliche Baselineassertions und der Umgang mit Importfehlern präzisiert. Korrigierter Vorherreview und abschließender Ergebnisreview ohne verbleibende Blocker im beschriebenen Scope. Leitung wiederholte Werkzeugtests, führte beide Parserläufe aus und rechnete Bindungen nach. Ein Review ist keine Produktfreigabe.

**Historische Nachweislücke:** Die erste Werkzeugfassung wurde vor Korrektur nicht als Bytekopie gesichert; ihre Hashes, das von der Leitung gespeicherte zwölfteilige Grünprotokoll und Reviewbefunde bleiben erhalten. Ursprüngliche rote Entwicklungsläufe sind nicht dauerhaft belegt. Deshalb keine vollständige TDD- oder reproduzierbare v1-Behauptung. Die tatsächlich ausgeführte v2-Fassung wurde vor Originalausführung als vollständige Bytekopie im neuen Prüfpunkt gesichert und nachgerechnet.

Guard-Negativtests lösen künstliche `sys.audit`-Ereignisse aus. Sie belegen die Behandlung dieser Ereignisse, keine realen OS-, Netzwerk- oder Prozessaktionen. Während der Parserproben wurden keine solchen Zugriffe versucht. Hash-/AST-/Pfadkontrollen und Python-Auditguard sind keine allgemeine oder racefreie Betriebssystem-Sandbox.

Nicht geprüft: Originalmethoden, echte Dateiöffnung/-speicherung, Locks, Worker-/Prozessautorität, API-Erstellungsvalidierung, Anmeldung/Mandantenrechte, Recovery, Restore, reale Gleichzeitigkeit oder Linuxparität. Zwei Wiederholungen derselben synthetischen Eingaben ersetzen keinen allgemeinen Stabilitätsnachweis.

## Konsequenzen für P4 und die späteren Gates

| Thema | Vorbereitung der zentralen Struktur |
|---|---|
| Alte/neue Datensätze | Eingangsformat und normalisierte Darstellung getrennt erfassen; ergänzte Defaults und ursprüngliche Feldpräsenz nachvollziehbar halten. |
| Status und Phase | Legacybeobachtungen und strengere v2-Konsistenz unterscheiden. Keine vorhandenen Aufträge stillschweigend umdeuten. |
| Zeitwerte | Rohrepräsentation, Zeitzonenbedeutung und normalisierte Vergleichswerte unterscheiden; keine Zeitnormalisierung als bereits vorhanden behaupten. |
| IDs und Zugriff | Job-, Autoritäts-, Report-, Tenant- und Operatorbezug getrennt festhalten. Parserannahme ist keine Berechtigung oder Klientenzuordnung. |
| Kontext und Hardware | Persistierte JSON-Repräsentation und unveränderlicher Auftragssnapshot brauchen eigene Nachweise; In-Memory-Aliasing nicht mit Snapshothoheit verwechseln. |

Keine DB-Technik, neue Formel oder Produktreparatur beschlossen. P4 vollständige siebenmodulige Matrix einschließlich Aurelia/Modul_Templates vor P5 Datenstrukturentscheidung; normative Anpassungen und Integrationen P6–P8/S4.8. Linux-/Backendpfade, RF-E1/aktuelle RMF-Parität, führende Morphic-Quelle und vollständiger Writer-/Job-/Readerweg bleiben offen.

## Lokaler Prüfpunkt

`checkpoints/Aurelia-P3-Morphic-Record-Status-20261014-164313Z`: drei Status-/Plandokumente vorher rückgeprüft, bisheriger 41-Dateien-Punkt samt Siegel bestätigt; neue Quellenmetadaten, v1-/v2-/Ergebnisreview und ausgeführte v2-Bytekopien erhalten. Das Abschlussmanifest und sein Rücklesebeleg bestätigen den genauen neuen Nachherumfang ausschließlich bei tatsächlichem Erfolg. Keine Gesamtprojekt-/Server-/F:-Sicherung oder private Schlüssel-/Access-Rohdatenkopie.
