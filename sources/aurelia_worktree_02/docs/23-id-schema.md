# ID-Schema: D ist keine Datei

Kanon: `src/lib/concept/id-legend.ts`. Portal: `/entscheidungen`.

| Präfix | Name | Bedeutung |
|---|---|---|
| **D** | Leitentscheidung | Architecture Decision Record. D08 ≠ docs/08. |
| **C** | Bestätigung | C01–C12, von Ihnen mit Ja gesetzt. |
| **X** | Katalog Prüfung | nicht umsetzbar / nicht relevant. Pause. |
| **U** | Unklar, Empfehlung übernommen | z. B. U12 HRV-Ohrclip. |
| **K** | Kozyrev-Katalog | K1–K5 gesetzt, K6–K8 gesperrt. |
| **L** | Lovable-Fläche | L01–L09, Urteil sinnvoll/bedingt/schädlich. |
| **H** | Hybrid-Alternative | H1–H8 in `standalone.ts`. |
| **O** | Offen | Restliste. Lage sagt, ob eine Entscheidung nötig ist. |
| **docs/NN** | Kapiteldatei | Markdown. Nummer trifft D nur zufällig. |

## Status D08–D12

D08, D10 und D12 sind gesetzt. D09 und D11 bleiben Wiedervorlage; ihre bereits
gesetzten technischen Grenzen gelten weiter.

| ID | Status | Inhalt | Statusgrund |
|---|---|---|---|
| D08 | gesetzt | Passkeys + TOTP, kein Social-Login | Produktregel gesetzt; Aktivierung auf M G1 unter WV03. |
| D09 | empfohlen | Abos an VRAM/Kanäle/Emitter | Technische Quotas gesetzt; Preise unter WV02. |
| D10 | gesetzt | Kein Video, kein WebRTC, keine Aufnahme | O08 entschieden; Phase 9 gestrichen. |
| D11 | empfohlen | AVIF/Opus/zstd, Zeugen nie im CDN | CDN-Verbot gesetzt; Codecwahl unter WV06. |
| D12 | gesetzt | WCAG 2.2 AA / BFSG / EEAT | O10 entschieden; bindet alle Oberflächen. |

Gesetzt bindet den nächsten Slice. Empfohlen bezeichnet eine Wiedervorlage mit
gesetzten technischen Grenzen, nicht eine unklare Produktentscheidung.
