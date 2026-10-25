# Feedback f / F5-B v11 / Gate REV: Request Changes

Stand: 2026-07-17
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: **REV v11 driftfrei, aber REQUEST CHANGES; F5-B bleibt NO-GO**

## 1. Kurzfazit

REV v11 ist formal gueltig, weil beide Reviews denselben SHA-256-gebundenen
Freeze v11 geprueft haben und keine Scope-Drift festgestellt wurde. Das Ergebnis
ist dennoch **REQUEST CHANGES**, weil Review 2 ein P1 im Backup-Publish-Pfad
gefunden hat.

## 2. Review-Ergebnis

| Review | Verdict | Findings | Scope-Drift | Dokument |
|---|---|---:|---|---|
| Review 1 | APPROVE | `P0=0, P1=0, P2=0, P3=0` | keine | `docs/reviews/2026-07-17-feedback-f-F5-B-technical-review-v11-1.md` |
| Review 2 | REQUEST CHANGES | `P0=0, P1=1, P2=0, P3=0` | keine | `docs/reviews/2026-07-17-feedback-f-F5-B-technical-review-v11-2.md` |

## 3. Konsolidiertes P1

| ID | Prioritaet | Thema | Bewertung |
|---|---|---|---|
| R2 | P1 | Backup-Publish bindet nur Inode/Groesse, nicht die validierten Bytes | same-size Mutation nach Schema-Validierung kann als Manifest-Hash autorisiert werden |

## 4. Auswirkung auf Gate-Status

| Ebene | Vor REV v11 | Nach REV v11 |
|---|---:|---:|
| F5-B/v11 Mikro-Gates | `9/10 = 90 %` | `9/10 = 90 %` |
| F5 gezaehlte Arbeitseinheiten | `12/14 = 86 %` | `12/14 = 86 %` |
| Feedback f gezaehlte Einheiten | `26/39 = 67 %` | `26/39 = 67 %` |

Der Fortschritt steigt nicht, weil REV v11 keinen Doppel-APPROVE geliefert hat.

## 5. Exakt hier weiter

Naechster Block ist **R2: bytegebundener Backup-Publish**.

Konkrete Schritte:

| Reihenfolge | Schritt | Ziel |
|---:|---|---|
| 1 | RED-Test fuer same-size Snapshot-Mutation | P1 reproduzierbar machen |
| 2 | Publish-Erwartungswerte fuer Groesse und SHA-256 einfuehren | validierte Bytes an Publish binden |
| 3 | Manifest und Completion aus validierten Snapshot-Werten ableiten | spaeteres Blessing geaenderter Zielbytes verhindern |
| 4 | Fokus-, Admin-, Source-, Vollsuite- und Top-5-Regression ausfuehren | R2 belastbar schliessen |
| 5 | neuen Freeze v12 erzeugen | Reviews auf aktualisierte Basis wiederholen |
