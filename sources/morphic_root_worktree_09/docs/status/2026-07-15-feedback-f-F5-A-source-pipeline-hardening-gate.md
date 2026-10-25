# Feedback f – F5-A Source-Pipeline-Hardening Gate

**Stand:** 2026-07-15
**Worktree:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Branch:** `operator-workbench-phase1`
**HEAD:** `619a1f5485a151816e32732929a6a823839ccb57`
**Makroblock:** F5-A = F5.5 + F5.4 + F5.1
**Entscheidungsstatus dieses Dokuments:** **CONDITIONAL GO**

## 1. Wirksamkeitsregel

F5-A wird ohne weiteren Repositorypatch genau dann formal **GO**, wenn alle folgenden Bedingungen
gemeinsam erfüllt und extern nachweisbar sind:

1. die beiden projektlokalen technischen Reviews v3 sind `APPROVE` mit null P0–P3 und binden
   denselben Freeze-v3-Hash;
2. ein finaler Dokument-Freeze bindet den vollständigen technischen und dokumentarischen Scope
   einschließlich dieses Records sowie beider technischen Reviewreports;
3. zwei unabhängige read-only Dokumentreviews bestätigen diesen Dokument-Freeze driftfrei mit
   `APPROVE` und null P0–P3;
4. nach Abschluss beider Dokumentreviews wird eine externe Post-State-ShadowCopy erzeugt, die den
   gesamten Dokument-Freeze-Scope, den Freeze selbst und beide vollständigen Dokumentreviewreports
   enthält;
5. ein `SOURCE_MANIFEST.sha256` in der ShadowCopy wird vollständig mit `sha256sum -c` verifiziert,
   und die ShadowCopy-Dateiliste wird gegen den erwarteten Scope rückverglichen.

Fehlt eine Bedingung, ist F5-A **NO-GO** und F5-B gesperrt. Ein Repositorypatch nach dem
Dokumentreview invalidiert dessen Snapshot und verlangt einen neuen Dokument-Freeze samt
Doppelreview und Post-State-Sicherung.

## 2. Technischer Abschlussnachweis

Maßgeblicher technischer Freeze:

`docs/status/2026-07-15-feedback-f-F5-A-technical-freeze-v3.md`

SHA-256:

`2fe918ab7298970ad8b072bcc1aeaf96341fae020502c51e823e5743806c31ca`

Technische Doppelreviews:

- `docs/reviews/2026-07-15-feedback-f-F5-A-technical-review-v3-1.md`
- `docs/reviews/2026-07-15-feedback-f-F5-A-technical-review-v3-2.md`

Beide Reviews sind unabhängig, driftfrei und enden mit `APPROVE`, null P0–P3. Beide binden Branch
`operator-workbench-phase1`, HEAD `619a1f5485a151816e32732929a6a823839ccb57`, denselben
Freeze-v3-Hash und dieselben 22 technischen Scope-Hashes zu Beginn und Ende.

Transparenzhinweis: Review 1 zeigt in seiner rein abgekürzten Übersicht für
`PROJECT_MEMORY/00_CURRENT_STATE.md` die fehlerhafte Darstellung `40da7e1c...66c31ca`.
Sie enthält sowohl einen falschen abgekürzten Präfix (`40da7e1c` statt `40da7e1b`) als auch ein
falsches Suffix (`66c31ca` statt `e2f64cf`). Das ist ein Darstellungsfehler des Reports, keine
gemessene Abweichung: derselbe Report bestätigt ausdrücklich 22/22 exakte Start-/Endtreffer;
Freeze v3 und Review 2 führen den vollständigen korrekten Hash
`40da7e1b43feb94a8fe4e8ecf6c3aa27e5783d2c78459befd0e0baabbe2f64cf`.
Der technische Reviewreport bleibt als Primärevidenz unverändert.

## 3. Verifikationsmatrix

```text
Betroffene Registry-/Ledgerdateien: 94 passed in 1.91s
Fokus: 114 passed, 1 skipped in 2.07s
Admin: 437 passed, 6 skipped in 21.25s
Breit: 921 passed, 8 skipped, exakt 14 bekannte Baselinefehler in 170.46s
Top-5: 1 passed in 98.70s
Ruff: PASS
py_compile: PASS
git diff --check: PASS; nur bekannte LF->CRLF-Hinweise ausserhalb des F5-A-Scopes
```

Die 14 breiten Fehler sind baseline-identisch: ein datumsabhängiger Consent-Test und 13 bekannte
HTTP-429-/Rate-Limit-Tests. Keine F5-A-Regression wurde beobachtet.

## 4. Geschlossene Sicherheitsbefunde

Die beiden historischen Freeze-/Reviewzyklen v1 und v2 sind ausdrücklich superseded und nicht
gatewirksam. Geschlossen wurden:

- Ledger-Hardlink-Aliasing;
- server-owned `source_type`-/Lizenz-/Trust-/Import-Policytransition für bestehende und neue Sources;
- finale Policyrevalidierung auch für intern konsistent neu gehashte Stage-Artefakte;
- zeitunabhängige Duplicate-Staging-Identität bei weiterhin zeitgebundenem Vollartefakthash;
- Dokumentdrift in Ist-Analyse und Stabilisierungsmatrix;
- verbliebenes Hardlink-TOCTOU nach Temp-`fsync` und vor Replace.

Registry und Ledger schreiben die Tempdatei, führen Flush und `fsync` aus, revalidieren danach unter
dem gehaltenen Authoritylock den Zielpfad und rufen unmittelbar anschließend `os.replace` auf. Zwei
deterministische Boundarytests injizieren exakt nach Temp-`fsync` einen Hardlink und beweisen
fail-closed unveränderte Authority-/Aliasbytes sowie Temp-Cleanup.

## 5. Freigegebener F5-A-Vertrag

- `sources data-record-consistency` ist der primäre Consistency-Befehl;
- `sources data-promote` bleibt nur sichtbar deprecateter No-Publish-Alias;
- Ledger-Schema v3 verwendet `entries` und `recorded_at`;
- v1/v2-Promotion-Ledger werden fail-closed und ohne Mutation abgewiesen;
- Duplicate-Staging und Replay werden über die stabile Batchidentität gesperrt;
- produktive Legacy-v1-Registry bleibt read-only;
- neue Sources beginnen deaktiviert und least-privileged;
- bestehende Policy-/Typfelder sind bei Manifestreplacement immutable;
- `data-import-draft` bleibt ein getrennter, noch nicht umgesetzter F5.3-Folgepfad.

## 6. Explizite Nichtwirkung

F5-A bewirkt nicht:

- keinen Catalog-Draft, Publish oder Activate;
- keine Scan-/Engine-/Runtimewirkung;
- keinen Netzwerkfetch oder Onlineadapter;
- kein produktives lokales Source-Daten-I/O;
- keine typenspezifischen F5.2-Normalizer;
- keinen externen Tamper-Evidence-Anker für das Consistency-Ledger;
- keine produktive Registry- oder Ledgermigration.

`config/source_repositories.json` und `data/remedies.db` blieben hashidentisch. Port 8000 blieb frei;
der bestehende Radi144-Listener auf 127.0.0.1:8090, PID 20404, blieb unangetastet.

## 7. Folgeschrittgrenze

Nach wirksamem F5-A-GO ist ausschließlich die Planung/Umsetzung von **F5-B** zulässig:

- F5.2 typenspezifische Source-Normalizer;
- F5.3 kontrollierte Übernahme in einen Catalog-Draft.

F5-B erbt keine automatische Publish-, Activate-, Runtime- oder Netzwerkfreigabe. F5-C, F6, F7,
Online-Repositories und Feedback f als Gesamtfeature bleiben bis zu ihren eigenen Gates NO-GO.

## 8. Kein Repository-Lifecycle-Eingriff

Kein Commit, Push, Staging, Reset, Clean oder History-Rewrite wurde ausgeführt. Der umfangreiche
vorbestehende Dirty-Worktree wurde außerhalb des F5-A-Scopes nicht bereinigt oder umformatiert.
