# AURELIA — Handlungsempfehlungen & Betreiber-Leitfaden

Stand: 2026-08-25  
Projekt: AURELIA  
Fokus: Konkrete Handlungsanweisungen, Priorisierung und nächste Schritte  

---

## 1. Strategische Empfehlungen für den Betreiber

Nach gründlicher Prüfung aller Dokumente, Pläne und des aktuellen Codebestands empfehle ich Ihnen folgende **5 strategische Kernmaßnahmen**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                  5 STRATEGISCHE KERNEMPFEHLUNGEN                       │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Stop-Gate-Disziplin wahren  │ Keine Vorgriffe auf spätere Phasen;   │
│                                │ Phase 1 erst formal abschließen.      │
├────────────────────────────────┼───────────────────────────────────────┤
│ 2. Test-Suite instandsetzen    │ Modulauflösung in `app-data.test.ts`  │
│                                │ und Invarianten-Checker reparieren.   │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. Debian-Daemon-Schnittstelle │ Definition der IPC (Protobuf/UDS) für │
│    präzisieren                 │ `timerd`, `gpud` und `emitterd`.      │
├────────────────────────────────┼───────────────────────────────────────┤
│ 4. Backup-Restore automatisieren│ WV01 vor der ersten Art. 9 Akte       │
│                                │ als echten Test-Job etablieren.       │
├────────────────────────────────┼───────────────────────────────────────┤
│ 5. CopyGuard-Grammar sichern   │ GBNF-Grammars für das RAM-LLM nutzen, │
│                                │ um 100% HWG-Konformität zu garantieren│
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 2. Detaillierte Erläuterung der Empfehlungen

### 1. Striktes Festhalten an der Stop-Gate-Architektur
* **Warum wichtig?** In innovativen Projekten besteht die größte Gefahr im vorzeitigen Bauen von "schönen" Features (z.B. 3D-Visualisierungen oder Quanten-Modulen), bevor die Datenhaltung (RLS), Mandantenisolation und Ausfallsicherheit stehen.
* **Aktion:** Halten Sie den Grundsatz bei: **Erst wenn Phase 1 mit echten negativen Isolationstests grün ist, wird die erste Zeile von Phase 2 implementiert.**

### 2. Instandsetzung des lokalen Entwicklungsvertrags
* **Befund:** Der Aufruf von `npm test` scheitert aktuell an einem Modulauflösungsfehler (`@tanstack/react-start` in `client.server.ts`), und `npm run check:auth` benötigt den laufenden Dev-Server.
* **Aktion:** Bereinigen Sie als ersten Schritt in Phase 1 die Testkonfiguration in `package.json` und die Pfad-Aliase in `tsconfig.json`, damit `npm test`, `npm run typecheck` und `npm run check:canon` in CI/CD mit Exit-Code 0 durchlaufen.

### 3. Frühzeitige Vorbereitung der Systemd-Daemons auf Debian
* **Befund:** Node.js/Vite eignet sich perfekt für Web-UI und SSR, ist aber ungeeignet für 50ms-Echtzeittimer und Low-Level-CUDA-Streams.
* **Aktion:** Halten Sie an der Mehrprozess-Architektur fest:
  - `aurelia-timerd` in C++ oder Rust (als eigenständige Systemd-Unit)
  - `aurelia-gpud` in Python/C++ mit PyTorch/CUDA C API
  - `aurelia-emitterd` in Python/C++ mit PySerial
  - Kopplung an Node.js über lokale Unix Domain Sockets oder Redis Streams.

### 4. Backup & Desaster Recovery (WV01) als echtes Artefakt
* **Befund:** Der Single-Server-Ansatz (GPU Server M G1) ist kosteneffizient und pragmatisch für den Pilotbetrieb, erfordert aber einen absolut wasserdichten Wiederherstellungspfad.
* **Aktion:** Erstellen Sie ein Skript `scripts/disaster-recovery-test.sh`, das automatisiert eine leere Docker-Postgres-Instanz hochzieht, die verschlüsselten Backups einspielt und per SQL-Query validiert.

---

## 3. Sofortige nächste Schritte (Action Plan)

| Schritt | Zuständigkeit | Dauer | Ziel-Ergebnis |
|---|---|---|---|
| **Schritt 1** | Entwickler / Agent | 1-2 Tage | Ausführung des Kanonbereinigungs-Plans (`scripts/canon-contract.mjs`), Fix der Unit-Tests in `npm test`. |
| **Schritt 2** | Entwickler / Agent | 2-3 Tage | Implementierung automatisierter Mandanten-Isolationstests (2 Tenants, synthetisch). Abnahme von Phase 1! |
| **Schritt 3** | Betreiber / Architekt | 1 Tag | Formale Freigabe von Phase 1 und Startwort für Phase 2 (Praxisorganisation & WV01). |
| **Schritt 4** | Entwickler / Agent | 1 Woche | Erstellung des Praxis-Schemas (`0003_praxis.sql`), RLS-Policies und Envelope-Encryption-Prototyp. |

---

## 4. Fazit

Das Projekt **AURELIA** verfügt über ein **überragendes konzeptionelles Fundament**. Die intellektuelle Klarheit, mit der rechtliche Risiken (HWG/DSGVO/MDR) ausgeschlossen und technische Ressourcen (20 GB VRAM / RAM-CopyGuard / Monotonic Timers) budgetiert wurden, ist beispielhaft.

Mit dem vorliegenden **Phasen- und Subschritt-Umsetzungsplan** und den vorgeschlagenen **Ergänzenden Innovationen** ist das Projekt nicht nur vollständig machbar, sondern hat das Potenzial, einen neuen Qualitäts-, Transparenz- und Sicherheitsstandard im Bereich moderner Wellbeing- und Praxissoftware zu setzen.
