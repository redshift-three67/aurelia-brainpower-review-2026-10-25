export type DecisionLock = "gesetzt" | "empfohlen" | "zur-bestaetigung";

export type Decision = {
  id: string;
  title: string;
  chapter: string;
  lock: DecisionLock;
  summary: string;
  recommendation: string;
  why: string;
  alternative: string;
  riskIfIgnored: string;
};

export const CANONICAL_DECISION_LOCKS = {
  D01: "gesetzt",
  D02: "gesetzt",
  D03: "gesetzt",
  D04: "gesetzt",
  D05: "gesetzt",
  D06: "gesetzt",
  D07: "gesetzt",
  D08: "gesetzt",
  D09: "empfohlen",
  D10: "gesetzt",
  D11: "empfohlen",
  D12: "gesetzt",
  D13: "gesetzt",
  D14: "gesetzt",
  D15: "gesetzt",
  D16: "gesetzt",
  D17: "gesetzt",
  D18: "gesetzt",
  D19: "gesetzt",
  D20: "gesetzt",
  D21: "gesetzt",
  D22: "gesetzt",
  D23: "gesetzt",
  D24: "gesetzt",
} as const satisfies Record<string, DecisionLock>;

export const DECISIONS: Decision[] = [
  {
    id: "D01",
    title: "Wellbeing-Compliance, kein Medizinprodukt",
    chapter: "Leitplanken",
    lock: CANONICAL_DECISION_LOCKS.D01,
    summary:
      "AURELIA ist Wellbeing- und Dokumentationssoftware für ausgebildete Praktiker. Keine Diagnose, keine Therapiezusage, kein Heilversprechen, kein MDR-Zweck. Alle sichtbaren Texte (UI, Analyse, Harmonisierung, Reports, importierte Kataloge, Zwischenablage) laufen durch CopyGuard.",
    recommendation:
      "Zweckbestimmung: Wellbeing / komplementäre Praxisorganisation. HWG und UWG: keine Krankheitsbehandlung in Werbung oder Sitzungstext. Pflicht: Disclaimer, Impressum, Datenschutz. CopyGuard vor jeder Veröffentlichung eines Textes.",
    why: "Google YMYL und HWG bestrafen denselben Fehler. Der Ist-Stand in radiquant-cloud-build ist bereits ‚Wellbeing, keine medizinische Diagnose‘.",
    alternative: "MDR-Pfad nur als eigener Track nach ausdrücklicher Zweckänderung.",
    riskIfIgnored:
      "Abmahnung, Indexverlust, unzulässige Medizinprodukteabgabe, unkontrollierte Heilstexte.",
  },
  {
    id: "D02",
    title: "Art.-9-Daten und Compute nur auf dem gemessenen Debian-Server",
    chapter: "Architektur",
    lock: CANONICAL_DECISION_LOCKS.D02,
    summary:
      "Zeugen, Sitzungen, Ergebnisse und Emitter bleiben auf GPU Server M G1. VRAM-Zahlen ändern sich: CUDA wird Job-Pool, CopyGuard rutscht in den RAM. Host-Fakten bleiben gesetzt.",
    recommendation:
      "Host unverändert: Ryzen 5 9600X, RTX 4000 SFF Ada 20 GB, 128 GB DDR5, 2×1 TB NVMe, 2×1 Gbit/s, IPMI, redundantes Netzteil. VRAM neu (C03): 2 GB Runtime, 16 GB Job-Pool, 2 GB Kopf. CopyGuard = 0 GB VRAM. NVMe: Akten-Spiegel plus Modell-Replica.",
    why: "Ihre Vorgabe a macht das alte 3/3/12/2-Budget falsch. Die Karte hat kein MIG. 20 parallele Occupancies passen nicht in 20 GB.",
    alternative: "Beim alten 3-GB-CopyGuard-Slot bleiben — dann fehlen 3 GB im Echtzeit-Pool.",
    riskIfIgnored: "Wächter und Analyse kämpfen um dieselbe Karte, oder Overcommit.",
  },
  {
    id: "D03",
    title: "Lovable: Preview und Gestaltung — nicht Control-Plane",
    chapter: "Architektur",
    lock: CANONICAL_DECISION_LOCKS.D03,
    summary:
      "Lovable-Projekt ccecde78-… ist an radiquant-cloud-build angebunden. Tabellen, RLS, Functions, Publish: nicht umgesetzt. Control-Plane bleibt Debian.",
    recommendation:
      "Nicht disconnecten. Nicht für Auth, USB, CUDA, Timer, Zeugen. Kein Force-Push auf Branch radiquant4.",
    why: "Ist-Stand Kapitel 11: leere Control-Plane. Das ist Architekturgrenze.",
    alternative: "Cloud-Control für Ciphertext-Refs erst nach Region, AVV, DSFA.",
    riskIfIgnored: "Vendor-Lock, Art.-9 in Scaffold-DB, Split-Brain.",
  },
  {
    id: "D04",
    title: "Mandanten: Shared Schema plus RLS, Isolation erst beweisen",
    chapter: "Mandanten",
    lock: CANONICAL_DECISION_LOCKS.D04,
    summary:
      "Produktiv gilt RLS auf Debian. Rolle client fail-closed bis Grant. Jeder CUDA-Buffer, jeder Timer-Kanal und jeder Draft trägt (tenant_id, client_id, job_id).",
    recommendation:
      "Jede Query und jeder GPU-Buffer tenant-scoped. Negative Isolationstests. dataClass synthetic bis Grant.",
    why: "20 parallele Klienten ohne Tenant-Marke auf dem Buffer sind ein Leak, kein Scheduler.",
    alternative: "Schema-per-Tenant nach dem ersten Isolationstest.",
    riskIfIgnored: "Cross-Tenant-Leak — Stop-the-line.",
  },
  {
    id: "D05",
    title: "Server ist die Uhr: Live, WebSocket, kein Browser-USB",
    chapter: "Compute",
    lock: CANONICAL_DECISION_LOCKS.D05,
    summary:
      "Analyse, Harmonisierung, Timer, Emitter-Lease laufen auf Debian. WebSocket trägt Analyse-Progress, Clipboard und Harmonisierungskommandos. Backbone senkt RTT, verlagert kein Compute. Die Uhr selbst liegt in timerd plus Postgres, nicht im VRAM.",
    recommendation:
      "aurelia-timerd (CPU, RAM-Arbeitsspeicher) + Postgres als dauerhafte Uhr + aurelia-gpud + aurelia-emitterd. UI nur aus RunEvents. Commands (start/pause/stop) client→server, ACK zurück. Kein WebRTC und kein WebUSB. HRV-Ohrclip: eigener Sensorpfad (D21).",
    why: "Ihre Vorgabe c. Tab-Schlaf lügt weiter über die Zeit — unabhängig von der Backbone-Lage.",
    alternative: "Getrennte Sockets für Analyse und Harmonisierung — mehr Drift, kein Gewinn.",
    riskIfIgnored: "Browser als Uhr, oder Klartext-Zeugen auf dem Socket.",
  },
  {
    id: "D06",
    title: "Dual-Modus plus CopyGuard-Stempel im Ausweis",
    chapter: "Compute",
    lock: CANONICAL_DECISION_LOCKS.D06,
    summary:
      "Default strikt. Stochastik/Quantum opt-in. Jeder Lauf: Passport mit Kernel-Hash, tenant_id, copyguard_digest. Zahlen brauchen eine Quelle.",
    recommendation:
      "executable: false / isHardwareActivatable: false bis Hardware-Gate. Kozyrev-REG immer simulated/derived. p-adische Haar-DWT darf strikt sein.",
    why: "151 Tests und ehrliche Copy in 65868a6 sind das Niveau.",
    alternative: "Forschungstenants: seeded Ensembles, getrennt gekennzeichnet.",
    riskIfIgnored: "Ergebnisse, die niemand wiederholen oder rechtlich halten kann.",
  },
  {
    id: "D07",
    title: "Kernel-ABI: sechs Cores andocken, nicht kopieren",
    chapter: "Module",
    lock: CANONICAL_DECISION_LOCKS.D07,
    summary:
      "Sextett: Radi144, RadiWorks, RadiMorphic, RadiBlohm, RadiThoms, RadiCopen. Kozyrev-Kerne sind DSP hinter derselben ABI, keine siebte Marketingmarke ohne Vertrag.",
    recommendation:
      "Nächster fachlicher Slice im Altprodukt: read-only RadiMorphic-Intake. Kozyrev.padic und kozyrev.reg nur als Kernel-IDs, sobald C09/C10 bestätigt.",
    why: "Stop-Gate: nicht Build 0 von Null, nicht /opt/radiquant4.",
    alternative: "Nur neue Referenzkernels, falls ein Prototyp nicht isolierbar ist.",
    riskIfIgnored: "Doppelte Fachlogik, globales RNG, Namenschaos Kozyrev.",
  },
  {
    id: "D08",
    title: "Identität: Passkeys plus TOTP, kein Social-Login",
    chapter: "Identität",
    lock: CANONICAL_DECISION_LOCKS.D08,
    summary:
      "Rollen: Plattform-Admin, Mandanten-Admin, Therapeut, Assistenz, Klient, System. Step-up für Promote, Harmonisierung starten, Emitter-Arming, Zeugen löschen. Produktpfad: Passkeys plus TOTP, kein Social-Login.",
    recommendation:
      "Auf GPU Server M G1: Passkeys primär, TOTP Fallback. In dieser Vorschau-Umgebung (Grok-Host): E-Mail/Passwort, weil Passkeys hier nicht unterstützt werden. Google/X sind Host-Methoden, nicht der Produktpfad.",
    why: "Phase 1 gestartet. Praxisdaten sind keine Social-App. Der Host zwingt die Vorschau auf unterstützte Methoden; Debian bleibt D08-rein.",
    alternative: "Keycloak auf Debian für Klinik-OIDC.",
    riskIfIgnored: "Account-Takeover, unklare Verantwortlichkeit.",
  },
  {
    id: "D09",
    title: "Abos: Quotas an VRAM, Timer-Kanälen, Emittern",
    chapter: "Identität",
    lock: CANONICAL_DECISION_LOCKS.D09,
    summary:
      "Quotas binden GPU-DSP-Jobs, Harmonisierungskanäle, Zwischenablagen, Emitter-Leases, Speicher. 20 Klienten ist ein Beispiel für Belegung. Virtuelle Timer sind zahlreich und billig; CUDA-Occupancy bleibt knapp.",
    recommendation:
      "Default-Quota 16 Harmonisierungskanäle pro Klient, hebbar durch Mandanten-Admin. GPU-DSP 1–4 concurrent im 16-GB-Pool. Emitter immer exklusiv 1. CPU-only-Stufe ohne GPU-Job.",
    why: "20 GB und ein USB-Generator sind harte Güter. C05 muss dazu passen.",
    alternative: "Selbstbedienung erst nach Kündigungs- und Löschfristen.",
    riskIfIgnored: "GPU-Kollision, Emitter-Doppelbelegung.",
  },
  {
    id: "D10",
    title: "Kein Video — WebRTC nicht im Produkt",
    chapter: "Sicherheit",
    lock: CANONICAL_DECISION_LOCKS.D10,
    summary:
      "Kein Video zwischen Therapeut und Klient. Kein WebRTC, kein TURN, keine Aufnahme. Live bleibt WebSocket für Analyse- und Harmonisierungsticks.",
    recommendation: "Phase 9 entfällt. Audio-Cues (Opus) für Harmonisierung bleiben später erlaubt, Bildtelefonie nicht.",
    why: "Operator 2026-08-24: O08 — Entscheidung, keine Videos.",
    alternative: "Externer EU-Konferenzdienst außerhalb von AURELIA, mit eigenem AVV — nicht in diesem Produkt.",
    riskIfIgnored: "Scope-Krieg, Mitschnitte, verzögerter Kern.",
  },
  {
    id: "D11",
    title: "Medien: AVIF/Opus/zstd — Zeugen nie im CDN",
    chapter: "Sicherheit",
    lock: CANONICAL_DECISION_LOCKS.D11,
    summary: "Kompression vor Envelope-Encryption. Öffentliches CDN nur für Marke.",
    recommendation: "Siehe D15. Adaptive Bitrate, keine unnötigen Videobilder.",
    why: "Bandbreite und Schutz gleichzeitig.",
    alternative: "JPEG XL als Archivoption später.",
    riskIfIgnored: "Zeugen im Klartext oder unspielbare Live-UX.",
  },
  {
    id: "D12",
    title: "Barrierefreiheit und EEAT sind Muss",
    chapter: "Gestaltung",
    lock: CANONICAL_DECISION_LOCKS.D12,
    summary: "WCAG 2.2 AA, BFSG, ruhige Kontraste, 44-px-Ziele, reduced motion.",
    recommendation:
      "Heilsam ohne Therapiebehauptung. Jede Zahl mit Quellenstempel. Kozyrev-Namen nur mit der mathematischen oder der simulierten Herkunft, nie vermischt.",
    why: "BFSG gilt. Namenskollision S.V. / N.A. Kozyrev ist ein EEAT-Risiko.",
    alternative: "Keine.",
    riskIfIgnored: "Recht und Glaubwürdigkeit.",
  },
  {
    id: "D13",
    title: "CopyGuard: lokal, schmal, im RAM — nicht auf der Ada",
    chapter: "Wellbeing",
    lock: CANONICAL_DECISION_LOCKS.D13,
    summary:
      "Jeder Text aus Analyse, Harmonisierung, Report, UI, Katalog und Zwischenablage wird geprüft, bevor ein Mensch ihn sieht oder ein PDF entsteht. Das Modell sitzt im RAM/NVMe, nicht im VRAM.",
    recommendation:
      "Lexikon fail-closed plus Phi-4-mini Q4 oder Gemma 3 4B Q4, mmap von NVMe, Replica auf der zweiten Platte. CPU-Fallback Gemma 3 1B. allow / rewrite / block plus reason_code, Digest in den Passport. Kein Cloud-LLM, kein CUDA-Resident.",
    why: "Ihre Vorgabe a. Der Wächter darf Echtzeitjobs nicht verdrängen und muss bei GPU-Last weiterlaufen.",
    alternative: "Nur Lexikon — schneller, blind gegen Paraphrasen.",
    riskIfIgnored: "Entweder Heilstexte oder ein blockierter Job-Pool.",
  },
  {
    id: "D14",
    title: "Emitter-HAL: Spooky2 nur über Debian-Daemon",
    chapter: "Live",
    lock: CANONICAL_DECISION_LOCKS.D14,
    summary:
      "Generator X Pro / XM hängen am Server per USB (CP210x → /dev/ttyUSB*). GPU-Job und Emitter sind getrennte Leases.",
    recommendation:
      "aurelia-emitterd: Lease → Arming → ACK → Emission → Reset. Occupied = Warteschlange. Kein WebUSB. Bis Hardware-Gate deklarativ false.",
    why: "Ein Generator ist nicht 20-fach teilbar. Isolation der CUDA-Jobs ändert das nicht.",
    alternative: "Windows-Companion hinter demselben Lease — nicht Default.",
    riskIfIgnored: "Zwei Sessions auf einem Generator, oder UI die Emission vortäuscht.",
  },
  {
    id: "D15",
    title: "Cache, Wischen, Live-Darstellung, WebSocket-Fachkanal",
    chapter: "Live",
    lock: CANONICAL_DECISION_LOCKS.D15,
    summary:
      "Marke darf cachen. Zeugen nicht. WebSocket ist der Fachkanal für Analyse und Harmonisierung. Wischen leert Object-URLs, Cache API, IndexedDB.",
    recommendation:
      "Zeugen: Cache-Control private, no-store. Live: Binary-Ticks, Canvas/SVG, Opus-Cues. Analyse-Progress und Harmonisierungs-ACK über denselben Socket. Service Worker in Phase 0/1 aus. UI-Ticks 50 ms aus timerd-RAM; durable Checkpoint 500–1000 ms (D20, U08).",
    why: "Vorgabe c plus niedrige Backbone-RTT. 1-Gbit-NIC der Maschine bleibt die Kante.",
    alternative: "Ciphertext im Cache API nur nach Opt-in, tenant-scoped, hartes TTL.",
    riskIfIgnored: "Aktenreste, erfundene Ticks, vorgetäuschte Live-Bilder.",
  },
  {
    id: "D16",
    title: "Repo-Matrix: drei Bäume, ein Schreibziel pro Session",
    chapter: "Repos",
    lock: CANONICAL_DECISION_LOCKS.D16,
    summary:
      "Diese Session schreibt nur redshift-three67/aurelia. Cloud-Build ist Altprodukt. radiquant4 ist tote Referenz.",
    recommendation:
      "Kein Disconnect, kein Force-Push, kein Merge der Cores ohne Intake. Codename radiquant4 ist Branch-Name.",
    why: "Kapitel 11. Ein Writer pro Zeitfenster.",
    alternative: "Verfassung später als docs/ in cloud-build spiegeln — nach Freigabe.",
    riskIfIgnored: "Zwei Writer, falsches Ziel, History-Rewrite.",
  },
  {
    id: "D17",
    title: "CUDA-Scheduler: nutzerisoliert, interferenzfrei, kein Overcommit",
    chapter: "Compute",
    lock: CANONICAL_DECISION_LOCKS.D17,
    summary:
      "aurelia-gpud vergibt den 16-GB-Job-Pool. Isolation auf (tenant_id, client_id, job_id): auch zwei Analysen oder eine Analyse und eine Harmonisierung desselben Klienten teilen keinen Buffer und keinen Default-Stream. Viele virtuelle Timer bedeuten nicht viele Occupancies.",
    recommendation:
      "Pre-flight gegen kernel.budget.vram_mb. Admit nur wenn Summe laufend + neu ≤ 16 GB. Fair-Queue nach Quota (D09). Nach Job: Stream destroy, Mempool-Trim. Telemetrie (Temp, ECC) darf pausieren. MPS höchstens intern, nie als Sicherheitsgrenze. MIG existiert hier nicht. Timer-Zustand gehört nicht in den Pool (D20).",
    why: "Ihre Vorgabe a. Isolation ohne MIG ist Scheduler-Arbeit plus Tests, die Cross-Tenant-Tensoren suchen.",
    alternative: "Strikt seriell ein Job global — interferenzfrei, aber langsam bei 20 Klienten.",
    riskIfIgnored: "Datenmix auf der GPU oder Karte im OOM.",
  },
  {
    id: "D18",
    title: "Zwischenablage vor der Harmonisierungsspur",
    chapter: "Daten",
    lock: CANONICAL_DECISION_LOCKS.D18,
    summary:
      "Eine Analyse liegt zuerst in der Zwischenablage, darf dort angepasst werden und wird erst danach in die klientenbezogene Harmonisierungsspur geschoben. Von dort: zeitgesteuert start, pause, stop, archivieren, löschen — auch parallel je Kanal.",
    recommendation:
      "AnalysisDraft → (CopyGuard) → optional Client-Felder → Praktiker-Promote → HarmonizationLane. Zustände der Spur: queued → armed → running ⇄ paused → stopped → archived | deleted. Kein stiller Copy. TTL 7 Tage, dann Archiv-Vorschlag, kein Auto-Delete (U10).",
    why: "Ihre Vorgabe b. Module reichen sich Artefakte, nicht Seiteneffekte.",
    alternative: "Direkt Scan→Timer — schneller, nicht auditierbar, CopyGuard zu spät.",
    riskIfIgnored: "Rohanalyse startet Harmonisierung, Klient überschreibt ohne Spur.",
  },
  {
    id: "D19",
    title: "Kozyrev-Kerne: S.V.-Math ja, N.A.-Physik nein",
    chapter: "Module",
    lock: CANONICAL_DECISION_LOCKS.D19,
    summary:
      "Zwei getrennte Kernel-Familien. kozyrev.padic.haar.v1 ist Haar-DWT plus optionaler Vladimirov-Faktor (Kozyrev 2002, Comm. Math. Phys.). kozyrev.reg.v1 ist statistisches Rauschen, Quelle simulated. Keine Torsionsfelder, keine c2-Messung, keine Weltenformel.",
    recommendation:
      "p=2 zuerst (Haar-Bibliotheken, AVX-512, CUDA-Filterbank). CPU für N≤2048, GPU für Batches. GPS-PPS nur als Uhr. 3-Tier-Transformer und Heilmittel-Ranking nicht bauen. UI trennt die Namen.",
    why: "Die Anhänge vermischen zwei verschiedene Kozyrevs. Nur der mathematische Teil ist implementierbar und EEAT-fähig. Der Rest verletzt D01 oder die Physik der Karte.",
    alternative: "Nur p-adisch — REG wäre streichbar gewesen; U05 behält es getrennt.",
    riskIfIgnored: "Physiktheater im Passport, CopyGuard-Dauerfeuer, VRAM an die falsche KI.",
  },
  {
    id: "D20",
    title: "Virtuelle Timer: CPU + Postgres sind die Uhr, GPU rechnet den Tick",
    chapter: "Compute",
    lock: CANONICAL_DECISION_LOCKS.D20,
    summary:
      "Viele Harmonisierungskanäle pro Klient sind leichtgewichtige Zustandsmaschinen. Die dauerhafte Wahrheit nach Reset liegt in Postgres (WAL). Der heiße Pfad liegt in aurelia-timerd im RAM. Die Ada rechnet nur dann, wenn ein Kanal DSP, Waveform oder Kernel braucht — und nur als Job im 16-GB-Pool, nie als Ledger.",
    recommendation:
      "Zustand und last_tick in Postgres, RLS, SKIP LOCKED je Kanal. UI-Ticks 50 ms aus RAM. Durable Checkpoint 500–1000 ms plus jeder Zustandswechsel (start/pause/stop) mit fsync. Nach Reboot: Kanäle in running/paused/armed laden, Lücke (now − last_checkpoint) in den Ausweis, nicht heimlich aufholen. Default-Quota 16 Kanäle/Klient, hebbar. Isolation (tenant_id, client_id, channel_id). GPU nie als Timer-Speicher: VRAM stirbt bei Reboot, Driver-Reset und Prozessende.",
    why: "Sie verlangen Persistenz nach Server-Reset und viele parallele virtuelle Timer ohne Interferenz. Genau das kann VRAM nicht. Ein Kanalzustand ist wenige KB — 128 GB RAM und Timescale tragen Hunderte von Kanälen. 50-ms-fsync jedes UI-Ticks wäre Schreibamplifikation ohne Genauigkeitsgewinn nach dem Crash.",
    alternative:
      "Redis AOF als Hot-Cache vor Postgres — zulässig, aber nicht statt WAL. Reines GPU-Resident-Ledger — unzulässig, weil flüchtig.",
    riskIfIgnored:
      "Nach einem Reboot erfundene Zeit, oder eine Ada die mit Timer-Metadaten statt DSP vollläuft, oder Interferenzen zwischen Kanälen desselben Klienten.",
  },
  {
    id: "D21",
    title: "HRV-Ohrclip am Menschen, nicht im Rack — kein EEG",
    chapter: "Live",
    lock: CANONICAL_DECISION_LOCKS.D21,
    summary:
      "Ein USB- oder BLE-Ohrclip liefert RR-Intervalle / PPG als 1D-Signal. Der Clip sitzt am Ohr der Person. Der GPU-Server im Rechenzentrum hat keine 20 Clips an der Rückseite. EEG bleibt draußen.",
    recommendation:
      "Sensorklasse hrv.earclip, bis Hardware-Gate deklarativ. Remote-Klient: Web Bluetooth (nicht WebUSB-Spooky2) oder Hersteller-SDK im Browser/Companion, RR über den Fachkanal, Envelope. Praxis vor Ort: USB am Praxis-Rechner, Relay-Daemon, nicht am Rack-Server. Speicherung derived, Quelle measured wenn der Clip ACK liefert sonst not-available. DSP darf kozyrev.padic.haar auf der RR-Reihe nutzen. CopyGuard blockt Stress- und Schlafdiagnose. Ein Clip = ein Klient, exclusive analog D14.",
    why: "U12. Art. 9 für die RR-Reihe. Physik: USB-Länge und Rechenzentrum passen nicht zusammen. D01: kein EEG-Medizinprodukt.",
    alternative: "Nur Praxis-USB, kein Remote-HRV — enger, ehrlicher, weniger Reichweite.",
    riskIfIgnored:
      "Schein-USB am GPU-Server, oder HRV-Texte die wie Befunde klingen, oder ein zweites WebUSB-Loch neben Spooky2.",
  },
  {
    id: "D22",
    title: "Kozyrev-Katalog: K1–K5 gesetzt, K6–K8 gesperrt",
    chapter: "Module",
    lock: CANONICAL_DECISION_LOCKS.D22,
    summary:
      "Nach zweiter Prüfung: Haar-DSP, REG, leerer Labor-Slot, p=3/5 und Haar-auf-HRV destabilisieren den Kern nicht. Autoencoder/LSTM/Transformer, Heilmittel-Ranking und PPS-als-c2 tun es — dafür gibt es keine Kernel-ID und keinen Schalter.",
    recommendation:
      "K1 default an, administrativ ausbar. K2–K5 default aus, administrativ anbar (AND-Kette). K6–K8: kein Scaffold, kein Flag, kein Reservieren einer ID. X05/X07 bleiben Ihre Pause, ändern aber nichts an der Sperre im Produktivpfad.",
    why: "Operator 2026-08-23: nur K1–K5, exakt nach Empfehlung, schaltbar. Zweite Prüfung bestätigt: Filterbanken und leere Verträge fressen den 16-GB-Pool nicht; 3-Tier und HWG-Outcomes tun es.",
    alternative: "K2–K5 dauerhaft aus lassen — zulässig, Schalter bleiben trotzdem liegen.",
    riskIfIgnored: "3-Tier rutscht über einen „Labor“-Schalter in die Ada, oder Haar ist unabschaltbar fest verdrahtet.",
  },
  {
    id: "D23",
    title: "Kernel-Schalter: AND-Kette, fail-closed, auditiert",
    chapter: "Module",
    lock: CANONICAL_DECISION_LOCKS.D23,
    summary:
      "Jeder zulässige Kozyrev-Kern und jede Labor-Capability ist administrativ an- und ausbar. Platform AND Mandant AND Sitzung. Fehlendes Flag = aus. Umschalten ist ein auditiertes Ereignis. Gesperrte IDs (K6–K8) haben bewusst keinen Schalter.",
    recommendation:
      "Flags in der Kernel-Registry, nicht in der UI-Config. Admit prüft Flag vor VRAM. UI blendet aus, fallbackt nicht. K5 folgt K1: Haar aus ⇒ on_hrv_rr tot. executable:false bei lab.* ist hart, kein Admin-Override ohne neues gesetztes Gate.",
    why: "Operator: optional aktivierbar und deaktivierbar, sofern möglich. So bleibt der Kern stabil, auch wenn eine Praxis Haar nicht will oder Labor nie öffnet.",
    alternative: "Nur globaler Superadmin-Schalter — zu grob für Mandantenisolation.",
    riskIfIgnored: "Stille Defaults, oder ein Mandant aktiviert 3-Tier über eine Lücke, die es nicht geben darf.",
  },
  {
    id: "D24",
    title: "Origin ist M G1 — öffentlicher Rand aus demselben Baum, Lovable nicht in der Laufzeit",
    chapter: "Architektur",
    lock: CANONICAL_DECISION_LOCKS.D24,
    summary:
      "H1–H3 gesetzt: GPU Server M G1 ist der einzige Origin. Verschlüsseltes EU-Offsite-Backup ist Pflicht. Öffentliche Pflichtseiten und Gestaltung leben in diesem Repo plus Caddy auf der Box. Lovable, Cloud-Auth, Cloud-GPU und Cloud-LLM sind nicht die Laufzeit.",
    recommendation:
      "Kein Lovable-Supabase, kein Publish, kein Cloud-Auth. Heritage-Link cloud-build↔Lovable darf tot liegen, bis Sie disconnecten (O03). Backup-SKU später (O04), vor dem ersten Art.-9-Datensatz. Designer arbeitet in redshift-three67/aurelia.",
    why: "Operator 2026-08-23: H1–H3 ab jetzt. Die Erstfassung nannte Hybrid Kern+Kante; die Kante war diese App.",
    alternative: "Kleines EU-VPS nur für statisches Marketing, falls Website-Uptime ≠ GPU-Wartung — unpersönlich, kein Login.",
    riskIfIgnored: "Zwei Wahrheiten, oder ein Server ohne Restore, oder Gestaltungsarbeit in einer leeren Cloud.",
  },
];

export const DECISION_STORAGE_KEY = "aurelia-decision-votes";

export type Vote = "zustimmen" | "aendern" | "offen";

export type VoteMap = Record<string, Vote>;

export const LOCK_LABEL: Record<DecisionLock, string> = {
  gesetzt: "gesetzt",
  empfohlen: "empfohlen",
  "zur-bestaetigung": "zur Bestätigung",
};
