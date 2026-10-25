# 07 — Vorgehensweise-Empfehlung & Fazit V3 (2026-08-25 17:33 CEST)

---

## 1. Meine Vorgehensweise als Architekt (V3, vollständig neu formuliert)

**Grundsatz: Der Kanon ist das Gesetz, die Qualitätsschleife ist der Vollzug, der Server ist das Territorium.** Alle drei müssen stimmen — aktuell stimmt nur der Kanon.

### Schrittfolge (nicht verhandelbare Reihenfolge)

1. **Woche 1 — Messinstrumente reparieren (lokal).**
   tsconfig-Fix → Test-Runner-Migration → `check:auth` statisch → Kanonbereinigung ausführen → CI mit `test/typecheck/check:canon/check:auth` als Pflicht-Gates. *Begründung:* Jede spätere Abnahme steht auf diesen Säulen; ohne sie sind Stop-Gates Meinung, nicht Messung.

2. **Woche 1–2 — Isolation beweisen und Phase 1 abschließen.**
   Negative Mandanten-Tests + `assertSynthetic`-Guard + Betreiber-Startwort. *Erst dann* irgendwelche neue Features.

3. **Woche 2 — Serverhärtung (Phase 1.5, SH-1…SH-8) in einem Wartungsfenster.**
   Die V3-Inventur hat gezeigt: Der Server ist die aktuell schwächste Säule (Root-Login, NOPASSWD:ALL, Cron-Passwort, keine Offsite-Backups, CUDA tot, 185 GB Docker-Müll, 9 failed Units). Alles zusammen ~2–3 Tage Arbeit — aber **vor** jedem Art.-9-Gedanken zwingend, und es koppelt WV01-Vorbereitung direkt an.

4. **Vor Phase 2 — die zwei fehlenden Verträge schreiben** (Krypto-Spezifikation, danach IPC-Vertrag vor Phase 3). Kleine Dokumente, unverhältnismäßig große Risikoreduktion der Phasen 2–5.

5. **Phasen 2–5 strikt sequenziell, agententauglich geschnitten.**
   Jeder Subschritt in 06 hat ein messbares [A]; so bleibt die Arbeit über Sessions/Agenten hingehend überprüfbar, und der Betreiber behält die Gate-Hoheit (Startworte wie in 11-llm-handoff).

6. **Betreiberverbund:** WV01 (Offsite-SKU) jetzt beschaffen lassen (Vorlauf!), DSB-Review der Krypto-Spec in Phase 2 einplanen, Pentest in Phase 7 fest buchen.

### Anti-Pattern, gegen die ich mich stellen würde
- GPU/CUDA „mal eben ausprobieren" vor SH-6 (NVML ist tot — jeder Versuch frustriert und verführt zu Workarounds).
- Art.-9-Daten vor Restore-Nachweis (Verstoß gegen WV01 und Vorbereitungsspezifikation).
- Die 9 failed Units „später aufräumen" (sie vernebeln jeden künftigen Incident-Debug).
- Archivierung der Alt-Container löschen statt beweissichern (Heritage-Regel).

---

## 2. Antwort auf die Fragen des Betreibers (kompakt)

| Frage | V3-Antwort |
|---|---|
| **Professionalität des Plans?** | Sehr hoch (95 %). Entscheidungskanon mit Sperren, Wiedervorlage, ehrliche Nicht-Ziele, Stop-Gates. Lücken: fehlende Aufwandsbänder (jetzt ergänzt) und die zwei Design-Verträge. |
| **Akkuranz des Bisherigen?** | Doku sehr akkurat; Code akkurat, aber ~25 % Substanz (phasengerecht); Server: Hardware exakt, Betrieb unter Soll (V3: 15 Einzelbefunde, davon 2 kritisch). |
| **Umsetzbarkeit?** | Ja. Kein technisches Unmöglich; X-Katalog hat Unmögliches bereits entfernt. Vorbedingungen: Härtung + 2 Verträge + grüne Schleife. |
| **Planbarkeit?** | Hoch mit den Aufwandsbändern aus 06; kritischer Pfad Phase 4–5; 9–15 Monate bis Pilot. |
| **Größtes Einzelrisiko?** | V3-Neubewertung: **nicht** die Technik, sondern der Serverbetrieb (R-08/R-03: Kompromittierung/Totalverlust ohne Offsite). Beide sind mit ~3 Tagen Arbeit behebbar — das ist die beste Nachricht dieser Analyse. |

---

## 3. Schlusswort

AURELIA ist ungewöhnlich gut verfasst und ungewöhnlich früh diszipliniert. Die Neuanalyse von Null bestätigt das Gesamtbild der Vorversionen, verschiebt aber die Dringlichkeit: **Von null auf heute ist der Server der Flaschenhals, nicht der Code.** Die nächsten 14 Tage entscheiden, ob das Projekt auf Messung (grüne Gates) und hartem Boden (gehärteter M G1) weiterwächst — alles danach ist Planarbeit nach bewährtem Kanon.

**Empfehlung: Sofortstart mit Maßnahme 1–7 aus `01_EXECUTIVE_SUMMARY.md`; Phase 1.5 (Serverhärtung) als neues, formales Gate vor jeder Art.-9-Annäherung.**

---

*Ende der V3-Analyse. Ablage: `aurelia-tiefenanalyse-v3-2026-08-25/` (7 Dateien). Provenienz: Projekt `redshift-three67/aurelia` @ `a726346`; Server `185.242.115.210` Inventur 17:33 CEST via SSH klaus999 (read-only).*
