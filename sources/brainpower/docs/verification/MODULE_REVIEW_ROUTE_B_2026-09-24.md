# Einzelreviews der registrierten Aurelia-Module mit Hermes-Route B

Stand: 24.09.2026. Umfang: **RadiWorks, Radi144, morphic_v1** als drei registrierte Module der Aurelia-Integrationsgruppe. Aurelia selbst und Modul_Templates sind gemeinsame Voraussetzungen, keine in diesem Durchlauf freigegebenen Module. Die Prüfungen sind quellgebundene, lesende **Planungsreviews**, kein vollständiges Audit jeder Codezeile und keine Aurelia-Produktabnahme. Automatische Modellreviews blieben ausgeschaltet; die Einzelaufträge wurden ausdrücklich gestartet. Für jedes Modul lagen gespeicherte Modellversandfreigaben vor.

| Modul | Route-B-Auftrag | Modellweg | Ergebnis und entscheidender offener Punkt |
| --- | --- | --- | --- |
| RadiWorks | `61b06596eff045a18af9ab46edb1b7b9` | Sol 6/xhigh → Luna 6/max | `REVIEW_ONLY`, keine Findings in der strukturierten Antwort. Aktuelle RadiWorks/Aurelia-Verträge und Quellen-Hashes müssen als eigener Contract-Intake abgeglichen werden; Aufnahme und gemeinsame Gates sind nicht bestätigt. Gespeicherter Job war zum Abschluss nicht stale. |
| Radi144 | `8e73bc1fc0e84f2e89bd579520f25a63` | Sol 6/xhigh → Luna 6/max → Astra 6/medium | `REVIEW_ONLY`. Sol und Luna identifizierten in zwei gestagten Plänen unterschiedliche G0-Bedeutungen; Astra wurde deshalb regelgemäß angefordert. Dieser Widerspruch muss vor Matrixplanung geklärt werden. Der gespeicherte Job ist als stale markiert; sein Votum ist **historische Beratung**, kein aktueller Freigabenachweis. |
| morphic_v1 | `11985b28577342f1a6c1d71649c91cd6` | Sol 6/xhigh → Luna 6/max | `REVIEW_ONLY`, keine Findings in der strukturierten Antwort. G0 Authority Freeze für Einstiegspunkte, Abhängigkeiten, Tenant-Pfade und Export-Autorität bleibt eine separat zu autorisierende Prüfung; Aufnahme und gemeinsame Gates offen. Gespeicherter Job war zum Abschluss nicht stale. |

Alle drei Modellpläne raten von Produktänderung und Gate-Freigabe durch diesen Review ab. Die Einzelreviews ersetzen weder die Aufnahme jedes Gruppenmitglieds noch die Prüfung gemeinsamer Aurelia-/Modul_Templates-Voraussetzungen. Besonders bei Radi144 sind gestagte Plan-Dateien nicht automatisch Teil von HEAD; eine berichtete Löschung im Arbeitsbaum ist ohne Vergleich mit HEAD kein Beweis irreversiblen Verlusts.

## Aktuelle Hash- und Freshness-Grenze

Nach lokalen Neuaufnahmen entsprachen die aktuellen Scope-Hashes den Hashes der drei Aufträge. Die Governor-API setzt in **angezeigten** Jobs `freshness=unknown_requires_rescan` und `stale=true`, wenn der lokale Scope-Cache älter als 15 Sekunden ist, selbst wenn der **gespeicherte** Job zum Abschluss `stale=false` hatte. Diese Anzeige ist absichtlich konservativ; ein neuer lokaler Scan ist für eine aktuelle Behauptung nötig. Radi144s gespeichertes `stale=true` wird durch den später gleichen Hash nicht rückwirkend aufgehoben. Kein Bericht darf daraus eine aktuelle Freigabe ableiten.

## Ergänzende technische Prüfung

| Umfang | Ergebnis | Aussagegrenze |
| --- | --- | --- |
| RadiWorks Engine | Gesamte lokale Testsuite: Exitcode 0, Ausgabe ohne Gesamtzahl; gezielte Gold-Parität: 9 bestanden. | Java-Orakelparität nur für drei seeded synthetische REST-Fixtures mit 300 Raten; [Paritätsmatrix](../../../Radiworks/radiworks_port/engine/PARITY_MATRIX.md). |
| Radi144 | Lokale Testsuite: 92 bestanden, 30 Deprecation-Warnungen. | Kein Ersatz für Aufnahme, G0-Auflösung oder Aurelia-Integrationstest. |
| morphic_v1 | 182 ausgewählte Tests zu Workbench-Laufzeit, Scan-Sicherheit, Review-Regression, Harmonisierung, Grenzwerten und Wellbeing-Berichten bestanden. | Die gesamte sehr große Suite wurde nach frühem Fortschritt beendet; ihr Gesamtergebnis ist **offen**. Vor dem fokussierten Lauf musste ein temporäres Jobverzeichnis gesetzt werden, weil der Checkout unter der Windows-Sandbox keine Verzeichnis-Flush-Rechte bot. Getrackte Produktdateien blieben unverändert. |
| Hermes Route B | 32 gezielte LLM-/Timeout-Unit-Tests und vier HTTP-/Workerprüfungen bestanden; JavaScript-Syntax/UI-Tests für das verlängerte Scope-/Route-B-Annahmefenster bestanden. | Ein Modelltimeout von 300 s ist lokal konfiguriert und im Client zugelassen. Es garantiert keinen Modellabschluss. |

## Bedienfolge in Hermes

1. **Projekte & Gruppen** öffnen. Für ein Einzelmodul **Aufnahme prüfen** (bei Gruppenkarte **Einzelaufnahme prüfen**) wählen. Das liest nur lokal und ruft kein Modell auf.
2. Im ausgewählten Modul **Route B · Umfang prüfen** verwenden. Das sendet den ausdrücklich freigegebenen Umfang an Sol und Luna; Astra wird bei gemeldetem kritischem Risiko/Widerspruch oder durch die eigene Checkbox hinzugezogen. Ein erneuter Aufruf verursacht neue Modellkosten und ist für die drei oben dokumentierten Reviews derzeit nicht nötig.
3. Unter **Aufträge & Ergebnisse** den Auftrag anhand der ID öffnen. Votum, Befunde, Quellen-Hash, `stale`/Freshness und tatsächliche Modellaufrufe getrennt lesen. „Historischer Nachweis · aktuell ungeprüft“ verlangt eine neue lokale Aufnahme, bevor man aktuelle Quellen behauptet.
4. Die **Aufnahmebestätigung** ist eine eigene Betreiberentscheidung mit Anforderungen, Teststrategie, Abhängigkeiten und offenen Nachweisen. Erst wenn alle Mitglieder samt gemeinsamen Voraussetzungen vollständig aufgenommen sind, kann **Route B · Matrixplan entwerfen** sinnvoll freigeschaltet und separat beurteilt werden. Weder Review noch Kandidat führen Produktcode aus.

Für die angefragten RadiWorks-Kernverfahren liegt das strukturierte, quellverlinkte Dokument [RADIWORKS_KERNENGINES_2026-09-24.md](../RADIWORKS_KERNENGINES_2026-09-24.md) vor.
