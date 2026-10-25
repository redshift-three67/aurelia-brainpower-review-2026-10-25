# Begrenzte Aufbewahrungsprüfung – 23.09.2026

Ergebnis: **vorhandene Vorschau entspricht der Vorgabe7täglich/4wöchentlich/6monatlich; keine Löschung ausgeführt oder aktiviert.** Prüfung des gesicherten echten Laufberichts um22:00CEST, keine neue Repositoryabfrage und kein weiterer Backup-Test.

Quelle: `artifacts/runtime-first-scheduled23.log`; implementierte Argumente in `artifacts/server-operations23.py`, Funktion retention_args. Installierte Restic-Version0.16.4. Versionspassende Dokumentation: https://restic.readthedocs.io/en/v0.16.4/060_forget.html.

| Stand23.09., CEST | Snapshot-Kurz-ID | Vorschau |
|---|---|---|
|20:55:23|84bb5f8c|behalten, ältester Profilstand|
|21:18:31|0c879b55|Entfernung vorgeschlagen|
|22:00:02|8591d898|behalten, jüngster erfolgreich zurückgelesener Stand|

Maschinell geprüft: Lauf ok=true; retention_dry_run=true; deletion_performed=false; erwarteter Host aureliaserver und einziges Gruppentag operations-cold; jüngster verifizierter Snapshot in keep; keep/remove ohne Überschneidung. Repository-ID im erfolgreichen Lauf geprüft. Host-/Tagfilter und Gruppierung host,tags vermeiden getrennte Aufbewahrung pro wechselndem Arbeitsverzeichnis. Andere Repositorys und das preparation-synthetic-Profil gehören nicht zu diesem Filter.

Laut versionspassender Dokumentation wird der jeweils jüngste Stand pro Zeitraum behalten; Zeiträume ohne Sicherung werden nicht gezählt. Bei noch unzureichender Historie bleibt zusätzlich der älteste Stand erhalten. Deshalb sind zwei Stände desselben Tages in dieser frühen Phase korrekt. Tages-/Wochen-/Monatsregeln dürfen denselben Snapshot erhalten; daraus folgen nicht zwingend17verschiedene Sicherungen.

Grenzen: Ein Tag Historie belegt keine sechsmonatige reale Aufbewahrung. Vierstündliche Sicherung bedeutet unter dieser Langzeitregel nicht dauerhaft sechs Stände pro Tag. Vorschau nicht als aktuelle Löschfreigabe für spätere Bestände verwenden. Vor tatsächlichem forget/prune muss ein aktueller, erfolgreicher Sicherungs-/Restorebeleg vorliegen, der neueste verifizierte Stand erhalten bleiben, die Kandidatenmenge frisch abgeglichen und Parallelbetrieb mit Backup ausgeschlossen sein. Tatsächliche Bereinigung weiterhin eigener offener Implementierungs-/Abnahmeschritt; insbesondere kein unbegrenztes Prune im Vierstundenlauf.
