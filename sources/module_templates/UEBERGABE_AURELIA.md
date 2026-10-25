# Übergabe an AURELIA — RadiWorks-Evidenzpaket (vorbereitet, nicht freigegeben)

> **Zweck:** Ein einziger, sanitierter Posten, den der Betreiber zu gegebener
> Zeit (Aurelia Phase 2/3: Praxisorganisation / Kernel-ABI + Raten-Registry)
> in den Aurelia-Prozess einreichen kann. Gemäß Aurelia-Verfassung ist die
> Einreichung ein Betreiber-Akt; dieses Dokument ist Evidenz-Angebot, kein
> Kanon. **Keine Art.-9-Daten, kein Personenbezug.** Historischer Ausgangsstand
> 2026-08-29; lokaler Kandidat und Evidenzstand 2026-09-30. Die Einreichung
> erfolgt erst nach den separaten Modul-/Matrix- und Aurelia-Gates.

## 1. Was übergeben wird

| Artefakt | Ort | Stand |
|---|---|---|
| RadiWorks-Engine (Python/FastAPI, Kernel-ABI v1) | `Radiworks/radiworks_port/engine` | Kandidat `a242d247`; lokaler Engine- und Linux-26.04-Testnachweis. Ubuntu Server 24.04.4, S4, Registry und Produktion ungeprüft |
| RadiWorks-Webapp (HTML) | `Radiworks/radiworks_port/webapp` | isolierter Chrome-Smoke 19/19; gezielte hörende Fallaktionsprobe bestätigt, keine vollständige WCAG- oder S4-Abnahme |
| Verbindliche Festlegungen (5) | `Modul_Templates/modules/radiworks/FESTLEGUNGEN.md` | abgestimmt 2026-08-29 |
| Funktionsabgleich Original ↔ Port | `Modul_Templates/modules/radiworks/FUNKTIONSABGLEICH_BILDER.md` | vollständig |
| API-Contract v1 (alle Module) | `Modul_Templates/standards/API_CONTRACT.md` | gemeinsamer Sollvertrag; [lokale RadiWorks-Abweichungen als Entwurf](standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md) dokumentiert |
| UI-/Design-Standard (alle Module) | `Modul_Templates/standards/UI_DESIGN_STANDARD.md` | bestehende Vorlage; Hermes-Designsynthese und modulweise Akzente nach D0/D1 noch offen |

## 2. Kernel-Ausweis (aus `/manifest`, live abrufbar)

```json
{
  "id": "radiworks.engine",
  "version": "0.2.0",
  "hash": "sha256:<dynamisch aus /manifest>",
  "class": "cpu",
  "repro": "seeded",
  "budget": { "vram_mb": 0, "cpu_ms_est": 5000, "max_batch": 1 },
  "abi_surface": "rest",
  "abi_version": "v1",
  "operations": [{ "id": "analysis", "method": "POST", "path": "/analysis", "version": "v1" }],
  "entry": "radiworks.core.analysis:analyse_rate_list",
  "entry_status": "deprecated-compatibility",
  "isHardwareActivatable": false
}
```

Java-Orakelparität ist ausschließlich im in
`Radiworks/radiworks_port/engine/PARITY_MATRIX.md` definierten Umfang der drei
versionierten seeded `POST /analysis`-Fixtures mit 300 synthetischen Raten
belegt. Darüber hinaus wird keine allgemeine Java-Parität behauptet. Der
Altbaum `radiquant4` bleibt tabu (keine Code-Anlehnung, kein Zugriff).

## 3. Was Aurelia vom Modul bekommt (Integration-Seite)

1. **Self-Manifesting Kernel:** `GET /manifest` liefert das ABI-v1-Objekt mit
   dynamischem Hash. Die spätere Kernel-Registry und eine Freigabe bleiben
   separate Aurelia-Admin-Akte; diese Übergabe zertifiziert weder S4 noch S5.
2. **Artefakt-Fluss nach D18:** Analyse erzeugt lokal einen AnalysisDraft
   (`draft → client_review → ready → promoted`), CopyGuard fail-closed vor
   Promote. Ein modulübergreifender Übergabeweg (z. B. Radi144-Baseline →
   RadiWorks-Korrelation) ist vorgesehen, aber noch nicht im Aurelia-Host belegt.
3. **Computation Passport** je Lauf: `run_id, kernel_hash, input_hash, seed,
   entropy_mode, dauer_ms, sources, signatur`. `tenant_id`/`client_id` werden
   lokal aus `state.scope` in Passport und Draft übernommen; der lokale
   Analysis-Request akzeptiert diese Body-Felder **nicht**. `job_id` steht im
   Draft-Scope, nicht im Passport. Host-Autorisierung und tenant-scoped Queries
   sind nicht nachgewiesen.
4. **WebSocket-Fachkanal** `v:1` mit `boot`, monotonen Event-IDs und
   boot-bewusstem Reconnect über `last_event_id` plus `last_boot`; bei Lücken
   folgt `server.replay_gap` (Server ist die Uhr).
5. **Same-Site-Einbettung:** Die Webapp läuft lokal autark; iframe-Hosting in
   Aurelias Preview-Host und Theme-Übergabe über `data-module-theme`/
   `data-accent` sind Zielverträge, keine geprüfte Aurelia-Integration.
6. **Keine Hardware-Aktivierung:** `isHardwareActivatable: false`; LED-
   Choreografie nur als Events; physische Emission ausschließlich via
   `aurelia-emitterd` (Hard Rule 11), Anschluss vorbereitet.

## 4. Was Aurelia dem Modul geben muss (Bedarf)

| Bedarf | Aurelia-Referenz | Zeitpunkt |
|---|---|---|
| Registry-Slot + Freigabe als Admin-Akt | `docs/06-kernel-abi.md:38-41` | Phase 3 |
| Mandanten-Kontext (`tenant_id`, `client_id`) im Aufrufkontext | `AGENTS.project.md:59` (Hard Rule 8) | Phase 2 |
| CopyGuard-LLM-Stufe für Draft-Texte (Lexikon-Stufe läuft bereits im Modul) | `docs/16-wellbeing.md` | Phase 2+ |
| Same-Site-Host/Preview-Brücke ohne Cross-Origin-Aufruf | `isolation.server.ts` | Phase 2+ |

## 5. Bewusste Abweichungen vom Original (alle dokumentiert, betreiberfestgelegt)

1. Entropie: seeded Factory-Default, `stochastic` als Settings-/Request-Wahl
   (Hard Rule 7), Provenienz je Lauf im Passport.
2. Broadcast-Mix: Zweiklick-Default (D18), Original-Einklick per
   `broadcast.legacyMixMode` zuschaltbar; CopyGuard in beiden Wegen.
3. Emitter: Original-Choreografie als VirtualEmitter-Events; keine physische
   Aktivierung.
4. GOOGLE-Links des Originals ersetzt (Datenaustritt); Zeugen-Bilder mit
   `no-store`-Auflage; Webcam-Entropie einwilligungspflichtig.

## 6. Hinweise zur Einreichung

- Einreichungsbote: Betreiber (in Aurelias Prozess; externe Quellen werden
  dort erst durch Übernahme in eine freigegebene Spezifikation ausführbar).
- Dieses Dokument enthält keine Personenbezug; Betriebsscreenshots mit
  Fallkennungen bleiben lokal (`Radiworks/screenshots/`, git-ignoriert).
- Lokaler Referenzstand jetzt: RadiWorks-Kandidat `a242d24758d53e86ab290454ae4772f0827acc06`;
  bei späterer Einreichung tatsächliche RadiWorks-, Modul_Templates- und
  Aurelia-Quellstände erneut fixieren. Der bisherige RadiWorks-Arbeitsbranch
  mit weiteren uncommitteten Änderungen ist kein identischer Release-Tag.


## 7. Review-Evidenz-Checkpoint — 2026-09-04

- Checkpoint-ID: `20260904T210517Z-radiworks-review-11`
- Befunde: 11, SHA-256: `78d7d8da48debaf01c32b20d61c28f292c7b4e8260fcee535038bc6c5a940899`
- Sanitierte technische Evidenz; kein Aurelia-Kanon und keine automatische Umsetzungsfreigabe.
- Modulübergreifende Themen: sichere Artefaktpfade, ABI-/Eingangsvalidierung, Worker-Fehlertoleranz, Persistenz, Provenienz, reproduzierbare Entropie, CopyGuard und Sanitierung.
- Der lokale Voll-Checkpoint kann sensible Laufzeitdaten enthalten und bleibt lokal.

## 8. S2-Entropie- und Provenienz-Entscheidungen — 2026-09-05

> **Status:** Betreiberfreigabe für RadiWorks; für Aurelia und weitere Module
> sanitierte Evidenz, kein automatischer Plattformkanon.

- Produktiver seeded-Pfad: Java-Master-PRNG, Java-Zweitstufe und Java-
  HashMap-Reihenfolge; abweichende historische Ergebnisse bleiben als solche
  nachvollziehbar.
- Stochastic-Pfad: Webcam-/Hotbits-FIFO → freigegebene random.org-Quelle →
  OS-CSPRNG. Egress ist ausschließlich für `stochastic` erlaubt und fällt bei
  Fehlern kontrolliert zurück.
- Passports: effektiver Seed plus `replayable`/`seed_scheme`; historische
  Derived-Seed-Passports werden nicht rückwirkend als replaybar ausgegeben.
- CopyGuard: ein gemeinsamer finaler Digest bindet Passport und Draft.
- Details und Konformitätstests: `modules/radiworks/FESTLEGUNGEN.md`, Ergänzung
  2026-09-05. Die zugehörige Aurelia-Evidenz bleibt dem Governance-Prozess
  vorbehalten.

## 9. S3-Persistenz- und Recovery-Entscheidungen — 2026-09-05

- Analysesessionen sind append-only, server-owned und über stabile IDs gebunden;
  historische Indexnavigation bleibt migrationskompatibel.
- GV-Schritte und Resets sind persistierte Ereignisse; die Runden-Grenze forked
  eine Child-Session statt den vorherigen Zustand zu löschen.
- Stochastic Roh-Seeds sind ausschließlich verschlüsselte private Runtime-
  Journaldaten. Öffentliche Artefakte enthalten nur Referenz und Integrität,
  keine Seeds oder Schlüssel.
- `RADIOWORKS_JOURNAL_KEY` ist ein Deployment-Secret. Recovery stellt den
  bestätigten Zustand wieder her; neue stochastic Ziehungen nach Neustart sind
  explizit als neuer Quellabschnitt markiert.
- Statusgebundene Draft-Projektion, Legacy-Lazy-Migration und Retention bis zur
  expliziten Falllöschung sind als modulübergreifende Sicherheitsmuster
  dokumentiert, aber nicht ohne Aurelia-Governance plattformweit bindend.

## 10. Aktueller Vorbereitungsstand — 2026-09-30

RadiWorks-Quelle und getrennter Kandidat sind für 105/105 Moduldateien bytegleich. Die gezielte lokale Bedien-/Screenreader-Probe ist bestätigt; der vollständige synthetische Chrome-Smoke bestand 19/19. Das Profil `standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md` und Brainpower `docs/verification/RADIWORKS_TEMPLATE_DELTA_V01_2026-09-29.md` listen die noch offenen Vertragsabweichungen. S4.6 liegt im lokalen Prüfplan bei ca. 98 %, S4.7 bei ca. 88 %, S4.8 hat keine Gesamtentscheidung. Diese Zahlen sind **keine** Reifegrad- oder Integrationsfreigabe. Die Reihenfolge bleibt: RadiWorks, Radi144, `morphic_v1` und neues Modul lokal vorbereiten; danach Matrixplan, erst danach Aurelia-Integration unter ihren eigenen Gates.

## 11. Lokaler RadiWorks-Nachtrag — 02.10.2026

Der historische Referenzstand oben bleibt als damaliger Beleg stehen. Der aktuelle Arbeitsstand ist über `Brainpower/runtime/rw-focus-search-20261002/promotion-manifest.json` quellengebunden: 14 geprüfte Dateien wurden nach leerer virtueller Queue in RadiWorks-Quelle und lokalen 8103-Kandidaten übernommen. Gesicherte Ausgangsdateien und der damalige 8103-Datenbestand liegen unter `Brainpower/checkpoints/radiworks-focus-search-20261002-before`. Die vollständige Engine-Suite und 21 synthetische Chrome-Abschnitte bestanden; auf 8103 bestätigte eine lesende Browserprobe die Datenbanksuche und das optionale Fokusfeld. Drei Fälle und 51 Drafts blieben sichtbar. Der aktive Fall muss nach Neustart erneut ausgewählt werden.

Der Fokus ist eine bewusst übernommene Katalog-Namenshilfe und ein Draft-Snapshot, keine diagnostische Einordnung oder Änderung der Analyseberechnung. Der lokale Fallverweis schützt gegen veraltete Formularantworten, ist aber pro Prozess neu und kein Host-Identitätsvertrag. Der gemeinsame API_CONTRACT v1, die Mandanten-/Auftragsisolation, die Design-Synthese und sämtliche S4-/Aurelia-Gates bleiben zur Entscheidung offen; der neue lokale Beleg ist keine Integrationsfreigabe.

## 12. Lokaler UI-Nachtrag — 02.10.2026

Die RadiWorks-Quelle enthält jetzt verständliche Wirkungshinweise zu allen derzeit sichtbaren Einstellungen sowie eine separate 31 × 12-Area-Farbansicht. Diese verwendet lokalen Browser-Zufall und ist ausdrücklich **kein** Hotbits- oder GV-Nachweis; der vorhandene Zahlen-Scan blieb erhalten. Fünf Webdateien wurden nach Sicherung hashgeprüft übernommen und auf 8103 ohne Prozessneustart bytegleich ausgeliefert. Die aktive Auto-Runde wurde nicht verändert. Eine isoliert getestete Peggotty-Korrektur für doppelte Skriptmarken wartet noch auf ein sicheres Engine-Wartungsfenster. Diese UI-Ergänzung ändert weder den gemeinsamen API_CONTRACT v1 noch die Host- und Integrationsgates. Aktueller Beleg: `Brainpower/docs/verification/RADIWORKS_EINSTELLUNGEN_AREA_PEGGOTTY_2026-10-02.md`.

## 13. RadiWorks-Live-Nachtrag und offene Host-Grenze — 02.10.2026

Der oben dokumentierte Peggotty-Wartungsvorbehalt ist inzwischen für die lokale 8103-Engine erledigt: Die Duplikatgrenze wurde nach gesicherter Wartung in die Quelle übernommen, gezielte Tests bestanden und ein künstlicher doppelter Label-Aufruf auf 8103 erhielt HTTP 422. Spaltenausrichtung und Broadcast-Dock werden aus geprüften Webbytes ausgeliefert. Ein extern gesicherter Fernet-Schlüssel auf E: ermöglicht lokal die Wiederherstellung fallgebundener Stochastic-Journale; eine künstliche Analyse samt Neustart bestand isoliert. Der 8103-Standard bleibt `seeded`, eine reale fallgebundene Stochastic-Bedienprobe ist offen.

Die lokale Kamera-Probe auf 8103 zeigte nur statische virtuelle Quellen und null serverbestätigte Feedwerte. Die später getestete Quellenwechsel-Korrektur verwirft ungesendete Kandidaten der vorherigen Kamera; 8103 liefert die geprüften neuen Webbytes. Eine geeignete bewegte Kamera und serverbestätigte Feedwerte bleiben für die Hotbits-Bedienabnahme offen. Mehrport-Isolation ist nur mit getrennten Prozessen/Homes synthetisch belegt. Der Auftrag-/Mandanten-/WebSocket-Hostvertrag und der Matrixplan bleiben offen. Keine Änderung an `API_CONTRACT.md` v1, kein Aurelia-Gate und keine Integrationsfreigabe. Aktueller Beleg: `Brainpower/docs/verification/RADIWORKS_8103_TRENDS_RECOVERY_PARALLEL_2026-10-02.md`.
