# Vollständig kopierbarer Prompt für die nächste Session

Kopiere ab der nächsten Trennlinie vollständig in eine neue Hermes-Session.

---

Arbeite im Repository `C:\morphic_v1\.worktrees\operator-workbench-phase1` auf Branch `operator-workbench-phase1`. Antworte auf Deutsch und arbeite konservativ, testgetrieben, hashgebunden und ohne Scope-Creep.

Lies zuerst vollständig, in dieser Reihenfolge:

1. `CLAUDE.md`
2. `docs/session-handoffs/2026-07-15_054538_f5a_pause/SESSION_HANDOFF.md`
3. `docs/session-handoffs/2026-07-15_054538_f5a_pause/VERIFICATION_EVIDENCE.md`
4. `PROJECT_MEMORY/00_CURRENT_STATE.md`
5. `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md`
6. `docs/status/2026-07-13-feedback-f-umsetzungsplan-kurz.md`
7. `docs/status/2026-07-12-gesamtstruktur-fortschritt.md`
8. die vollständige aktuelle Reviewsummary `C:\Users\Hubert111\AppData\Local\hermes\cache\delegation\subagent-summary-1-20260715_015628_277528.txt`

Verifiziere danach read-only:

- `git branch --show-current` muss `operator-workbench-phase1` ergeben;
- HEAD war beim Handoff `619a1f5485a151816e32732929a6a823839ccb57`;
- gezielten Git-Status und SHA-256 des F5-A-Scopes;
- Ports 8000 und 8090, ohne Dienste zu verändern;
- `config/source_repositories.json` muss weiterhin SHA-256 `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3` besitzen;
- `data/remedies.db` muss weiterhin SHA-256 `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` besitzen.

Aktueller formaler Zustand:

- F3 GO;
- F4 GO;
- F5-A technisch weitgehend GREEN, formal NO-GO;
- F5-B gesperrt;
- Feedback f insgesamt NO-GO bis F8;
- keine Catalog-Promotion, kein Publish, kein Activate, keine Runtimefreigabe, kein Netzwerk und kein lokales Source-Daten-I/O.

Letzter ausgeführter technischer Stand:

- Fokus `103 passed, 1 skipped`;
- Adminmatrix `426 passed, 6 skipped`;
- breite Suite `910 passed, 8 skipped` plus exakt 14 bekannte Baselinefehler;
- Ruff, `py_compile`, `git diff --check` PASS;
- Top-5 zuletzt vor dem abschließenden bool-sicheren `record_count`-Patch `1 passed in 94.87s`; daher nach den nächsten Patches zwingend erneut ausführen.

Die zwei offenen P2 aus dem jüngsten driftfreien Data-/CLI-/Docs-Review `deleg_11f0ea26` sind verbindlich zu schließen:

1. Der Maschinenvertrag und die öffentliche CLI verwenden noch missverständliche Promotion-Begriffe (`morphic_source_data_promotion_ledger`, `promoted_at`, `data-promote`), obwohl F5-A nur lokale Konsistenz dokumentiert. Führe zuerst eine read-only Usage-/Artefakt-Inventur durch. Ergänze dann RED-Verträge und führe einen neuen versionierten Consistency-Vertrag ein. Alte Namen dürfen nicht still umgedeutet werden; sie müssen explizit abgelehnt oder eindeutig deprecatet werden. Keine produktiven Ledgerdaten still migrieren.
2. `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md:592-604` ist veraltet und weist F5.1 fälschlich als neu zu beginnenden Block aus. Korrigiere den Vollplan auf: F5-A = F5.5/F5.4/F5.1 technisch umgesetzt, formal NO-GO; jetzt P2 schließen, Matrix, Freeze, Doppelreview, Dokumentation, dokumentationsgebundener Doppelreview und Post-State; F5-B gesperrt.

Arbeite strikt RED→GREEN:

1. Usage und reale Ledgerartefakte read-only inventarisieren.
2. Exakte RED-Verträge für neues Schema, Zeitfeld, CLI-Namen/Hilfe und Legacy-/Aliasverhalten schreiben.
3. RED-Lauf bestätigen.
4. Kleinsten konsistenten GREEN-Patch implementieren.
5. Vollplan korrigieren.
6. Vollständige Matrix ausführen:
   - F5-A-Fokus mit `-W error`;
   - Adminmatrix mit `-W error`;
   - gesamte Suite;
   - Top-5 mit `-W error`;
   - Ruff;
   - `py_compile`;
   - `git diff --check`.
7. Bei der breiten Suite sind ausschließlich die bekannten 14 Baselinefehler zulässig: ein datumsabhängiger Consent-Test und 13 bestehende HTTP-429-/Rate-Limit-Tests. Jede Abweichung stoppt das Gate.
8. Statusdokumente mit den tatsächlich neu gemessenen Zahlen aktualisieren.
9. Finalen Code-/Test-/Dokumentscope plus Git-Statusfingerprint und SHA-256 einfrieren.
10. Zwei unabhängige read-only technische Abschlussreviews auf exakt diesem Freeze einholen. Beide müssen Start-/Endhashes vergleichen und F5.5, F5.4 und F5.1 separat mit ausdrücklichem APPROVE bewerten.
11. Bei jedem Finding oder Patch Matrix, Freeze und beide Reviews wiederholen.
12. Erst danach F5-A-Gate-Record und alle Statusauthorities final aktualisieren.
13. Zwei dokumentationsgebundene Reviews auf dem vollständigen finalen Code-/Dokumentsnapshot einholen. Jeder Patch invalidiert beide.
14. Externe F5-A-Post-State-ShadowCopy unter `E:\mprphic_v1_Backups` erzeugen und jedes Manifestobjekt aus dem Ziel vollständig rückverifizieren.
15. Erst danach F5-A formal GO setzen. F5-B vorher nicht beginnen.

Verbindliche Grenzen:

- Kein Serverstart und kein Netzwerkzugriff.
- Port 8000 freihalten; bestehenden Dienst auf 8090 nicht stören.
- Kein Commit, Push, Staging, Reset oder Clean.
- Den stark dirty/untracked Worktree nicht pauschal bereinigen.
- `config/source_repositories.json` und `data/remedies.db` nicht mutieren.
- Keine Credentials oder `.env`-Dateien lesen oder ausgeben.
- Point-in-time-`local_path`-Validierung nicht fälschlich als sicherer späterer Windows-Dateiconsumer darstellen. Ein späterer Consumer braucht handle-basierte Prüfung und immutable Snapshotkopie.
- Das Ledger hat keinen externen Tamper-Anker; Replay-Garantie nur im intakten aktuellen Ledger.
- F3 und F4 bleiben geschlossen und dürfen nicht wieder geöffnet werden.

Nutze `C:\morphic_v1\.venv\Scripts\python.exe` beziehungsweise unter Git-Bash `/c/morphic_v1/.venv/Scripts/python.exe`; setze `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1` und `OPENBLAS_NUM_THREADS=1`.

Beginne mit read-only Discovery und berichte knapp den verifizierten Wiederanlaufstand, bevor du die RED-Verträge schreibst. Frage nicht nach bereits dokumentiertem Kontext. Fahre danach autonom bis zum nächsten echten Stop-Gate fort.
