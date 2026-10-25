export type FreigabeRow = {
  id: string;
  thema: string;
  vorschlag: string;
  begruendung: string;
};

export type XKategorie = "nicht umsetzbar" | "nicht relevant";

export type XRow = FreigabeRow & { kategorie: XKategorie };

/**
 * C01–C12: operator confirmed 2026-08-23.
 * C05 restated: 20 is an example occupancy, not a cap on virtual timers.
 */
export const C_GESETZT: FreigabeRow[] = [
  {
    id: "C01",
    thema: "CUDA-Zweck",
    vorschlag:
      "Die RTX 4000 SFF Ada rechnet Analyse-, Harmonisierungs-DSP und optionale Quantum-Jobs. Nachvollziehbar, isoliert, kein Overcommit. Sie ist nicht die Uhr.",
    begruendung: "Bestätigt. 20 GB sind der Job-Pool, nicht der Wächter und nicht das Timer-Ledger.",
  },
  {
    id: "C02",
    thema: "CopyGuard vom VRAM",
    vorschlag:
      "Phi-4-mini Q4 oder Gemma 3 4B Q4 im DDR5, mmap von NVMe, Replica auf der zweiten NVMe, Fallback Gemma 3 1B. CUDA bleibt frei.",
    begruendung: "Bestätigt. 128 GB RAM tragen den Wächter redundant.",
  },
  {
    id: "C03",
    thema: "VRAM-Umbau",
    vorschlag: "2 GB Runtime · 16 GB Job-Pool · 2 GB Kopf. CopyGuard = 0 GB VRAM. Kein Overcommit.",
    begruendung: "Bestätigt. Ersetzt 3/3/12/2.",
  },
  {
    id: "C04",
    thema: "CUDA-Scheduler",
    vorschlag:
      "aurelia-gpud. Kein MIG. Isolation auf (tenant_id, client_id, job_id): eigener Stream, eigene VRAM-Arena, Drain. Auch zwei Jobs desselben Klienten mischen sich nicht. Pool voll = Queue oder Ablehnung.",
    begruendung: "Bestätigt und nachgeschärft: Interferenzen auch innerklientlich verboten.",
  },
  {
    id: "C05",
    thema: "Belegung und virtuelle Timer",
    vorschlag:
      "„20 Klienten“ ist ein Beispiel für gleichzeitige Plattformnutzung, keine Obergrenze der Timer. Viele virtuelle Harmonisierungskanäle pro Klient. GPU-DSP-Jobs fair 1–4 im 16-GB-Pool. Emitter weiter exklusiv 1. Uhr und Kanalzustand: CPU + Postgres, nicht VRAM.",
    begruendung:
      "Bestätigt in Ihrer Präzisierung. Ein Timer-Zustand ist klein (RAM). Persistenz nach Reset verlangt eine Disk-Uhr — VRAM überlebt keinen Reboot und keinen Driver-Reset.",
  },
  {
    id: "C06",
    thema: "Analyse-Zwischenablage",
    vorschlag:
      "AnalysisDraft (tenant + Klient + Praktiker). Promote einziger Weg in die Spur. CopyGuard vor Sicht und Promote.",
    begruendung: "Bestätigt.",
  },
  {
    id: "C07",
    thema: "Harmonisierungsspur",
    vorschlag:
      "queued → armed → running ⇄ paused → stopped → archived | deleted. Parallel je Kanal, Server-Uhr, Command+ACK.",
    begruendung: "Bestätigt.",
  },
  {
    id: "C08",
    thema: "WebSocket-Fachkanal",
    vorschlag:
      "Ein Kanal: Analyse-Progress, Clipboard, Ticks, ACK. Commands nur Debian. Kein Zeugenklartext.",
    begruendung: "Bestätigt.",
  },
  {
    id: "C09",
    thema: "Kozyrev p-adisch",
    vorschlag:
      "Kernel kozyrev.padic.haar.v1 (p=2 = Haar-DWT + optional Vladimirov). CPU klein, CUDA Batch. UI: Rechenmodell.",
    begruendung: "Bestätigt.",
  },
  {
    id: "C10",
    thema: "Kozyrev REG",
    vorschlag:
      "Kernel kozyrev.reg.v1, Quelle immer simulated oder derived. Nie still mit p-adisch vermischt.",
    begruendung: "Bestätigt.",
  },
  {
    id: "C11",
    thema: "GPS-PPS",
    vorschlag: "Nur Uhr für aurelia-timerd (chrony). Kein c2-Sensor.",
    begruendung: "Bestätigt.",
  },
  {
    id: "C12",
    thema: "Draft-Edits",
    vorschlag:
      "Praktiker legt an. Klient nur client_editable_fields. Promote durch Praktiker plus CopyGuard.",
    begruendung: "Bestätigt.",
  },
];

/** Kept as ZUR_BESTAETIGUNG alias so older imports do not rot during the slice. */
export const ZUR_BESTAETIGUNG = C_GESETZT;

export const X_LAGE_DEFINITION = {
  "nicht umsetzbar":
    "Physik der Karte, fehlende API, Recht (D01/HWG/DSGVO) oder ein Stop-Gate machen genau diese Bauweise unmöglich oder unzulässig. Es gibt keinen haltbaren Workaround, der dasselbe verspricht.",
  "nicht relevant":
    "Wäre technisch denkbar oder existiert als Idee in einem Anhang, gehört aber nicht in dieses Produkt, diese Phase oder diese Hardware. Bau würde Haltbarkeit, VRAM oder EEAT verbrennen, ohne den Wellbeing-Kern zu tragen.",
} as const;

export const X_KATALOG: XRow[] = [
  {
    id: "X01",
    thema: "MIG-Partition der Ada",
    kategorie: "nicht umsetzbar",
    vorschlag: "Hardware-Scheiben je Mandant oder Job",
    begruendung:
      "NVIDIA Multi-Instance GPU gibt es auf A100/H100, nicht auf der RTX 4000 SFF Ada. Die Karte kann den Speicher nicht in isolierte Hardware-Slices schneiden. Isolation muss aurelia-gpud im Software-Scheduler leisten (C04): Stream, Arena, Drain, Tests auf Cross-Job-Tensoren.",
  },
  {
    id: "X02",
    thema: "Ebenso viele volle CUDA-Occupancies wie Klienten",
    kategorie: "nicht umsetzbar",
    vorschlag: "Jeder aktive Klient hält dauerhaft mehrere GB VRAM",
    begruendung:
      "20 GB minus 4 GB Runtime/Kopf lassen 16 GB Job-Pool. Ein Analyse- oder Quantum-Job kann 1–8 GB ziehen. Zwanzig volle Occupancies gleichzeitig überbuchen die Karte zwingend (OOM oder stilles Throttling). Time-Sharing plus Queue ist Physik, kein Geiz. Virtuelle Timer zählen hier nicht — die liegen nicht im VRAM (C05, D20).",
  },
  {
    id: "X03",
    thema: "CopyGuard-LLM resident auf CUDA",
    kategorie: "nicht umsetzbar",
    vorschlag: "Wächter dauerhaft in 3 GB VRAM",
    begruendung:
      "Widerspricht C01/C02, die Sie bestätigt haben. Der Wächter muss bei GPU-Last weiterlaufen und darf den Job-Pool nicht verdrängen. 128 GB DDR5 plus NVMe-mmap sind der richtige Ort. CUDA-Inference für CopyGuard wäre ein Rückfall in das verworfene 3/3/12/2-Budget.",
  },
  {
    id: "X04",
    thema: "Qwen2.5-14B oder Llama-3.1-8B als Betrieb",
    kategorie: "nicht relevant",
    vorschlag: "Große Demo-Modelle aus der Karten-Benchmark als Wächter oder Analyse-KI",
    begruendung:
      "Die Anbieter-Scores (268 / 507) sind Marketing der Workstation-Karte, kein Betriebsmodus. 8B/14B Q4 würden den 16-GB-Job-Pool oder den RAM-Wächter sprengen und C01 verletzen. Phi-4-mini / Gemma 3 4B bleiben der Wächter. Fachrechnen bleibt Kernel, nicht ein zweites LLM.",
  },
  {
    id: "X05",
    thema: "3-Tier-KI aus dem zweiten Kozyrev-Dokument",
    kategorie: "nicht relevant",
    vorschlag: "c2-Autoencoder, TRI-LSTM, Morphic-Transformer, XGBoost-Heilmittel auf der Ada",
    begruendung:
      "Baubar im Labor, aber es widerspricht dem bestätigten CUDA-Zweck (C01), dem VRAM-Budget (C03) und D01 (Heilmittel, Torsionsfeld, Time-to-Zero). Ein Transformer „wie ein LLM“ auf derselben Karte wäre genau das, was Sie von der Ada fernhalten wollten. Kein Heimlich-Pfad.",
  },
  {
    id: "X06",
    thema: "GPS-PPS-Jitter als Messung der Zeitdichte c2",
    kategorie: "nicht umsetzbar",
    vorschlag: "Hardware-Jitter gegen PPS als Kozyrev-c2-Sensor",
    begruendung:
      "PPS ist eine Taktquelle. Abweichungen messen Oszillator- und Pfadqualität, keine physikalische „Zeitdichte“. Es gibt keine etablierte, nachvollziehbare Messtechnik, die diesen Sprung hält. denselben Anschluss nutzen wir ehrlich: chrony für aurelia-timerd (C11). Als c2-Sensor wäre jeder Passport eine Falschbezeichnung (D06, X20).",
  },
  {
    id: "X07",
    thema: "Weltenformel, Petrov-Gleichungen, Heilmittel-Ranking, Time-to-Zero",
    kategorie: "nicht umsetzbar",
    vorschlag: "Mathematisch-esoterischer Heilkern mit Remedy-Scores und Heilungsfrist in Tagen",
    begruendung:
      "HWG und UWG verbieten Krankheitsbehandlung und unverifizierbare Wirkversprechen in diesem Produkt. D01 ist gesetzt. CopyGuard müsste die Texte blocken. Es gibt keine replaybare, quellenstempelbare Implementierung, die EEAT überlebt. Das ist Recht, nicht Geschmack.",
  },
  {
    id: "X08",
    thema: "RT-Cores für holographische Torsions-Fibonacci",
    kategorie: "nicht relevant",
    vorschlag: "Raytracing-Kerne der Ada als Torsionsfeld-Renderer",
    begruendung:
      "RT-Cores beschleunigen Bounding-Volume-Hierarchien für Grafikstrahlen. Es gibt kein seriöses Mapping auf Harmonisierung oder p-adische DSP. Der Aufwand würde Live-UX und VRAM fressen, ohne einen Kernel-Vertrag zu erfüllen. Ungenutzt lassen.",
  },
  {
    id: "X09",
    thema: "16-Kanal-EEG und EDA als Produktkern",
    kategorie: "nicht relevant",
    vorschlag: "Klinische EEG-Kappe / Hautleitwert als Standard-Ingest",
    begruendung:
      "EEG-Kappen ziehen MDR- und Diagnose-Nähe nach sich, die D01 geschlossen hat. Sie haben EEG ausdrücklich gestrichen. HRV per Ohrclip ist ein anderer Track (U12): 1D-PPG/RR, Wellbeing, kein Hirnstrom. EDA bleibt draußen, bis Sie es extra öffnen.",
  },
  {
    id: "X10",
    thema: "1-MHz-Sensorpipeline",
    kategorie: "nicht relevant",
    vorschlag: "Dauerhaft 1 Million Samples/s vom Sensor in die Ada",
    begruendung:
      "Am M G1 und am Ohrclip sind keine 1-MHz-Wandler belegt. HRV-RR liegt bei wenigen Hertz bis wenigen hundert Hz Roh-PPG. Eine Megahertz-Pipeline wäre totgeborene Bandbreite. Wenn später ein Sensor das wirklich liefert, neuer Kernel mit Budget — nicht jetzt.",
  },
  {
    id: "X11",
    thema: "WebUSB / Browser-HID für Spooky2 und Generator X Pro",
    kategorie: "nicht umsetzbar",
    vorschlag: "Handy oder Tablet spricht den Generator direkt per WebUSB",
    begruendung:
      "Spooky2-GUI ist Windows; Linux spricht CP210x als ttyUSB am Server. WebUSB ist nicht exklusiv, nicht lease-fähig, auf iOS unbrauchbar und würde Arming in den Browser legen — das bricht D14 und die Server-Uhr. HRV-Ohrclip am Klienten-Gerät ist ein anderer Pfad (Web Bluetooth oder Praxis-USB), nicht dasselbe Gerät.",
  },
  {
    id: "X12",
    thema: "Physische Kozyrev-Dioden oder -Spiegel in den Chips",
    kategorie: "nicht relevant",
    vorschlag: "Bauteile in Ryzen oder Ada, die Zeitwellen spiegeln",
    begruendung:
      "Das zweite Anhangdokument sagt selbst: es sind Software-Algorithmen, keine mystischen Strukturen in Silizium. Es gibt nichts zu löten und nichts zu aktivieren. Relevant ist nur, welche Kernel auf CPU/GPU laufen (D19).",
  },
  {
    id: "X13",
    thema: "N. A. Kozyrev-Physik als Nachweis",
    kategorie: "nicht umsetzbar",
    vorschlag: "UI oder Passport behauptet gemessene Torsionsfelder oder Zeitwellen",
    begruendung:
      "Das ist keine etablierte Laborphysik und fällt unter D01/EEAT. S. V. Kozyrev 2002 (p-adische Wavelets) ist ein anderes Werk und bleibt als Rechenkern (C09). Die Namenskollision darf die UI nicht verwischen. Ein „Nachweis“ im Ausweis wäre X20 (Falschquelle).",
  },
  {
    id: "X14",
    thema: "Lovable als CUDA- oder Control-Plane",
    kategorie: "nicht umsetzbar",
    vorschlag: "Auth, RLS, Timer, USB, Zeugen in Lovable/Supabase",
    begruendung:
      "Ist-Stand Kapitel 11: 0 Tabellen, 0 RLS, 0 Functions, Publish nie, Region unbelegt. Lovable hat keine GPU-, USB- oder langlaufende Worker-Garantie. Art.-9-Daten dorthin zu legen wäre Drittland- und Control-Plane-Bruch (D03). Preview darf bleiben, Akte nicht.",
  },
  {
    id: "X15",
    thema: "Schreiben nach /opt/radiquant4, Force-Push, Publish, Build 0 von Null",
    kategorie: "nicht umsetzbar",
    vorschlag: "Altes Repo oder Lovable-Produktion als Ziel dieser Session",
    begruendung:
      "Stop-Gate aus Kapitel 11 und D16. Das alte FastAPI-Repo ist Referenz. Cloud-Build hat bereits Build 0 in 65868a6. Ein zweiter Writer oder ein History-Rewrite zerstört den Altstand. Diese Session schreibt nur aurelia.",
  },
  {
    id: "X16",
    thema: "Cloud-LLM über Akten-Copy",
    kategorie: "nicht umsetzbar",
    vorschlag: "GPT/Claude/Grok-Cloud prüft Analyse- oder Reporttexte",
    begruendung:
      "Akten-Copy ist Art. 9 bzw. praxisnah. Ein Cloud-LLM ist Drittland, Auftragsverarbeitung und oft Training. D13 verlangt lokalen Wächter. C02 legt ihn in den RAM. Es gibt keinen AVV-Pfad, der das in Phase 0/1 heil macht.",
  },
  {
    id: "X17",
    thema: "Medizinische Lesart von Merkmalen",
    kategorie: "nicht umsetzbar",
    vorschlag: "„Gesunder Schlaf“, Stress-Diagnose, Krankheitsbezug aus p-adischen oder HRV-Zahlen",
    begruendung:
      "D01 und HWG. Zahlen dürfen mit Quelle im Passport stehen (HRV-RMSSD = derived). Texte, die daraus Krankheit oder Heilung machen, blockt CopyGuard. Das gilt erst recht, sobald ein Ohrclip RR-Intervalle liefert (U12).",
  },
  {
    id: "X18",
    thema: "Zwei Sessions auf einem Generator X Pro",
    kategorie: "nicht umsetzbar",
    vorschlag: "Mehrere Harmonisierungsspuren teilen sich denselben Emitter gleichzeitig",
    begruendung:
      "Ein USB-Generator ist ein exklusives Gerät. D14: Lease → Arming → ACK. Occupied = Warteschlange. Viele virtuelle Timer (C05) ändern das nicht — Timer sind Zustände, Emission ist Hardware. GPU-Jobs und Emitter bleiben getrennte Leases.",
  },
  {
    id: "X19",
    thema: "Service Worker in Phase 0/1 und Zeugen im CDN",
    kategorie: "nicht relevant",
    vorschlag: "Offline-PWA cached Sitzungsbilder und Session-Audio",
    begruendung:
      "Build 0 hat den Service Worker bewusst aus. Ein SW legt Zeugen in den Disk-Cache des Browsers — genau das, was D15 mit no-store verhindert. Öffentliche Marke darf long-cache. Sitzung nicht. Später, nach Wipe-Konzept und Opt-in, neu entscheiden — nicht jetzt.",
  },
  {
    id: "X20",
    thema: "Stiller Simulationsfallback, der wie Messung wirkt",
    kategorie: "nicht umsetzbar",
    vorschlag: "Wenn GPU, Sensor oder Emitter fehlt, trotzdem „gemessen“ anzeigen",
    begruendung:
      "D06: jede Zahl braucht eine Quelle (simulated / measured / derived / manual / ai-generated). Ein Fallback ohne Stempel fälscht den Ausweis, auch nach einem Reboot, auch bei HRV-Lücken. Lieber Status not-available als eine erfundene Messung.",
  },
];

export const X_STATUS = {
  stand: "akzeptiert",
  am: "2026-08-24",
  satz: "Operator akzeptiert den X-Katalog samt Kategorien nicht umsetzbar / nicht relevant. Kozyrev folgt den Empfehlungen (K1–K5, nicht K6–K8).",
} as const;

/**
 * U-points resolved 2026-08-23: U01 by C05 restatement, U12 by HRV earclip,
 * remainder by operator: follow the recommendation.
 */
export const U_GESETZT: FreigabeRow[] = [
  {
    id: "U01",
    thema: "Was die Zahl 20 bedeutet",
    vorschlag:
      "Beispiel für gleichzeitige Klienten auf der Plattform, nicht die Timer-Kapazität. Viele virtuelle Kanäle pro Klient (Default-Quota 16, hebbar). GPU-DSP 1–4 concurrent. Emitter 1.",
    begruendung: "Von Ihnen präzisiert. Details D20.",
  },
  {
    id: "U02",
    thema: "Klient-Edits",
    vorschlag: "Nur client_editable_fields, Promote durch Praktiker (C12).",
    begruendung: "Empfehlung übernommen.",
  },
  {
    id: "U03",
    thema: "Mehrere Spuren pro Klient",
    vorschlag: "Ja, bis Quota. Emitter trotzdem max. 1 global.",
    begruendung: "Folgt aus C05. Timer ≠ Generator.",
  },
  {
    id: "U04",
    thema: "p=3/5 in v1",
    vorschlag: "Nein. v1 nur p=2 Haar. p>2 Labor-Mandant.",
    begruendung: "Empfehlung übernommen. Haar ist bibliotheksreif.",
  },
  {
    id: "U05",
    thema: "REG-Modul",
    vorschlag: "Ja, getrennt, Quelle simulated (C10).",
    begruendung: "Empfehlung übernommen.",
  },
  {
    id: "U06",
    thema: "cuQuantum-Pool",
    vorschlag: "Gleicher 16-GB-Pool, opt-in, nie CopyGuard-RAM stehlen.",
    begruendung: "Empfehlung übernommen.",
  },
  {
    id: "U07",
    thema: "CopyGuard-Redundanz",
    vorschlag: "Gewichte auf beiden NVMe, eine Runtime, Gemma 3 1B Fallback.",
    begruendung: "Empfehlung übernommen.",
  },
  {
    id: "U08",
    thema: "Tick-Rate",
    vorschlag:
      "UI-Harmonisierung 50 ms aus timerd-RAM. Durable Checkpoint der Uhr 500–1000 ms nach Postgres. Analyse-Progress 200 ms. Mobilfunk darf droppen, nicht erfinden.",
    begruendung: "Nachgeschärft: 50 ms fsync jedes Ticks wäre Schreibamplifikation, kein Genauigkeitsgewinn nach Reset.",
  },
  {
    id: "U09",
    thema: "Phase 1",
    vorschlag: "Gehäuse. Startwort 2026-08-24.",
    begruendung: "Genehmigt. Auth an, Mandant synthetic, keine Klientenakten.",
  },
  {
    id: "U10",
    thema: "Draft-TTL",
    vorschlag: "7 Tage, Archiv-Vorschlag, kein Auto-Delete.",
    begruendung: "Empfehlung übernommen.",
  },
  {
    id: "U11",
    thema: "D08–D12",
    vorschlag: "D08/D10/D12 gesetzt. D09 Preise und D11 Codecs Wiedervorlage.",
    begruendung: "Operator 2026-08-24: Empfehlungen plus kein Video.",
  },
  {
    id: "U12",
    thema: "HRV-Ohrclip, kein EEG",
    vorschlag:
      "Sensorklasse hrv.earclip. Clip sitzt am Menschen, nicht im Rack. Remote: Web Bluetooth oder Praxis-USB-Relay → RR-Intervalle über den Fachkanal. Server speichert derived, CopyGuard auf Text, DSP-Kernel generisch (auch p-adisch auf RR). Kein WebUSB für Spooky2. Kein EEG.",
    begruendung:
      "Von Ihnen gesetzt. Der GPU-Server hat nicht 20 Ohrclips an der Rückseite — das wäre physikalisch falsch. Art. 9 gilt für die RR-Reihe.",
  },
];

export const UNKLAR = U_GESETZT;
