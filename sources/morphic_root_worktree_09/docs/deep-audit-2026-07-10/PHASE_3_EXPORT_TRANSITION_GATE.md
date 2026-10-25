# Phase 3 – Exportadapter: Übergangsgate (Read-only)

**Stand:** 2026-07-10
**Zweck:** Bestehende Exportpfade mit dem additiven `TenantClientArtifactRepository` gegenüberstellen, ohne einen bestehenden Exportpfad, Dateinamen oder ein Artefakt zu verändern.

## Bestandsbelege

| Bestehender Pfadbereich | Codebeleg | Aktueller Charakter | Übergangsrisiko |
|---|---|---|---|
| Scan-/Analyseexport | `apps/cli/commands/scan.py:1093,2289` | `--export` defaultet auf globalen Root; bestehende Auflösung | Dateischema und Konsumenten hängen am Legacy-Pfad |
| Workflow-Export | `apps/cli/workflow/orchestrator.py:43`, `step11_export.py:14` | globaler Defaultroot | muss rückwärtskompatibel bleiben |
| Trendexport | `apps/cli/commands/trend.py:190-203` | getrennte Archive-/Trendroots | Cross-root-Beziehungen erhalten |
| Berichtshierarchie | `tools/reporting_common.py:57-86` | `report_type / client_slug` | bestehender Client-Slug kann Rückschlüsse erlauben |
| Web-Reportkatalog | `apps/web/main.py:72-80,270-285` | leseseitige tenant-suffixierte Roots | kein schreibender Repositoryadapter |

## Neuer additiver Zielvertrag

`core/compliance/artifact_repository.py` plant ausschließlich:

```text
<repository-root>/<tenant_id>/<client_id>/<category>/<session_id>/<filename>
```

- `tenant_id` und `client_id` sind serverseitig abgeleitet.
- `client_id` ist die pseudonyme `cli-...`-ID, kein Klarname.
- Der Adapter schreibt nichts und ersetzt aktuell keinen Legacy-Pfad.
- Kategorien, Sessions und Dateinamen werden auf kanonische Segmente begrenzt.

## Integrationsreihenfolge

1. **Keine Migration:** Legacy-Exportabläufe und vorhandene Artefakte unverändert lassen.
2. **Opt-in Exportmodus:** erst als neue, klar benannte CLI-/Serveroption hinzufügen; Default bleibt Legacy, bis E2E-Vergleich grün ist.
3. **Paralleler Testexport:** mit synthetischen Daten nur Pfadplan, Manifestregistrierung und Reportkatalog-Lesepfad prüfen.
4. **Äquivalenzgate:** Scores, Reportinhalt und vorhandene Dateinamen/Strukturen des Legacy-Modus dürfen sich nicht ändern.
5. **Erst danach:** neue Artefakte client-/tenantpseudonym registrieren und im Erasure-Dry-run als zuverlässig zuordenbar ausweisen.

## Nicht zulässig

- Keine stille Verschiebung oder Umbenennung bestehender Klientenexporte.
- Kein Browserwert für `tenant_id`, `client_id` oder Exportroot.
- Keine Behauptung, dass der neue Adapter bereits alle CLI-Exporte steuert.
