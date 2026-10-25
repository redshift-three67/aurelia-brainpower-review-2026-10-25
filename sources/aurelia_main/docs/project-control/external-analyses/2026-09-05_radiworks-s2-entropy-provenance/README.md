# RadiWorks S2 — Entropie und Provenienz

**Status:** Sanitierte externe Evidenz für Aurelia; keine automatische Plattformnorm.

## Betreiberfreigegebene RadiWorks-Entscheidungen

1. Der produktive seeded-Pfad verwendet Java-Master-PRNG, Java-Zweitstufe und Java-HashMap-Reihenfolge.
2. Der stochastic-Pfad verwendet Webcam-/Hotbits-FIFO, danach die ausdrücklich freigegebene random.org-Quelle und zuletzt OS-CSPRNG. Nur stochastic darf Egress auslösen.
3. Neue Passports führen den effektiven Seed, `replayable` und `seed_scheme=effective-v2`; stochastic ist nicht replaybar.
4. Historische Passports ohne diese Metadaten bleiben als frühere Derived-Seed-Semantik erkennbar und werden nicht rückwirkend umgedeutet.
5. Der CopyGuard-Digest der final sichtbaren Raten muss Passport und Draft identisch binden.

## Übernahmevorbehalt

Eine Übernahme in eine Aurelia-Spezifikation erfordert weiterhin den vorgesehenen Governance-Akt. Diese Evidenz enthält weder Betriebsdaten noch Fallinformationen, Entropie-Rohwerte, Zugangsdaten oder andere Geheimnisse.
