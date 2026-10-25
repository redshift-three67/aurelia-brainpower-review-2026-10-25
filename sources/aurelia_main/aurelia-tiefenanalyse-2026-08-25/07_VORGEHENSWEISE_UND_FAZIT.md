# 07 — Vorgehensweise-Empfehlung & Fazit (2026-08-25)

---

## 1. Meine empfohlene Vorgehensweise (als Architekt)

### Grundsatz: „Vertrag vor Bau, Test vor Vertrag-Ende, Gate vor Phase"
Die Verfassung liefert bereits die richtige Leitidee. Ich würde die Umsetzung mit folgender Arbeitsweise koppeln:

1. **Erst Reparatur, dann Neubau (Diese Woche).**
   Die verifiziert rote Qualitätsschleife (`npm test`, `typecheck`) ist kein Detail — sie ist das Messinstrument aller Stop-Gates. Ein Projekt, dessen Zollstock kaputt ist, kann keine Phasen ehrlich abnehmen. Reihenfolge: DEF-02 (tsconfig, Stunden) → DEF-01 (Test-Runner, 1 Tag) → DEF-03 (check:auth statisch, Stunden) → 1.1 (Kanonbereinigung ausführen).

2. **Design-Docs für die zwei fehlenden Verträge JE Phase-Beginn, nicht mitten drin.**
   - Vor Phase 2: Krypto-Spezifikation (GAP-01).
   - Vor Phase 3: IPC-/Daemon-Vertrag (GAP-02).
   Beide sind kleine Dokumente (2–4 Tage), die das Fehlerrisiko der teuersten Phasen halbieren. Das ist die höchstverzinstste Investition des ganzen Projekts.

3. **Server in einem Wartungsfenster in Soll-Zustand bringen, bevor Phase 3 beginnt.**
   NVML-Reboot + CUDA-Toolkit + Port-/Rechte-Hygiene (SRV-01..04). Kein Schreibzugriff auf `/opt/radiquant4` — Alt-Container bleiben unangetastet, werden aber per Firewall/Loopback von der AURELIA-Fläche getrennt.

4. **CPU/VRAM als Betriebsverfassung festschreiben.**
   Der 6-Kern/20-GB-Server trägt das Konzept nur mit diszipliniertem Pinning und dem 2/16/2-Budget. Diese Pläne gehören — wie CopyGuard — in den Kanon, nicht in Erinnerung.

5. **Agententaugliche Aufgabenstruktur beibehalten.**
   Der Kanon (IDs, Sperren, Wiedervorlage) ist bereits so gebaut, dass ein LLM-Entwickler sicher navigieren kann. Ich empfehle, pro Subschritt einen kurzen „Done-when"-Satz (wie in Dokument 06 als [A]) zu pflegen — dann bleibt die Arbeit auch über Sessions hinweg überprüfbar.

6. **Betreiber-Entscheidungen antizipieren, nicht blockieren.**
   WV01–WV06 sind richtig terminiert. Ich würde nur WV01 (Backup-SKU) aktiv vorziehen, sobald Phase 2 näher rückt, weil Beschaffung (EU-Offsite-Speicher) Vorlauf hat.

---

## 2. Abschlussurteil

| Frage des Betreibers | Antwort |
|---|---|
| **Professionalität des Plans?** | Sehr hoch. Entscheidungskanon, Ausschlusskatalog, Stop-Gates und Wiedervorlage sind State of the Art für ein Einzelbetreiber-Projekt dieser Komplexität. |
| **Akkuranz des Bisherigen?** | Dokumentation: sehr akkurat (ein adressierter Bereinigungsrückstand). Code: akkurat, aber frühestens 25 % der Substanz. Server: Hardware exakt wie spezifiziert; Betriebszustand braucht ein Wartungsfenster. |
| **Umsetzbarkeit?** | Gegeben. Kein identifiziertes technisches „unmöglich"; die X-Katalog-Entscheidungen haben die tatsächlich unmöglichen Pfade bereits sauber entfernt. |
| **Planbarkeit?** | Hoch, sobald zwei fehlende Verträge (Krypto, IPC) und Zeitaufwandsbänder (Dokument 06) ergänzt sind. Kritischer Pfad: Phase 4–5 (GPU-Scheduler + timerd), nicht das Frontend. |
| **Größte Gefahr?** | Nicht Technik, sondern **Disziplin-Erosion**: rote Tests ignorieren, Gates überspringen, Art. 9 vor WV01. Die Verfassung verhindert das auf dem Papier — die Qualitätsschleife muss es auf dem Boden tun. |

**Gesamtempfehlung: Weiterführen exakt nach Roadmap, mit den fünf Sofortmaßnahmen aus `01_EXECUTIVE_SUMMARY.md` beginnend diese Woche.**

---

## 3. Änderungsprotokoll gegenüber Analyse v1 (`aurelia-tiefenanalyse/`)

| Neuerung in v2 | Quelle |
|---|---|
| Verifizierte Test-/Typecheck-Defekte DEF-01..04 | Live-Ausführung in dieser Session |
| Vollständige Server-Ist-Analyse (SRV-01..05) inkl. NVML-Mismatch, Portbelegung, Alt-Containern | Live-SSH-Inventur 2026-08-25 |
| GAP-Nummern mit Nachweisen und Gegenmaßnahmen je Phase terminiert | Synthese aus Code- + Server-Befunden |
| Aufwandsbänder je Subschritt und Gesamtdauer-Szenarien | Neue Schätzung |
| IPC- und Krypto-Vertrag als vorziehbare Design-Dokumente eingestuft | Architekturbewertung |
| Innovationsliste um Verfassungs-Prüfung und Abglehne-Liste erweitert | Governance-Abgleich |
