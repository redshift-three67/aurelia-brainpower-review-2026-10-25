# D-Vorlage: `aurelia-entropyd` — zentraler Entropie-Dienst (Diskussionsentwurf)

> **Für den Betreiber als Leitentscheidung (D-Katalog) vorbereitet.** Status:
> VORSCHLAG aus der Modulseite — Evidenz, kein Kanon. Einzureichen, wenn
> Aurelia Phase 2/3 wiederaufnimmt. Fassung 2026-08-29.

## Vorschlag (Kurzfassung)

`aurelia-entropyd` = gemeinsamer Echtzeit-Dienst für stochastische Entropie,
strukturell parallel zu `timerd` (Uhr) und `emitterd` (Emission):

```
Modul (Kernel, repro: stochastic)
   │  Contract: POST /lease  {modul, menge, qualität}
   ▼
aurelia-entropyd   ── Lease → Bezug → Audit (wie emitterd: Lease → Arming → ACK)
   │  Quellen (Priority-Kette, plattformseitig):
   │  1. HWRNG/QRNG-Karte (M G1, wenn beschafft)
   │  2. Anbieter-QRNG-API (EU)
   │  3. OS-CSPRNG (Fallback, fail-closed deklariert)
   ▼
Ausgabe: Entropie-Pakete im bewährten Format {"integerList":[…]}
         (AetherOnePi-kompatibel, Seed-Semantik wie gehabt)
```

## Meine Empfehlung: **ZENTRAL (Variante 2) — in zwei Stufen**

**Warum zentral vorteilhaft ist:**

1. **Eine Quelle, eine Wahrheit:** Jede Zahl im System hat einen prüfbaren
   Ursprung (Audit wie beim Emitter). Passt zu Aurelias
   Passport-/Herkunftsphilosophie — `sources` im Passport zeigt dann
   `entropyd/lease-<id>` statt „modul-intern, Quelle unbekannt".
2. **Optimale Hardware-Ausnutzung (Prämisse des Betreibers):** Eine
   QRNG-Karte am M G1 versorgt ALLE sechs Module — statt sechs Modul-Stacks
   mit sechs Webcam-/API-Wege. Failover (Karte → API → OS) wird EINMAL
   gebaut und EINMAL geprüft.
3. **Klienten-Vektor-sauber:** Lease trägt `(tenant_id, client_id, job_id)`
   — die Entropieziehung wird mandantenbezogen nachvollziehbar, ohne die
   Kernstatik zu ändern (Antwort auf deine Beobachtung, dass Resonanzen
   vektorbezogen akkurat sind: Der VEKTOR wird so im Audit sichtbar, die
   Zufallsmechanik bleibt unangetastet).
4. **Radi144 + RadiWorks teilen denselben Modus** — dein Wunsch, dass beide
   Welten stochastisch arbeiten können, wird zum Standard statt zur
   Einzelanpassung.

**Warum in zwei Stufen (nicht alles auf einmal):**

- **Stufe A (jetzt, Modulseite — bereits erfüllt):** Der
  `EntropyProvider`-Standard aus `Modul_Templates` (Kette Webcam-Feed →
  QRNG-API → OS, seeded als Default, Passport-Provenienz) läuft in jedem
  Prototyp autark. Kein Aurelia-Input nötig; Schnittstelle ist stabil.
- **Stufe B (bei Aurelia Phase 4/5):** `entropyd` baut den Lease-/Auditweg;
  die Module tauschen nur ihre Quelle — `EntropyProvider` bekommt einen
  zusätzlichen Provider „entropyd" vor die Kette. Die Festlegung 1
  (seeded Default, stochastisch explizit) bleibt unverändert.

## Regeln, die der Dienst übernehmen würde

1. `repro: stochastic` bleibt explizit pro Lauf (Hard Rule 7) — entropyd
   ändert nichts an der Deklarationspflicht, nur an der Beschaffung.
2. Kein Zeugenklartext, keine Klientendaten im Entropie-Call — nur Mengen
   und Qualitätsanforderungen.
3. Seeds werden pro Lauf im Passport vermerkt (bereits implementiert).
4. Fail-closed-Fallback auf OS-CSPRNG ist deklariert (kein stiller Wechsel —
   Passport dokumentiert die tatsächlich genutzte Quelle, Lücke ggü. dem
   Original, das still wechselte).

## Offene Punkte für die Entscheidung

- Beschaffung einer QRNG-Quelle für M G1 (Hardware oder EU-Anbieter-API)
- Lease-Granularität (je Lauf vs. je Paket)
- Verhältnis zu Kozyrev-DSP-Entropie (K-Katalog, `lab.*` bleibt `executable:
  false`) — entropyd liefert nur klassische Entropie, keine Kozyrev-Annahmen
