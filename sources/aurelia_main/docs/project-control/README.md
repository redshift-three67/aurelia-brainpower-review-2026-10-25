# AURELIA Project Control

Stand: 2026-08-25, Europe/Berlin

Dieser Ordner ist der lesende Einstieg für zusätzliche Entwickler und
Reviewer. Er fasst keine Produktregeln neu zusammen, sondern zeigt auf die
jeweils kanonische Quelle und hält externe Analysen nachvollziehbar getrennt.

## Aktueller Arbeitsstand

| Feld | Wert |
|---|---|
| Produktphase | Phase 1 „Gehäuse“ |
| Produktarbeit | pausiert |
| Aktives Gate | `G0-SRV-GROUND-ZERO` |
| Nächster Nachweis | `G0-SRV-0`: externes Backup plus Restore-Beweis |
| Zielbetriebssystem | Ubuntu Server 24.04.4 LTS amd64 plus minimales GNOME |
| Serveränderungen | noch nicht begonnen |
| Datenklasse | ausschließlich synthetisch |
| AUDIT-02 | pausiert bis zur Server-Gesamtabnahme |
| GitHub-Ziel | `redshift-three67/aurelia`, Branch `codex/aurelia-vorbereitung` |

## Verbindliche Lesereihenfolge

1. [`AGENTS.project.md`](../../AGENTS.project.md)
2. [`docs/STATUS.md`](../STATUS.md)
3. [Ground-Zero-Serverdesign](../superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md)
4. [Ground-Zero-Preflightplan](../superpowers/plans/2026-08-25-aurelia-ground-zero-preflight.md)
5. [`docs/09-roadmap.md`](../09-roadmap.md)
6. [`docs/26-wiedervorlage.md`](../26-wiedervorlage.md)
7. [`docs/20-freigabe.md`](../20-freigabe.md)
8. [`docs/10-decisions.md`](../10-decisions.md)

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

## Bekannte, bewusst noch nicht bereinigte Altverweise

Einige Portal-/Quellcodedateien nennen noch Debian/Bookworm und 2×1 TB. Diese
Darstellungen stammen aus dem vorigen Kanon und sind seit dem 25. August 2026
historisch. Verbindlich sind `AGENTS.project.md`, `docs/STATUS.md` und das
Ground-Zero-Serverdesign. Die sichtbare Portalbereinigung erfolgt nach der
Serverbaseline im wiederaufgenommenen AUDIT-02 mit automatischem Kanontest.

## Review- und Tokenstrategie

- Orchestrierung und endgültige Konsolidierung bleiben bei der primären
  AURELIA-Instanz.
- Externe Reviews werden nur für klar abgegrenzte, sanitierte Artefakte
  eingesetzt. Der Betreiber erhält dafür einen exakten Prompt und übermittelt
  das Ergebnis zurück.
- Reviewer erhalten niemals Secrets, Art.-9-Daten oder lokale
  Analyse-`source/`-Ordner.
- xHigh wird für Architektur-, Security-, Datenschutz-, Migrations- und
  finale Konsolidierungsentscheidungen verwendet.
- Günstigere Modelle sind für mechanische Inventarisierung, Formatprüfung und
  klar begrenzte Gegenleseaufgaben zulässig, wenn das Ergebnis anschließend
  primär verifiziert wird.
- Physische Serveraktionen, Destruktion und Gatefreigaben werden nicht an ein
  Reviewmodell delegiert.

## Änderungspflicht

Nach jedem bestandenen oder fehlgeschlagenen Ground-Zero-Gate werden mindestens
`docs/STATUS.md`, der aktive Runbook-Nachweis und dieser Einstieg aktualisiert.
Ein zusätzlicher Entwickler muss den Stand ohne Chatverlauf rekonstruieren
können.
