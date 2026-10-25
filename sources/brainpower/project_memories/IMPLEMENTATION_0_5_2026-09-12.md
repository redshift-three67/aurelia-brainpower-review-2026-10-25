# Fortsetzungsstand Governor 0.5 – 12.09.2026

Aktuell maßgeblich: docs/GOVERNOR_0_5.md, docs/RESTARBEITEN_0_5.md und docs/LLM_OPERATING_CONTRACT.json. Der Nutzer hat Fortsetzung der Empfehlungen autorisiert; ältere Pausen sind für diese Umsetzung aufgehoben. Grundsatzfreigabe A–D nicht erneut erfragen.

Implementiert und geprüft: lokale quellengebundene Aufnahmeentwürfe, Einbeziehung aktueller unbestätigter Entwürfe in scoped Modellreviews, explizite unveränderliche Strategieübernahme, UI-Herkunft und Aktualitätsprüfung, interner Schutz gegen parallel neue Aufnahmen. Zusätzlich fehlenden Entscheidungsfingerprint im historischen Gruppenpfad korrigiert: vorhandene Berichte werden nun wie in der Hauptmatrix erkannt.

343 Tests: 341 bestanden, zwei Windows-Symlinktests ausgelassen. JS-Syntax und isolierte Browserbedienung geprüft. Reale Vergleichsrunde r2: `1b278124a55f4effb8864ab05a1f0b9d`; Terra/Hermes zero-tool, Sol und Astra erfolgreich, beide REVIEW_ONLY mit weiterhin offenen Nachweisen. Keine Produktabnahme oder Implementierungsfreigabe. Erste Vergleichsrunde ist wegen korrigiertem Gruppen-Matrixkontext historisch. Hauptmatrix verwendet dieselbe 200-Auftrags-Historie wie Gruppenreviews statt nur der 40 UI-Aufträge.

Hauptdienst: http://127.0.0.1:8787, Version 0.5.0. Ausgewählt Sol; lokale Beobachtung an; automatische Modellreviews aus. Fünf aktuelle, unbestätigte Aufnahmeentwürfe in der Live-Datenbank (r2). Noch kein angenommener Gruppenstrategieplan. Externe Produktdateien wurden durch diese Umsetzung nicht geändert.

Nächste Betreiberprüfung: vier Aufnahmefelder je Projekt über „Aufnahmeentwurf laden“ prüfen und bestätigen; danach vorhandenen Quellenabgleich unter Governance annehmen, wenn zutreffend. Der vorhandene Bericht `5e718d54b8fe4e49afb37e2f39795bd7` ist weiterhin quellengebunden; nicht unnötig neu erzeugen. Lesbare Zusammenfassung artifacts/QUELLENABGLEICH_0_5.md. Anschließend hybrider Planentwurf und ausdrückliche Strategieübernahme. Nicht automatisch als Betreiber annehmen.

Priorität danach: allgemeine Produktausführungsadapter und schrittspezifische Freigaben, Live-/Testnachweise, begrenzte Reparaturen, verifizierter Fortschritt, freigegebene Folgen, Mehrgruppen-/Vault-Gesamtabnahme, erst danach vollständiges Windows-Erstsetup einschließlich Hermes. Der vorhandene Installer ist weiterhin Workbench-Setup, keine auf fremder Windows-Instanz vollständig abgenommene Gesamtinstallation.

Belege: artifacts/unit-tests-v05-release.txt; artifacts/strategy-live-final-verification.json; artifacts/intake-review-live-result-r2.json; artifacts/intake-review-preflight-context-r2.json; artifacts/intake-drafts-live-receipts-2026-09-12-r2.json; artifacts/HYBRID_REVIEW_0_5.md. Vor Upgrade gesicherte DB: artifacts/pre-strategy-upgrade/journal.db. Frühere D:-Sicherung enthält 0.4; neuer Workspace-Checkpoint: checkpoints/2026-09-12_GOVERNOR_0_5. Quellpaket: dist/GovernorWorkbench-0.5.0-Windows.zip.

Wichtig: niemals Store auf laufender runtime/journal.db initialisieren; vorhandene Aufträge würden unterbrochen markiert. SQLite nur read-only oder laufende API benutzen. Weder Produktrepos noch Profile-Git-Root breit bearbeiten. Modellantworten bleiben Daten. Hashrollen und aktuelle-byte/Index/HEAD-Nachweise getrennt behandeln.
