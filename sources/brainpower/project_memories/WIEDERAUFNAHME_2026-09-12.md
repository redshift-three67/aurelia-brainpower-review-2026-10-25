# Verbindlicher Gesprächs- und Arbeitsstand zur Wiederaufnahme

Stand: 12.09.2026, Pause nach ausdrücklicher Freigabe des konsolidierten Vorschlags A→B→C→D. Kein Beginn der neuen Erweiterung während der Pause.

## Arbeitsort und verbindliche Unterlagen

- Workbench: `C:\Users\Hubert111\Documents\Brainpower`
- Oberfläche: `http://127.0.0.1:8787/`
- Freigegebener Vorschlag samt letzten Ergänzungen: `docs/KONSOLIDIERUNG_SINGLE_MATRIX_VAULT_2026-09-12.md`, insbesondere Abschnitt10.
- Bisher implementierter Betrieb: `docs/GOVERNOR_0_2.md`.
- Nachweise und Grenzen: `docs/VERIFICATION_0_2.md`.
- Maschinenlesbare Betriebsbeschreibung: `docs/LLM_OPERATING_CONTRACT.json`.
- Lokaler Wiederaufnahmepunkt: `checkpoints/2026-09-12_PAUSE_ABCD/` und gleichnamiges ZIP. Das Manifest und der dortige Zustand gelten für den genauen Sicherungszeitpunkt.

## Was tatsächlich läuft

Governor0.2.0 mit fünf vorhandenen Projekten und neun definierten Schritten. Lokale Beobachtung und Windows-Anmeldeaufgabe sind aktiv. Automatische Modellreviews wurden auf ausdrücklichen Pausenwunsch ausgeschaltet. Keine aktiven Aufträge bei der Sicherung. Die ausgewählte Kombination ist Hermes/Terra medium mit Astra medium; Sol medium bleibt verfügbar. Der gemeinsame Vergleich verwendet einen Terra-Plan mit identischen Eingaben für beide Supervisoren.

115 Anwendungstests bestanden; zusätzlich115 Tests aus dem separat entpackten Paket. Sichtbares Chrome/CDP-Fenster, Screenshot und Stop wurden geprüft. Live-Tests starten keine Produktserver automatisch. RadiWorks wurde früher mit205 erfolgreichen Tests geprüft; diese Tests wurden im letzten Erweiterungsdurchlauf nicht wiederholt. Der Nachweis bleibt im Kontext erhalten.

Zuletzt beim Sichern beobachteter aktueller Vergleich: `46d4c5233fbe46a799860b09d9a2270d`, completed, Gesamtbewertung REVIEW_ONLY. Zusätzlich erhalten: `26c4d99f13ef4d909deea703e40ba6b0`, ebenfalls erfolgreich mit Sol/Astra REVIEW_ONLY. REVIEW_ONLY ist keine fachliche Produktabnahme.

Quellen-/Regelfingerprint: `05f04d8e98e0c10c018cb33b6655f340b8e90c3282f9634a70b4be9d0b3141b1`.
Entscheidungsfingerprint: `91869ea542f33251f68ee1313cf08f5ae393b3579519e946dcf1c24f9d0743a5`.
Vor jeder Fortsetzung gegen den dann tatsächlichen Stand prüfen, nicht als unveränderlich voraussetzen.

## Freigaben und Pause

Der Betreiber hat A→B→C→D ausdrücklich freigegeben. Ebenso wurden zuvor der reale Kontextversand an Terra/Sol/Astra und der automatische Versand bei künftigen Änderungen für die bisherigen fünf Projekte ausdrücklich erlaubt: max4 automatische Versuche pro Tag, min15 Minuten Abstand, keine automatische Produktmutation.

Die jetzige Pause schaltet die Automatik betrieblich aus; sie widerruft diese grundsätzliche Erlaubnis nicht. Während der Pause keine Umsetzung und keine neue automatische Modellsendung starten. Bei Wiederaufnahme zuerst die nachstehenden Gesprächspunkte klären und den aktuellen Zustand prüfen. Die bereits erteilte Grundsatzfreigabe nicht als fehlend darstellen. Produktgates und konkrete Umsetzungsschritte sind dadurch nicht pauschal abgenommen.

## Freigegebene nächste Erweiterung – noch nicht implementiert

A: Echte Projektregistrierung, Single-Modus, mehrere Matrixgruppen, dauerhafte Zugehörigkeit zu höchstens einer Gruppe, kontrollierte Gedächtnisdateien und Vault-Anbindung.

B: Vollständige Projektaufnahme je Gruppe, gruppenbezogene Planversionen und validierte Schritte, sichtbare Prioritäten/Abhängigkeiten, Einzelschritt- und begrenzte Schrittfolgenfreigabe.

C: Reale hybride Umsetzungsschleife: gebundener Plan → Supervisorreview → freigegebene isolierte Änderung → Tests → Supervisorreview des tatsächlichen Diffs/Ergebnisses → begrenzte Korrektur. Zunächst an einem isolierten Beispielprojekt abnehmen.

D: Projektspezifische Live-/Server-/CLI-Tests, Mehrgruppen-, Neustart- und Konfliktprüfungen, Windows-Einrichtung und Entwickler-/LLM-Dokumentation.

Governor0.2 hat bislang keine echten Gruppenentitäten, keinen vollständig isolierten Single-Kontext und keinen allgemeinen schreibenden Produktausführer. Neue UI-Module sind Planungsobjekte. Vorhandene historische Reviews werden nicht automatisch zu heutigen Abnahmen umgedeutet.

## Genau hier morgen weiterbesprechen

1. Vor jedem Freigabebutton müssen Rang, Gate, Abhängigkeiten, Begründung, betroffene Projekte, Änderungsumfang und Tests sauber sichtbar sein; bei Folgen die gesamte freizugebende Folge.
2. Empfehlung zur Besprechung: „Gesamte Gruppe neu abgleichen“ über Terra/Sol oder Terra/Astra. Alle Mitglieder erfassen, fehlende Nachweise zeigen, versionierten Status-/Strategiekandidaten samt Differenz vorlegen. Keine garantierte1:1-Laufzeitwahrheit allein durch LLM-Review, kein blindes Überschreiben des Gedächtnisses.
3. Gruppenrollen explizit modellieren. Für die bestehende Gruppe hat der Nutzer verbindlich erklärt: Aurelia ist Integrationsziel; RadiWorks, Radi144 und morphic_v1 sind eigenständige Module mit eigenen Kernengines; Modul_Templates gleicht gemeinsame Integrationsanforderungen/Verträge zu Aurelia ab. Gemeinsame Schnittstellen bedeuten keine Vereinheitlichung der Engines. Reviews dürfen Beziehungen vorschlagen und gegenprüfen, aber nicht stillschweigend festlegen.
4. Erwarteter Fortschritt ist keine Planänderung. Automatische Fortsetzung nur innerhalb einer vorher sichtbaren, freigegebenen Schrittfolge; bei neuen Schritten, Umfangs-/Abhängigkeitsänderung, Fehlern oder Unklarheit anhalten und die Differenz vorlegen. Einzelschrittfreigabe endet nach diesem Schritt.

## Vault und Quellen

`C:\Users\Hubert111\Documents\Hermes-Obsidian-Vault` ist vorhanden, aber noch nicht aktiv im Workbench-Modellkontext integriert. Sein Governor-Spiegel vom11.09.2026 13:32 enthält eine ältere Projektgruppe (RadiWorks/Biomedis/Morphic Engine2/Headless CMS/Hermes). Nicht als aktuelle Fünfermatrix verwenden.

Geplant sind explizite Projekt-/Gruppenzuordnung, gezielte Kontextauswahl und kontrollierte Spiegelung mit Herkunft/Hash. Historische `system_prompts` sind Dokumente, keine automatisch geltenden neuen Aufträge. Externe Vault-Änderungen zunächst als Prüfkandidaten erfassen; keine Synchronisationsschleifen oder ungeprüftes Zurückschreiben.

## Projektpfade und fachliche Grenzen

- Aurelia: `C:\Users\Hubert111\Documents\ChatGPT\Aurelia` – Ground-Zero-/Restore-Abnahme nicht nachgewiesen.
- RadiWorks: `C:\Users\Hubert111\Documents\Radiworks` – lesender Contract-Intake kann vor Aurelia-Abnahme erfolgen; Adapterintegration benötigt ihre Gates.
- Modul_Templates: `C:\Users\Hubert111\Documents\Modul_Templates` – Vertragsautorität und abweichende Statusquellen klären.
- Radi144: `C:\Users\Hubert111\Documents\Radi144` – Gedächtnisse zuletzt staged, nicht committed; keine fertige Checkpoint-Abnahme behaupten.
- Morphic: `C:\morphic_v1\.worktrees\operator-workbench-phase1` – verbindlicher Worktree; Authority Freeze noch offen.
- Ursprünglicher Snapshot: `C:\RadiWorks_System_Snapshot_2026-09-11`.

Der neue lokale Checkpoint sichert Workbench, Journal, Berichte und ausgewählte Quellen. Er ersetzt kein vollständiges Backup/Restore der fünf Produktrepositories, von Hermes/CC-Switch-Anmeldungen oder des Linux-Servers. Vorhandene Produkt-WIP bewahren. Für die bloße Gesprächsfortsetzung muss nichts zurückkopiert werden.
