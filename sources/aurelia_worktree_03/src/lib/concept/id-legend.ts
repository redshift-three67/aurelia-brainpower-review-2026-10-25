import {
  CANONICAL_DECISION_LOCKS,
  type DecisionLock,
} from "./decisions.ts";

export type IdFamily = {
  prefix: string;
  name: string;
  bedeutet: string;
  wo: string;
  beispiel: string;
};

export const ID_FAMILIEN: IdFamily[] = [
  {
    prefix: "D",
    name: "Leitentscheidung",
    bedeutet:
      "Architecture Decision Record. Eine gesetzte oder empfohlene Produktregel, nicht eine Datei. D08 ist nicht docs/08.",
    wo: "src/lib/concept/decisions.ts · Portal /entscheidungen · docs/10-decisions.md",
    beispiel: "D20 = Timer-Persistenz in Postgres, nicht „Dokument 20“.",
  },
  {
    prefix: "C",
    name: "Bestätigung",
    bedeutet: "Punkte, die Sie mit Ja gesetzt haben (C01–C12).",
    wo: "src/lib/concept/freigabe.ts · /freigabe · docs/20-freigabe.md",
    beispiel: "C05 = Isolation vieler Klientenjobs, 20 war ein Beispiel.",
  },
  {
    prefix: "X",
    name: "Katalog — akzeptiert",
    bedeutet: "Nicht umsetzbar oder nicht relevant. 2026-08-24 akzeptiert. Nicht still löschen, nicht bauen.",
    wo: "freigabe.ts · /freigabe",
    beispiel: "X14 = Lovable nicht als Control-Plane.",
  },
  {
    prefix: "U",
    name: "Unklar, Empfehlung übernommen",
    bedeutet: "Offene Stellen, bei denen Sie der Empfehlung gefolgt sind.",
    wo: "freigabe.ts · /freigabe",
    beispiel: "U12 = HRV-Ohrclip, kein EEG.",
  },
  {
    prefix: "K",
    name: "Kozyrev-Katalog",
    bedeutet: "K1–K5 gesetzt und schaltbar. K6–K8 gesperrt, kein Schalter.",
    wo: "kozyrev-labor.ts · /kozyrev · docs/22-kozyrev-labor.md",
    beispiel: "K1 = Haar-DSP.",
  },
  {
    prefix: "L",
    name: "Lovable-Fläche",
    bedeutet: "Was Lovable tun könnte. Urteil sinnvoll / bedingt / schädlich. Keine Leitentscheidung.",
    wo: "lovable-nutzen.ts · /lovable · docs/13-lovable.md",
    beispiel: "L03 = unpersönliche Trust-Seiten.",
  },
  {
    prefix: "H",
    name: "Hybrid-/Origin-Alternative",
    bedeutet: "Origin- und Betriebsalternativen H1–H8. H1–H3 gesetzt, H4 optional, H5–H8 gesperrt.",
    wo: "standalone.ts · /lovable · docs/24-standalone.md",
    beispiel: "H1 = M G1 allein als Origin.",
  },
  {
    prefix: "O",
    name: "Offen",
    bedeutet: "Rest nach geschlossenem Kern. Lage sagt, ob Sie entscheiden müssen.",
    wo: "offen.ts · /offen · docs/25-offen.md",
    beispiel: "O02 = Phase-1-Schale vorhanden, Produktarbeit pausiert.",
  },
  {
    prefix: "WV",
    name: "Wiedervorlage",
    bedeutet: "Spätere Frage, geparkt an der passenden Phase.",
    wo: "wiedervorlage.ts · /offen · docs/26-wiedervorlage.md",
    beispiel: "WV01 = Backup-Ort vor Art. 9.",
  },
  {
    prefix: "docs/NN",
    name: "Kapiteldatei",
    bedeutet: "Markdown im Ordner docs/. Nummer ≠ D-Nummer.",
    wo: "docs/00-index.md",
    beispiel: "docs/08-ui-a11y.md gehört thematisch zu D12, ist aber nicht D08.",
  },
];

type DecisionSummaryId = "D08" | "D09" | "D10" | "D11" | "D12";

type DecisionSummaryContent = {
  id: DecisionSummaryId;
  titel: string;
  kern: string;
  statusgrund: string;
};

export type DecisionStatusSummary = DecisionSummaryContent & {
  status: DecisionLock;
};

const D08_D12_SUMMARY_CONTENT: DecisionSummaryContent[] = [
  {
    id: "D08",
    titel: "Identität: Passkeys + TOTP auf M G1, E-Mail/Passwort nur in der Vorschau",
    kern: "Kein Social-Login als Produktpfad.",
    statusgrund: "Gesetzt 2026-08-24. WV03 = Passkeys beim Umzug auf M G1.",
  },
  {
    id: "D09",
    titel: "Abos: Quotas an VRAM, Timer-Kanälen, Emittern",
    kern: "Technische Quotas sind verbindlich; Euro-Beträge bleiben WV02.",
    statusgrund: "Wiedervorlage WV02 in Phase 10.",
  },
  {
    id: "D10",
    titel: "Kein Video",
    kern: "Kein WebRTC, keine Aufnahme; Phase 9 gestrichen.",
    statusgrund: "Gesetzt (O08). Phase 9 gestrichen.",
  },
  {
    id: "D11",
    titel: "Medien: AVIF/Opus/zstd — Zeugen nie ins CDN",
    kern: "Zeugen nie ins CDN; Codec-Familie bleibt WV06.",
    statusgrund: "Wiedervorlage WV06 in Phase 6.",
  },
  {
    id: "D12",
    titel: "Barrierefreiheit und EEAT sind Muss",
    kern: "WCAG 2.2 AA / BFSG / CopyGuard.",
    statusgrund: "Gesetzt 2026-08-24.",
  },
];

export const D08_D12_SUMMARIES: DecisionStatusSummary[] =
  D08_D12_SUMMARY_CONTENT.map((summary) => ({
    ...summary,
    status: CANONICAL_DECISION_LOCKS[summary.id],
  }));
