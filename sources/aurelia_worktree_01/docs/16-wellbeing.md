# Wellbeing-Compliance / CopyGuard

Jeder Text aus UI, Analyse, **Zwischenablage**, Harmonisierung, Report und
Katalog-Import wird geprüft, bevor ein Mensch ihn sieht oder ein PDF entsteht.

## Zwei Stufen

1. **Lexikon, fail-closed** (DE/EN): heilen, diagnostiz*, Krebs behandeln,
   „beseitigt Erreger“, Heilversprechen, MDR-Claims, Torsionskorrektur als Cure.
2. **Lokales schmales LLM im RAM**. Gesetzt: C02 und D13.
   Phi-4-mini Q4 oder Gemma 3 4B Q4, mmap von NVMe, Replica auf der zweiten
   Platte. CPU-Fallback Gemma 3 1B.
   **Kein Cloud-LLM. Kein CUDA-Resident.**

Ausgabe: `allow` | `rewrite` | `block` plus `reason_code`, Digest in Passport
und Draft.

Qwen2.5-14B bleibt Demo. Alte Engines und Kozyrev-Anhänge laufen nicht ungeprüft
in Klienten-PDFs. Siehe [19-kozyrev.md](19-kozyrev.md).
