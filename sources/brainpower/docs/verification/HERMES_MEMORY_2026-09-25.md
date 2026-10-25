# Hermes: Gedächtnisabdeckung beider Modellwege, 25.09.2026

## Befund und Änderung

Der frühere Aufruf von Terra über die isolierte Hermes-Laufzeit verwendete **kein** internes Hermes-Sitzungs- oder Profilgedächtnis (`memory_enabled=false`, `skip_memory=true`). Das projektbezogene Gedächtnis liegt in `project_memories/*.md` und wird zusammen mit Quellen- und Gate-Metadaten in den Governor-Kontext eingebunden. Zuvor enthielt der Modellkontext bei Dateien mit mehr als 75 Zeilen nur die ersten und letzten 35 Zeilen, höchstens 9.000 Zeichen je Datei. Das war gekennzeichnet, konnte aber einen relevanten Mittelteil auslassen.

Der Browserkontext bleibt begrenzt. Bei einem ausdrücklich gestarteten alten Hybrid-/Vergleichs-/Planauftrag oder Route-B-Review/-Planauftrag liest der Worker die **für den gewählten Projektumfang erfassten Gedächtnisdateien vollständig** neu. Er vergleicht die Dateinamenliste und jeden SHA-256-Wert mit der frischen Aufnahme. Ein neues, entferntes oder geändertes Gedächtnis stoppt den Auftrag vor einem Modellaufruf. Der Modellkontext kennzeichnet vollständige, leere oder fehlende Gedächtnisse und der Job speichert Dateinamen, SHA-256, Umfang sowie `model_context_hash`. Die bestehende Freigabe für Modellversand und die Projektgrenzen bleiben unverändert. Beide Routen verwenden dieselbe Aufbereitung.

Eine **neue Strategieübernahme** verlangt außerdem einen abgeschlossenen Planauftrag mit diesem Vollständigkeitsbeleg. Ältere Plankandidaten ohne Beleg bleiben historische Nachweise und können nicht nachträglich als voll gedächtnisgeprüfte Strategie übernommen werden; ein neuer ausdrücklicher Plan ist dafür nötig. Bereits gespeicherte Strategierevisionen und andere historische Journale werden nicht umgeschrieben.

Die vorhandene Grenze von 95.000 Zeichen für den Reviewkontext und die Transportgrenzen bleiben erhalten. Überschreitet ein vollständiger Kontext sie, stoppt der Auftrag; es gibt keinen automatischen Rückfall auf Teilauszüge. Ein `memory_coverage.status=full` bezieht sich **nur auf die ausgewählten und inventarisierten `project_memories`**, nicht auf Vault-Quellen, ungetrackte Produktdateien oder eine fachliche Qualitätsgarantie. Vault-Auszüge und nicht vollständig gescannte Quellbäume bleiben separat als Grenzen ausgewiesen. Der `model_context_hash` enthält auch Beobachtungsmetadaten und ist deshalb kein alleiniger Beweis für zwei bytegleiche Modellprompts.

## Lokale Größenordnung ohne Modellversand

Am 25.09.2026 wurden die vorhandenen Markdown-Dateien lokal gelesen; die Zahlen sind Zeichen-/Byteumfänge, **keine Tokenmessung**. Für die Kontextgrößenschätzung wurden die übrigen Daten mit synthetischem Git-Status aufgebaut; sie ist kein aktueller Git-/Gate-Nachweis.

| Projekt | Dateien | Gedächtnis-Bytes | Volltext als JSON-Zeichen | Geschätzter gesamter alter → neuer Einzelkontext |
| --- | ---: | ---: | ---: | ---: |
| Aurelia | 1 | 38.021 | 39.284 | 21.522 → 55.904 |
| RadiWorks | 2 | 59.161 | 60.394 | 29.181 → 78.782 |
| Modulvorlagen | 1 | 24.390 | 26.252 | 21.866 → 42.887 |
| Radi144 | 2 | 64.905 | 67.430 | 25.628 → 84.606 |
| morphic_v1 | 1 | 41.214 | 42.864 | 22.740 → 59.557 |

Die fünf Volltexte benötigen zusammen mindestens **236.224 JSON-Zeichen**, bevor Gruppenmetadaten und Governance-Quellen hinzukommen. Eine vollständige Gruppenprüfung passt deshalb nicht in die derzeitige 95.000-Zeichen-Grenze. Sie wird bewusst abgewiesen und benötigt eine eigenständige, beleggebundene Mehrstufenverarbeitung, bevor ein vollständiger realer Matrixplan möglich ist. Auch einzelne Kontexte müssen ihre tatsächlichen Prompt- und Transportgrenzen im Auftrag bestehen; die Tabelle ist keine Zusage, dass jeder künftige Umfang passt.

Für diese Mehrstufenverarbeitung muss der Gruppen-Scope zuerst auf einen Quellenhash eingefroren werden. Anschließend wären alle Projektgedächtnisse je Mitglied vollständig zu lesen und einzeln von den jeweils gewählten Rollen gegen aktuelle Gates und Quellen zu prüfen; jeder Zwischenbeleg müsste Dateiname, SHA-256, offene Widersprüche und unbekannte Fakten führen. Erst aus vollständig vorhandenen, unabhängig geprüften Zwischenbelegen und den gemeinsamen Abhängigkeiten darf ein Gruppenentwurf entstehen. Eine abschließende Gegenprüfung muss bei fehlendem Beleg, widersprüchlichem Gate oder Quellen-Drift stoppen. Auch dieses Verfahren garantiert kein fehlerfreies Modellverständnis; es verhindert nur einen stillen Textverlust und macht verbleibende Unsicherheit sichtbar. Es ist **noch nicht implementiert** und wird nicht vorweg als fertige Gruppenplanung ausgegeben.

## Prüfungen und Genauigkeitsgrenze

Synthetische Tests belegen, dass ein Gate-Hinweis ausschließlich in der Dateimitte beide Modellwege und jeweils beide Rollen erreicht. Weitere Tests belegen Hash-Drift, nachträglich hinzugekommene Gedächtnisdatei, fehlenden Gedächtnisordner, den Stopp beider Wege bei zu großem vollständigem Kontext vor jedem Modellaufruf sowie die Ablehnung alter/unvollständiger Planbelege bei neuer Strategieübernahme. Zwei lokale HTTP-/Workerprüfungen mit simulierten Modellantworten belegen dieselbe Übergabe für einen Route-B-Auftrag mit drei Rollen und einen alten Hybridauftrag mit Terra/Sol. Diese synthetischen Prüfungen änderten keine Produktdateien.

Der [frühere echte RadiWorks-Paarvergleich](HERMES_ROUTENVERGLEICH_RADIWORKS_2026-09-25.md) verwendete noch die alte Auszugsregel. Der folgende neue Paarlauf verwendet die vollständigen Gedächtnisse. Beide Aufträge sind in der Datenbank mit `stale=false` gespeichert; der abschließende frische Scan bestätigte erneut denselben Scope-Hash. Die kurzzeitig als „veraltet“ angezeigte Browser-Kopie entstand, weil ihr 15-Sekunden-Frischecache abgelaufen war, nicht durch einen nachgewiesenen Quellenwechsel.

| Weg und Auftrag | Tatsächliche Rollen | Gedächtnis | Bericht und Grenzen | Gemeldete Tokens |
| --- | --- | --- | --- | ---: |
| Alt `50c263da44484d588da1ef064bcd38b3` | Terra 5.6/medium, Sol 5.6/medium | `full`, zwei RadiWorks-Dateien | `REVIEW_ONLY`; fünf Plan-Blocker, elf Review-Befunde und neun verlangte Nachweise | 38.845 Eingabe + 1.718 Ausgabe = **40.563** |
| B mit ausdrücklich gewähltem Astra `643cd2d8985b43518eee0b86ed3ca457` | Sol 6/xhigh, Luna 6/max, Astra 6/medium | `full`, dieselben zwei Dateien | Konservativ zusammengeführtes `BLOCK`; vier Plan-Blocker, zwei blockierende Review-Befunde und zwei Nachweise. Luna meldete `BLOCK`, Astra unabhängig `REVIEW_ONLY`. | 57.297 Eingabe + 8.238 Ausgabe = **65.535** |

Beide Aufträge binden `scope_hash=9a07a4dc02dc9696cc12cbde95f23972737ff690f2b548a6b31ac95db153d917`. Beide erkannten die unbestätigte RadiWorks-Aufnahme, fehlende HEAD-Bindung aktueller Gedächtnisbytes, unvollständig inventarisierte ungetrackte Quellen, nicht nachgewiesene Tests und fehlende Aurelia-/Gruppenvoraussetzungen. Der alte Supervisor benannte die fehlenden Nachweise ausführlicher, einschließlich exakter Bindung und zweier unabhängiger Vertragsreviews. Luna stellte zusätzlich fest, dass Sols späterer Integrationsschritt die kumulativen Bedingungen für Contract-Intake, zwei P0–P3-freie Reviews, Aurelia-G0 und erneute Freeze-/Review-Runde nicht vollständig enthält; dieses Veto blieb trotz Astras milderem Einzelurteil erhalten. Die `REVIEW_ONLY`-Bezeichnung des alten Reviewformats erlaubt zugleich Befundlisten, während Route B solche Listen als `BLOCK` codiert. Die Entscheidungslabels sind daher nicht als reine Qualitätsnoten vergleichbar.

Route B verwendete hier **24.972 Tokens mehr** als der alte Weg (rund **61,6 %**). Der Vergleich belegt Zustellung, Quellenbindung und konkrete gemeinsame bzw. unterschiedliche Befunde in **einem** Fall; er belegt weder generelle Überlegenheit noch vollständige fachliche Erinnerung. Eine blind gegen vorab festgelegte Prüfpunkte bewertete Aufgabenserie ist für eine belastbare Genauigkeitsrangfolge weiterhin nötig.

Die tatsächlichen Tokens des RadiWorks-Paars sind oben gemessen; Geldkosten, Cache-Treffer und belastbare Latenzvergleiche nicht. Es wurde keine spekulative Kürzung oder Modellumschaltung zur Effizienz aktiviert. Die bestehende verlustfreie Matrixreferenzierung für Planprompts bleibt erhalten; unabhängige Prüfer erhalten weiterhin dieselbe Rohgrundlage. Prompt-Caching ersetzt keine dauerhafte oder überprüfbare Projekterinnerung. Route-B-Matrixpläne verlangen seit diesem Stand Astra zusätzlich und unabhängig; das Paar oben war ein **Review** mit ausdrücklich angeforderter Astra-Rolle, kein Planlauf.
