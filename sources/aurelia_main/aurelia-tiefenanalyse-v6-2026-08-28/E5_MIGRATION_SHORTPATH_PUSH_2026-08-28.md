# E5-Evidenz: Verkürzter Migrationspfad + der eine autorisierte Push — 2026-08-28, Abend

**Diese Datei ist Ausführungsevidenz. Der Push wurde vom Betreiber freigegeben
(„Du hast meine Freigaben") und nach Plan `2026-08-27-aurelia-linux-workstation-
migration-recovery.md`, Tasks 8–9, im vom Betreiber entschiedenen verkürzten
Pfad ausgeführt. Kein Force, kein weiterer Ref.**

## 1. Entscheidungsgrundlage

1. **Infrastruktur-Klärung des Betreibers:** Windows-Workstation = nur
   Entwicklungsumgebung; Debian-Server beim Provider, ausschließlich RDP +
   WinSCP, keine USB-Medien; Server wird später mit GitHub gekoppelt.
   → In Memory `infrastruktur-topologie` und im Plan §Shortened path
   festgehalten.
2. **Betreiberangabe:** Lokale Sicherungen sind **vollständig inkl. `.git`**
   vorhanden. → Tasks 2–7 + 10 (Kapsel, Spiegel, Restaurationsnachweis,
   Cold-Backup) sind redundant und wurden per Plan-Amendierung **entfallen**
   gelassen („Shortened execution path", committed als `0414146`).
3. Übrig blieb der einzige Schritt mit zusätzlichem Replikationswert:
   **Task 9, der einzelne private Fast-Forward-Push.**

## 2. Ausführungsnachweis

| Schritt | Ergebnis |
|---|---|
| Task 1: Plan-Commit | `2f86d6b`, exakt 1 Datei, Parent `aec827f`, 4 Schritte grün |
| Plan-Amendierung | `0414146` „docs: authorize shortened migration execution path" (nur Plan-Dokument) |
| Task 8 S1: Identität | Origin/Push-URL kanonisch ohne pushurl/URL-Rewrites; `gh repo view` = `redshift-three67/aurelia\|true` |
| Task 8 S2: Fetch + FF | Nur `konsolidierung` gefetcht; Remote unverändert `029bdce`; HEAD strikter Nachfahre |
| Task 8 S3: Zustand | Zweig ✓ · Index leer · Dirty exakt **5** autorisierte Dateien · Scanner-Hashes `32c0b5b4…`/`81607e33…` ✓ · G0 untracked **15** ✓ · Branch-Set **5** ✓ · Worktrees **4**, prep/canon sauber · kein Stash · keine Fremd-Refs · **Ignored neu: 81 Dateien, Digest `f7a77c7b…`** (Gegenüber `52`/`afc5834d…` von 27.08. gewachsen durch heutige Analyseordner — laut Amendierung frisch fixiert, muss post-push identisch sein) |
| Task 8 S4: Graphvergleich | **Exakt die Plavorhersage:** `published_records=15, candidate_records=15, added_records=0, removed_records=0`, Kategorien identisch (`absolute_user_path 7 · credential_like 5 · env_or_key_material 1 · operational_identity 2 · unscannable 1`) — die 15 Commits führen keinen neuen Publikationsbefund ein |
| Task 8 S5: Ziel | `pushTarget = 04141462492ebf96c5c62841cb17812ea8ec2ad4` = Branch-Spitze, strikter Nachfahre |
| Task 9 S1: Push | Privatinachweis unmittelbar vorher; **isolierter Pre-Push-CAS-Hook** (validiert lokal/ref/remote-OID = `029bdce`, genau 1 Ref; SHA-256 `ebb28572fc73f1dd9ee30222cf2eb270179c476a4ddf1ee21c004906a0051038`); `git -c core.hooksPath=… push --porcelain origin refs/heads/codex/aurelia-konsolidierung:…` — **`029bdce..0414146`, Fast-Forward, kein `--force`, kein `--all`, kein weiterer Ref** |
| Task 9 S2: Rücklesung | `ls-remote` = `0414146…` ✓; frische Kontrolle aus Haupt-Checkout: alle anderen Refs (`main`, `vorbereitung`, `g0-governance`, `kanon`) unverändert |
| Task 9 S3: Beleg | Push-Receipt in lokalem Temp (außerhalb aller Worktrees), SHA-256 `2cac8441df816ae776a0759ab3efeb9cc6cc04ee82695bb307131882f6f50963` |
| Task 9 S4: Overlay | Post-Push: Index leer, Dirty weiterhin exakt 5 autorisierte Dateien, Scanner-Hashes unverändert, G0 weiterhin 15, Ignored weiterhin `81`/`f7a77c7b…` |

## 3. SPOF-Bilanz nach dem Push

- **Committierter Zustand (15 Commits): jetzt auf GitHub (privat) repliziert.**
- Verbleibend nur lokal: die 5 Dirty-Dateien (2 Scanner = dokumentiertes
  Overlay; 3 amendierte K1-Dokumente — inhaltlich in E3/E4 + Checkpoint
  beschrieben) und die 15 ungetrackten G0-Pläne — beides durch die
  vollständigen lokalen Dateisicherungen des Betreibers abgedeckt; Kapsel
  entfiel per Betreiberentscheidung.
- Publikations-Gate: weiter formal **blocked** und unverändert funktionsfähig
  (15 Records, keine neuen). Die 8-Bedingungs-Ausnahme des Migrationsdesigns
  wurde genau einmal, ref-scharf und nachweislich genutzt.

## 4. Nächste Schritte (unverändert)

1. Betreiberfreigabe für den **Overlap-TDD-Lauf** (namentlich; Plan amendiert,
   Digest `c8a54422…`).
2. Danach Spec- + Quality-Review des Umbaus → Task 3 beidseitig PASS →
   Tasks 4–14.
3. G0-SRV-0-Nachweis: wegen Provider-Server **remote-tauglich** entwerfen
   (z. B. Sicherung per WinSCP-Pull auf lokale verschlüsselte Medien +
   Restaurationsprobe lokal).
