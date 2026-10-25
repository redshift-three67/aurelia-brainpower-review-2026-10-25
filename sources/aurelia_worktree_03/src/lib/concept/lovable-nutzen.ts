export type NutzenRow = {
  id: string;
  flaeche: string;
  nutzen: string;
  verbesserung: string;
  risiko: string;
  urteil: "sinnvoll" | "bedingt" | "schädlich";
};

export const LOVABLE_NUTZEN: NutzenRow[] = [
  {
    id: "L01",
    flaeche: "Preview des Altprodukts (radiquant-cloud-build)",
    nutzen: "Stakeholder sehen das Cloud-Build-Frontend ohne Zugriff auf M G1. Schneller visuell als ein Server-Deploy.",
    verbesserung: "Abnahme von Build-0-Copy und Trust-IA, sobald Preview auf HEAD liegt (heute: letzte Belege M7, nicht 65868a6).",
    risiko: "Preview wird mit Produktivakte verwechselt. HEAD unbelegt.",
    urteil: "sinnvoll",
  },
  {
    id: "L02",
    flaeche: "GitHub-Sync auf Branch radiquant4",
    nutzen: "Eine Datei, zwei Werkzeuge. Designer und Grok-Altpfad sprechen denselben Tree.",
    verbesserung: "Kein zweites Git. Kapitel-11-Stop-Gate „nicht disconnecten“ bleibt erfüllt.",
    risiko: "Zwei Writer auf radiquant4. AURELIA darf dort nicht still mitschreiben.",
    urteil: "sinnvoll",
  },
  {
    id: "L03",
    flaeche: "Unpersönliche Trust-/Marketingseiten",
    nutzen: "Impressum, Methodengrenzen, Designer-Iteration, HTML/CSS ohne Art. 9.",
    verbesserung: "EEAT-Seiten können schneller iterieren als auf M G1, solange kein Zeuge einfließt.",
    risiko: "Heilstext in der Preview (CopyGuard gilt trotzdem, sobald Texte nach AURELIA fließen).",
    urteil: "sinnvoll",
  },
  {
    id: "L04",
    flaeche: "Designer ohne Serverzugang",
    nutzen: "Gestaltung an der Kante, während Compute auf M G1 bleibt.",
    verbesserung: "Trennt Rollen: Look vs. Uhr vs. GPU.",
    risiko: "Designer legt „Timer in der Cloud“ an, weil die UI es hergibt.",
    urteil: "sinnvoll",
  },
  {
    id: "L05",
    flaeche: "TanStack-Start-Template / Experience-Iterationen",
    nutzen: "Gleiche Familie wie AURELIA-Frontend. Muster für IA, leere Zustände, ehrliche Copy (Build 0).",
    verbesserung: "AURELIA muss das nicht nachbauen, nur den Vertrag halten.",
    risiko: "Code-Copy aus Cloud-Build nach aurelia ohne Intake. Namensfalle radiquant4.",
    urteil: "bedingt",
  },
  {
    id: "L06",
    flaeche: "Supabase Auth / RLS / Tabellen",
    nutzen: "Theoretisch schnelle Memberships.",
    verbesserung: "Keine — Ist ist 0 Tabellen, 0 RLS, Region unbekannt.",
    risiko: "Art. 9 oder Steuerdaten in unbekannter Region. Split-Brain zum M-G1-Origin. D03, X14.",
    urteil: "schädlich",
  },
  {
    id: "L07",
    flaeche: "Edge Functions, Publish, Produktiv-Hosting",
    nutzen: "Theoretisch CDN-Kante.",
    verbesserung: "Keine. Publish nie. Keine GPU-, USB-, Timer-Garantie.",
    risiko: "Scheinproduktion. Zeugen im US-Pfad. D03.",
    urteil: "schädlich",
  },
  {
    id: "L08",
    flaeche: "Ciphertext-Refs / Memberships später",
    nutzen: "Denkbare schlanke Cloud-Control nach EU-Region, AVV, DSFA.",
    verbesserung: "Nur nach Isolationstests. Nicht Phase 1. Nicht die Akte.",
    risiko: "Zu früh gebaut = Drittland und zwei Wahrheiten.",
    urteil: "bedingt",
  },
  {
    id: "L09",
    flaeche: "CUDA, Timer, CopyGuard, Spooky2, Zwischenablage, HRV",
    nutzen: "Keiner. Lovable kann das nicht ausführen.",
    verbesserung: "Hybrid heißt harte Grenze, nicht Mischung.",
    risiko: "Genau das 3-Tier- oder Control-Plane-Missverständnis.",
    urteil: "schädlich",
  },
];

export const LOVABLE_URTEIL = {
  note: "Gesamturteil",
  satz: "Behalten, nicht ausbauen. Preview- und Gestaltungsfläche für das Altprodukt: nützlich. Control-Plane, Akte, GPU, Timer: schädlich. Netto positiv nur mit Disziplin.",
  preview: "hoch — das ist der echte Nutzen",
  kern: "null — und so lassen",
  investition: "Kein Supabase-Ausbau, kein Publish, kein Disconnect, kein zweiter Writer auf radiquant4.",
};
