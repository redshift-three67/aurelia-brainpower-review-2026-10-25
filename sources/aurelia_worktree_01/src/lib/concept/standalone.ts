export type HybridLock = "gesetzt" | "optional" | "gesperrt";

export type HybridRow = {
  id: string;
  kombination: string;
  mehrwertFuerDebian: string;
  urteil: "optimal" | "empfohlen" | "optional" | "schädlich";
  lock: HybridLock;
  grund: string;
};

/** First-elaboration hybrid surfaces vs Lovable L-IDs. */
export const ERSTE_HYBRID_FLAECHEN: {
  damals: string;
  quelle: string;
  l: string;
  fuerAurelia: string;
}[] = [
  {
    damals: "Preview / Experience des damaligen Frontends",
    quelle: "D03, Kapitel 11, docs/02-architecture.md „Neben Spur“",
    l: "L01",
    fuerAurelia: "Betrifft das Altprodukt radiquant-cloud-build, nicht die Debian-Akte.",
  },
  {
    damals: "GitHub als gemeinsame Datei, nicht disconnecten",
    quelle: "D03, docs/12-heritage.md",
    l: "L02",
    fuerAurelia: "Heritage-Stop-Gate. Kein Rechennutzen für M G1. AURELIA verdrahtet Lovable nicht.",
  },
  {
    damals: "Unpersönliche Trust-/Marketingseiten, UI ohne Art. 9",
    quelle: "docs/02-architecture.md „schlanke öffentliche Kante“; 01-vision Pflichtseiten",
    l: "L03",
    fuerAurelia: "Gesetzt als H3: AURELIA + Caddy auf M G1, nicht Lovable.",
  },
  {
    damals: "Designer-Fläche ohne Serverzugang / schnelle Gestaltung",
    quelle: "D03 „Preview und Gestaltung“",
    l: "L04",
    fuerAurelia: "Gesetzt: dieses Repo. Preview hier, nicht Lovable-Supabase.",
  },
];

export const HYBRID_ALTERNATIVEN: HybridRow[] = [
  {
    id: "H1",
    kombination: "M G1 allein als Origin (Auth, Akte, CUDA, Timer, CopyGuard, WS)",
    mehrwertFuerDebian: "Eine Wahrheit, eine Uhr, Art. 9 am Ort der GPU. Backbone-Lage wird genutzt.",
    urteil: "optimal",
    lock: "gesetzt",
    grund: "Operator 2026-08-23. Jede zweite Control-Plane ist Split-Brain.",
  },
  {
    id: "H2",
    kombination: "M G1 + verschlüsseltes Offsite-Backup (zweites EU-Ziel)",
    mehrwertFuerDebian: "Überleben bei Diebstahl, Brand, Platten Tod. Restore getestet.",
    urteil: "optimal",
    lock: "gesetzt",
    grund: "Standalone ohne Backup wäre ein Single Point of Failure. SKU noch offen (O04). Kein Klartext offsite.",
  },
  {
    id: "H3",
    kombination: "Öffentliche Pflichtseiten aus demselben AURELIA-Baum (Caddy auf M G1)",
    mehrwertFuerDebian: "L03/L04 ohne dritten Vendor. CopyGuard und Tokens eine Codebasis.",
    urteil: "optimal",
    lock: "gesetzt",
    grund: "Die hybride Kante der Erstfassung war diese Web-App.",
  },
  {
    id: "H4",
    kombination: "Kleines EU-VPS nur statisches Marketing, falls GPU-Wartung ≠ Website-Uptime",
    mehrwertFuerDebian: "Impressum bleibt erreichbar, wenn die Ada in Wartung ist.",
    urteil: "optional",
    lock: "optional",
    grund: "Kein Login, kein WS. Default: nicht. O05.",
  },
  {
    id: "H5",
    kombination: "Lovable + Debian als Plattform",
    mehrwertFuerDebian: "Keiner am Kern.",
    urteil: "schädlich",
    lock: "gesperrt",
    grund: "H1–H3 ersetzen das. Heritage-Link darf tot liegen (O03).",
  },
  {
    id: "H6",
    kombination: "Supabase/Firebase/Cloud-Auth + Debian",
    mehrwertFuerDebian: "Scheinbar schnellere Memberships.",
    urteil: "schädlich",
    lock: "gesperrt",
    grund: "X14, Art. 9, zwei Wahrheiten.",
  },
  {
    id: "H7",
    kombination: "Cloud-GPU neben der Ada",
    mehrwertFuerDebian: "Mehr VRAM theoretisch.",
    urteil: "schädlich",
    lock: "gesperrt",
    grund: "Bricht Isolation, USB-Nähe, C01.",
  },
  {
    id: "H8",
    kombination: "Cloud-LLM für CopyGuard",
    mehrwertFuerDebian: "Keiner.",
    urteil: "schädlich",
    lock: "gesperrt",
    grund: "D13, X16. Akten-Copy bleibt auf der Box.",
  },
];

export const H_GESETZT = HYBRID_ALTERNATIVEN.filter((r) => r.lock === "gesetzt");
export const H_GESPERRT = HYBRID_ALTERNATIVEN.filter((r) => r.lock === "gesperrt");

export const STANDALONE_URTEIL = {
  kurz: "H1–H3 gesetzt. Origin M G1, EU-Backup, Caddy-Kante. Lovable nicht in der Laufzeit.",
  lang: "H1–H3 sind gesetzt. Die Ada ist der Origin. Backup ist Pflicht, nicht Kür. Pflichtseiten kommen aus diesem Baum. Lovable, Cloud-Auth, Cloud-GPU und Cloud-LLM sind gesperrt. Offen bleiben die Backup-SKU und das optionale H4.",
};
