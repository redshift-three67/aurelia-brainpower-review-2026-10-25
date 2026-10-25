# Tokeneffizienz – Änderungen seit der Wiederaufnahme

Stand: 16.09.2026. Projekt: Governor Workbench / Hermes.

Dieses Dokument fasst drei umgesetzte Regel-/Planungsänderungen und einen verworfenen Ansatz zusammen. Es ist ein Statusbericht, keine zusätzliche Ausführungsfreigabe. Maßgeblich bleiben die geltenden Projektanweisungen und Betreiberentscheidungen.

## 1. Übersicht: drei übernommene Punkte und ein verworfener Punkt

| ID | Thema / ursprünglicher Vorschlag | Tatsächlich ausgeführt | Status und Geltungsbereich | Empfehlung und Schutz der Qualität | Erwarteter Effizienzbeitrag |
|---|---|---|---|---|---|
| TE-1 | Ausgabe-/Arbeitsvertrag: strikt nur Code, keine Erklärungen oder Rückfragen | Einen angepassten Vertrag in projektbezogener und globaler `AGENTS.md` hinterlegt; `.cursorrules` als Verweis auf Projektregeln angelegt. Globale Vorfassung gesichert. | **Als Anweisung umgesetzt.** Projekt und persönliche Codex-Regeln; kein technischer Modellwechsel. | Knappe Antworten, minimale Diffs bei Codeausgaben, keine Wiederholung bereits bearbeiteten Codes. Statusfragen bleiben beantwortbar. Notwendige Rückfragen, Fehler, Einschränkungen, Prüfungen und Freigaben bleiben erhalten. Fehler nicht still verschlucken. | Weniger redundante Ausgabe, gezieltere Lese-/Prüfschritte. Keine gemessene Einsparquote. |
| TE-2 | Reasoning-Shifting: Medium für Planung, Low für Code | Verbindliche manuelle Umschalthinweise mit Bestätigungsablauf in Projektregeln hinterlegt; Wiederaufnahmestand ergänzt. Hermes-Auswahlharmonisierung als **RH-1** in Abschlussplan und Restarbeiten aufgenommen. | **Hinweisablauf und Planung umgesetzt.** Automatisches Hermes-Routing **noch nicht implementiert oder aktiviert**. | Medium als Standard. Low nur für lohnende, klar geplante Routinepakete. Komplexe Umsetzung, Sicherheit, Migration, Backup/Restore und anspruchsvolle Prüfung bleiben Medium. High/xHigh nur ausdrücklich durch den Betreiber. | Potenziell geringerer Reasoning-Aufwand bei geeigneten Paketen; Wechselaufwand und Nacharbeit müssen berücksichtigt werden. |
| TE-3 | Scope-/Kontextbegrenzung: nur offene Dateien, andere Komponenten als korrekt annehmen | Sichere Alternative als `Scope & Context Rules` in Projekt-`AGENTS.md` ergänzt; `.cursorrules` verweist darauf. | **Als Projektanweisung umgesetzt.** Keine zusätzliche globale Scope-Regel eingerichtet. | Gezielte Suche statt pauschaler Gesamtanalyse. Betroffene Aufrufer, Schnittstellen, Konfiguration, Datenverträge und Tests bei Bedarf einbeziehen. Ungeprüft bedeutet unbestätigt. Bei Fehlern, Abhängigkeiten oder Unsicherheit Untersuchung erweitern, ohne dadurch fremde Änderungen zu autorisieren. | Weniger unnötige Kontextaufnahme und Wiederholungsprüfungen; notwendige Belege bleiben maßgeblich. |
| TE-X | Terminal-Kompression per Prompt „nur Root Cause lesen“, pauschalem Stacktrace-Filter oder ungeprüfter Tool-Pipeline | Vorschlag bewertet; **kein Skript, Filter oder zusätzliches Tool installiert oder implementiert**. | **In vorgeschlagener Form verworfen.** Konservative lokale Aufbereitung bleibt eine bedarfsabhängige Möglichkeit, kein beschlossener Umsetzungsschritt. | Ein Zusatzprompt verkleinert das übertragene Log nicht. Abhängigkeits-Stackframes können entscheidend sein. Bei belegtem Bedarf Original lokal erhalten, ANSI/Progress-Ausgabe bereinigen, identische Wiederholungen zählen und Kürzungen markieren. Kontext, Ursachenketten, Pfade und Exitcode erhalten. | Nur eine tatsächliche Verringerung des übertragenen Textes spart Eingabetokens. Keine pauschale Filterung zur vermeintlichen Effizienz. |

## 2. Verbindlicher manueller Umschaltablauf im Chat

| Situation | Hinweis / Verhalten | Voraussetzung für Fortsetzung |
|---|---|---|
| Planung, Analyse oder komplexe Umsetzung | Medium beibehalten. | Keine Low-Phase beginnen, solange der Plan nicht ausreichend eindeutig ist. |
| Lohnendes, begrenztes Routinepaket mit feststehendem Plan | `Bitte jetzt auf Low umschalten. Danach: „Low bereit“.` | Nutzer stellt um und antwortet `Low bereit`; erst dann beginnt das Paket. |
| Low-Paket abgeschlossen; nächste Phase benötigt Medium | `Bitte jetzt zurück auf Medium umschalten. Danach: „Medium bereit“.` | Nutzer stellt zurück und antwortet `Medium bereit`; erst dann beginnt die betreffende Arbeit. |
| Unerwartete Komplexität während Low | An sicherer Stelle anhalten und Medium anfordern. | Keine komplexe Weiterarbeit vor Bestätigung. |
| Pause oder unklarer Kontext | Angeforderte/bestätigte Phase im Wiederaufnahmestand festhalten; bei Unklarheit Medium bestätigen lassen. | Keine tatsächliche Einstellung aus einer früheren Empfehlung ableiten. |
| Kleine Routineänderung ohne lohnenden Wechsel | Medium beibehalten. | Kein zusätzlicher Wechsel allein wegen einer kleinen Codeänderung. |

Grenze: Dies ist ein gespeicherter Hinweisablauf, kein technischer Schalter oder erzwingender UI-Mechanismus. Eine laufende Antwort stellt sich durch eine Textanweisung nicht um. Ohne verlässliche Laufzeitinformation gilt eine Nutzerbestätigung als Bestätigung, nicht als technisch ausgelesener Einstellungsnachweis. Aktuell ist Medium vorgesehen; in dieser Optimierungsrunde wurde kein Low-Paket bestätigt.

## 3. RH-1: geplante Harmonisierung im Hermes-Modellrouting

| Aspekt | Geplante Vorgabe | Aktueller Status |
|---|---|---|
| Reihenfolge | Nach belastbaren Schritt-/Abschlussnachweisen in Paket 2; vor automatisierten Reparatur-/Schrittfolgen in Paket 3; Teil der Gesamtabnahme in Paket 4. | Im Abschlussplan eingeordnet. |
| Auswahl | Gemeinsame validierte Regel für Oberfläche und Backend. Medium bei unklarer Einordnung; Low nur für geeignete Routineaufträge bei ausdrücklich aktivierter automatischer Auswahl. | Noch zu implementieren. |
| Betreiberkontrolle | Explizite Auswahl, Supervisor, Modellrouting und Projektgates bewahren. Keine automatische High/xHigh-Wahl. | Als Anforderung dokumentiert. |
| Nachvollziehbarkeit | Gewünschte/effektive Stufe, Grund und Regelversion je Auftrag sichtbar und dauerhaft speichern. Keine stille Ersatzwahl bei Inkompatibilität. | Noch zu implementieren und zu testen. |
| Prüfungen | Regelmatrix, manuelle Priorität, Provider-Payload, Persistenz/Neustart, Rückkehr zu Medium, inkompatible Modelle, unveränderte Gates und Hermes ohne Werkzeuge prüfen. | Offen. |
| Wirksamkeitsnachweis | Qualität und Gesamtverbrauch einschließlich Wiederholungen vergleichen; reale Modellevaluation getrennt und ausdrücklich autorisiert durchführen. | Kein Vergleich durchgeführt; keine Einsparung behauptet. |
| Kommunikation | Implementierungsbeginn und anschließend geprüften Abschluss im Chat melden; Aktivierungszustand und Grenzen benennen. | Verbindlich hinterlegt, Abschluss noch ausstehend. |

## 4. Dateien und Nachweise

Pfade relativ zum Projektstamm `C:/Users/Hubert111/Documents/Brainpower`, sofern nicht absolut angegeben.

| Datei | Inhalt / Änderung | Reichweite |
|---|---|---|
| `AGENTS.md` | Tokenvertrag, Umschalthinweise und Scope-/Kontextregeln | Dieses Projekt |
| `.cursorrules` | Verweis auf die Projektregeln, ohne zweiten abweichenden Regeltext | Cursor-Projektanweisung; keine technische Codex-Konfiguration |
| `C:/Users/Hubert111/.codex/AGENTS.md` | Angepasster globaler Tokenvertrag | Persönliche Codex-Anweisungen; kein Modellparameter |
| `checkpoints/TOKEN_RULES_2026-09-16/global-AGENTS.before.md` | Gesicherte globale Vorfassung | Rückgriff auf ursprünglichen Regeltext |
| `docs/HERMES_APP_ABSCHLUSS.md` | RH-1 mit Einordnung, Anforderungen und Prüfungen | Verbindlicher Hermes-Abschlussplan |
| `docs/RESTARBEITEN_0_5.md` | Verweis auf offenen RH-1-Punkt | Restarbeitenübersicht |
| `WIEDERAUFNAHME.md` | Hinweisablauf, vorgesehener Medium-Standard und RH-1-Status | Fortsetzung nach Pause |

Prüfumfang: Gespeicherte Regel- und Planungsabschnitte wurden zurückgelesen und auf die beabsichtigten Inhalte geprüft. Für diese Dokumentationsänderungen wurden keine funktionalen Tests oder neuen Modellläufe durchgeführt. Die Regeln sind keine formale Garantie für Fehlerfreiheit oder eine bestimmte Tokenersparnis.

## 5. Empfehlung für die Fortsetzung

Medium bleibt für die nächsten anspruchsvollen Hermes-Arbeiten vorgesehen. Zuerst technische Abschlussadapter für Test-/Änderungsschritte und Nachweise nach tatsächlicher Übernahme bearbeiten. RH-1 anschließend an der eingeordneten Stelle umsetzen und prüfen. Danach die übrigen Hermes-Abschlusspakete; erst anschließend SMB und Backup-/Restore-Abnahme, danach die fünf Produktprojekte. Die Effizienzregeln ändern keine dieser Freigaben oder Prioritäten.
