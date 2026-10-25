# AURELIA – Planungsreview und empfohlene Fortsetzung

```yaml
document_set: AURELIA-PLAN-REVIEW-20260907-112958-CEST
created_at: 2026-09-07T11:29:58+02:00
timezone: Europe/Berlin
language: de
status: proposed_for_discussion
authority: advisory_not_product_canon
execution_authorized_by_this_package: false
authorized_current_work: documentation_in_this_new_folder_only
reviewed_branch: codex/aurelia-konsolidierung
reviewed_head: 1185a68ed984b525686764f995513355701929e3
reviewed_worktree_dirty: true
```

## Ergebnis

Die bestehende K1-Planung ist als Grundstruktur tragfähig. Sie braucht einen aktuellen Wiederaufnahmepunkt, korrigierte Prüfverträge und eindeutig getrennte Abnahmen. Tasks 5 und 6 sind bereits committed; zu Task 7 liegen uncommittierte Änderungen vor. Historische Statusangaben sind teilweise überholt. Das Servergate bleibt laut Dokumentation bei `G0-SRV-0`; dieser Review bestätigt keinen tatsächlichen Serverzustand.

**Keine pauschale Freigabe:** Dieses Paket dokumentiert Befunde und Empfehlungen. Es ersetzt weder Betreiberentscheidungen noch den Produktkanon, den alten Masterplan oder Server-/Publikationsfreigaben. Die Genehmigung zur Erstellung dieser Dokumente ist keine Genehmigung zur Umsetzung ihrer Vorschläge.

## Lesereihenfolge

| Dokument | Zweck | Zielgruppe |
|---|---|---|
| [01 – Ist-Stand und Review](01_IST_STAND_UND_REVIEW.md) | Tatsachen, Prüfergebnisse, Befunde und Aussagegrenzen | Entwickler, Reviewer, Betreiber |
| [02 – Alt-/Neu-Vergleich](02_ALT_NEU_VERGLEICH.md) | Vollständige Zuordnung aller 14 alten Tasks zur Empfehlung | Besprechung und Änderungsentscheidung |
| [03 – Empfohlene Umsetzungsplanung](03_EMPFOHLENE_UMSETZUNGSPLANUNG.md) | Arbeitspakete, Dateien, Abhängigkeiten und Abnahmen | Ausführender Entwickler / LLM |
| [04 – Weitere Lücken und Verbesserungen](04_WEITERE_LUECKEN_UND_VERBESSERUNGEN.md) | Zusätzliche Prüfaufträge und optionale Ideen, getrennt von bestätigten Fehlern | Architektur- und Qualitätsbesprechung |
| [05 – Entwickler-/LLM-Übergabe](05_ENTWICKLER_LLM_UEBERGABE.md) | Kompakter Einstieg, Grenzen und Wiederaufnahmeprotokoll | Neue Entwicklungssitzung |
| [06 – Quellen und Verifikation](06_QUELLEN_UND_VERIFIKATION.md) | Pfade, Hashes und technische Dokumentprüfung | Nachvollziehbarkeit und Übergabe |

## Begriffe und Pfadkonvention

- **ROOT:** Projekt-Hauptverzeichnis `C:/Users/Hubert111/Documents/ChatGPT/Aurelia`.
- **K1:** `ROOT/.worktrees/aurelia-konsolidierung`; hier liegt die untersuchte neuere Implementierung.
- **ALT:** `K1/docs/superpowers/plans/2026-08-25-aurelia-k1-canon-consolidation.md`.
- **EMPFOHLEN:** Dokument 03 dieses Pakets; noch kein freigegebener Ersatzplan.
- Alle Implementierungspfade in Dokument 03 sind relativ zu **K1**, sofern nicht anders angegeben.
- `K1` als Konsolidierungsprogramm ist nicht mit dem gleichnamigen Kozyrev-Katalogeintrag zu verwechseln.
- **Belegt** bedeutet lokal nachgelesen oder mit benanntem Befehl geprüft. **Historisch dokumentiert** bedeutet kein erneuter Test. **Empfehlung** bedeutet vorgeschlagene Änderung. **Prüfauftrag** bedeutet keine bestätigte Schwachstelle.

## Umgang mit dem alten Plan

ALT bleibt unverändert. Dokument 02 gibt dessen Taskstruktur und relevante Abnahmeanforderungen sinngenau wieder; es ist keine wörtliche Vollkopie. Für den exakten Originalwortlaut dienen ALT sowie sein SHA-256 im Quellenmanifest. So werden historische, möglicherweise publikationsrelevante Fixtures nicht unnötig dupliziert.

Bei späterer Übernahme: explizit festhalten, welche Empfehlungen ALT ergänzen oder ersetzen. Historische Nachweise unverändert lassen und neue Entscheidungen mit Datum ergänzen. Keine Empfehlung allein wegen dieses Dokuments als bereits genehmigt markieren.

## Qualität und Aufwand

Die bestehende Zwei-Spuren-Strategie bleibt maßgeblich: deterministische, risikoarme Prüfungen primär; kritische Vertragsänderungen mit fokussiertem Spec- und anschließendem Quality-/Securityreview. Keine erneute Vollanalyse unveränderter Flächen ohne sachlichen Grund. Neue Tests nur für tatsächliche Verhaltens- und Sicherheitsverträge, nicht für bloße redaktionelle Änderungen.

Absolute Fehlerfreiheit ist nicht nachweisbar. Ziel ist eine reproduzierbare, explizit begrenzte Abnahme ohne unbelegte Erfolgsaussagen.
