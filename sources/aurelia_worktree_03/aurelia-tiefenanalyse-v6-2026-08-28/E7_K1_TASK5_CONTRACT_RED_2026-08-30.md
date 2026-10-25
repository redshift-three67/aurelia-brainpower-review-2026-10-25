# E7-Evidenz: K1 Task 5 — Decision-Contract und RED-Baseline (2026-08-30)

Verfahren nach `docs/project-control/QUALITY-ROUTING.md`, Spur B. Maßgeblich sind
das freigegebene K1-Design `7de43db7bdaf87132de6893daf6acdad46d9c9ba`,
der Masterplan `docs/superpowers/plans/2026-08-25-aurelia-k1-canon-consolidation.md`
(Task 5) und die Session-Übergabe vom 2026-08-30, 17:39 CEST.

**Diese gitignorierte Datei ist lokale Arbeitsevidenz, keine Gate-, Commit- oder
Publikationsfreigabe.** Sie enthält keine Rohdaten, Secrets, Identitäten oder
Serverzugriffe.

## 1. Verifizierter Ausgangspunkt

Zeitpunkt der frischen Baseline: 2026-08-30, 18:25 CEST.

- Worktree: `.worktrees/aurelia-konsolidierung`
- Branch: `codex/aurelia-konsolidierung`
- HEAD: `1257283d0b4fd54da9278195c899bea56ca901f5`
- Remote-Tracking-Ref: `e6f308958a3f14dcfac346e2ae5c273795abb77d`
- Status: sauber, lokal genau 1 Commit voraus
- `8706186af01e10e4253e25abb31bf3577110dae4` ist Vorfahr von HEAD
- `git diff --check`: Exit 0
- Canon-Unit-Suite: Exit 0, 8/8 PASS
- `npm run typecheck`: Exit 0
- `npm run check:k1-control`: Exit 0

## 2. Korrigierte RED-Evidenz

`npm run check:canon` wurde frisch mit dem Worktree als `process.cwd()`
ausgeführt und endete mit Exit 1. Der Lauf meldete **44 aktive Textrecords** und
**10 als doppelt klassifizierte ID-Records** (D08–D12, K1–K5), insgesamt 54
Fehlerzeilen.

Damit ist die Übergabeangabe „10 aktive Textverletzungen“ keine reproduzierbare
Baseline dieses Worktrees. Sie wird nicht als aktuelle Evidenz weiterverwendet.
Die echte Liste umfasst 20 Textrecords in Task-5-Dateien, 16 in zwölf
präsentierenden Routen und acht in weiteren aktiven Quellen. Historische
Specs/Pläne und externe Analysen erschienen nicht als aktive Textbefunde.

Zusätzlich ist ein systemischer Vertragsdefekt bestätigt: Die pauschale Regel
`/webrtc/i` meldet auch den zwingenden Kanonwert `webrtc: "excluded"` und klare
No-WebRTC-Aussagen. Ein Repository-PASS wäre damit selbst nach korrekter
Konsolidierung unmöglich. Das freigegebene Design verlangt hingegen, optionales
oder nachrangiges WebRTC/Video zu erkennen und den No-Video-/No-WebRTC-Kanon zu
übernehmen. Die aktuelle Regel prüft trotz ihres Namens Video gar nicht und die
Phase-Regel übersieht gleichbedeutende Formen wie „gestartet“ oder „startet“.

## 3. Schriftlicher Decision-Contract vor Mutation

### Ziel

Aktive K1-Quellen werden auf eine widerspruchsfreie Matrix konsolidiert. Der
Validator muss echte veraltete/optionale Medienaussagen, alte Betriebssystem- und
Storageziele, unqualifizierte Phase-1-Aussagen sowie unvollständige oder doppelte
kanonische ID-Mengen fail-closed erkennen. Explizite Ausschlussaussagen dürfen
nicht als Verstoß gelten. `npm run check:canon` muss am Ende Exit 0 erreichen.

### Autoritative Aussagen

- Phase 0 ist abgenommen.
- Die Phase-1-Schale einschließlich Auth und Mandantenbasis ist technisch
  vorhanden; weitere Produktarbeit ist bis dokumentiert bestandenem
  `G0-SRV-12` pausiert.
- Auth und Datenbank sind an; Datenklasse ausschließlich `synthetic`.
- Ziel: Ubuntu Server 24.04.4 LTS amd64 mit minimalem GNOME.
- Storage: 2×2 TB WD_BLACK SN850X; RAID1/LUKS2/LVM ist geplant, nicht ausgeführt.
- Kein Video, kein WebRTC, kein TURN, keine Videoaufzeichnung; Phase 9 gestrichen.
- CUDA, USB und Art.-9-Klartext bleiben gesperrt.

### Medien-/Phasenregel

- `src/lib/concept/canon.ts` wird ausschließlich strukturell durch
  `matrixErrors` geprüft und nicht zusätzlich durch eine rohe Textsuche.
- Jede sonstige aktive Aussage mit Video/WebRTC bleibt rot, sofern sie nicht auf
  derselben Aussagezeile den Ausschluss eindeutig ausdrückt. `optional`,
  `nachrangig` oder eine Aktivierungs-/Scaffold-Aussage bleiben immer rot.
- Debian/Bookworm ist nur in einem ausdrücklich als `historisch`, `superseded`
  **und** `nicht ausführbar` markierten Kontext zulässig; aktuelle Bindungen
  werden auf Ubuntu/M G1 neutralisiert.
- `Phase 1 läuft`, `Phase 1 gestartet`, `Phase 1 startet …` und ein nackter
  Phasenstatus `läuft` bleiben rot. Zulässig ist nur Schale vorhanden plus
  Produktarbeit pausiert bis G0-SRV-12.

### ID-Auslegung

- H bezeichnet die Hybrid-/Origin-Architekturalternativen H1–H8 in
  `standalone.ts`; H1–H3 gesetzt, H4 optional, H5–H8 gesperrt.
- L01–L09 ist eine eigenständige Lovable-Bewertungsfamilie und wird nicht durch H
  ersetzt. Weil die freigegebene Pflichtfamilienliste L nicht nennt, wird L als
  **zusätzliche aktive Hilfsfamilie** ausdrücklich und genauso fail-closed
  validiert; D/C/X/U/K/H/O/WV bleiben die benannten Pflichtfamilien.
- Exakte kanonische Mengen: D01–D24, C01–C12, X01–X20, U01–U12, K1–K8,
  H1–H8, O01–O10, WV01–WV06, L01–L09.
- D08–D12 in der Legende sind Summary-Referenzen, keine zweiten Entscheidungen.
  K1–K5 in der Schaltertabelle sind Schalter-Referenzen, keine zweiten
  Kernelkatalogeinträge.
- Der reale Repositorycheck validiert ausschließlich die autoritativen Sammlungen
  `DECISIONS`, `C_GESETZT`, `X_KATALOG`, `U_GESETZT`, `KOZYREV_OPTIONAL`,
  `HYBRID_ALTERNATIVEN`, `OFFEN`, `WIEDERVORLAGE` und `LOVABLE_NUTZEN`.
  Projektionen bleiben erhalten; es wird nicht global dedupliziert und eine
  echte Doppelung innerhalb einer autoritativen Sammlung bleibt rot.
- H und WV müssen in beiden aktiven Legenden erscheinen. L bleibt als eigene
  Hilfsfamilie sichtbar.

### Zentrale D-Locks

`CANONICAL_DECISION_LOCKS` ist die einzige D01–D24-Lockquelle.
`DECISIONS[].lock` wird daraus abgeleitet. D08/D10/D12 sind gesetzt, D09/D11
empfohlen. Die D08–D12-Summaries besitzen keinen zweiten Lock; ihre Benennung und
Statusbegründung werden als Projektion kenntlich gemacht.

### Erlaubte Mutationsfläche

- Task-5-Dokumente und Konzeptdaten aus dem Masterplan;
- aktive Portaltexte, soweit die neuere Übergabe sie für Task-5-Exit-0 verlangt;
- `scripts/canon-contract.mjs` und `scripts/canon-contract.test.mjs` als zwingende
  Korrektur des in RED nachgewiesenen Task-4-Vertragsdefekts;
- direkte Consumer umbenannter Summaryfelder;
- `docs/project-control/K1-STATUS.md` für den überfälligen Task-4-/Task-5-Ledger;
- ausschließlich gitignorierte E7-/Live-View-Evidenz außerhalb des Git-Scopes.

### Nichtziele und Verbote

Keine funktionale Task-6-Schalenimplementierung, kein Serverzugriff, keine echte
Daten- oder DB-Migration, kein Build, kein Push, Merge, Rebase, Reset,
History-Rewrite, `git add -f`, CUDA-/USB-Aktivierung und keine Änderung
historischer Analysen/Specs/Branches.

### Fehlerverhalten

- Unklare Medienaussage bleibt rot; nur expliziter Ausschluss ist zulässig.
- Fehlende, unerwartete oder doppelte kanonische IDs bleiben pro Familie rot.
- Projektionen werden nicht als Definitionen gezählt und nicht durch
  `Set`-Normalisierung versteckt.
- Unlesbare/fehlende aktive Dateien und fehlende Rohquellengrenzen bleiben rot.

### RED/GREEN- und Abnahmebefehle

1. Neue Negativ-/Positivtests zuerst; RED aus dem jeweils erwarteten Grund.
2. `node --experimental-strip-types --test scripts/canon-contract.test.mjs`
3. `npm run check:canon`
4. `npm run typecheck`
5. `npm run check:k1-control`
6. `git diff --check`
7. Nach GREEN fokussiertes Spec-Review; nur nach Spec-PASS separates
   Qualitätsreview durch eine frische Instanz.
8. Jeder akzeptierte Reviewerbefund wird durch die primäre Instanz mit einer
   Minimalprobe reproduziert und danach gezielt erneut geprüft.

## 4. RED-Nachweis

Nach Fixierung des Contracts wurden neun neue/verschärfte Testgruppen ergänzt.
Frischer Lauf:

```text
node --experimental-strip-types --test scripts/canon-contract.test.mjs
Exit 1 · 17 Tests · 7 PASS · 10 FAIL
```

Alle zehn FAILs stammen aus den absichtlich noch fehlenden Task-5-Verträgen:
explizite Medienausschlüsse und vollständig markierte historische Supersession
werden noch verworfen; äquivalente Phase-Startformen und positives Video werden
noch nicht vollständig erkannt; `canon.ts` wird noch doppelt textuell geprüft;
L und exakte ID-Mengen fehlen; zentrale D-Lockmap, autoritative
Repositorysammlungen und Projektionsprüfung fehlen. Kein Altvertrag regressierte.

Arbeitsbaum enthält zu diesem Zeitpunkt ausschließlich den neuen Testdiff;
Implementierungsdateien sind noch unverändert. Nächste Stufe: minimale
Implementierung bis 17/17 GREEN, anschließend reale Quellenkonsolidierung.

## 5. Vertrags-GREEN und neue reale RED-Grenze

Die minimale Vertragsimplementierung trennt nun autoritative Records von
D-/K-Projektionen, validiert exakte D/C/X/U/K/H/O/WV- sowie aktive L-Mengen,
prüft beide Legenden, leitet alle D-Locks aus einer einzigen D01–D24-Map ab und
wertet Medien-/Phasenaussagen kontextsensitiv aus. `canon.ts` wird nur strukturell
geprüft.

```text
node --experimental-strip-types --test scripts/canon-contract.test.mjs
Exit 0 · 17/17 PASS
npm run typecheck
Exit 0
```

Der danach frisch ausgeführte reale Check bleibt korrekt rot, jetzt ohne
D08–D12-/K1–K5-Projektionsfehlalarme:

```text
npm run check:canon
Exit 1 · 43 aktive Textrecords
```

Diese 43 Records waren die Implementierungsgrenze für die redaktionelle
Konsolidierung.

## 6. Quellen-GREEN vor unabhängigen Reviews

Die aktiven Dokumente, Konzeptdaten und rein redaktionellen Portaltexte wurden
auf Ubuntu 24.04.4, den geplanten 2×2-TB-Storagepfad, die vorhandene aber
pausierte Phase-1-Schale, Auth/DB-on + synthetic-only sowie den vollständigen
Medienausschluss konsolidiert. Veraltete Produktaktionen vor G0-SRV-12 wurden in
den betroffenen Darstellungen als pausiert gekennzeichnet. Task-6-Funktionalität
oder ein globaler Schalenbanner wurden nicht implementiert.

Der Realcheck sank nach dem ersten Editlauf von 43 auf drei rein syntaktisch noch
uneindeutige Medienzeilen und nach deren expliziter Formulierung auf null.
Frische Pre-Review-Evidenz:

| Befehl | Ergebnis |
|---|---|
| `node --experimental-strip-types --test scripts/canon-contract.test.mjs` | Exit 0, **17/17 PASS** |
| `npm run check:canon` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| `git diff --check` | Exit 0; ausschließlich erwartete LF/CRLF-Hinweise für vier bestehende Dateien |

Repositorydiff: 40 aktive Dateien, 717 Einfügungen / 293 Löschungen; keine
historische Analyse, Spec, externe Quelle, Plattformdatei oder Remote-Ref wurde
verändert. `K1-STATUS.md` führt Task 4 nun als `1257283` abgeschlossen und Task 5
als lokal grün, aber reviewoffen.

**Zustand vor Review:** Implementierung lokal GREEN; noch kein Task-5-PASS.
Kein Commit oder Push ist autorisiert.

## 7. Fokussiertes Spec-Review — FAIL und primäre Reproduktion

Der erste Reviewerstart endete ausschließlich mit einem externen HTTP-502-
Transportfehler und erzeugte kein Urteil. Derselbe read-only Reviewer wurde mit
unverändertem Paket fortgesetzt und lieferte **VERDICT: FAIL** mit fünf
blockierenden Findings:

| ID | Schwere | Befund | Primäre Reproduktion |
|---|---|---|---|
| K1-T5-SPEC-01 | P1 | Matrixprüfung verwendet importierten Ist-Kanon zugleich als Erwartung; zusätzliche Felder passieren, tiefe Arraykopie scheitert fälschlich | exakt: `[]`; Zusatzfeld: `[]`; strukturgleicher Clone: falscher `storagePlan`-Fehler |
| K1-T5-SPEC-02 | P1 | fehlende allowlistete aktive Datei wird übersprungen | synthetischer fehlender Pfad → `[]` |
| K1-T5-SPEC-03 | P1 | qualifizierte Medienverbote passieren; TURN/Aufzeichnung allein unsichtbar | vier Minimalzeilen jeweils `[]` |
| K1-T5-SPEC-04 | P2 | D13/D18/C02 weiterhin als „zur Bestätigung“ präsentiert | drei aktive Fundstellen dynamisch gelesen und bestätigt |
| K1-T5-SPEC-05 | P2 | O01 behauptet K1–K5 alle an; X-Legende nennt Prüfung statt akzeptiert | beide aktiven Zeilen dynamisch bestätigt |

Alle fünf Befunde sind **akzeptiert**. Die Korrekturschleife erhielt zuerst neue
Regressionstests. Frischer RED-Lauf:

```text
node --experimental-strip-types --test scripts/canon-contract.test.mjs
Exit 1 · 22 Tests · 17 PASS · 5 FAIL
```

Die fünf FAILs entsprechen eins zu eins SPEC-01…05; alle bisherigen 17 Tests
blieben grün. Qualitätsreview startet gemäß Spur B weiterhin nicht. Nächste
Stufe: minimale Korrektur, voller fokussierter GREEN-Lauf und scoped Spec-
Re-Review derselben Instanz.

## 8. Spec-Korrekturschleife — GREEN

Die fünf bestätigten Findings wurden minimal geschlossen:

- SPEC-01: unabhängiges `EXPECTED_K1_CANON`, tiefer Strukturvergleich, fehlende
  und unerwartete Keys rot; Mutationstest über jedes Feld einschließlich Array;
- SPEC-02: fehlende allowlistete aktive Dateien ergeben stabil `pfad: fehlt`;
- SPEC-03: Medienmenge umfasst Video, WebRTC, TURN, Recording/Aufzeichnung/
  Aufnahme; qualifizierte Verbote bleiben rot; beide aktiven Schwachtexte wurden
  auf vollständigen Ausschluss korrigiert;
- SPEC-04: C02/D13 und D18 in allen drei Präsentationen als gesetzt;
- SPEC-05: K1 default an / K2–K5 default aus sowie X akzeptiert explizit und
  deterministisch geprüft.

Frische Korrekturevidenz:

| Befehl/Probe | Ergebnis |
|---|---|
| Canon-Tests | Exit 0, **22/22 PASS** |
| `npm run check:canon` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| `git diff --check` | Exit 0; nur bekannte LF/CRLF-Hinweise |
| Matrix Minimalprobe | exakt `[]`, tiefer Clone `[]`, Zusatzfeld stabil rot |
| Missing-File-Minimalprobe | stabil `docs/DOES-NOT-EXIST.md: fehlt` |
| vier Medien-Minimalproben | alle stabil `webrtc_or_video` |
| Statusprojektionen | alle fünf kanonischen Zieltexte dynamisch vorhanden |

Nächster Schritt war ausschließlich der betroffene scoped Spec-Re-Review plus
notwendige Regression. Quality blieb bis zu dessen PASS gesperrt.

## 9. Scoped Spec-Re-Review — ein P1 offen, fokussiert nachkorrigiert

Der scoped Re-Review schloss SPEC-01, -02, -04 und -05. SPEC-03 blieb als P1
offen: Ein zeilenweiter Ausschlussmarker konnte eine positive Nachbarklausel
verdecken. Keine neuen korrekturinduzierten P0–P2-Befunde entstanden.

Die primäre Minimalprobe bestätigte alle drei Reviewerbeispiele zunächst
fail-open (`[]`). Drei Regressionen wurden ergänzt und fokussiert RED bewiesen.
Die Nachkorrektur entfernt den globalen Shortcut und prüft Medienausschlüsse nun
klausel- und vorkommensbezogen; gruppierte vollständige Ausschlüsse besitzen
einen eng definierten Pfad. Der reale Check deckte dabei zusätzlich vier bislang
syntaktisch mehrdeutige aktive Zeilen auf; sie wurden ohne Semantikänderung
explizit formuliert beziehungsweise für strukturierte `excluded`-Felder und
gesperrte ID-Listen eng unterstützt.

Frische Evidenz nach der fokussierten Nachkorrektur:

| Befehl/Probe | Ergebnis |
|---|---|
| fokussierte SPEC-03-Regression | Exit 0, 1/1 PASS |
| volle Canon-Suite | Exit 0, **22/22 PASS** |
| `npm run check:canon` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| `git diff --check` | Exit 0; nur bekannte LF/CRLF-Hinweise |
| drei gemischte Medienproben des Reviewers | alle stabil `webrtc_or_video` |

Zur finalen Spec-Gateentscheidung wurde dieselbe Instanz ausschließlich um die
Schließung von SPEC-03 gebeten; kein rekursiver neuer Reviewer wurde gestartet.

## 10. SPEC-03 Prefix-Pfad — erneut offen, systemisch gehärtet

Die Einzelprüfung bestätigte die drei vorigen Mischklauselproben als geschlossen,
fand jedoch denselben P1 im Prefix-Zweig: Ein Ausschlusswort vor der Mediengruppe
akzeptierte weiterhin aktivierende Suffixe. Die drei gelieferten Minimalproben
wurden primär als fail-open reproduziert, als neue Regressionen RED fixiert und
systemisch geschlossen:

- Prefix-Ausschluss gilt nur noch, wenn nach dem letzten Mediensubjekt
  ausschließlich enge, nichtsemantische Metadaten verbleiben;
- `aber`/`jedoch`/`dennoch` sowie Aktivierungs-, Nutzungs- und Erlaubnissprache
  machen die Klausel vor jeder Gruppenadjudikation rot;
- bestehende kanonische Gruppenformen, strukturierte `excluded`-Felder und
  gesperrte ID-Listen bleiben positiv getestet.

Frisch: fokussierte Regression 1/1, volle Suite 22/22, Realcheck, Typecheck,
K1-Control und Diff-Check grün; alle drei neuen Prefix-Proben melden stabil
`webrtc_or_video`. Dieselbe Instanz führt nun ausschließlich die finale
Prefix-Pfad-Schließungsprüfung aus. Blieb danach ein P0–P2 offen, war Task 5
zur Betreiberkonsolidierung zu stoppen statt weiterer Reviewrekursion.

## 11. Finaler Prefix-Check — SPEC-03 weiter offen, Konsolidierungsstopp

Die finale Einzelprüfung bestätigte die drei letzten Prefix-Proben als rot, fand
aber einen verbleibenden P1: Beliebiger Klammertext wurde als Metadaten entfernt,
sodass `Gesperrt: Video (später freigegeben).` noch passierte. Die primäre
Minimalprobe reproduzierte exakt `[]`; der Befund ist bestätigt.

Damit bleibt nach der dokumentierten Korrektur-/Re-Review-Folge ein P1 offen.
Gemäß `QUALITY-ROUTING.md` §4 stoppt Task 5 hier zur Betreiberkonsolidierung.
Keine weitere Validator- oder Testmutation, kein Quality-Review, kein Commit und
kein Push erfolgen ohne neue, ausdrücklich abgegrenzte Entscheidung. Der engste
Korrekturpfad wäre: Klammermetadaten nur als syntaktisch begrenzte ID-/
Quellenzitate zulassen, Zukunfts-/Freigabesprache rot testen und danach genau
eine finale SPEC-03-Schließungsprüfung derselben Instanz ausführen.

## 12. Betreiberfreigabe und engster Parenthesen-Fix

Der Betreiber wählte ausdrücklich „Engen Fix freigeben“: nur der beschriebene
Parenthesen-Fix plus eine letzte SPEC-03-Schließungsprüfung; weiterhin kein
Commit oder Push.

TDD-Nachweis und Implementierung:

- Reviewerprobe `Gesperrt: Video (später freigegeben).` vorab fokussiert RED;
- Klammerinhalt wird nicht mehr pauschal gelöscht, sondern ausschließlich dann
  als Metadaten akzeptiert, wenn er aus eng begrenzten ID-Zitaten (`D10`, `O08`,
  `WV03` usw.) beziehungsweise `Phase 9` besteht;
- positive Quellenprobe mit `(D10, Phase 9)` bleibt grün;
- Zukunfts-/Freigabesprache bleibt als semantischer Suffix sichtbar und damit
  rot.

Frisch: 2/2 fokussierte Parenthesenfälle, volle Suite 22/22,
`check:canon`, Typecheck, K1-Control und Diff-Check grün. Minimalprobe:
Zukunftsfreigabe → `webrtc_or_video`; enges ID-/Phase-Zitat → `[]`. Gemäß der
Betreiberfreigabe folgt jetzt genau eine finale SPEC-03-Schließungsprüfung
derselben Instanz.

## 13. Finale Spec-Schließungsprüfung — PASS

Die autorisierte letzte Einzelprüfung bestätigte:

- `Gesperrt: Video (später freigegeben).` wird abgelehnt;
- `Gesperrt: Video/WebRTC (D10, Phase 9)` wird akzeptiert;
- der reale Repositorykanon liefert `[]`.

`K1-T5-SPEC-03` ist **CLOSED**. **VERDICT: PASS.** Damit sind SPEC-01…05
geschlossen und die Vorbedingung des separaten Qualitätsreviews erfüllt. Erst
jetzt wurde eine frische, unabhängige Qualitätsinstanz mit dem finalen Diff, dem
Spec-PASS und den frischen Gates gestartet.

## 14. Qualitäts-/Securityreview — FAIL, acht Befunde bestätigt

Die frische Qualitätsinstanz lieferte **VERDICT: FAIL** mit vier P1- und vier
P2-Befunden. Alle wurden durch die primäre Instanz dynamisch reproduziert und
akzeptiert:

| ID | Schwere | Bestätigte Minimalreproduktion |
|---|---|---|
| K1-T5-QUAL-01 | P1 | zwei Prefix-Klammerformen mit Zukunfts-/Freigabesprache → `[]` |
| K1-T5-QUAL-02 | P1 | aktive + historische OS-Klausel sowie U+2028-Trennung → `[]` |
| K1-T5-QUAL-03 | P1 | mutierte H1-Lock-, K1-Switch-Default- und D10-Summary-Semantik → jeweils `[]` |
| K1-T5-QUAL-04 | P1 | `diagrams.tsx` nicht in `ACTIVE_FILES` |
| K1-T5-QUAL-05 | P2 | 49-Zeichen-, U+2011- und Wrap-Phase-1-Formen → jeweils `[]` |
| K1-T5-QUAL-06 | P2 | leeres Aggregat liefert 68 Fehler nur aus fehlenden Dateien; Matrix/ID/Projektion nicht nachgewiesen |
| K1-T5-QUAL-07 | P2 | K1-STATUS enthält 17/17, beide Reviews ausstehend und obsolete Task-3/Task-4-Resumeanweisungen |
| K1-T5-QUAL-08 | P2 | Lovable-UI führt X-Katalog und „Wort Phase 1“ weiter als offen |

Die Quality-Korrekturschleife begann test-first. Frischer RED-Lauf:

```text
node --experimental-strip-types --test scripts/canon-contract.test.mjs
Exit 1 · 27 Tests · 18 PASS · 9 FAIL
```

Die neun FAILs decken die acht Findings ab (QUAL-03 besitzt getrennte Record-
und Projektionsverträge); alle bisherigen Kernverträge bleiben grün. Nächster
Schritt: minimale Korrektur, volle lokale Gates und scoped Quality-Re-Review.
Kein Commit oder Push.

## 15. Quality-Korrekturschleife — GREEN

QUAL-01…08 wurden testgetrieben und fokussiert geschlossen:

- Prefix-Grammatik akzeptiert nur Ausschlusssyntax plus enge IDs/Zitate;
- OS-Historie wird pro Klausel adjudiziert, alle Standard-Line-Terminatoren
  werden normalisiert;
- unabhängige H-/K-Lockmaps, K-Switch-Defaults und abgeleitete D-Summary-Status
  werden validiert; freier Summary-Kern enthält keine Locksprache;
- `diagrams.tsx` ist aktive Quelle;
- Phase-Parser normalisiert Unicode-Hyphens und prüft gewrappte Records ohne
  48-Zeichen-Lücke;
- Aggregation besitzt benannte Validatorfamilien und Markerbeweis;
- operative K1-Chronologie ist auf 22/22, Spec-PASS und laufende Quality-
  Korrektur aktualisiert;
- Lovable-Offenliste enthält nur tatsächlich offene Punkte.

Frische Evidenz:

| Befehl/Probe | Ergebnis |
|---|---|
| Canon-Suite | Exit 0, **27/27 PASS** |
| `npm run check:canon` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| `git diff --check` | Exit 0; nur bekannte LF/CRLF-Hinweise |
| fokussiertes ESLint der Korrekturdateien | Exit 0 |
| volles `npm run lint` | erwartbare spätere Task-13-Baseline: 1 Fehler/5 Warnungen ausschließlich außerhalb der neuen Validatorlogik |
| QUAL-01-/02-/03-/05-Minimalproben | alle erwartungsgemäß rot |
| Allowlist/Aggregation | Diagramm erfasst; 8/8 Validatorfamilien mit Markern |
| K1-Status/Lovable | kanonische Zieltexte dynamisch bestätigt |

Nächster Schritt war der scoped Quality-Re-Review derselben frischen
Qualitätsinstanz, nur QUAL-01…08 plus notwendige Regression. Task 6 blieb bis
zum PASS gesperrt.

## 16. Scoped Quality-Re-Review — drei Befunde offen, Konsolidierungsstopp

Der Re-Review schloss QUAL-01, -03, -04, -05, -06, -07 und -08. Offen blieben
beziehungsweise entstanden:

- **QUAL-02 · P1:** OS-Mischklausel mit `, aber` wird noch zeilenweit als
  historisch befreit;
- **QUAL-09 · P1:** Phase-Parser ordnet ein fremdes Gate-„läuft“ Phase 1 zu und
  skaliert bei wiederholtem no-match quadratisch;
- **QUAL-10 · P2:** K1-STATUS-Anforderung ist synthetisch getestet, aber die
  reale Datei fehlt in `ACTIVE_FILES`.

Alle drei wurden primär bestätigt. Die valide Aussage „Phase 1 bleibt pausiert,
während G0-SRV-1 läuft“ wird fälschlich rot. Die no-match-Messung ergab
36,36 ms bei 4.000 gegenüber 139,88 ms bei 8.000 Wiederholungen. Der
K1-STATUS-Allowlist-Check ergab `false`.

Damit bleibt nach der regulären Quality-Korrekturschleife ein P1/P2-Satz offen.
Task 5 stoppt gemäß `QUALITY-ROUTING.md` §4 zur Betreiberkonsolidierung. Engster
Folgepfad: OS-Kontext an Adversativ-/Aktivprädikate binden, Phase-1-Status linear
pro Subjektklausel prüfen und K1-STATUS samt Repositoryassertion in die aktive
Allowlist aufnehmen; danach genau ein scoped Quality-Schließungsreview. Kein
Quality-PASS, Task 6, Commit oder Push ohne neue ausdrückliche Entscheidung.

## 17. Betreiberfreigabe und drei enge Quality-Fixes — GREEN

Der Betreiber gab ausdrücklich „Drei enge Fixes freigeben“ frei: exakt
QUAL-02, QUAL-09 und QUAL-10 plus ein letztes scoped Quality-Schließungsreview;
kein Commit oder Push.

Die neuen Verträge wurden vor Implementierung RED nachgewiesen (30 Tests,
26 PASS/4 FAIL; QUAL-09 besitzt Funktions- und Performanzfall). Danach:

- OS-Kontext trennt Adversativklauseln und macht aktive/produktive Prädikate
  unabhängig von historischen Markern rot;
- Phase-Status wird linear pro Subjektklausel über getrennte Phase-/Verbmarker
  geprüft; fremde Gate-Subjekte bleiben zulässig;
- `docs/project-control/K1-STATUS.md` liegt nun real in `ACTIVE_FILES` und wird
  durch die normale Repositoryprüfung kontrolliert.

Frische Evidenz:

| Befehl/Probe | Ergebnis |
|---|---|
| Canon-Suite | Exit 0, **30/30 PASS** |
| `npm run check:canon` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| `git diff --check` | Exit 0; nur bekannte LF/CRLF-Hinweise |
| fokussiertes ESLint | Exit 0 |
| OS-Mischprobe | stabil `debian_or_bookworm` |
| valide Phase-/Fremdgate-Probe | `[]` |
| Phase-No-Match 4k / 8k | 0,42 ms / 0,52 ms statt 36,36 ms / 139,88 ms |
| K1-STATUS-Allowlist | `true` |

Gemäß der Betreiberfreigabe folgt genau ein letztes, auf QUAL-02/-09/-10 und
Regression begrenztes Quality-Schließungsreview derselben Instanz.

## 18. Abbruchrekonstruktion, neue Konsolidierung und enger RED-Nachweis

Die Session endete vor dem angekündigten Quality-Schließungsreview. Eine frische
read-only Rekonstruktion am 2026-08-31 bestätigte den unveränderten HEAD
`1257283`, 46 ausschließlich unstaged Änderungen und die 30/30-Gates aus §17,
fand aber drei neue P1 sowie eine veraltete Statuschronologie:

- historische Debian-Klausel vor `, aber` konnte ein nachfolgendes aktives
  Prädikat verdecken;
- D01–D24-Locks wurden nicht unabhängig von der produktiven Lockmap exakt
  validiert;
- `docs/02-architecture.md` vermischte die Produktpause bis G0-SRV-12 mit einer
  pauschalen Pause jeder Serveraktivierung und widersprach damit der
  sequenziellen Gateautorität;
- K1-STATUS und dessen Assertion hielten 22/22 statt 30/30 und den offenen
  Quality-Abschluss fest.

Die primäre Instanz reproduzierte beide maschinellen P1-Befunde mit synthetischen
Minimalproben jeweils fail-open (`[]`) und bestätigte den Dokumentwiderspruch
direkt gegen `ground-zero/GATE-STATUS.md`. Der Betreiber gab anschließend
explizit den empfohlenen engen Fixpfad frei: nur diese P1-Befunde sowie
Statuschronologie/Live-Evidenz test-first korrigieren, danach frische Gates und
ein scoped Quality-Review; weiterhin kein Task 6, Commit oder Push.

Frischer fokussierter RED-Lauf um 03:23 CEST:

```text
node --experimental-strip-types --test --test-name-pattern="active OS claims|product pause distinct|current Task 5 chronology|authoritative D, H and K" scripts/canon-contract.test.mjs
Exit 1 · 4 Tests · 0 PASS · 4 FAIL
```

Jeder FAIL entspricht genau einem freigegebenen Vertrag; die Implementierung war
zu diesem Zeitpunkt noch unverändert. Nächster Schritt: minimale Korrektur bis
zum fokussierten GREEN, danach vollständige lokale Task-5-Gates.

## 19. Enger Abbruchkorrekturtranche — GREEN vor scoped Review

Die vier freigegebenen Verträge wurden minimal geschlossen:

- OS-Adversativkontexte behalten ein vollständig historisch markiertes
  Debian-/Bookworm-Subjekt für ein nachfolgendes aktives Prädikat gebunden; ein
  ausdrücklich neues Ubuntu-Subjekt bleibt zulässig;
- eine unabhängige exakte D01–D24-Lockmap ergänzt die bestehenden H-/K-Locks;
- die aktive Architektur trennt die Produktpause bis G0-SRV-12 von der allein in
  `ground-zero/GATE-STATUS.md` sequenziell autorisierten Servergatefolge;
- K1-STATUS und seine aktive Assertion nennen 31/31, Spec-PASS und das weiterhin
  offene scoped Quality-Schließungsreview.

Frische Evidenz um 03:30 CEST:

| Befehl/Probe | Ergebnis |
|---|---|
| fokussierte Korrekturregressionen inklusive OS-Positivkontrolle | Exit 0, **5/5 PASS** |
| volle Canon-Suite | Exit 0, **31/31 PASS** |
| `npm run check:canon` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| `git diff --check` | Exit 0; nur bekannte LF/CRLF-Hinweise |
| fokussiertes ESLint der beiden Canon-Dateien | Exit 0 |
| Arbeitsdiff | 46 tracked Dateien, 1.404 Einfügungen / 325 Löschungen, vollständig unstaged |

Die gezielten Tests beweisen den vormals fail-open OS-Fall und die D13-Lockmutation
nun rot, halten die historische-Debian-plus-neues-Ubuntu-Form grün und erzwingen
die getrennte Servergateaussage sowie aktuelle Chronologie. Task 6, Commit und
Push bleiben unverändert gesperrt. Nächster Schritt ist genau ein frisches,
scoped Quality-Schließungsreview dieses engen Korrekturdeltas plus notwendiger
Regression.

## 20. Scoped Quality-Schließungsreview — FAIL, zwei P1 bestätigt

Die frische, read-only Quality-Instanz prüfte ausschließlich den autorisierten
engen Korrekturtranche und lieferte **VERDICT: FAIL** mit zwei P1:

1. Die OS-Subjektbindung wertete jedes Ubuntu-Vorkommen als neues Subjekt und
   jedes Debian-Vorkommen als altes Subjekt. Dadurch blieben sowohl ein
   aktives Debian-Prädikat mit Ubuntu als Vergleichsobjekt fail-open als auch ein
   explizit neues Ubuntu-Subjekt mit späterem Debian-Objekt fail-closed.
2. Die positive Architekturanforderung verlangte Produktarbeit und G0-SRV-12 in
   räumlicher Nähe, aber nicht das Wort beziehungsweise die Semantik `pausiert`.
   Eine aktiv laufende Produktarbeit passierte deshalb.

Die primäre Instanz reproduzierte um 03:39 CEST alle drei Reviewerproben mit
synthetischen Tempdateien exakt:

```text
historisches Debian + „wird produktiv statt Ubuntu eingesetzt“ -> []
neues Subjekt „Ubuntu ist aktuell und ersetzt Debian“ -> debian_or_bookworm
„Weitere Produktarbeit läuft bereits vor G0-SRV-12 … GATE-STATUS.md“ -> []
```

Beide P1 sind bestätigt. Gemäß `QUALITY-ROUTING.md` §4 stoppt Task 5 erneut zur
Betreiberkonsolidierung. Kein weiterer Test-/Validatorfix, kein Task 6, Commit
oder Push erfolgt ohne neue eng abgegrenzte Freigabe. Der kleinste Folgepfad ist
eine syntaktisch enge Erkennung eines expliziten Ubuntu-Neusubjekts statt eines
beliebigen Ubuntu-Vorkommens sowie eine positive Pflicht für `pausiert` in der
Produktarbeitsaussage; danach fokussiertes RED/GREEN, lokale Gates und genau ein
scoped Schließungsreview.

## 21. Zweite Betreiberfreigabe und fokussierter RED-Nachweis

Der Betreiber gab den empfohlenen zweiten Korrekturtranche ausdrücklich frei:
exakt die zwei P1 aus §20 test-first schließen, danach fokussierte und vollständige
Gates sowie ein scoped Re-Review; weiterhin kein Task 6, Commit oder Push.

Drei gezielte Regressionen wurden ergänzt: OS-False-negative mit Ubuntu als
Vergleichsobjekt, OS-False-positive mit explizitem Ubuntu-Neusubjekt und eine
laufende statt pausierte Produktarbeit. Frischer RED-Lauf um 07:00 CEST:

```text
node --experimental-strip-types --test --test-name-pattern="explicit media exclusion|active OS claims|product pause distinct" scripts/canon-contract.test.mjs
Exit 1 · 3 Tests · 0 PASS · 3 FAIL
```

Alle drei FAILs entsprechen exakt den primär bestätigten Reviewerproben. Die
Implementierung war zu diesem Zeitpunkt seit §20 unverändert. Nächster Schritt:
explizites Ubuntu-Neusubjekt syntaktisch eng binden und die positive
Produktpausenanforderung zwingend an `pausiert` koppeln.

## 22. Zweiter enger Korrekturtranche — GREEN vor Re-Review

Die zwei P1 wurden minimal geschlossen:

- Ein Ubuntu-Vorkommen setzt den historischen Debian-Kontext nur noch zurück,
  wenn Ubuntu syntaktisch als explizites neues Subjekt beginnt. Ein späteres
  Ubuntu-Vergleichsobjekt verdeckt das geerbte Debian-Subjekt nicht. Ein im
  selben Kontext genanntes Debian ist nur dann ein zulässiges Objekt des neuen
  Ubuntu-Subjekts, wenn es eng durch `ersetzt`, `statt` oder `anstelle von`
  gebunden ist.
- Die positive Architekturanforderung verlangt nun ausdrücklich die Sequenz
  „Weitere Produktarbeit bleibt … G0-SRV-12 … pausiert“ vor der separaten
  Servergateaussage. Reine räumliche Nähe ohne Pause bleibt rot.

Frische Evidenz um 07:05 CEST:

| Befehl/Probe | Ergebnis |
|---|---|
| fokussierte OS-/Produktpause-Regressionen | Exit 0, **3/3 PASS** |
| volle Canon-Suite | Exit 0, **31/31 PASS** |
| `npm run check:canon` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| `git diff --check` | Exit 0; nur bekannte LF/CRLF-Hinweise |
| fokussiertes ESLint der beiden Canon-Dateien | Exit 0 |

Task 6, Commit und Push bleiben gesperrt. Nächster Schritt ist ausschließlich
das scoped Re-Review derselben Quality-Instanz für die zwei P1 aus §20 und die
notwendigen Regressionen.

## 23. Scoped Re-Review — FAIL, korrekturinduzierter P1 bestätigt

Das auf die zwei P1 aus §20 begrenzte Re-Review bestätigte die drei autorisierten
Regressionen als 3/3 geschlossen, fand aber einen korrekturinduzierten P1: Die
Ersetzungsausnahme bewies nur ein zulässiges Debian-Objekt und übersprang danach
jede weitere Debian-Nennung derselben Klausel.

Die primäre Instanz reproduzierte um 07:10 CEST die Reviewerprobe exakt:

```text
Debian Bookworm ist historisch, superseded und nicht ausführbar,
aber Ubuntu ersetzt Debian und Debian wird produktiv eingesetzt.
-> []
```

Erwartet ist `debian_or_bookworm`, weil nach dem zulässigen Ersatzobjekt ein
zweites aktives Debian-Subjekt folgt. Der P1 ist bestätigt. Gemäß
`QUALITY-ROUTING.md` §4 stoppt Task 5 erneut zur Betreiberkonsolidierung. Kein
weiterer Test-/Validatorfix, kein Task 6, Commit oder Push erfolgt ohne neue eng
abgegrenzte Freigabe. Der kleinste Folgepfad ist eine vorkommensbezogene
Adjudikation: ausschließlich die syntaktisch eng gebundene Debian-Nennung direkt
hinter `ersetzt|statt|anstelle von` als Objekt ausblenden; jede übrige
Debian-/Bookworm-Nennung derselben Klausel normal prüfen. Danach fokussiertes
RED/GREEN, lokale Gates und eine letzte scoped Schließungsprüfung.

## 24. Dritte Betreiberfreigabe und vorkommensbezogener RED-Nachweis

Der Betreiber gab ausdrücklich den empfohlenen letzten engen Pfad frei: exakt
die kombinierte Reviewerprobe test-first verankern, nur den direkt an
`ersetzt|statt|anstelle von` gebundenen stale-OS-Objektspan ausblenden und alle
übrigen Vorkommen normal adjudizieren; danach Gates und eine letzte scoped
Schließungsprüfung. Task 6, Commit und Push bleiben gesperrt.

Frischer RED-Lauf um 07:17 CEST:

```text
node --experimental-strip-types --test --test-name-pattern="active OS claims" scripts/canon-contract.test.mjs
Exit 1 · 1 Test · 0 PASS · 1 FAIL
```

Der einzelne FAIL stammt exakt aus der kombinierten Reviewerprobe; alle vorherigen
Fälle derselben Testgruppe liefen bis zu ihr durch. Die Implementierung war seit
§23 unverändert. Nächster Schritt: vorkommensbezogene minimale Korrektur.

## 25. Vorkommensbezogene Korrektur — GREEN vor letzter Schließungsprüfung

Die Ausnahmelogik arbeitet nun auf dem konkreten Kontexttext: Nur stale-OS-Spans,
die bei einem expliziten Ubuntu-Neusubjekt direkt hinter
`ersetzt|statt|anstelle von` stehen, werden aus einer separaten
Adjudikationskopie entfernt. `debian bookworm` wird als ein Objektspan entfernt;
jede weitere Debian-/Bookworm-Nennung bleibt erhalten und durchläuft die normale
Aktiv-/Historienprüfung.

Frische Evidenz um 07:23 CEST:

| Befehl/Probe | Ergebnis |
|---|---|
| fokussierte OS-Positiv-/Negativgruppe | Exit 0, **2/2 PASS** |
| volle Canon-Suite | Exit 0, **31/31 PASS** |
| `npm run check:canon` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| `git diff --check` | Exit 0; nur bekannte LF/CRLF-Hinweise |
| fokussiertes ESLint der beiden Canon-Dateien | Exit 0 |

Die kombinierte Reviewerprobe wird jetzt rot, während das einzelne zulässige
Ersatzobjekt und das explizite Ubuntu-Neusubjekt grün bleiben. Task 6, Commit und
Push bleiben gesperrt. Nächster Schritt ist ausschließlich die letzte scoped
Schließungsprüfung derselben Quality-Instanz für diesen P1 und notwendige
Regression.

## 26. Letzte scoped Quality-Schließungsprüfung — PASS

Dieselbe Quality-Instanz prüfte ausschließlich den vorkommensbezogenen P1 aus
§23, seine positive/negative OS-Regression und die korrekturinduzierte Fläche.
Ergebnis um 07:27 CEST:

```text
VERDICT: PASS
Occurrence-level P1 geschlossen · scoped OS-Regressions 2/2 PASS ·
keine korrekturinduzierte P0–P2-Regression gefunden
```

Damit sind der ursprüngliche Task-5-Spec-Review PASS und das separate
Quality-/Securityreview nach den dokumentierten, jeweils betreiberautorisierten
Korrekturschleifen abschließend PASS. Task 5 ist fachlich lokal abgenommen; der
Status-/Ledgerabschluss und seine frischen Gates werden noch mechanisch
nachgezogen. Ein Commit, Push oder Beginn von Task 6 ist dadurch nicht
autorisiert.

## 27. Mechanischer Ledgerabschluss — RED

Nach Quality-PASS wurde der aktive Chronologievertrag test-first von „Review
offen“ auf „scoped Quality-Schließungsreview PASS / Task 5 lokal abgeschlossen“
umgestellt. Frischer fokussierter Lauf um 07:31 CEST:

```text
node --experimental-strip-types --test --test-name-pattern="current Task 5 chronology" scripts/canon-contract.test.mjs
Exit 1 · 1 Test · 0 PASS · 1 FAIL
```

Der FAIL stammt erwartungsgemäß daraus, dass der Validator den nun veralteten
`offen`-Status noch akzeptiert. Nächster Schritt: Assertion und K1-STATUS exakt
auf den belegten PASS umstellen, anschließend alle lokalen Task-5-Gates frisch
wiederholen. Dies ist nur der mechanische Nachzug des bereits erteilten
Reviewurteils; Task 6, Commit und Push bleiben unautorisiert.

## 28. Mechanischer Ledgerabschluss und finale Task-5-Gates — GREEN

K1-STATUS und die aktive Chronologieassertion führen nun exakt 31/31,
Spec-Review PASS, scoped Quality-Schließungsreview PASS, keine offenen
P0–P2-Befunde und Task 5 lokal abgeschlossen. Der alte `offen`-Status sowie die
obsoleten E7-Quality-Resumeformulierungen sind negativ getestet beziehungsweise
fail-closed verboten. Task 6 ist ausdrücklich nicht begonnen; Task-5-Commit und
Push bleiben unautorisiert.

Frische Abschlussevidenz um 07:37 CEST:

| Befehl/Probe | Ergebnis |
|---|---|
| fokussierter Chronologievertrag | Exit 0, **1/1 PASS** |
| volle Canon-Suite | Exit 0, **31/31 PASS** |
| `npm run check:canon` | Exit 0 |
| `npm run typecheck` | Exit 0 |
| `npm run check:k1-control` | Exit 0 |
| `git diff --check` | Exit 0; nur bekannte LF/CRLF-Hinweise |
| fokussiertes ESLint der beiden Canon-Dateien | Exit 0 |
| Arbeitsdiff | 46 tracked Dateien, 1.429 Einfügungen / 325 Löschungen, vollständig unstaged |

**Task-5-Gateentscheidung: PASS.** Spec- und Qualityreview sind abgeschlossen;
alle lokal kontrollierbaren Task-5-Gates sind grün. Der nächste mögliche
Projektabschnitt ist Task 6, aber erst nach einer separaten Betreiberfreigabe.
Vorher ist ausschließlich eine ebenfalls separate Entscheidung über den
Task-5-Commit zulässig. Push und Publikations-Gate bleiben unverändert gesperrt.

## 29. Separat autorisierter lokaler Task-5-Commit

Der Betreiber gab nach dem vollständigen Task-5-PASS ausdrücklich den lokalen
Commit der exakt geprüften 46 tracked Dateien frei; Push und Task 6 blieben
unautorisiert. Alle 46 Dateien wurden explizit gestaged, der Index per
`git diff --cached --check` (Exit 0) und staged Stat (1.429/325) verifiziert und
anschließend committet:

```text
c00fd83cdea707d5ed6587d5703b35cef0460fe6
docs: reconcile active K1 product canon
```

Der Commit besitzt Parent `1257283`, enthält die vorgeschriebene Co-Author-Zeile
und exakt 46 Dateien. Frischer Post-Commit-Status um 07:45 CEST:

```text
codex/aurelia-konsolidierung ... origin/codex/aurelia-konsolidierung [ahead 2]
Working tree clean
```

Kein Push und kein Task 6 wurden ausgeführt. Das Publikations-Gate bleibt formal
blocked; der nächste Schritt benötigt erneut eine separate Betreiberfreigabe.
