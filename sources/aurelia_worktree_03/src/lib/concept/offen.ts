export type OffenLage =
  | "gesetzt"
  | "Entscheidung später"
  | "Optional — Default: nein"
  | "Keine Entscheidung — Empfehlung gilt";

export type OffenGruppe = "erledigt" | "spaeter" | "nicht";

export type OffenRow = {
  id: string;
  thema: string;
  lage: OffenLage;
  gruppe: OffenGruppe;
  braucheSie: string;
  stand: string;
  naechsterSchritt: string;
};

export const OFFEN: OffenRow[] = [
  {
    id: "O01",
    thema: "Liste der Dinge, die wir nicht bauen (X01–X20)",
    lage: "gesetzt",
    gruppe: "erledigt",
    braucheSie: "Erledigt",
    stand: "2026-08-24 akzeptiert. Kategorien nicht umsetzbar / nicht relevant gelten. Kozyrev: K1 default an; K2–K5 default aus; K1–K5 gesetzt und schaltbar; K6–K8 gesperrt ohne Schalter.",
    naechsterSchritt: "Nichts. Katalog bleibt dokumentiert, nichts still löschen.",
  },
  {
    id: "O02",
    thema: "Wann die erste Programm-Schale gebaut wird",
    lage: "gesetzt",
    gruppe: "erledigt",
    braucheSie: "Erledigt",
    stand: "Die Phase-1-Schale mit Anmeldung, Mandant und Rolle ist technisch vorhanden. Authentifizierung und Datenbank sind aktiv; Datenklasse ausschließlich synthetic.",
    naechsterSchritt: "Keine weitere Produktarbeit vor dem dokumentiert bestandenen G0-SRV-12.",
  },
  {
    id: "O08",
    thema: "Ausgeschlossene Medienkommunikation zwischen Therapeut und Klient",
    lage: "gesetzt",
    gruppe: "erledigt",
    braucheSie: "Erledigt",
    stand: "Keine Videos. D10 gesetzt. Phase 9 entfällt.",
    naechsterSchritt: "Nichts. Video und WebRTC sind vollständig ausgeschlossen; Phase 9 nicht anlegen.",
  },
  {
    id: "O04",
    thema: "Wo die verschlüsselte Sicherheitskopie physisch liegt",
    lage: "Entscheidung später",
    gruppe: "spaeter",
    braucheSie: "Wiedervorlage Phase 2, vor dem ersten Art.-9-Datensatz",
    stand: "Regel steht: verschlüsselt, EU, Restore-Test, kein Klartext.",
    naechsterSchritt: "Siehe WV01. Jetzt nichts.",
  },
  {
    id: "O07",
    thema: "Was ein Abo in Euro kostet",
    lage: "Entscheidung später",
    gruppe: "spaeter",
    braucheSie: "Wiedervorlage Phase 10",
    stand: "Quotas gesetzt. Preise nicht.",
    naechsterSchritt: "Siehe WV02. Jetzt keine Preisliste.",
  },
  {
    id: "O03",
    thema: "Alte Lovable-Verbindung zum Vorgänger-Projekt",
    lage: "Optional — Default: nein",
    gruppe: "nicht",
    braucheSie: "Nein",
    stand: "AURELIA nutzt Lovable nicht.",
    naechsterSchritt: "WV04. Nichts tun, außer Sie wollen disconnecten.",
  },
  {
    id: "O05",
    thema: "Zweite Mini-Website bei GPU-Wartung",
    lage: "Optional — Default: nein",
    gruppe: "nicht",
    braucheSie: "Nein",
    stand: "H3: Pflichtseiten auf M G1.",
    naechsterSchritt: "WV05. Ignorieren.",
  },
  {
    id: "O06",
    thema: "Wie sich Praktiker später anmelden",
    lage: "gesetzt",
    gruppe: "erledigt",
    braucheSie: "Erledigt mit D08",
    stand: "M G1 unter Ubuntu: Passkeys + TOTP. Diese Vorschau: E-Mail/Passwort (Host-Grenze).",
    naechsterSchritt: "WV03 wenn AURELIA auf M G1 umzieht.",
  },
  {
    id: "O09",
    thema: "Bild- und Tonformate",
    lage: "Keine Entscheidung — Empfehlung gilt",
    gruppe: "spaeter",
    braucheSie: "Wiedervorlage Phase 6",
    stand: "AVIF/Opus/zstd vorgeschlagen. CDN-Verbot gesetzt.",
    naechsterSchritt: "WV06.",
  },
  {
    id: "O10",
    thema: "Barrierefreiheit und ehrliche Texte",
    lage: "gesetzt",
    gruppe: "erledigt",
    braucheSie: "Erledigt — D12 gesetzt",
    stand: "WCAG 2.2 AA / BFSG / CopyGuard.",
    naechsterSchritt: "Nichts. Produkt-UI erbt die Regeln.",
  },
];

export const OFFEN_ERLEDIGT = OFFEN.filter((r) => r.gruppe === "erledigt");
export const OFFEN_SPAETER = OFFEN.filter((r) => r.gruppe === "spaeter");
export const OFFEN_NICHT = OFFEN.filter((r) => r.gruppe === "nicht");

/** @deprecated use OFFEN_ERLEDIGT */
export const OFFEN_JETZT = OFFEN_ERLEDIGT;

export const OFFEN_URTEIL = {
  kurz: "X akzeptiert. Phase-1-Schale vorhanden; Produktarbeit bis G0-SRV-12 pausiert. Video ausgeschlossen.",
  lang: "O01, O02, O06, O08, O10 sind gesetzt. Wiedervorlage: Backup vor Art. 9, Preise im Betrieb, Passkeys auf M G1, Codecs beim Archiv. Lovable und Mini-VPS bleiben Default nein.",
};

export const GESETZT_KERNE = [
  "C01–C12, X-Katalog akzeptiert",
  "D01–D08, D10, D12–D24 (D09/D11 später)",
  "K1–K5 schaltbar, K6–K8 gesperrt",
  "H1–H3, kein Video (D10)",
  "Phase-1-Schale: Authentifizierung + Datenbank + Mandant technisch vorhanden; ausschließlich synthetic; Produktarbeit bis G0-SRV-12 pausiert",
];
