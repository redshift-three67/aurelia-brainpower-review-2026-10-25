# ID-Schema: D ist keine Datei

Kanon: `src/lib/concept/id-legend.ts`. Portal: `/entscheidungen`.

| Präfix | Name | Bedeutung |
|---|---|---|
| **D** | Leitentscheidung | Architecture Decision Record. D08 ≠ docs/08. |
| **C** | Bestätigung | C01–C12, von Ihnen mit Ja gesetzt. |
| **X** | Katalog — akzeptiert | X01–X20 sind als nicht umsetzbar / nicht relevant akzeptiert; nicht bauen und nicht still löschen. |
| **U** | Unklar, Empfehlung übernommen | z. B. U12 HRV-Ohrclip. |
| **K** | Kozyrev-Katalog | K1–K5 gesetzt, K6–K8 gesperrt. |
| **L** | Lovable-Fläche | L01–L09, Urteil sinnvoll/bedingt/schädlich. |
| **H** | Hybrid-Alternative | H1–H8 in `standalone.ts`. |
| **O** | Offen | Restliste. Lage sagt, ob eine Entscheidung nötig ist. |
| **WV** | Wiedervorlage | WV01–WV06, spätere Fragen an der passenden Phase. |
| **docs/NN** | Kapiteldatei | Markdown. Nummer trifft D nur zufällig. |

## D08–D12 (gesetzte und empfohlene Projektion)

| ID | Lock | Titel | Statusgrund |
|---|---|---|---|
| D08 | gesetzt | Passkeys + TOTP, kein Social-Login | Authentifizierung ist aktiv; Vorschau nutzt E-Mail/Passwort, Produktpfad auf M G1 bleibt Passkeys + TOTP. |
| D09 | empfohlen | Abos an VRAM/Kanäle/Emitter | Preismodell offen; technische Quotas bereits gesetzt. |
| D10 | gesetzt | Video, WebRTC, TURN und Aufzeichnung vollständig ausgeschlossen | O08 entschieden; Phase 9 gestrichen. |
| D11 | empfohlen | AVIF/Opus/zstd, Zeugen nie im CDN | Codec-Familie bleibt WV06; CDN-Verbot ist gesetzt. |
| D12 | gesetzt | WCAG 2.2 AA / BFSG / EEAT | UI-Pflicht und CopyGuard gesetzt. |

Gesetzt bindet den nächsten Slice. Empfohlen bezeichnet hier ausschließlich D09
und D11 als Wiedervorlage. Diese Tabelle ist eine Projektion; die einzige
Lockquelle ist `CANONICAL_DECISION_LOCKS` in `decisions.ts`.
