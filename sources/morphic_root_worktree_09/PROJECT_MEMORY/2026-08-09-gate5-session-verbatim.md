# Gate 5 Session Verbatim And Directive Record

**Created:** 2026-08-09
**Use:** Requirement provenance only. Read the migration handoff first.

## Initial Continuation Directive

The user supplied the following controlling points at session start:

> `C:\morphic_v1\.worktrees\operator-workbench-phase1`
>
> Ignoriere den aktuellen VS-Code-Arbeitsordner
> `C:\Users\Hubert111\Documents\VSCodeNeu` vollständig als Projektziel.
> Verwende für jeden Shell-Aufruf explizit den oben genannten Worktree als
> workdir.
>
> Setze Gate 5, Task 8 exakt am abgebrochenen finalen Spezifikationsreview fort.
> Arbeite präzise, stabil, tokenergonomisch und autonom bis zur Gate-5-Acceptance,
> sofern keine technisch unauflösbare oder genehmigungspflichtige Blockade
> entsteht.
>
> Branch: `report-ux-polish`; HEAD:
> `2d38d3bfa3f204491fe066fbc986e07fffc2ff06`; Upstream:
> `upstream/report-ux-polish`; Git-Index leer. Der Worktree ist absichtlich
> umfangreich dirty und enthält akzeptierte uncommittete Arbeit sowie historische
> untracked Artefakte. Niemals pauschal bereinigen, löschen, zurücksetzen,
> stagen oder auschecken. Kein commit, push, reset, clean, checkout, stash oder
> autostash ohne separate ausdrückliche Nutzeranweisung. Änderungen anderer
> Personen oder historischer Gates nicht anfassen. Gate 4 ist ACCEPTED. Gate 5
> ist noch NICHT ACCEPTED. Gate 6 bleibt bis zur vollständigen Gate-5-Acceptance
> gesperrt.
>
> Verwende in diesem Projekt KEIN integriertes grep-Tool. Verwende in diesem
> Projekt KEIN integriertes glob-Tool für offene oder breite Suchen.
> Inhaltssuchen ausschließlich mit gezieltem `rg` über das Shell-Tool. Jeder
> `rg`-Aufruf benötigt einen expliziten Dateisatz und einen harten Timeout von
> typischerweise 30 Sekunden. Keine Suche über den gesamten Worktree, wenn die
> relevanten Dateien bekannt sind. Verwende Read für benannte Dateien. Keine
> breiten git-status-Ausgaben mit untracked Dateien.
>
> Führe keine Vollsuite erneut aus, solange keine Bytes geändert wurden.
>
> Gate 5 darf ausschließlich als ACCEPTED bezeichnet werden, wenn:
> Spezifikationsreview APPROVE mit P0=P1=P2=P3=0;
> Qualitäts-/Sicherheitsreview APPROVE mit P0=P1=P2=0;
> beide Reviews denselben verifizierten Source-Snapshot betreffen;
> alle geforderten Manifest-, Review-, Freeze- und Acceptance-Dateien existieren;
> alle Hashes verifiziert sind; Index leer ist; keine temporären Gate-5-Prozesse
> oder Artefakte verbleiben; kein Commit, Staging, Push, Reset oder Clean erfolgt
> ist.

The complete authoritative scope and acceptance sequence are preserved in
`PROJECT_MEMORY/2026-08-09-gate5-linux-migration-handoff.md` and the Gate-5
design/plan documents.

## Resource Strategy Requests

After the first RAM stop, the user wrote:

> Vielen Dank, können wir den Speicherbedarf für den Review minimieren, also
> z.B den Review aufteilen, oder muss dieser komplett erfolgen. Ich habe jetzt
> Ram freigegeben. Gibt es eine weitere Stragegie um de Review jetzt
> unterbrechungsfrei zu Ende zu führen? Du kannst jetzt starten.

Later the user wrote:

> Vielen Dank. Wir müssen auf jeden Fall eine Stratgegie entwickeln, dass wir
> nicht immer anhalten müssen und RAM freigeben müssen bzw. dies weitestgehend
> minimieren. Ich habe wieder RAM freigegeben, prüfe das bitte. Prüfe bitte bitte
> aber auch noch weitere strategiche Maßnahmen um die Blocker durch zu wenig RAM
> zumindest zu minimieren, ohne die Präzision, Akkuranz und Stabilität zu
> beeinträchtigen.

The user then provided an image whose visible text stated (obscured portions
are intentionally not reconstructed):

> Entwickle, wenn notwendig eine Tokenergonomische und Effektive Strategie für
> die generelle Umsetzung des Projektes, ohne die Präzision, die Akkuranz, die
> Stabilität und auch die vollumfängliche Umsetzung des Projektes zu gefährden.
> Stelle hierzu die notwendigen Informationen wenn sinnvoll jeweils direkt bzw.
> im Memory mit zur Verfügung in der weiteren Abarbeitung. Optimale akkurate
> Qualität in der Umsetzung ist in dem Projekt prior[... geschwärzt/nicht
> lesbar ...].

The resulting controlling interpretation is:

- accuracy, stability, and complete implementation take priority;
- token/resource optimization may change execution mechanics, never acceptance
  criteria;
- important durable state belongs in focused memory files;
- heavy phases remain serial and evidence is reused only on unchanged bytes.

## External Radi144 Process Decision

When the preflight found the external Radi144 server on port 8090, the user
wrote:

> Normal laufen lassen, er ist für ein anderes Programm notwendig, sofern dies
> für dich machbar ist. Ansonsten gebe mir bitte Bescheid.

Therefore that Windows process was not terminated. The Gate-5 plan explicitly
allows port 8090 to be owned by a separately documented user process. Gate-5
manual acceptance still must use another isolated port.

## Linux Migration And Push Authorization

The final user instruction for this Windows session was:

> Also, wir machen jetzt folgendes. Da wir immer wieder das RAM Problem haben,
> wird das Projekt auf den lokalen Debian Root Hauptserver verlagert. Hierzu
> erstellst Du mir für eine neue Session einen präzisen und voll detaillierten
> Wortlaut zum aktuellen Stand in vollem Detail, um auf dem Lokalen Linux
> Hauptserver in einer neuen Session genau an dieser Stelle weiter zu gehen.
> Dort gibt es keine RAM Beschränkungen mehr. Sichere auch noch alle wichtigen
> Sessioninformationen und Wortlaute im Chat von mir. Ich lade dann den Ordner
> morphic_v1 auf den lokalen Linux Hauptserver hoch, pushe bitte auch den
> aktuellen Stand sync auf das GitHub Repository redshift-three67 / radimorphic.
> Danke.

This is the separate explicit authorization for the migration checkpoint push.
It does not authorize reset, clean, checkout, stash, force-push, or unrelated
historical/untracked staging.

## Completeness Recheck Directive

After the first migration push, the user wrote:

> Jetzt die Frage, können wir an Hand des repository auf GitHub exakt und
> lückenlos auf dem lokalen Debian Hauptserver genau an dieser Stelle dort
> weiter machen? Kannst Du das bitte nochmals akkurat prüfen und die
> Dokumentation daraufhin nochmals auch exakt konsolidieren? Gebe mir dann
> nochmals den Pfad des Handoffs an. Gehe präzise akkurat und stabil so weiter.

The resulting audit found six remaining tracked Windows changes. Because two
were in the persistent CLI-Smoke path and three participated in the full suite,
the GitHub branch was not yet an exact tracked checkpoint. They were reviewed
and added through a separate scoped completeness commit. Historical untracked
runtime/shadow artifacts remain intentionally excluded and are not part of the
reproducible project state.

## Final Root And Debian Path Verification Directive

The user then wrote:

> Ausgezeichnet. Jetzt nochmals abschließend die Frage. Ist GitHub Radimorphic
> jetzt synchron zur hier Lokal C:/morphic_v1 und exakt Dokumentiert. Kannst Du
> ggf. noch, wenn notwendig, anpassen dass auf Debian unter
> /opt/Prototypen/Radimorphic integriert wird. Danke. Bitte Prüfe den Vorgang
> nochmal.

The verification established that `C:/morphic_v1` is the common multi-worktree
container and its root checkout is a separate dirty `master@411ff09`. The exact
GitHub checkpoint corresponds to the active source worktree
`C:/morphic_v1/.worktrees/operator-workbench-phase1`, not to that root checkout.
The canonical Debian target is `/opt/Prototypen/Radimorphic`, created as a fresh
GitHub clone. Windows linked-worktree metadata and virtual environments must not
be copied into the Debian repository.
