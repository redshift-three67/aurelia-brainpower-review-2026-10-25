export type Wiedervorlage = {
  id: string;
  thema: string;
  wann: string;
  phase: string;
  frage: string;
  defaultBisDahin: string;
};

/** Later operator questions, parked at the phase where they belong. */
export const WIEDERVORLAGE: Wiedervorlage[] = [
  {
    id: "WV01",
    thema: "Wo die verschlüsselte Sicherheitskopie liegt (O04 / H2)",
    wann: "Bevor der erste echte Klienten-Datensatz (Art. 9) gespeichert wird",
    phase: "2 — Praxisorganisation",
    frage: "Welches EU-Ziel? Zum Beispiel Hetzner Storage Box. Restore-Test ist Pflicht.",
    defaultBisDahin: "Regel steht: verschlüsselt, EU, kein Klartext. Anbieter offen.",
  },
  {
    id: "WV02",
    thema: "Abo-Preise in Euro (O07 / D09)",
    wann: "Wenn Mandanten bezahlen sollen — nicht beim Gehäuse",
    phase: "10 — Betrieb",
    frage: "Welche Euro-Beträge zu den schon gesetzten Quotas (16 Timer, 1–4 GPU-Jobs, 1 Emitter)?",
    defaultBisDahin: "Technische Quotas gelten. Keine Preisliste in Phase 1.",
  },
  {
    id: "WV03",
    thema: "Passkeys auf M G1 unter Ubuntu statt Vorschau-E-Mail/Passwort (D08 Produktpfad)",
    wann: "Sobald AURELIA auf GPU Server M G1 läuft, nicht in dieser Vorschau",
    phase: "1 Abschluss auf dem Server / Betrieb",
    frage: "Passkeys plus TOTP scharfschalten, Social-Login weiter aus.",
    defaultBisDahin: "Diese Vorschau darf nur E-Mail/Passwort (Host-Grenze).",
  },
  {
    id: "WV04",
    thema: "Alte Lovable-Verbindung kappen (O03)",
    wann: "Nur wenn Sie das Altprojekt von der Cloud trennen wollen",
    phase: "beliebig, Default nie",
    frage: "„Lovable disconnecten“ — sonst tot liegen lassen.",
    defaultBisDahin: "Kein Ausbau. AURELIA nutzt Lovable nicht.",
  },
  {
    id: "WV05",
    thema: "Zweite Mini-Website bei GPU-Wartung (O05 / H4)",
    wann: "Nur wenn Impressum online bleiben muss, während M G1 aus ist",
    phase: "10 — Betrieb",
    frage: "„H4 ja“ oder ignorieren.",
    defaultBisDahin: "Nein. Pflichtseiten laufen auf M G1 (H3).",
  },
  {
    id: "WV06",
    thema: "Bild- und Tonformate (O09 / D11)",
    wann: "Wenn Medien-Uploads gebaut werden, nicht vorher",
    phase: "6 — Archiv / Report",
    frage: "AVIF/Opus/zstd bestätigen oder andere Codec-Familie. Zeugen nie ins CDN.",
    defaultBisDahin: "Akten-Verbot fürs CDN gilt schon (D15).",
  },
];
