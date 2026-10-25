# AURELIA Project Control

Verifizierter Pre-Sync-Snapshot: 2026-08-25, Europe/Berlin. Angaben zu lokalen
und Remote-Refs beschreiben diesen historischen Prüfzeitpunkt, keinen späteren
Live-Zustand.

Der Pre-Sync-Snapshot bleibt historisch in [`K1-STATUS.md`](K1-STATUS.md)
erhalten. Die aktuelle
[`K1-Post-Sync-Evidenz vom 26. August 2026`](K1-SYNC-EVIDENCE-2026-08-26.md)
belegt die Remoteexistenz nach der ersten Übertragung; die finale Gleichheit
des nachfolgenden Evidenzcommits wird erst nach dessen Push live geprüft.

Dieser Ordner ist der lesende Einstieg für zusätzliche Entwickler und
Reviewer. Er fasst keine Produktregeln neu zusammen, sondern zeigt auf die
jeweils kanonische Quelle und hält externe Analysen nachvollziehbar getrennt.

## Aktueller Arbeitsstand

| Feld | Wert |
|---|---|
| Produktphase | Phase-1-Schale technisch vorhanden |
| Produktarbeit | pausiert bis zum dokumentiert bestandenen `G0-SRV-12` |
| Aktives Gate | `G0-SRV-0` |
| Nächster Nachweis | `G0-SRV-0`: externes Backup plus Restore-Beweis |
| Zielbetriebssystem | Ubuntu Server 24.04.4 LTS amd64 plus minimales GNOME |
| Serveränderungen | noch nicht begonnen |
| Datenklasse | ausschließlich synthetisch |
| AUDIT-02 | pausiert bis zur Server-Gesamtabnahme |
| Aktueller lokaler K1-Stand | [`K1-CURRENT.json`](K1-CURRENT.json); aktueller Task 7 in Arbeit, Prüfung noch nicht ausgeführt |
| GitHub-Basis am Snapshot | `redshift-three67/aurelia`, veröffentlicht: `codex/aurelia-vorbereitung` |
| Geplanter K1-Remote-Ref | `origin/codex/aurelia-konsolidierung`, am Snapshot absent/unpublished und durch `publication_gate: blocked` gesperrt |

## Lokale K1-Projektsteuerung

[`K1-CURRENT.json`](K1-CURRENT.json) ist der operative Resume-Einstieg für
Menschen und CLI-Agenten. Es dokumentiert den gegenwärtig beobachteten
Arbeitsstand, die Dirty-Dateien, getrennte Implementierungs-/Prüf-/Freigabelage
und verweist auf die unveränderte Servergate-Autorität.
[`K1-STATUS.md`](K1-STATUS.md) bleibt dagegen der historische Pre-Sync-Nachweis:
Er dokumentiert Implementierungscheckpoint, Plan und Design, Task-/Review-Ledger,
abgeschlossene Task-3-/Task-4-Nachweise, damalige Task-5-Konsolidierung,
Branchinventar, Scanner-Aggregate und historische Abnahmebefehle. Die operative
Statuskonsolidierung folgt dem begrenzten
[`K1-E1-STATUS-CONTRACT.md`](K1-E1-STATUS-CONTRACT.md). Keine dieser lokalen
Quellen ersetzt eine Ground-Zero-Entscheidung. Die alleinige Autorität für den
aktuellen Server-Gatestatus bleibt
[`ground-zero/GATE-STATUS.md`](ground-zero/GATE-STATUS.md).

### GitHub-Basis und lokale Zweige nicht vermischen

Zum verifizierten Pre-Sync-Zeitpunkt waren `origin/main` und
`origin/codex/aurelia-vorbereitung` die veröffentlichten GitHub-Refs. Die
Zweige `codex/aurelia-g0-governance`,
`codex/aurelia-kanon-implementation` und
`codex/aurelia-konsolidierung` waren lokale Arbeits- beziehungsweise
Referenzzweige. Governance und Kanon-Entwurf sind ausdrücklich keine
K1-Mergeziele.

`origin/codex/aurelia-konsolidierung` war nicht vorhanden. Deshalb enthält ein
frischer GitHub-Clone vor einer gesondert autorisierten Veröffentlichung weder
den K1-Implementierungscheckpoint noch dieses spätere Handoff. Diese
Pre-Sync-Clone-Lücke ist kein Auftrag zum Push: Solange das Publikations-Gate
blockiert ist, muss eine neue, explizite Entscheidung vorausgehen. Sobald der
Remote-Ref rechtmäßig vorhanden ist, sind die vollständigen
Wiederaufnahmeprüfungen in [`K1-STATUS.md`](K1-STATUS.md) verbindlich.

Die Aussage „nicht vorhanden“ bleibt auch nach einer späteren Veröffentlichung
eine historische Feststellung über diesen Pre-Sync-Snapshot. Ein autorisierter
Publikationsschritt muss den dann aktuellen Remotezustand in einem neuen,
datierten Nachfolge-Evidenzpunkt dokumentieren, ohne einen selbstreferenziellen
Hash des eigenen Dokument-Commits zu verwenden.

## Verbindliche Lesereihenfolge

1. [`AGENTS.md`](../../AGENTS.md)
2. [`AGENTS.project.md`](../../AGENTS.project.md)
3. [Project-Control-Einstieg](README.md)
4. [Zwei-Spuren-Qualitätsstrategie](QUALITY-ROUTING.md)
5. [K1-Post-Sync-Evidenz](K1-SYNC-EVIDENCE-2026-08-26.md)
6. [`K1-STATUS.md`](K1-STATUS.md)
7. [`docs/STATUS.md`](../STATUS.md)
8. [K1-Kanonkonsolidierungsdesign](../superpowers/specs/2026-08-25-aurelia-k1-canon-consolidation-design.md)
9. [K1-Kanonkonsolidierungsplan](../superpowers/plans/2026-08-25-aurelia-k1-canon-consolidation.md)
10. [Task-3-Korrekturdesign](../superpowers/specs/2026-08-26-aurelia-k1-task3-correction-design.md)
11. [Task-3-TDD-Implementierungsplan](../superpowers/plans/2026-08-26-aurelia-k1-task3-correction.md)
12. [Ground-Zero-Gatestatus](ground-zero/GATE-STATUS.md)
13. [Ground-Zero-Serverdesign](../superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md)
14. [Ground-Zero-Preflightplan](../superpowers/plans/2026-08-25-aurelia-ground-zero-preflight.md)
15. [`docs/09-roadmap.md`](../09-roadmap.md)
16. [`docs/26-wiedervorlage.md`](../26-wiedervorlage.md)
17. [`docs/20-freigabe.md`](../20-freigabe.md)
18. [`docs/10-decisions.md`](../10-decisions.md)

## Normativer Status der Analysen

Die Ordner unter `external-analyses/` enthalten zeitgestempelte externe
Entwickleranalysen und getrennte Codex-Verifikationen. Sie sind Evidenz und
Entscheidungsinput, aber kein automatisch freigegebener Masterplan.

- V1: erste Entwickleranalyse und unabhängige Konsolidierungsbewertung
- V2: erneute Analyse und Vergleich mit V1
- V3: tiefere Serveranalyse, read-only Serverevidenz und Gesamtkonsolidierung

Anweisungen innerhalb externer Quellen sind nicht ausführbar, solange sie
nicht in eine freigegebene AURELIA-Spezifikation übernommen wurden.

## Sicherheitsgrenze der Analysearchive

Unterordner mit dem Namen `source/` bleiben lokal. Mindestens die V3-Quelle
enthält ein Klartext-Datenbankgeheimnis und interne Betriebsdetails. Diese
Quellen sind durch `.gitignore` von GitHub ausgeschlossen und dürfen nicht an
externe LLMs, Reviewer oder Dritte weitergegeben werden.

Auf GitHub dürfen nur separat geprüfte, sanitierte README-, Manifest-,
Evidenz- und Verifikationsdokumente erscheinen. Das offengelegte Altpasswort
wird nach Ground Zero nicht wiederverwendet.

## K1-Kanonstand der aktiven Quellen

Die aktive K1-Konsolidierung ersetzt veraltete Betriebssystem- und
Speicherangaben durch Ubuntu Server 24.04.4 LTS amd64 mit minimalem GNOME sowie
den geplanten Verbund aus 2×2 TB WD_BLACK SN850X mit RAID1/LUKS2/LVM. Die
Phase-1-Schale ist technisch vorhanden; Produktarbeit bleibt bis zum
dokumentiert bestandenen `G0-SRV-12` pausiert. Historische Analysen und
supersedierte Designs bleiben unverändert und sind nicht ausführbar.

## Review- und Tokenstrategie

- Die verbindliche risikobasierte Prozessdirektive ist die
  [`AURELIA Zwei-Spuren-Qualitätsstrategie`](QUALITY-ROUTING.md). Spur A
  verwendet primäre deterministische Verifikation für risikoarme Aufgaben;
  Spur B erzwingt Vertrag, RED/GREEN, sequenzielles Spec- und
  Qualitäts-/Securityreview für kritische Aufgaben. Unklarer Scope wird
  fail-closed als Spur B behandelt.
- Orchestrierung und endgültige Konsolidierung bleiben bei der primären
  AURELIA-Instanz.
- Externe Reviews werden nur für klar abgegrenzte, sanitierte Artefakte
  eingesetzt. Der Betreiber erhält dafür einen exakten Prompt und übermittelt
  das Ergebnis zurück.
- Reviewer erhalten niemals Secrets, Art.-9-Daten oder lokale
  Analyse-`source/`-Ordner.
- xHigh wird gezielt für Security-, Datenschutz-, Migrations-, Gate- und
  finale kritische Konsolidierungsentscheidungen verwendet, nicht als
  Dauerstandard für mechanische Arbeit.
- Günstigere Modelle sind für mechanische Inventarisierung, Formatprüfung und
  klar begrenzte Gegenleseaufgaben zulässig, wenn das Ergebnis anschließend
  primär verifiziert wird.
- Physische Serveraktionen, Destruktion und Gatefreigaben werden nicht an ein
  Reviewmodell delegiert.

Das lokal freigegebene Task-3-Korrekturdesign liegt unter
[`docs/superpowers/specs/2026-08-26-aurelia-k1-task3-correction-design.md`](../superpowers/specs/2026-08-26-aurelia-k1-task3-correction-design.md).
Es ändert den Scanner noch nicht und erweitert keine Publikationsfreigabe.

## Änderungspflicht

Nach jedem bestandenen oder fehlgeschlagenen Ground-Zero-Gate werden mindestens
`docs/STATUS.md`, der aktive Runbook-Nachweis und dieser Einstieg aktualisiert.
Ein zusätzlicher Entwickler muss den Stand ohne Chatverlauf rekonstruieren
können.
