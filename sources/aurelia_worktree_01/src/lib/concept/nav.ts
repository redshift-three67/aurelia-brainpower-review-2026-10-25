export type NavItem = {
  href: string;
  label: string;
  chapter: string;
  blurb: string;
};

export const NAV: NavItem[] = [
  {
    href: "/praxis",
    label: "Praxis",
    chapter: "1",
    blurb: "Gehäuse: Mandant und Rolle",
  },
  {
    href: "/",
    label: "Überblick",
    chapter: "00",
    blurb: "Zweck, Geltungsbereich, Leitentscheidung",
  },
  {
    href: "/freigabe",
    label: "Freigabe",
    chapter: "00b",
    blurb: "C gesetzt, X akzeptiert, U übernommen",
  },
  {
    href: "/offen",
    label: "Offen",
    chapter: "00c",
    blurb: "Wo Sie entscheiden müssen — und wo nicht",
  },
  {
    href: "/leitplanken",
    label: "Leitplanken",
    chapter: "01",
    blurb: "Wellbeing, HWG, CopyGuard",
  },
  {
    href: "/architektur",
    label: "Architektur",
    chapter: "02",
    blurb: "Souveräner Kern, Systemgrenzen",
  },
  {
    href: "/repos",
    label: "Repo-Matrix",
    chapter: "02b",
    blurb: "Drei Bäume, Stop-Gates, kein WinSCP",
  },
  {
    href: "/lovable",
    label: "Lovable",
    chapter: "02c",
    blurb: "H1–H3 gesetzt, Lovable nicht Runtime",
  },
  {
    href: "/hardware",
    label: "Hardware",
    chapter: "03a",
    blurb: "GPU Server M G1, VRAM-Umbau",
  },
  {
    href: "/compute",
    label: "Echtzeit-Compute",
    chapter: "03",
    blurb: "CUDA-Scheduler, Timer, Passport",
  },
  {
    href: "/live",
    label: "Live & Emitter",
    chapter: "03b",
    blurb: "WebSocket-Fachkanal, Spooky2, Wischen",
  },
  {
    href: "/timer",
    label: "Timer & Persistenz",
    chapter: "03c",
    blurb: "Virtuelle Kanäle, Reset, GPU vs RAM",
  },
  {
    href: "/daten",
    label: "Datenhaltung",
    chapter: "04",
    blurb: "Mandanten, Würfel, Archive",
  },
  {
    href: "/zwischenablage",
    label: "Zwischenablage",
    chapter: "04b",
    blurb: "Analyse → Spur → Timer",
  },
  {
    href: "/module",
    label: "Fachmodule",
    chapter: "05",
    blurb: "Sextett, ABI, Intake",
  },
  {
    href: "/kozyrev",
    label: "Kozyrev",
    chapter: "05b",
    blurb: "K1–K5 schaltbar, K6–K8 gesperrt",
  },
  {
    href: "/identitaet",
    label: "Mandanten & Rollen",
    chapter: "06",
    blurb: "Tenants, Gruppen, Abos",
  },
  {
    href: "/sicherheit",
    label: "Sicherheit",
    chapter: "07",
    blurb: "DSGVO, E2E, kein Video",
  },
  {
    href: "/wellbeing",
    label: "Wellbeing",
    chapter: "07b",
    blurb: "CopyGuard im RAM, HWG",
  },
  {
    href: "/gestaltung",
    label: "Gestaltung",
    chapter: "08",
    blurb: "EEAT-UI, Barrierefreiheit",
  },
  {
    href: "/roadmap",
    label: "Phasenplan",
    chapter: "09",
    blurb: "Reihenfolge nach Altstand",
  },
  {
    href: "/entscheidungen",
    label: "Entscheidungen",
    chapter: "10",
    blurb: "D ≠ Dokument. H1–H3 gesetzt",
  },
];
