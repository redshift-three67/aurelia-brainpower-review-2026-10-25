# Gemeinsame Punkte aller Module mit der Aurelia-Plattform

> Frage des Betreibers (2026-08-29): Welche Berührungspunkte teilen alle
> RadiX-Module mit Aurelia, was ist Plattform-, was Modulseite — und was muss
> bereits im PROTOTYP-Stadium berücksichtigt sein vs. was kommt erst bei der
> Integration? Quelle: Aurelia-Verfassung + docs (Stand 25.08.2026) und die
> Modul-Standards dieses Projekts. **This is a discussion paper (Evidenz,
> kein Kanon)** — Übernahme in Aurelia-Spezifikationen ist Betreiber-Akt.

## 1. Matrix: Berührungspunkt · Plattform · Modul · Prototyp-Stadium

| # | Berührungspunkt | Aurelia-Seite (Plattform) | Modul-Seite | Im Prototyp bereits? | Wird wirksam |
|---|---|---|---|---|---|
| 1 | **Mandanten/Klienten (Multitenant)** | Auth, Mandanten, RBAC (Phase 1 shell), Scoping-Pflicht `(tenant_id, client_id, job_id)` Hard Rule 8 | Draft-/Case-Schemas tragen `tenant_id`/`client_id` (nullable); Queries scoping-fähig | ✅ Felder + Struktur vorbereitet | **Phase 2** (Praxisorganisation) — Plattform übergibt Kontext, Modul filtert damit |
| 2 | **Gruppenverwaltung** | Phase 2 (Klienten, Gruppen, Dienste, Einwilligungen) | nichts modulspezifisch | — (rein Plattform) | Phase 2 |
| 3 | **Einwilligungen** | Phase 2, Art.-9-Pfad, WV01 Backup davor | nichts | — | Phase 2 |
| 4 | **Zwischenablage (AnalysisDraft)** | D18-Vertrag: Statusmaschine, CopyGuard, Promote | **VOLL implementiert** (Draft-Store, /drafts/*, CopyGuard fail-closed) | ✅ Kernstück | Phase 2/3 — Vertragsobjekt existiert schon jetzt identisch |
| 5 | **Harmonisierungsverwaltung (HarmonizationLane)** | timerd-Zustandsmaschine `queued→armed→running⇄paused→stopped→archived`, Spuren je Mandant bis Quota, Emitter max 1 (D14) | RadiWorks-Broadcast-Queue ist das **Artefakt-Vorläufermodell** (FIFO, Events); fördert Promote-Einträge ein | ✅ Vorlauf, ❌ noch nicht timerd-konform verdrahtet | **Phase 5** — dann Queue → Lane-Mapping (Einträge werden Spuren) |
| 6 | **Berichtswesen/Report** | Phase 6 (PDF, Continuous Aggregates), CopyGuard vor jedem sichtbaren Text | RadiWorks: CaseToHtml-Äquivalent + Statistik vorhanden; Clarke-Reports | 🟡 Bausteine da | Phase 6 |
| 7 | **Archivwesen** | Phase 6, „Auskunft = derselbe Export", Draft-TTL 7 Tage → Archiv-Vorschlag (kein Auto-Delete) | Cases als JSON-Dateien (Port-kompatibel); Draft-TTL-Feld vorhanden | 🟡 | Phase 6 |
| 8 | **Trendwesen** | Phase 6 (Continuous Aggregates) | GV-Verläufe/Sessions bereits als Daten basis da | 🟡 Datenbasis | Phase 6 |
| 9 | **Abo-System/Quotas** | D09 (empfohlen), C05 Quotas technisch; Kanäle/Emitter/VRAM | nichts | — | Phase 10 (Betrieb), WV02 Preise |
| 10 | **Kernel-ABI/Registry** | Phase 3 Registry, Freigabe = Admin-Akt | `/manifest` liefert ABI-v1 + Hash | ✅ self-manifesting | **Phase 3** |
| 11 | **Computation Passport** | docs/04-compute.md Felder | Voll implementiert je Analyse-Lauf | ✅ | ab Phase 3/4 im Audit sichtbar |
| 12 | **CopyGuard** | Lexikon (fail-closed) + LLM im RAM (Plattform) | Lexikon-Stufe im Kernel vor Promote/Speichern | ✅ Stufe 1 | LLM-Stufe Phase 2+ (Plattform) |
| 13 | **Live/WebSocket** | Fachkanal v:1, Server ist Uhr, Reconnect an Event-ID | implementiert | ✅ | Phase 2+ |
| 14 | **Identity/Auth** | Better Auth, authMiddleware auf JEDE Server-Function mit User-Daten | Engine hat (bewusst) keine Auth im Solo-Betrieb; bei Integration hinter Aurelia-Auth | ✅ vorbereitet (keine Doppel-Auth) | Phase 2 |
| 15 | **Audit** | Audit-Index, Flags audited | Passport + Event-Historie (Ring) als Bausteine | 🟡 | Phase 2+ |

## 2. Stochastik im System (Frage g2)

**Befund Aurelia-Seite:** Stochastik ist derzeit nur als *Deklaration* definiert —
ABI-Feld `repro: strict|seeded|stochastic` und Hard Rule 7 („Default strikt
reproduzierbar, stochastisch/quantum explizit"). **Ein zentraler Entropie-Dienst
ist in der Aurelia-Planung (noch) nicht benannt** — es gibt timerd, emitterd,
gpud, aber kein „entropyd".

**Befund Modul-Seite (RadiWorks):** vollständige Entropie-Architektur implementiert:
Provider-Kette (Webcam-Feed → random.org → OS-CSPRNG), seeded-Modus,
Seed-Semantik wie das Original (Entropiewert = Seed eines zweiten PRNG),
Provenienz je Lauf im Passport.

**Empfehlung zur Diskussion (zwei Wege, beide regelkonform):**
1. **Dezentral (aktuell):** Jedes Modul besorgt Entropie selbst hinter
   `repro: stochastic` und dokumentiert die Quelle im Passport. Geringster
   Plattform-Aufwand; Radi144 (hat ebenfalls einen stochastischen Modus)
   könnte denselben Provider-Standard aus `Modul_Templates` übernehmen.
2. **Zentral (Vorschlag):** Ein `aurelia-entropyd` (analog timerd/emitterd)
   als gemeinsamer Echtzeit-Dienst: Lease → Entropie-Bezug → Audit; Quellen
   (QRNG-Karte/HWRNG/Anbieter-API) hängen an der Plattform, Module fordern
   Entropie-Pakete per Contract an (Format wie `hotbits_*.json` bleibt
   kompatibel). Konsistent mit Aurelias Philosophie „gemeinsame
   Echtzeitkomponenten liegen plattformseitig" — **aber: neuer Baustein,
   braucht eine Leitentscheidung (D-Katalog) des Betreibers.**

## 3. Native Echtzeithardware (Frage h)

Aurelia hat Ablauf und Zuständigkeit klar definiert; Module beachten:

| Komponente | Aurelia-Regel | Konsequenz für Module (RadiWorks umgesetzt?) |
|---|---|---|
| **aurelia-emitterd** (Spooky2/GenX Pro, CP210x) | Lease → Arming → ACK → Emission → Reset; **kein WebUSB**; Emitter-Lease ≠ GPU-Lease (Hard Rule 11) | ✅ Kein eigener Hardwarezugriff; VirtualEmitter liefert Events; LED-Choreografie als Datenstruktur bereit für den Connector |
| **aurelia-timerd** (chrony + monotonic) | Server ist die Uhr; Browser-`setInterval` ist keine Uhr; Spuren-State + Tick 50 ms | 🟡 Broadcast-Ticks laufen im Engine-Thread (serverseitig ✓); Spur-Zustände kommen mit Phase 5 |
| **GPU-Pool** | 16-GB-Job-Pool, tenant-isoliert, kein MIG; RadiWorks ist `class: cpu` | ✅ kein Bedarf |
| **HRV-Ohrclip (D21)** | Sensorvertrag über Fachkanal; kein EEG | — (RadiThoms-Thema) |
| **`isHardwareActivatable`** | false bis Hardware-Gate | ✅ im Manifest gesetzt |

**Merksatz für ALLE Module:** Hardware wird nie direkt, sondern nur über
Plattform-Daemons angesprochen; Module liefern die *fachliche Choreografie*
(Schritte, timings, Frequenzen) als Artefakte/Events.

## 4. Was der Prototyp JETZT beachten muss vs. später

**Jetzt (Prototyp-Disziplin — bei RadiWorks erfüllt, Standard für alle):**
1. Vertragskonformität: ABI-Manifest, Draft-Statusmaschine, Passport-Felder,
   WS-Envelope v:1, CopyGuard-Lexikon.
2. Scoping-Vorbereitung: `tenant_id`/`client_id` in allen Schemas (nullable).
3. Keine versteckten Netz-/Hardwareaufrufe; keine Tabu-Bäume.
4. Deutsche Wellbeing-Sprache; kein Medizinprodukt-Claim.
5. Datenhygiene: Pseudonym-Dateinamen, keine Art.-9-Daten in Repos.

**Später (erst bei Integration, Phase für Phase):**
- Auth-/Mandanten-Kontext injiziert die Plattform; Modul filtert.
- Drafts wandern in Postgres (OLTP) statt Dateisystem.
- Broadcast-Queue wird HarmonizationLane-Spur (timerd übernimmt die Uhr).
- Reports/Archiv/Trend bauen auf den Passport-/Session-Daten auf.
- Abos/Quoten greifen auf Kanal-/Emitter-/Spurebene.

**Faustregel:** Der Prototyp hält die *Verträge* und die *Fachlogik* fertig;
die Plattform bringt *Identität, Zeit, Emission, Archiv, Abrechnung*. So
bleibt jede Kernengine erhalten und wird doch nahtlos eingespannt — genau die
„Blaupausen"-Idee aus `UI_DESIGN_STANDARD.md` und `API_CONTRACT.md`.

## 5. Vektor (Fälle) und Fokus in der Analyse (Frage g)

Befund aus dem Original-Bytecode: Der Fall (Case) ist **Dokumentations-
container**, nicht Algorithmuseingang — die Analyse zieht ausschließlich aus
Raten-Datenbank + Entropie. Der „Fokus" wirkt im Original an genau zwei
Stellen: (1) Broadcast-Signatur = Fallname + Eingabe (Kontext-Verknüpfung),
(2) Essential Questions als GV-Orakel. Der Port ist hier 1:0 treu.
**Aurelia-Perspektive:** Genau dafür ist der AnalysisDraft gebaut —
`client_id` + Witness-Bezug (`input_hash`) machen Klient und „Fokus" zu
vertragspflichtigen Feldern des Artefakts, ohne die Kernstatik zu ändern.
Eine algorithmische Kopplung (z. B. zeugenbasierte Saat) wäre eine neue
Festlegung (D-Katalog) und ist derzeit weder im Original noch in Aurelia
vorgesehen.
