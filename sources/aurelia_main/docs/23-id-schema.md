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

## D08–D12 (empfohlen, nicht unsicher)

| ID | Titel | Warum noch empfohlen |
|---|---|---|
| D08 | Passkeys + TOTP, kein Social-Login | Auth ist aus. Regel klar, Bau später. |
| D09 | Abos an VRAM/Kanäle/Emitter | Preismodell offen. Technische Quotas schon in C05. |
| D10 | WebRTC optional, E2E, keine Aufnahme | Nachrangig nach Live-Tick. |
| D11 | AVIF/Opus/zstd, Zeugen nie im CDN | Codec später; Verbot schon über D15 hart. |
| D12 | WCAG 2.2 AA / BFSG / EEAT | Inhalt über D01; UI-Pflicht gebündelt. |

Gesetzt bindet den nächsten Slice. Empfohlen ist die bevorzugte Lösung, sobald der Slice dran ist.
