# AURELIA G0 Governance Design

**Status:** Vom Betreiber am 2026-08-24 mit „G0-Design freigegeben“ zur
Ausarbeitung freigegeben. Diese Spezifikation ist noch keine Freigabe für
Produktivdaten, Serveränderungen oder AURELIA-Releases.

**Baseline:** Branch `codex/aurelia-g0-governance`, vollständiger
Ausgangs-Commit `b20ee873347c5fd767e2089c993f1cf93a625def`.

Der Wortlaut „G0-Design freigegeben“ autorisiert ausschließlich die
Ausarbeitung ab dem oben genannten Ausgangs-Commit. Er wird als
`REV-G0-ELABORATION-AUTHORIZATION` historisch erfasst, genehmigt aber weder
spätere Textänderungen noch einen noch unbekannten Designcommit. Nach
abgeschlossenen Reviews muss der Betreiber den konkreten vollständigen
Designcommit und dessen Dateihash in einer separat signierten
`REV-G0-DESIGN-APPROVAL` bestätigen. Ohne diese zweite, kryptografisch
verifizierte Freigabe bleibt `GATE-G0` `red` und es findet kein Governance-
Bootstrap statt.

## 1. Zweck

G0 macht den bestehenden AURELIA-Produktkanon revisionsfest, bevor Threat
Model, Datenschutz-Folgenabschätzung, Debian-Pilotarchitektur oder weitere
Produktfunktionen verbindlich geplant werden. Jede sicherheits-, datenschutz-,
betriebs- oder produktrelevante Aussage erhält eine eindeutige Quelle,
Verantwortung, Prüfspur und Freigabebedingung.

G0 löst vier konkrete Probleme:

1. `AGENTS.project.md`, TypeScript-Kanon, Markdown und Portal besitzen bislang
   keine ausdrückliche Präzedenzregel.
2. Anforderungen, Controls, Risiken, Datenflüsse, Tests und Gates sind nicht
   bidirektional verknüpft.
3. Freigaben nennen nicht durchgängig Baseline, Umfang, Prüfer, Evidenz und
   Ablauf- oder Reviewdatum.
4. Reasoning-, Subagent-, externe LLM-Zuarbeits- und Serverzugriffsregeln sind noch
   nicht als Entwicklerdirektive festgehalten.

## 2. Umfang und Nicht-Ziele

### 2.1 G0 umfasst

- Quellenhierarchie und Konfliktbehandlung;
- Governance-Rollen und Funktionstrennung;
- stabile Governance-ID-Namensräume und Statusmodelle;
- Traceability-, Risiko-, Datenverarbeitungs- und Gate-Register;
- revisionsfeste Review-, Evidenz-, Ausnahme- und Freigaberegeln;
- Reasoning-Eskalationsregeln für agentische Arbeit;
- Regeln für interne Subagents und externe LLM-Zuarbeit als unvertrauenswürdige Evidenz;
- gestufte Zugriffsregeln für den M-G1;
- maschinenprüfbare Struktur- und Referenzverträge;
- Korrektur der unmittelbar governance-relevanten Kanonlücken.

### 2.2 G0 umfasst ausdrücklich nicht

- eine Serverinventur oder eine Änderung am M-G1;
- Threat-Model-Inhalte oder eine abgeschlossene DSFA;
- Auswahl eines Backup-Anbieters oder Offsite-Ziels;
- produktive Authentifizierung, RLS, Schlüsselverwaltung oder Datenmigration;
- Bereinigung, Deinstallation oder Abschaltung bestehender Debian-Dienste;
- Aktivierung von Art.-9-Daten, CUDA, USB, Emitter oder Sensoren;
- rechtliche, datenschutzrechtliche, Penetrations- oder Hardwarefreigaben.

Unbesetzte externe Fachrollen werden nicht mit Platzhaltern übergangen. Der
zugehörige Gate-Status bleibt ausdrücklich `red`, bis eine qualifizierte Person
benannt und ihre Evidenz protokolliert ist.

## 3. Bewertete Ansätze und Entscheidung

### 3.1 Nur Markdown

Menschenlesbare Tabellen wären schnell erstellt, könnten aber erneut
auseinanderlaufen. Freie Statuswerte, fehlende Referenzen und doppelte IDs
wären nicht zuverlässig erkennbar. Dieser Ansatz wird verworfen.

### 3.2 Dokumentation plus maschinenprüfbarer Vertrag

Menschenlesbare Governance-Dokumente bleiben die Arbeitsoberfläche. Ein
deterministischer Validator prüft Pflichtabschnitte, ID-Eindeutigkeit,
Statuswerte, Referenzziele, Quellenpräzedenz und No-Waiver-Gates. Tests
definieren den Vertrag zuerst und verhindern stille Drift.

**Entscheidung:** Dieser hybride Ansatz wird umgesetzt. Er passt zum bereits
vorhandenen Kanonvertrag, benötigt kein externes GRC-System und bleibt lokal
reproduzierbar.

### 3.3 Externes GRC-System

Ein eigenständiges Governance-, Risk- und Compliance-System würde derzeit
zusätzliche Konten, Datenflüsse, Kosten und Betriebsabhängigkeiten schaffen.
Es wird für G0 nicht eingeführt. Ein späterer Export bleibt möglich, weil IDs
und Felder stabil definiert werden.

## 4. Verbindliche Quellenhierarchie

Keine interne Projektquelle kann zwingendes Recht, vertragliche Pflichten,
technische Realität oder Sicherheitsnachweise außer Kraft setzen. Innerhalb
des Repositories gilt für denselben Sachverhalt folgende Reihenfolge:

1. revisionsfeste Betreiberfreigabe mit Scope, Commit-Baseline und REV-ID;
2. `AGENTS.project.md` als Produktkonstitution und `GOVERNANCE.md` als
   Prozesskonstitution;
3. maschinenlesbare Produkt- und Governance-Register;
4. freigegebene Spezifikationen und Architecture Decision Records;
5. freigegebene Implementierungspläne;
6. Implementierung und ausführbare Tests;
7. abgeleitete Markdown-, Portal- und UI-Darstellungen.

Eine ausdrückliche Betreiberanweisung bindet die laufende Arbeit sofort. Für
eine dauerhafte Wirkung muss sie vor dem nächsten Gate als revisionsfeste
REV- oder Entscheidungsakte in das Repository übernommen werden.

Bei einem Konflikt gewinnt keine Datei stillschweigend. Der Validator oder ein
Reviewer setzt `GATE-G0` auf `red`; der Konflikt erhält eine REV- oder RISK-ID
und wird durch den Betreiber oder den fachlich zuständigen Entscheider
aufgelöst. Abgeleitete Quellen werden anschließend aktualisiert.

## 5. Governance-IDs und Statusmodelle

Bestehende Produkt-IDs `D`, `C`, `X`, `U`, `K`, `L`, `H`, `O` und `WV`
bleiben unverändert. G0 ergänzt folgende Namensräume:

| Präfix | Bedeutung | Beispiel |
|---|---|---|
| `REQ` | überprüfbare Anforderung | `REQ-001` |
| `CTRL` | organisatorische oder technische Kontrolle | `CTRL-001` |
| `RISK` | bewertetes Risikoszenario | `RISK-001` |
| `DATA` | Datenobjekt oder Datenklasse | `DATA-001` |
| `FLOW` | Datenbewegung über eine Vertrauensgrenze | `FLOW-001` |
| `GATE` | Stop-, Freigabe- oder Übergangsgate | `GATE-G0` |
| `REV` | Review- oder Freigabeakte | `REV-001` |
| `EXC` | befristete Ausnahme | `EXC-001` |
| `EVID` | unveränderlicher Evidenzverweis | `EVID-001` |
| `PROFILE` | Laufzeit- oder Zugriffsprofil | `PROFILE-PREVIEW` |
| `ROLE` | Governance-Rolle und ihre aktuelle Besetzung | `ROLE-OPERATOR` |
| `COMP` | logische, providerneutrale Systemkomponente | `COMP-EDGE` |
| `EVT` | append-only Governance-Zustandsübergang | `EVT-000001` |
| `KEY` | öffentlicher, rollen- und assigneegebundener Verifikationsschlüssel | `KEY-OPERATOR-001` |
| `KEYREV` | append-only Schlüsselwiderruf | `KEYREV-000001` |
| `RECEIPT` | externe, append-only Annahmequittung | `RECEIPT-000000000001` |
| `POLICYTRANS` | externe, append-only Branch-Policy-Transition, die alle Receipts der alten Policy-Epoch entwertet | `POLICYTRANS-000000000001` |

IDs werden nie wiederverwendet. Entfernte Einträge erhalten den Status
`retired`, `closed`, `expired`, `revoked` beziehungsweise `superseded` gemäß
ihrer Recordfamilie und verweisen über die in Abschnitt 12 definierten
bidirektionalen Felder auf ihren Nachfolger.
`KEY`, `KEYREV`, `RECEIPT` und `POLICYTRANS` sind keine statusbehafteten
Registerrecords; sie werden ausschließlich über ihre append-only
Kryptoverträge fortgeschrieben und niemals entfernt.

Zulässige Kernstatuswerte sind:

- Anforderungen: `proposed`, `approved`, `implemented`, `verified`, `retired`;
- Controls: `proposed`, `implemented`, `verified`, `retired`;
- Risiken: `open`, `treated`, `accepted`, `closed`;
- Gates: `red`, `amber`, `green`, `expired`;
- Reviews: `requested`, `changes-required`, `approved`, `superseded`;
- Evidenzen: `expected`, `captured`, `verified`, `invalidated`, `superseded`;
- Ausnahmen: `requested`, `approved`, `expired`, `revoked`;
- Profile: `proposed`, `approved`, `active`, `retired`;
- Datenobjekte und Flows: `catalogued`, `planned`, `active`, `retired`;
- Rollen: `unassigned`, `assigned`, `suspended`, `retired`;
- Komponenten: `proposed`, `approved`, `implemented`, `retired`.

`amber` bedeutet weder bestanden noch produktionsfähig. Es bezeichnet eine
bekannte, nicht unmittelbar freigabefähige Vorbedingung mit Owner und Frist.

## 6. Artefaktarchitektur

### 6.1 Entwicklerdirektiven

`AGENTS.project.md` erhält einen kompakten verbindlichen Abschnitt mit:

- Verweis auf `GOVERNANCE.md`;
- Quellenhierarchie und Konflikt-Stop-Gate;
- Pflicht zur Traceability für sicherheitsrelevante Änderungen;
- Trennung von Implementer, Spec-Reviewer, Quality/Security-Reviewer und
  Freigabeinstanz;
- Reasoning-Eskalationspflicht;
- Verbot ungeprüfter externer Kontextweitergabe;
- M-G1-Zugriffs- und In-place-Härtungsgrundsatz.

`GOVERNANCE.md` enthält die vollständigen Prozessregeln. Produktentscheidungen
bleiben in `AGENTS.project.md` und den Produktregistern; Prozessregeln werden
nicht redundant in Fachkapiteln gepflegt.

### 6.2 Governance-Register

Vier menschenlesbare Register bilden G0:

1. `docs/governance/traceability-register.md`
2. `docs/governance/risk-register.md`
3. `docs/governance/data-processing-inventory.md`
4. `docs/governance/gate-register.md`

Jedes dieser vier Markdown-Register enthält genau einen kanonischen JSON-Block zwischen den
HTML-Kommentaren `governance-data:start` und `governance-data:end`. Der Block
muss valides UTF-8-JSON ohne Kommentare sein und besitzt
`schemaVersion: "aurelia-governance-v1"`. Text außerhalb dieses Blocks erklärt
die Daten, ist aber abgeleitet und darf ihnen nicht widersprechen. Der
Validator extrahiert nur diesen eindeutig markierten Block, verwendet
`JSON.parse` und lehnt fehlende, doppelte oder nachgestellte Governance-Blöcke
ab. Damit bleibt das Register menschenlesbar und ohne zusätzliche
Parserabhängigkeit deterministisch prüfbar.

Die separate Datei `docs/governance/governance.schema.json` ist reines valides
JSON ohne HTML-Kommentare oder Markdown-Marker. Sie verwendet JSON Schema Draft
2020-12 und bildet die in
Abschnitt 12 normativ definierten Typen exakt ab. Jeder Objekttyp setzt
`additionalProperties: false`; der Validator lädt das Schema lokal und prüft
jeden extrahierten Block vor allen Cross-Reference-Regeln.

`docs/governance/trust-roots.json` ist ebenfalls reines JSON, wird durch ein
Draft-2020-12-Teilschema validiert und enthält ausschließlich öffentliche Verifikationsschlüssel, niemals
private Schlüssel oder Secrets. Das Array `keys` ist append-only; jeder
unveränderliche Eintrag besitzt eine stabile `KEY-*`-ID, Assignee- und
ROLE-Bindung, den festen Algorithmus `ed25519`, einen exakt 32 Byte langen
Base64url-Public-Key ohne Padding, dessen kleingeschriebenen SHA-256-
Fingerprint, `validFrom`, nullable `validUntil` und `introducedByEventRef`.
Widerrufe werden nicht in alte Einträge geschrieben, sondern append-only im
Array `revocations` mit `KEYREV-*`-ID, `keyRef`, Zeitpunkt, Grund,
`revokedByEventRef` und nullable `supersededByKeyRef` ergänzt. Effektiv aktiv
ist nur ein zeitlich gültiger Key ohne passende Revocation. Rotation oder
Widerruf benötigt eine Attestation des bisher aktiven Schlüssels oder den in
Abschnitt 12.5 definierten, offline verankerten Recoveryweg. Der initiale Operator-
Fingerprint wird außerhalb des editierbaren Ledgers bestätigt und in der
signierten finalen Designfreigabe gebunden.

Detached Signaturen liegen unter `docs/governance/attestations/` als
kanonische JSON-Artefakte. Ihr Dateiname ist
`<EVT-ID>--<attestationPurpose>--<keyRef>.json`; Artefakt,
Signaturwert und Public Key werden lokal und offline geprüft. Die
Attestationsdatei ist die RFC-8785-kanonische JSON-Darstellung des bytegleich
im zugehörigen EVT-Array `authorizationAttestations` enthaltenen Objekts;
fehlendes oder abweichendes Duplikat ist ungültig. Die Attestationsdateien
sind nach Aufnahme append-only. Branchschutz verlangt für
Governance-Änderungen Pull Requests, grüne Pflichtchecks, signierte Commits,
CODEOWNERS-Freigabe durch den Betreiber, gesperrte Force-Pushes/Löschungen und
kein Bypass für reguläre Writer. Diese Repositorykontrollen ersetzen die
Eventsignatur nicht, sondern schützen zusätzlich Trust-Roots, Validator und
Historie.

Die kanonische Ablage ist fest:

- Traceability-Register: `requirements`, `controls`, `profiles`, `roles`,
  `components`;
- Risikoregister: `risks`;
- Datenverarbeitungsinventar: `dataObjects`, `flows`;
- Gate-Register: `gates`, `reviews`, `evidence`, `exceptions`, `transitions`.

`docs/00-index.md` verlinkt alle Register. `docs/23-id-schema.md` erhält die
neuen Präfixe, führt `WV` vollständig und beschreibt `X` als akzeptierten
Katalog statt als offene Prüfung.

### 6.3 Maschinenprüfbarer Vertrag

`scripts/governance-contract.mjs` liest ausschließlich Repository-Dateien und
benötigt keine Netzwerkverbindung. `scripts/governance-contract.test.mjs`
definiert mindestens folgende negative und positive Fälle:

- doppelte oder syntaktisch ungültige IDs werden abgewiesen;
- REQ-Quellzitat, Zeilenlocator und Git-Blob-Digest werden positiv bytegenau,
  fehlende Zeilen, freie Paraphrase oder abweichender Digest negativ geprüft;
- unbekannte Statuswerte werden abgewiesen;
- Verweise auf nicht vorhandene REQ-, CTRL-, RISK-, FLOW-, GATE- oder EVID-IDs
  werden abgewiesen;
- ein `green`-Gate ohne Approver, Baseline und Evidenz wird abgewiesen;
- eine genehmigte Ausnahme für jedes einzelne initiale No-Waiver-Gate wird
  durch einen eigenen Negativtest abgewiesen;
- direkte sowie mindestens zwei- und dreistufige Ausnahmeprovenienz über
  Evidenz, Review, Control oder Hilfsgate wird an jedem initialen No-Waiver-
  Gate abgewiesen; widerrufene oder abgelaufene Ausnahmen löschen historischen
  Taint nicht;
- eine unbesetzte Pflichtrolle lässt das zugehörige Gate `red`;
- getrennte Rollen mit demselben Assignee werden abgewiesen, verschiedene
  Assignees am selben Gate werden akzeptiert;
- widersprüchliche REV-Status/Verdict-Kombinationen, unbelegte
  Finding-Auflösungen und ungeprüfte `verified`-Evidenz werden abgewiesen;
- der Bootstrap `captured → approved review → verified evidence` wird positiv,
  ein direkter `expected → verified`-Sprung und abgelaufene Gate-Reviews werden
  negativ geprüft;
- REV-/EVID-Assignee-Snapshots bleiben nach simulierter Rollenumbesetzung
  unverändert; Selbst-Review, Self-Resolution sowie scope- oder
  baselinefremde Review/Evidenz werden abgewiesen;
- bidirektionale REV- und EVID-Supersession wird positiv, Selbstreferenz,
  falscher Scope, falscher Typ und nicht nachfolgende Baseline werden negativ
  geprüft; eine `approved@epoch1`-Review wird durch eine vollständig aktuelle
  `approved@epoch2`-Nachfolgerreview historisch superseded, ohne die alte
  Entscheidung gegen Epoch 2 neu zu validieren; Reaktivierung des Vorgängers
  wird abgewiesen;
- exakt das dreiteilige Genesis-Bündel wird akzeptiert; zusätzliche,
  umsortierte, anders besetzte oder anders verankerte Genesis-Events werden
  abgewiesen;
- Pre-Ledger-Bundle und finale Designfreigabe werden gegen feste Pfade,
  geschlossene Schemata, Operator-/Root-/Validator-Controller-/
  Transparenzinstanz-/Witness-Pins und ihre exakten
  signierten Payloads geprüft; Einzelsignatur, Schlüssel-Selbsteinführung,
  abweichende `logId`/Key-Epoch/Witnessliste, Artefakt-/Commit-Zyklus oder
  abweichender Bootstrap-Validator-Digest werden abgewiesen;
- genau ein Event je Record und Transaktion wird akzeptiert, ein zweites Event
  desselben Records im Working Tree oder Commit wird abgewiesen;
- erlaubte `amend`-Events werden positiv geprüft; Amendments an finalen
  Zuständen, historischen Feldern oder außerhalb der typspezifischen
  Feldfreigabe werden abgewiesen;
- jeder Event-Akteur wird gegen die zum Eventzeitpunkt gültige Rollenbelegung
  und die geschlossene Autorisierungsmatrix geprüft; unbesetzte, falsch
  gespiegelte oder nicht autorisierte Akteure werden abgewiesen;
- jede normale EVT-Attestation wird kryptografisch gegen den vor dem Event
  aktiven Trust Root und den exakten Signatur-Envelope geprüft; gefälschte
  Actor-Strings, geänderte Digests, unbekannte/revozierte Schlüssel,
  Nonce-Wiederverwendung und Trust-Root-Austausch im selben Commit werden
  abgewiesen;
- Mehrfachattestationen besitzen verschiedene signer-spezifische Envelopes,
  aber exakt denselben Event-Core-Digest; Purpose-/Signer-Swapping, fehlende
  Sekundärattestation oder abweichender Core werden abgewiesen; der Offline-
  Recovery-Root wird für jeden seiner geschlossenen Bootstrap-, Handover-,
  Recovery-, TCB-, Custodian- und Transparenz-Key-Zwecke positiv, für Gate-,
  Review-, Fachfreigabe- oder frei erfundene Zwecke negativ geprüft;
- eine zum Change-Digest und Basiscommit passende Übergangsevidenz wird
  akzeptiert; fremder Recordhash, fremde Baseline, fehlender Digest oder erst
  nach dem konsumierenden Event erfasste Evidenz werden abgewiesen;
- zwischen fachlicher Evidenzbaseline und Konsum sind ausschließlich extern
  quittierte Governance-only-Commits sowie schema- und
  transitionskonforme REV-/EVID-Lebenszyklen erlaubt; ein dazwischenliegender
  Code-, Rollen-, Anforderungs-, Control-, Gate- oder sonstiger Fachcommit
  wird abgewiesen;
- EVID-Selbstevents werden ohne Self-Digest-Fixpunkt positiv, eine Nutzung
  derselben Evidenz für einen fremden Recordwechsel negativ geprüft;
- `null|expected → captured` setzt den Producer-Snapshot; ein abweichender
  oder nachträglich geänderter Snapshot wird abgewiesen;
- `baselineCommit` bindet Subjecttree/-manifest und `captureBaseCommit` den
  vorherigen Ledgerzustand; Selbstreferenz auf den entstehenden Commit,
  Vertauschung oder Nutzung eines nicht extern quittierten Zwischencommits
  wird abgewiesen;
- Subjectmanifest und Inputmanifest werden getrennt auf vollständige Subjects,
  Tree-Modi/-Hashes, Baseline und Ableitungsinputs geprüft; fehlende,
  zusätzliche, vertauschte oder fremdbaselinegebundene Einträge werden
  abgewiesen; `D01` wird positiv als `product-decision` mit Indexquelle,
  Exportname, Source-Blob- und Statusdigest geprüft, ein fehlender, doppelter
  oder durch File-/Record-Entry maskierter Produkt-Subject negativ;
- EVT-IDs ohne Lücke, die globale Hashkette und nicht fallende Zeitpunkte
  werden positiv, ID-Lücken, Rückdatierung, Umsortierung und falsche Hashes
  negativ geprüft;
- Zukunftszeiten, bei Erstannahme zu alte Attestationen, fehlende oder
  manipulierte Acceptance-Receipts und Abweichungen außerhalb des erlaubten
  CI-Zeitskews werden abgewiesen; alte, korrekt quittierte Historie bleibt
  ohne Re-Attestation replayfähig;
- regulärer Operator-Handover sowie Recovery vor und nach Pilot werden mit
  Offline-Recovery-Root, Epochwechsel und atomarem Gate-Reset positiv;
  einseitige Rotation, Wiederverwendung früherer Epoch-Signaturen und das
  Suspendieren des einzigen Operators werden negativ geprüft; initiale
  Custodian-Besetzung verlangt Operator, Root und Kandidatenannahme,
  post-Pilot-Rotation Root und verbleibenden Custodian als Autorisierer sowie
  den eingehenden Custodian nur als Annahmenachweis und alle Gate-Resets.
  Operator-only-Unassign/Suspend/Retire, Keytausch per Amendment
  und Recovery beim Verlust beider Custodians werden fail-closed abgewiesen;
  vor Pin-Transition darf der Kandidat keinen Reset autorisieren, fehlende oder
  gesplittete Pin-Logeinträge halten sämtliche Gates `red`;
- `GATE-G0 green` ohne assigned und extern gepinnten Recovery-Root,
  Validator-Controller, Recovery-App, Recovery-Write-ahead-Gateway,
  Provider-Ref-Verifier, Egress-Enforcement-Monitor, Transparenzinstanz, alle Witnesses oder frischen
  co-signierten Checkpoint sowie `GATE-PILOT green` ohne zwei getrennte
  Custodians werden abgewiesen; Pilot-Green verlangt zusätzlich genehmigte und
  praktisch getestete Verlust-/Rotationsverfahren für Recovery-Root,
  Validator-Controller, Recovery-App, Transparenzinstanz, alle Witnesses und Custodian-Pins;
- `requested@epoch1→approved@epoch2` und
  `captured@epoch1→verified@epoch2` werden abgewiesen; vollständig neu
  erzeugte REV/EVID in Epoch 2 sowie die historische Supersession einer
  `approved`-REV beziehungsweise `verified`-EVID aus Epoch 1 werden positiv
  geprüft; beide Vorgänger bleiben dauerhaft nicht gatewirksam;
- die geschlossene Reviewtyp-/Rollen-/Approvermatrix und P0/P1-Dismissalregel
  werden je Reviewtyp positiv und mit Rollenidentität bzw. falscher
  Qualifikation negativ geprüft;
- agentische Reasoning-Freigaben sowie externe LLM-Due-Diligence und
  Sanitisierung sind schema- und evidenzpflichtig; fehlende, nachträgliche
  oder produktionsnahe Nachweise werden abgewiesen. Positiv ist die Sequenz
  „DD/Sanitisierung/Egress-Dispatcher-Vertrag extern quittiert → erwarteter EVID-
  Semantikkern gebunden → Preflight-Receipt geloggt → versiegelte Enforcement-
  Lease und Dispatch-Attestation erzeugt → Request gesendet → vollständigen
  Transport-Receipt erzeugt → identische Raw-Bytes erfasst“. Dispatch vor Receipt,
  nachträgliche Subject-/Scope-/Command-Änderung, Token-Reuse, Rückdatierung,
  Envelope-/Receipt-/Runner-Key-Abweichung oder
  `EVID.sha256 != providerResponseSha256` wird einzeln abgewiesen. Ebenso
  scheitern direkter Host-/Runner-Egress, leerer oder falsch typisierter
  Dispatcherbeleg, fremder Binary-/Netzwerkpolicy-Digest, DNS-/Proxy-Bypass,
  Parallelverbrauch und Versand an einen nicht gebundenen Endpoint. Zusätzliche
  Body-/Application-Headerbytes, uncheckpointetes Fork-Receipt, alte Witness-
  Challenge, abgelaufener Dispatcher-/Netzwerkvertrag oder fehlende frische
  Monitor-Attestation müssen jeweils vor dem ersten Netzwerkbyte scheitern.
  Ein Policywechsel nach Vorabprüfung, zwischen Tokenverbrauch und erstem Byte
  oder während des Transports erzwingt atomaren Abbruch; abweichende Start-/
  End-Epoch, fehlender Wire-/TLS-Transcript, falsche HTTP/1.1-Hostfelder oder
  falsche HTTP/2-Pseudoheader dürfen keinen gültigen Output stützen. Separat
  scheitern Zusatz- oder Doppelheader, Trailer, Connection-Reuse, ein fremder
  H2-Stream, fehlender SETTINGS-/ACK-Präfix und identische H2-Headerblockbytes
  unter zwei verschiedenen HPACK-Ausgangszuständen;
- Provider-, Endpoint-, Modell-, Region-, Retention-, Training-, Sanitizer-
  oder Inputhash-Abweichungen zwischen Due-Diligence, Sanitization und
  External-Model-Output werden einzeln abgewiesen;
- ein externes Modell wird ausschließlich als EVID-Quelle eines lokal
  attestierten Runners akzeptiert; seine Ausgabe kann weder Reviewer-,
  Approver- noch Akteuridentität erfüllen;
- jedes Inputmanifest muss die vollständige transitive Ableitung samt
  Ausnahmeprovenienz binden; fehlende Inputs, geänderte Pfade oder ein
  Versuch, No-Waiver-Taint über eine neue EVID zu waschen, werden abgewiesen;
- Ableitungen aus PROFILE, ROLE, COMP, DATA und FLOW werden je Familie mit
  tainted und untainted Fällen geprüft; Weglassen des Ursprungsrecords oder
  seiner transitiven Provenienz hält das No-Waiver-Gate `red`;
- das Auditprofil akzeptiert ausschließlich den signierten Forced-Command-
  Collectorvertrag; interaktive Shell, PTY/Forwarding, freie Argumente,
  ausgehendes Netz, Schreibversuche nach `/tmp`/`/var/tmp`, jede verfügbare
  Socket-/Netlink-/AF_UNIX-/D-Bus-/Container-Verbindung oder pauschales `sudo`
  werden negativ geprüft. Der geschützte Manifestzustand von Dateien, Paketen
  und Services muss bytegleich bleiben; ausschließlich die zwei expliziten,
  auditierten Supervisor-Deltas für Journal und Invocation-Accounting werden
  akzeptiert, jede weitere Zustandsänderung abgewiesen;
- typsichere bidirektionale Record-Supersession wird positiv, fremde Familien,
  einseitige Referenzen, Kreise und nicht terminale Vorgänger negativ geprüft;
- nur existierende COMP-IDs werden in Flows akzeptiert; freie logische,
  Host-, IP-, Provider- oder Tenantbezeichner werden abgewiesen;
- die Schema-Datei ist reines Draft-2020-12-JSON und jeder Markdown-Registerblock
  erfüllt genau dieses Schema;
- die vorgeschriebene Quellenhierarchie und Reasoning-Direktive müssen in den
  Entwicklerdirektiven vorhanden sein;
- ein PR-eigener oder mit dem geprüften Head veränderbarer Validator darf
  weder Remote-Kontrollen noch die eigene Promotion bestätigen;
- Validator-/Policy-/Workflow-/Schema-/Trust-Protokoll-Promotion ohne
  Operator, Offline-Recovery-Root, alte Validatorprüfung oder – sobald der
  Pilot jemals aktiviert war – beide Custodians wird abgewiesen; ein
  Sockpuppet-Review genügt nicht. Positiv wird die konstruktive Sequenz
  unveränderlicher Request ohne Zukunfts-SHA und mit zwei grünen Gate-Resets →
  alter TCB-Receipt des atomaren Reset-Heads → Activation → Rollback-
  Autorisierung → witness-bestätigtes Activation-Bundle geprüft; ein nur
  eventgebundener Einzel-Scope für beide Gates, falscher Requesthash, fremdes
  Receipt, fehlende Rollback-Autorisierung, Request-Reuse oder abweichender
  Head/Tree scheitert. Ein vor einer `A→B→A`-Folge erzeugter Request bleibt
  trotz identischer späterer TCB-Digests stale. Zu früher Activation-
  Checkpoint, zu später Rollback-Checkpoint und jede rückdatierte
  Zwischenzeit scheitern. Ausgeblendeter Rollback, verzweigter TCB-State und
  Receipts einer verworfenen State-Epoch sind ungültig. Normaler und Emergency-
  Restore werden nur mit extern gepinnter App, korrekten App-/Policy-/
  Permission-Digests, vollständig vorher witness-bestätigter Autorisierung und
  providerverifiziertem CAS akzeptiert; falscher Key, abweichende Ref-OIDs oder
  bloß behaupteter Restore scheitern. CAS-Precondition-Failure wird über den
  witness-bestätigten Abort sicher entsperrt; die alte Lease bleibt permanent
  unbrauchbar und nur eine neu autorisierte Recovery kann erneut versuchen.
  Getrennt positiv geprüft werden Authorization-Checkpoint ohne erzeugbare
  Lease sowie App-Crash/Berechtigungsverlust nach Claim, aber vor Gateway-
  Akzeptanz und der anschließende Retry nach checkpointetem `cancelled`-Beleg.
  Crash nach `accepted`, aber vor `dispatch-started`, sowie Crash nach
  `dispatch-started` mit unabhängig belegten null Providerbytes werden sicher
  abgebrochen; ohne Zero-Byte-Beleg bleibt der zweite Fall fail-closed. Ein
  Sendepfad auf Control-Plane-Handle A mit nachträglichem Zero-Byte-Closure für
  Handle B, ein abweichender Namespace, Counter, Policy- oder Tokenhash und
  jedes Egress-Intent ohne vorherigen Vollquorum-Checkpoint scheitern. Direkter
  Gateway-/Host-Egress über DNS, Proxy, IPv4, IPv6, Unix-Socket, fremde
  Credentialkopie oder ein zweites Netzwerk-Namespace wird negativ geprüft;
  Parallel-Issue
  auch mit abweichender Subject-ID unter derselben Authorization, Doppel-Claim,
  Geschwister-Nachfolger, Operationskennungs-/Providerreceipt-Replay bei
  identischer späterer OID-Folge, Providerstart oder -abschluss nach Lease-/
  Authorization-Ablauf, zurückdatierte App-Zeit, replayte Floor-Responses,
  ausgelassene Gateway-Sequenz, konkurrierendes Accept/Cancel,
  zwei je intern signierte, aber konkurrierende Gateway-/Transparenzköpfe,
  direkter Recovery-App-Egress oder App-Providercredential, automatische
  Retransmission nach `dispatch-started` und Wiederholung desselben atomaren
  Branch-/Marker-Requests nach `A→B→A`, auch wenn der Marker zwischen zwei
  Remote-Snapshots gelöscht und identisch wiederangelegt wurde, scheitern am
  extern witness-checkpointierten Idempotenz-Tombstone. Ein fehlender,
  doppelter oder umgehbarer Tombstone sowie ein zweites Egress-Intent für
  denselben Tombstone werden abgewiesen;
  App-Erfolgsbehauptung ohne unabhängigen Providerbeleg, falsche
  Provideridentität und ein als `failed` getarnter erfolgreicher CAS scheitern;
  das vollständige Kreuzprodukt aus Leasephase, Gatewayphase, Tombstonezustand,
  Egress-Intent-Zustand, Closuregrund, Abortgrund, Failure-Proof-Typ und
  Nullability wird als Schema-/Replaytest festgeschrieben;
- Acceptance-Receipts bilden jede Attestation eines Events exakt einmal ab;
  fehlende sekundäre Nonces, falsche Purposes oder zusätzliche Einträge
  werden abgewiesen. Ein Transparency-Bundle muss exakt die Logindizes
  `0..treeSize-1` enthalten und Root sowie Hashkette neu ergeben; Weglassen
  eines späteren Kontroll- oder Revocation-Eintrags, Lücke, Duplikat oder
  Fremdeintrag scheitert. Drei Receipts derselben alten Branch-Policy-Epoch
  werden durch eine Transition sämtlich nicht gatewirksam. Normale und
  Recovery-Rotation des Instanzkeys werden vom Genesis-Pin über vollständige
  Transition-/Checkpoint-/Witness-Floor-Ketten replayt; fehlende Transition,
  alter Checkpoint unter aktuellem Floor, vorzeitiger Pinwechsel, fehlender
  Witness oder inkonsistente Key-Epoch scheitert. Zwei kollidierende, erst
  teilweise witness-signierte Proposals genügen für eine gültige
  Equivokationsmeldung und setzen alle Gates `red`;
- RFC-8785-Testvektoren legen für Promotion-, Activation-, Rollback-,
  Emergency-, Recovery-App-, Key-Transition-, Equivocation-Report-,
  Provider-Receipt-, Recovery-Write-ahead-, Recovery-Idempotency-Tombstone-,
  Recovery-Egress-Intent-, Recovery-Egress-Closure-,
  Pin-Transition-, Egress-
  Dispatcher-, Enforcement-Lease-Intent-, Enforcement-Lease-,
  Dispatch-Attestation-, Transport- und
  Request-Receipt-Core exakt
  Bytes und Digest fest; jede zusätzliche, ausgelassene oder anders sortierte
  Eigenschaft sowie jeder fremde Purpose scheitert. Beim Lease-Intent mutiert
  der Test jedes gebundene Feld einzeln und weist nach, dass Intentfeld,
  Witness-Arrayhash, Aktivierungszeit, Core und Signatur nicht im Intent-
  Preimage liegen. Für Gateway-Receipts prüfen feste Vektoren getrennt
  `receiptCoreSha256` über ausschließlich den spezifischen Gateway-Payload und
  `entryCoreSha256` über den vollständigen Logeintrag; jede alternative
  Projektion, insbesondere die Aufnahme von `repositoryId`, `logId` oder
  `entryKind` in den Receipt-Core, wird zwingend verworfen;
- jeder Eintrag des geschlossenen initialen G0-Manifests besteht.

Das Package-Skript `check:governance` wird in die bestehenden lokalen
Qualitätsgates aufgenommen. Die bekannte Windows-Glob-Lücke des allgemeinen
MJS-Testskripts wird als eigener Task innerhalb des G0-Pakets korrigiert, damit
Governance-Tests nicht nur über einen Sonderaufruf nachgewiesen werden.

Der Offline-Validator behauptet keinen Live-Zustand von GitHub.
Der verpflichtende Remote-Check wird nicht aus dem PR-Head ausgeführt. Eine
separate read-only GitHub-App oder ein immutable wiederverwendbarer Workflow
aus einem getrennt geschützten Repository startet einen signierten Validator-
Container über einen außerhalb von AURELIA gepinnten SHA-256-Digest. Er liest
Branchschutz, Bypass-, Signatur-, CODEOWNERS- und Pflichtcheckstatus und
schreibt akzeptierte Nonces, Head-/Tree-Digests und Receipts in ein externes
append-only Transparenzlog. Validator-, Workflow-, Schema- oder
Trust-Protokolländerungen benötigen zuerst einen eigenen Bootstrap-Change,
Prüfung durch den bisher gepinnten Validator, unabhängige Quality/Security-
Freigabe und danach eine zweistufige externe Aktivierung ohne zukünftigen
Git-SHA im Repositoryartefakt.

Der nach `validator-promotion-request.schema.json` geschlossene Request unter
`docs/governance/promotions/<EVID-ID>.json` enthält ausschließlich
`schemaVersion`, `promotionEvidenceRef`, `repositoryId`,
`previousTcbStateEpoch`, `previousTcbStateEntryId`,
`previousTcbStateEntrySha256`,
`previousValidatorImageDigest`, `nextValidatorImageDigest`,
`previousPolicySha256`, `nextPolicySha256`, `previousWorkflowSha256`,
`nextWorkflowSha256`, `previousSchemaSetSha256`, `nextSchemaSetSha256`,
`previousTrustProtocolSha256`, `nextTrustProtocolSha256`, sortierte
`reviewRefs`, `gateResetPlan`, `gateResetTransactionSha256`,
`activationNotBefore`, `expiresAt`, `rollbackValidUntil`, `nonce` und
`authorizationSignatures`. Er nennt weder einen zukünftigen
Commit noch Tree oder Receipt. Operator und `ROLE-RECOVERY-ROOT` signieren immer
dieselbe Promotion-Core-Payload; sobald `GATE-PILOT` jemals grün war,
signieren zusätzlich beide Custodians. Jede Signatur besitzt Purpose, KeyRef,
Signerrolle/-identität, Zeitpunkt, eigene Nonce, Core-Digest und Ed25519-
Signatur. Der bisher gepinnte Validator prüft Reviews, alte und neue Digests,
Schwelle, Ablauf und Rollback, bevor die externe Instanz atomar umstellt.
Zulässige Promotion-Purposes sind exakt `operator`, `recovery-root`,
`custodian-a` und `custodian-b`; Key-/Assigneebindung wird gegen den aktuellen
Replayzustand und die externen Offline-Pins geprüft.
Vorgänger-Epoch, -ID und -Hash müssen bei Requesterzeugung, Gate-Reset-Head und
Activation bytegleich dem aktuellen Replayzustand sein; selbst bei später
wieder identischen TCB-Digests ist eine andere State-Epoch stale. Es gilt strikt
`activationNotBefore < expiresAt < rollbackValidUntil`; der Abstand zwischen
`expiresAt` und `rollbackValidUntil` liegt zwischen einer und 24 Stunden.
Die vollständige vertrauenswürdige Ordnung lautet
`activationNotBefore <= preparedAt <= activationBundle.loggedAt <=
activationCheckpoint.issuedAt <= expiresAt`. Der Checkpoint-Zeitpunkt ist der
einzige effektive Aktivierungszeitpunkt. Für Rollback gilt strikt
`activationCheckpoint.issuedAt < rolledBackAt <= rollbackEntry.loggedAt <=
rollbackCheckpoint.issuedAt <= rollbackValidUntil`; der alte TCB bleibt bis
einschließlich zum wirksamen Rollback-Checkpoint isoliert verfügbar.

`gateResetPlan` enthält nach `gateRef` sortiert exakt jedes beim Request-Head
grüne Gate. Jeder Eintrag besitzt ausschließlich `gateRef`,
`previousRecordSha256`, `resultingRedRecordSha256` und `changeDigest`;
`changeDigest` folgt der normalen EVT-Projektion. `gateResetTransactionSha256`
ist SHA-256 der RFC-8785-kanonischen Projektion aus `repositoryId`,
`promotionEvidenceRef` und dem vollständigen `gateResetPlan`. Die
Promotion-Request-EVID besitzt den Scope
`governance-transaction:tcb-promotion:<gateResetTransactionSha256>` und führt
sämtliche Plan-`changeDigest`-Werte in `governanceChangeDigests`. Ausschließlich
für diese atomare Resettransaktion ersetzt sie damit den sonst eventgenauen
EVID-Scope; fehlendes, zusätzliches oder inzwischen anders grünes Gate macht
den Request stale.

Jeder Eintrag von `authorizationSignatures` enthält ausschließlich `purpose`,
`signerRole`, `signerIdentity`, `keyRef`, `signedAt`, `nonce`,
`promotionCoreSha256` und `signature`, sortiert nach `purpose,keyRef`.
`promotionCoreSha256` ist der Hash aller Top-Level-Requestfelder außer
`authorizationSignatures`; das gleichnamige Digestfeld liegt ausschließlich
in den Signatureinträgen und gehört deshalb nicht zu dieser Projektion. Alle
Signaturen binden exakt diesen Core. Ein
zusätzliches oder fehlendes Feld, eine doppelte Purpose-/Key-Kombination oder
eine Signatur über eine andere Projektion ist ungültig.

Nach verifizierter Request-EVID erzeugt das Repository einen noch durch den
alten TCB quittierten Governance-only-Head, der jede grüne Gate-Akte auf
`red` setzt und ausschließlich über Request-EVID-ID, Artefaktpfad und -hash
auf den unveränderten Request verweist. Jeder Reset-EVT muss exakt einem
`gateResetPlan`-Eintrag entsprechen und konsumiert dieselbe transaktionsgebundene
Request-EVID; die atomare Transaktion darf keine andere Änderung enthalten.
Der alte Validator vergleicht die drei signierten Vorgänger-State-Felder vor
und nach dieser Transaktion erneut mit seinem aktiven TCB-State; eine
zwischenzeitliche Activation, Rollback- oder Recovery-Transition macht Request,
Reset-Head und Receipt ungültig.
Erst jetzt erzeugt der externe alte Controller einen noch inerten, signierten
`validator-activation`-Record. Dieser enthält ausschließlich `schemaVersion`,
`repositoryId`, `activationId`, `requestEvidenceRef`, `requestSha256`,
`resetReceiptId`, `resetHeadCommit`, `resetHeadTreeOid`,
`previousTcbStateEpoch`, `previousTcbStateEntryId`,
`previousTcbStateEntrySha256`, `previousTcb`, `nextTcb`, `preparedAt`,
`activationNonce` und `controllerSignature`. `previousTcb` und `nextTcb`
enthalten jeweils ausschließlich `validatorImageDigest`, `policySha256`,
`workflowSha256`, `schemaSetSha256` und `trustProtocolSha256`.
`controllerSignature` enthält ausschließlich `keyRef`, `signedAt`, `nonce`,
`activationCoreSha256` und `signature`; der Core ist die RFC-8785-Projektion
aller übrigen Activation-Felder ohne `controllerSignature`. Der
`activationSha256` ist stets der SHA-256 der vollständigen kanonischen,
bereits signierten Activation-Bytes. Die drei Vorgänger-State-Felder sind
bytegleich zum Promotion-Request und zum beim Reset-Receipt aktiven State.

Vor jeder Umschaltung entsteht die nach
`validator-rollback-authorization.schema.json` geschlossene
Rollback-Autorisierung. Sie enthält ausschließlich `schemaVersion`,
`repositoryId`, `activationId`, `activationSha256`, `requestEvidenceRef`,
`requestSha256`, `rollbackHeadReceiptId`, `rollbackHeadCommit`,
`rollbackHeadTreeOid`, `previousTcb`, `nextTcb`, `rollbackValidUntil`,
`allowedReasons`, `rollbackCoreSha256` und `authorizationSignatures`.
Rollback-Head und -Receipt sind exakt der durch den alten TCB akzeptierte
Reset-Head. `allowedReasons` ist das sortierte, duplikatfreie Array aus
`health-check-failed`, `policy-regression` und `validator-unusable`.
`rollbackCoreSha256` ist der Hash aller Felder außer sich selbst und
`authorizationSignatures`. Jeder nach `purpose,keyRef` sortierte
Signatureintrag enthält ausschließlich `purpose`, `signerRole`,
`signerIdentity`, `keyRef`, `signedAt`, `nonce`, `rollbackCoreSha256` und
`signature`; Purposes sind `controller`, `operator`, `recovery-root`,
`custodian-a` und `custodian-b`. Controller, Operator und Root sind immer,
nach erstmaligem Pilot-Green zusätzlich beide Custodians erforderlich. Der
`rollbackAuthorizationSha256` ist der Hash der vollständigen kanonischen,
signierten Autorisierung.

Activation und Rollback-Autorisierung werden zyklusfrei durch einen nach
`validator-activation-bundle.schema.json` geschlossenen
`entryKind: "tcb-activation"`-Eintrag verbunden. Sein spezifischer Payload
enthält ausschließlich `activationId`, `activationSha256`,
`rollbackAuthorizationSha256`, `requestEvidenceRef`, `requestSha256`,
`requestConsumed: true`, `previousTcbStateEpoch`, `tcbStateEpoch` exakt um eins
erhöht, `previousTcbStateEntryId`, `previousTcbStateEntrySha256`, `nextTcb`,
`rollbackValidUntil`, `effectiveAfterCheckpoint: true`,
`controllerBundleCoreSha256` und `controllerSignature`. Die Controller-
Signatur enthält ausschließlich `keyRef`, `signedAt`, `nonce`,
`controllerBundleCoreSha256` und `signature`; der Core ist die
RFC-8785-Projektion aller spezifischen Payloadfelder außer Core und Signatur.
Die gemeinsamen Transparenzlogfelder werden erst beim Append hinzugefügt und
durch `entryCoreSha256` gebunden. Der Request darf in der gesamten Logfolge nur
einmal verbraucht werden. Erst wenn der Eintrag im vollständigen Logpräfix
liegt und ein Checkpoint mit allen Witness-Signaturen ihn umfasst, schaltet der
Controller auf `nextTcb`; vorher bleiben Activation und Bundle inert. Jedes
spätere Acceptance-Receipt bindet diese TCB-State-Epoch sowie ID und Hash des
aktiven State-Eintrags. Für Bootstrap-Epoch `1` sind Vorgänger-ID/-Hash `null`;
danach ist die State-ID je nach aktivierender Transition exakt `activationId`,
`rollbackId` oder `recoveryId`, und ihr State-Hash ist der SHA-256 der
vollständigen kanonischen, signierten Logentry-Bytes.

Der Controller hält den alten TCB mindestens bis `rollbackValidUntil` isoliert
ausführbar. Innerhalb dieser Frist kann er ohne Mitwirkung des neuen Validators
den gebundenen Reset-Head und exakt `previousTcb` wiederherstellen. Der nach
`validator-rollback-record.schema.json` geschlossene
`entryKind: "tcb-rollback"`-Logeintrag besitzt spezifisch ausschließlich
`rollbackId`, `activationId`, `activationEntrySha256`,
`rollbackAuthorizationSha256`, `reason`, `attemptedHeadCommit`,
`attemptedHeadTreeOid`, `restoreReceiptId`, `restoreHeadCommit`,
`restoreHeadTreeOid`, `restoredTcb`, `authorizationCheckpointSha256`,
`authorizationCheckpointTreeSize`, `authorizationCheckpointIssuedAt`,
`recoveryOperationLeaseId`, `recoveryOperationLeaseSha256`,
`recoveryAppAttestationRef`, `recoveryAppAttestationSha256`,
`gatewayAcceptedReceiptRef`, `gatewayAcceptedReceiptSha256`,
`recoveryIdempotencyTombstoneRef`, `recoveryIdempotencyTombstoneSha256`,
`recoveryEgressIntentRef`, `recoveryEgressIntentSha256`,
`gatewayDispatchStartedReceiptRef`, `gatewayDispatchStartedReceiptSha256`,
`gatewaySettledReceiptRef`, `gatewaySettledReceiptSha256`,
`providerReceiptRef`, `providerReceiptSha256`,
`compareAndSwapOperationIdSha256`, `previousTcbStateEpoch`, `tcbStateEpoch`
exakt um eins erhöht, `previousTcbStateEntryId`,
`previousTcbStateEntrySha256`, `rolledBackAt`, `rollbackRecordCoreSha256` und
`controllerSignature`. `reason` muss in den vorab autorisierten
`allowedReasons` liegen; Restore-Receipt, -Head, -Tree und TCB müssen bytegleich
der Rollback-Autorisierung sein. Der Authorization-Checkpoint ist exakt der
Vollquorum-Checkpoint, der die Activation samt gebundener
Rollback-Autorisierung aktivierte. Vor Append des Rollback-Records reicht die
extern gepinnte Recovery-App ausschließlich den signierten, vollständig
gebundenen Auftrag beim Write-ahead-Gateway ein; nur dieses Gateway führt den
providerseitigen Compare-and-swap von `attemptedHeadCommit` auf
`restoreHeadCommit` aus. Die geschlossene App-Attestation und der
providerseitige Operationsbeleg werden durch Ref und Vollbyteshash gebunden.
Die Controller-Signatur enthält ausschließlich
`keyRef`, `signedAt`, `nonce`, `rollbackRecordCoreSha256` und `signature` und
bindet den Core aller übrigen spezifischen Payloadfelder. Der Eintrag wird erst
nach vollständigem Witness-Checkpoint aktiv. Alle Receipts der verworfenen
TCB-State-Epoch bleiben historisch, dürfen ab diesem Logindex aber kein Gate
oder Release mehr stützen; alle Gates sind abgeleitet `red`.

Nach Fristablauf oder wenn der aktive TCB bereits einen unzulässigen Head
akzeptiert hat, hängt Recovery nicht vom aktiven Validator ab. Das nach
`emergency-tcb-recovery.schema.json` geschlossene Zustandsverfahren schreibt
zuerst einen witness-bestätigten `entryKind: "tcb-emergency-recovery"`,
`phase: "authorized"`-Eintrag. Sein spezifischer Payload enthält
ausschließlich `recoveryId`, `phase`, `incidentArtifactUri`,
`incidentArtifactSha256`, `branch`, `expectedCompromisedHeadCommit`,
`recoveryTargetReceiptId`, `recoveryTargetHeadCommit`,
`recoveryTargetHeadTreeOid`, `recoveryTargetTcb`, `previousTcbStateEpoch`,
`reservedTcbStateEpoch` exakt um eins erhöht,
`previousTcbStateEntryId`, `previousTcbStateEntrySha256`, `authorizedAt`,
`authorizationExpiresAt`,
`recoveryAuthorizationCoreSha256` und `authorizationSignatures`. Die nach
`purpose,keyRef` sortierten geschlossenen Signatureinträge enthalten
ausschließlich `purpose`, `signerRole`, `signerIdentity`, `keyRef`, `signedAt`,
`nonce`, `recoveryAuthorizationCoreSha256` und `signature`; erforderlich sind
Controller, Operator und Recovery-Root sowie nach erstmaligem Pilot-Green beide
Custodians. Während dieser reservierten Phase sind weitere TCB-Transitions,
Annahmen und Releases gesperrt. Die Frist liegt höchstens 15 Minuten nach
`authorizedAt`; Fristablauf allein entsperrt jedoch nichts.
Eine separat geschützte Recovery-App darf danach ausschließlich den signierten
Auftrag für den exakt gebundenen Branchref beim Write-ahead-Gateway einreichen;
nur das Gateway führt den Compare-and-swap vom beobachteten Head auf den Last-
known-good-Head aus. App und Gateway erhalten kein Wildcard-, Shell- oder
allgemeines Force-Push-Recht. Der ebenfalls witness-bestätigte
`phase: "completed"`-Eintrag besitzt spezifisch ausschließlich `recoveryId`,
`phase`, `authorizationEntrySha256`, `authorizationCheckpointSha256`,
`authorizationCheckpointTreeSize`, `authorizationCheckpointIssuedAt`,
`recoveryOperationLeaseId`, `recoveryOperationLeaseSha256`, `branch`,
`observedRestoredHeadCommit`, `observedRestoredHeadTreeOid`, `restoredTcb`,
`recoveryAppAttestationRef`, `recoveryAppAttestationSha256`,
`gatewayAcceptedReceiptRef`, `gatewayAcceptedReceiptSha256`,
`recoveryIdempotencyTombstoneRef`, `recoveryIdempotencyTombstoneSha256`,
`recoveryEgressIntentRef`, `recoveryEgressIntentSha256`,
`gatewayDispatchStartedReceiptRef`, `gatewayDispatchStartedReceiptSha256`,
`gatewaySettledReceiptRef`, `gatewaySettledReceiptSha256`,
`providerReceiptRef`, `providerReceiptSha256`,
`compareAndSwapOperationIdSha256`,
`previousTcbStateEpoch`, `tcbStateEpoch` gleich der reservierten Epoch,
`previousTcbStateEntryId`, `previousTcbStateEntrySha256`, `completedAt`,
`recoveryCompletionCoreSha256` und `controllerSignature`. Die geschlossene
Controller-Signatur enthält `keyRef`, `signedAt`, `nonce`,
`recoveryCompletionCoreSha256` und `signature`. Authorization-Hash, Branch,
Vorgänger-State, reservierte Epoch und beobachteter Restore müssen exakt zur
autorisierten Phase und zum ausgeführten Compare-and-swap passen. Die App-
Attestation bindet App-Image/Policy, unverbrauchte Authorization, erwarteten
und gesetzten Ref-OID, Marker-Ref, externen Idempotenz-Tombstone,
checkpointetes Egress-Intent, checkpointete Gatewayphasen sowie den
providerseitigen Operationsbeleg. Erst dieser
zweite Eintrag aktiviert den Wiederanlauf. Sämtliche Receipts der verworfenen
Epochen bleiben nicht gatewirksam; neuer Betrieb verlangt frische Receipts,
Reviews und Gatefreigaben.

Scheitert der Compare-and-swap, läuft die Autorisierung ab oder soll sie vor
Ausführung verworfen werden, ist statt `completed` ausschließlich ein
witness-bestätigter `phase: "aborted"`-Eintrag zulässig. Sein spezifischer
Payload enthält ausschließlich `recoveryId`, `phase`,
`authorizationEntrySha256`, `authorizationCheckpointSha256`,
`authorizationCheckpointTreeSize`, `authorizationCheckpointIssuedAt`,
`recoveryOperationLeaseId`, `recoveryOperationLeaseSha256`, `abortReason:
"lease-unavailable"|"gateway-not-dispatched"|"cas-precondition-failed"|"provider-error"|"authorization-expired"|"operator-abort"`,
`observedBranchHeadCommit`,
`failureProofType: null|"gateway-cancelled"|"gateway-settled-failure"`,
`failureProofRef`, `failureProofSha256`, `failureProofCheckpointSha256`,
`failureProofCheckpointTreeSize`, `previousTcbStateEpoch`,
`reservedTcbStateEpoch`, `previousTcbStateEntryId`,
`previousTcbStateEntrySha256`, `abortedAt`, `recoveryAbortCoreSha256` und
`authorizationSignatures`. Die Signaturform und Schwelle sind bytegleich zur
Authorized-Phase, binden aber den Abort-Core. Falls nach dem Authorization-
Checkpoint noch keine Lease erzeugt werden konnte, sind beide Leasefelder
ausschließlich bei `lease-unavailable|authorization-expired|operator-abort`
`null`; der Abort bindet weiterhin Authorization-Checkpoint und volle Schwelle.
Ohne Claim sind alle fünf Failure-Felder `null`. Nach Claim, aber vor einer
witness-bestätigten `dispatch-started`-Phase verlangt
`gateway-not-dispatched` Typ `gateway-cancelled` und Ref/Vollbyteshash sowie
Vollquorum-Checkpoint des unten geschlossenen, nach Lease-Ablauf erzeugten
Cancellation-Logeintrags. Ein Recovery-App-Crash wird ausschließlich über
diesen Gatewayzustand aufgelöst und besitzt keinen uneindeutigen eigenen
Failure-Typ. Nach `dispatch-started` verlangt jeder abschließend belegte CAS-/
Providerfehler Typ `gateway-settled-failure` und den checkpointeten `settled`-
Gateway-Logeintrag, der den fehlgeschlagenen Providerbeleg bindet; ein nur
unbekannter Providerausgang darf nicht als Fehler deklariert werden.
Abort aktiviert keinen neuen TCB-State, gibt die Reservierung erst nach seinem
Vollquorum-Checkpoint frei und hält alle Gates `red`. Ein Retry verlangt neue
Recovery-ID, neue Lease und neue Schwellenautorisierung; er darf dieselbe
nächste Epoch erneut reservieren.

Der Vollpräfix-Replay führt jede Recovery-Lease atomar in genau einem Zustand
`pending|executing|failed|completed|aborted`: die unten witness-bestätigten
Lease-Phasen bilden `pending`, `executing` und `failed`; der zugehörige
Rollback-/Recovery-Terminaleintrag bildet `completed` oder `aborted`. Die App
akzeptiert nur die jüngste live witness-bestätigte `executing`-Lease. Der
Abort-Pfad kann nur `pending|failed` beenden. Unklarer Providerausgang bleibt
`executing` und damit fail-closed, bis die Provideroperation eindeutig
reconciled und als `failed` oder erfolgreich attestiert ist. Nach Abort,
Completion, Supersession oder Claim-Verbrauch lehnt die App jede alte
Autorisierung anhand des aktuellen Vollpräfixes und aller live abgefragten
Witness-Floors permanent ab.
Die Recovery-App besitzt weder Provider-Schreibcredential noch einen direkten
Provider-Egresspfad. Ausschließlich das extern gepinnte
`recoveryWriteAheadGateway` darf den gebundenen Ref über die unten festgelegte
CAS-Primitive und ausschließlich über das für genau einen Auftrag vom
unabhängigen Egress-Monitor versiegelte Control-Plane-Handle schreiben. Stürzt
die App nach Claim, aber vor der atomaren
Gateway-Akzeptanz ab, wechselt das Gateway den bereits dauerhaft registrierten
Auftrag nach Lease-Ablauf atomar von `registered` auf `cancelled`. Weil nur
eine eigene witness-bestätigte `dispatch-started`-Phase Providerbytes senden
darf und die Gateway-Credential ausschließlich an denselben isolierten
Control-Plane-Pfad gebunden ist, beweist dieser
Receipt ohne negative Provider-Auditannahme, dass die Operation nicht begonnen
hat. Auch nach `accepted` ist nach Lease-Ablauf `cancelled` zulässig, solange
kein `dispatch-started` existiert. Nach `dispatch-started` ist Cancellation nur
mit einem unabhängigen, unten geschlossenen und an dasselbe vorab
checkpointete Egress-Intent gebundenen Zero-Byte-Egress-Closure-Beleg
zulässig. Sobald mindestens ein Providerbyte möglich war, bleiben Crash,
Timeout oder verlorene Antwort `executing`, bis Provider-Marker,
Provider-Ref-Verifier und Gateway den Ausgang eindeutig als `settled` belegen.
Es gibt weder blinde noch automatische Retransmission und keinen
unspezifizierten manuellen Entsperrpfad.

Die Lease ist selbst eine nach `recovery-operation-lease.schema.json`
geschlossene `entryKind: "recovery-operation-lease"`-Kette im vollständigen
Transparenzlog. Ihr spezifischer Payload enthält ausschließlich `leaseId`,
`phase: "issued"|"claimed"|"failed"`,
`operationType: "tcb-rollback"|"tcb-emergency-recovery"`,
`operationSubjectId`, `authorizationEntrySha256`, `authorizationCheckpointSha256`,
`authorizationCheckpointTreeSize`, `previousLeaseEntrySha256`, `branch`,
`expectedRefOid`, `targetRefOid`, `operationCorrelationId`,
`providerIdempotencyKeySha256`, `gatewayRegistrationReceiptRef`,
`gatewayRegistrationReceiptSha256`, `gatewayRegistrationCheckpointSha256`,
`gatewayRegistrationCheckpointTreeSize`, `issuedAt`,
`expiresAt`, `failureProofType:
null|"gateway-cancelled"|"gateway-settled-failure"`,
`failureProofRef`, `failureProofSha256`, `failureProofCheckpointSha256`,
`failureProofCheckpointTreeSize` und `effectiveAfterCheckpoint: true`.
`issued` wird
erst nach dem Authorization-Checkpoint erzeugt, hat
`previousLeaseEntrySha256: null`, alle vier Gateway-Registration-Felder `null`
und alle fünf Failure-Felder `null`. Nach dessen Vollquorum-Checkpoint erzeugt
das Gateway den `registered`-Logeintrag. `claimed` bindet die vollständigen
Issued-Entry-Bytes, Ref/Vollbyteshash und Vollquorum-Checkpoint exakt dieses
Eintrags und behält alle übrigen Operationsfelder bytegleich. `failed` bindet
die Claim-Bytes und Ref/Vollbyteshash sowie Vollquorum-Checkpoint entweder des
`cancelled`- oder des fehlgeschlagenen `settled`-Gateway-Logeintrags. Jede
Phase wird erst mit ihrem eigenen Vollquorum-Checkpoint
wirksam. Die App darf ausschließlich nach dem Claim-Checkpoint die Operation
an das Gateway übergeben; nur das Gateway darf danach die vor Issue global
einmalige rohe `operationCorrelationId` und deren als
`providerIdempotencyKeySha256` gebundenen SHA-256-Digest der exakten UTF-8-
Bytes verwenden. Der Feldname bezeichnet nur die lokale Korrelationsbindung;
er behauptet keine GitHub-Idempotenz. Die wiederholungsfeste Providerwirkung
entsteht aus dem vor Provider-Egress extern witness-checkpointierten,
create-only Idempotenz-Tombstone und zusätzlich dem atomaren create-only
Marker-Ref.
Die Lease-Frist liegt innerhalb der Autorisierungs-/Rollbackfrist und höchstens
15 Minuten nach `issuedAt`; Claim-Vollbyteshash und ID werden in erfolgreicher
App-Attestation und nachfolgendem Rollback oder Completion gebunden. Abort darf
nur die jüngsten vollständigen Issued- oder Failed-Bytes binden. Für
`operationType: "tcb-rollback"` ist `operationSubjectId` exakt die
`activationId` des durch `authorizationEntrySha256` gebundenen Activation-
Eintrags; für `tcb-emergency-recovery` ist sie exakt dessen `recoveryId`.
Unabhängig von dieser abgeleiteten Subject-ID ist im gesamten Vollpräfix pro
`authorizationEntrySha256` höchstens eine einzige `leaseId` zulässig. Die rohe
`operationCorrelationId` ist repositoryweit und epochenübergreifend global
einmalig und wird niemals wiederverwendet. Issued hat höchstens einen Claimed-Nachfolger
und Claimed höchstens einen Failed- oder Terminalnachfolger. Eine lineare
Logposition ersetzt diese semantische Eindeutigkeit nicht. Ein zweites Issue,
Doppel-Claim oder Geschwister-Nachfolger wird abgewiesen; nach Failure ist die
Autorisierung verbraucht und jeder Retry benötigt eine neue Emergency-
Authorization. Da `issued`
erst nach dem Authorization-Checkpoint entsteht, gibt es keinen Zukunftshash-
Kreis; Vollpräfix und Witness-Floors verhindern Replay oder Lease-Forks.
Für Emergency gilt vollständig `authorizedAt <=
authorizationEntry.loggedAt <= authorizationCheckpoint.issuedAt <=
authorizationExpiresAt`. Für jede Lease gilt `authorizationCheckpoint.issuedAt
< issuedAt <= issuedEntry.loggedAt <= issuedCheckpoint.issuedAt <=
claimedEntry.loggedAt <= claimedCheckpoint.issuedAt < expiresAt <=
authorizationExpiresAt`; beim Normal-Rollback ersetzt `rollbackValidUntil` die
letzte Grenze. Ein verspäteter Authorization-/Issued-/Claimed-Checkpoint oder
rückdatierter Lease-Zeitpunkt ist ungültig.

Jeder Auftrag des Gateways besitzt eine geschlossene, signierte und
append-only fortgeschriebene Kette nach
`recovery-write-ahead-receipt.schema.json`. Jeder Receipt enthält
ausschließlich `gatewayReceiptId`,
`gatewaySequence`, `previousGatewayReceiptSha256`,
`previousOperationReceiptSha256`, `phase:
"registered"|"accepted"|"dispatch-started"|"cancelled"|"settled"`,
`gatewayServiceIdentity`, `gatewayKeyRef`, `gatewayImageDigest`,
`gatewayPolicySha256`, `gatewayPermissionsSha256`,
`providerInstallationIdentitySha256`,
`providerCredentialIdentitySha256`,
`trustedTimeSourceSha256`,
`authorizationEntrySha256`, `authorizationCheckpointSha256`, `leaseId`,
`issuedLeaseEntrySha256`, `claimedLeaseEntrySha256`,
`leaseCheckpointSha256`, `operationCorrelationId`,
`providerIdempotencyKeySha256`, `providerApiOrigin`,
`providerEndpointSha256`, `branch`, `expectedRefOid`, `targetRefOid`,
`providerMarkerRef`, `providerMarkerTargetOid`, `providerRequestSha256`,
`recoveryIdempotencyTombstoneRef`, `recoveryIdempotencyTombstoneSha256`,
`recoveryIdempotencyTombstoneCheckpointSha256`,
`recoveryIdempotencyTombstoneCheckpointTreeSize`,
`recoveryEgressIntentRef`, `recoveryEgressIntentSha256`,
`recoveryEgressIntentCheckpointSha256`,
`recoveryEgressIntentCheckpointTreeSize`,
`controlPlaneHandleSha256`, `networkNamespaceSha256`,
`networkPolicySha256`, `providerByteCounterIdSha256`,
`oneShotEgressTokenSha256`,
`floorChallengeNonce`, `witnessFloorResponsesSha256`, `registeredAt`,
`acceptedAt`, `dispatchStartedAt`, `cancelledAt`, `settledAt`,
`recoveryEgressClosureRef`, `recoveryEgressClosureSha256`, `providerReceiptRef`,
`providerReceiptSha256`, `receiptCoreSha256` und `signature`. Der Receipt-Core
ist ausschließlich die RFC-8785-Projektion aller in diesem Absatz genannten
spezifischen Gateway-Payloadfelder außer `receiptCoreSha256` und `signature`.
Kein gemeinsames Logfeld – insbesondere `repositoryId`, `logId`, `entryKind`,
Logposition, `loggedAt`, Instanzcore oder Instanzsignatur – gehört in diese
Projektion. Die Gateway-Signatur enthält
ausschließlich `keyRef`, `signedAt`, `nonce`, `receiptCoreSha256` und
`signature`. Service, Key, Image, Policy, Permission- und Trusted-Time-Digest müssen
bytegleich zu Pre-Ledger und externen Pins sein.
Jeder Gateway-Receipt ist zugleich der spezifische Payload eines Eintrags
`entryKind: "recovery-write-ahead-receipt"` in der einzigen extern
witness-checkpointierten Transparenzfolge; die gemeinsamen Logfelder und die
Instanzsignatur kommen zum oben geschlossenen Payload hinzu. Keine Gatewayphase
ist vor ihrem eigenen Vollquorum-Checkpoint wirksam. Damit muss jeder
verwendete Beleg den vollständigen Hauptlogpräfix enthalten, und konkurrierende
Gatewayzweige erfordern konkurrierende Transparenzköpfe, deren Split View nach
den bestehenden Witness-/Equivokationsregeln alle Recovery-Gates dauerhaft
`red` setzt.

`registered` bindet Issued-Lease, Authorization-Checkpoint, den exakten
Providerrequest sowie den reservierten Marker-Ref;
Claim-/Floor-/Accepted-/Tombstone-/Egress-Intent-/Dispatch-/Cancelled-/Settled-/
Closure-/Providerfelder sind `null`. Erst nach seinem Vollquorum-Checkpoint darf die Claimed-Lease
entstehen. `accepted` folgt nach Claim-Checkpoint exakt `registered`, bindet
Claim-Vollhash/-Checkpoint, Challenge und Vollhash der frischen Witness-
Responses und setzt ausschließlich `acceptedAt`. Noch ist jeder Provider-
Egress gesperrt. Nach dem Accepted-Checkpoint entstehen nacheinander der unten
geschlossene externe Idempotenz-Tombstone und das Egress-Intent; jedes muss
separat vollständig witness-checkpointet sein. `dispatch-started` folgt
ausschließlich dem checkpointeten `accepted`, bindet Ref, Vollbyteshash und
Checkpoint beider Kontrollakten sowie sämtliche dort festgelegten Egress-
Identitäten bytegleich, setzt `dispatchStartedAt` und verbraucht im Gateway-Journal
irreversibel den einzigen Sendversuch. Erst nach dem eigenen Vollquorum-
Checkpoint und challenge-frischen Witness-Floors mindestens dieses Heads darf
der unabhängige Monitor exakt den im Egress-Intent vorab versiegelten
One-shot-Token atomar verbrauchen und damit das dort gebundene Handle
freischalten. Nur dieser isolierte
Egress-Control-Plane darf exakt diesen Request senden.
Eine automatische oder blinde Retransmission ist in jeder späteren Phase
verboten.

`cancelled` darf nach `expiresAt` aus `registered` oder `accepted` entstehen,
wenn kein `dispatch-started` im aktuellen witness-bestätigten Vollpräfix liegt.
Existiert bereits ein checkpointetes Egress-Intent, verlangt auch dieser Pfad
den unten geschlossenen `pre-dispatch-expiry`-Closure; ohne Egress-Intent bleiben
die Closurefelder `null`.
Aus `dispatch-started` ist es nur mit Ref/Vollbyteshash des nach
`recovery-egress-closure.schema.json` geschlossenen unabhängigen
Zero-Byte-Belegs zulässig. Es setzt ausschließlich `cancelledAt` und bindet
gegebenenfalls diesen Closure-Beleg. `settled` folgt ausschließlich
`dispatch-started`, setzt `settledAt` und bindet Ref/Vollbyteshash des
unabhängigen Providerbelegs. Auch `cancelled` und `settled` werden erst mit
ihrem eigenen Vollquorum-Checkpoint wirksam.
Ein `cancelled` aus `registered` führt Tombstone-, Intent- und Closurefelder
`null`. Ein `cancelled` aus `accepted` bindet jeden bereits existierenden
Tombstone; existiert noch kein Intent, bleiben Intent und Closure `null`, sonst
sind Intent und `pre-dispatch-expiry`-Closure vollständig non-null. Jeder
`dispatch-started`- und `settled`-Receipt bindet Tombstone, Intent und sämtliche
Egress-Identitäten non-null; `settled` führt Closurefelder `null`. Ein
`cancelled` nach `dispatch-started` bindet dieselben Werte und einen
`post-dispatch-zero-byte`-Closure. Jede andere Nullability-Kombination ist
schemaungültig.

Für jede Operation gibt es genau einen zulässigen Phasennachfolger; global
steigen `gatewaySequence` lückenlos um eins und
`previousGatewayReceiptSha256` bindet die vollständigen Vorgängerbytes,
während `previousOperationReceiptSha256` die Operationskette schließt. Pro
`(leaseId, operationCorrelationId)` ist exakt ein `registered` zulässig; bei
`registered` ist `previousOperationReceiptSha256: null`, bei `accepted` exakt
der Vollbyteshash von `registered`, bei `dispatch-started` der von `accepted`,
bei `cancelled` der unmittelbar zulässige Operationsvorgänger und bei
`settled` der von `dispatch-started`. Der vollständige Hauptlogpräfix
rekonstruiert zusätzlich die Gatewaysequenz und beide Hashketten. Ein fehlender,
doppelter oder nicht erreichbarer Vorgänger, Sequenzloch, zweites
Accept/Dispatch/Cancel, Geschwister-Nachfolger oder Settlement ohne
Providerbeleg ist fail-closed. Registrierung, Phasenwechsel und Journal-Fsync
sind atomar. Kann Exklusivität, Dauerhaftigkeit, Logcheckpoint, externer
Tombstone, Pfadidentität oder Zero-Byte-Closure auf dem Zielsystem nicht extern
verifiziert werden, bleiben die Recovery-Gates `red`.

Vor jedem Egress entsteht nach
`recovery-idempotency-tombstone.schema.json` genau ein spezifischer Payload
`entryKind: "recovery-idempotency-tombstone"` mit ausschließlich
`tombstoneId`, `tombstoneNamespace:
"aurelia-recovery-provider-operations"`, `leaseId`,
`operationCorrelationId`, `providerIdempotencyKeySha256`,
`authorizationEntrySha256`, `claimedLeaseEntrySha256`,
`gatewayAcceptedReceiptRef`, `gatewayAcceptedReceiptSha256`,
`gatewayAcceptedCheckpointSha256`, `gatewayAcceptedCheckpointTreeSize`,
`providerInstallationIdentitySha256`, `providerCredentialIdentitySha256`,
`branch`, `expectedRefOid`, `targetRefOid`, `providerMarkerRef`,
`providerMarkerTargetOid`, `providerRequestSha256`, `createdAt`,
`tombstoneCoreSha256` und `gatewaySignature`. Der Tombstone-Core ist die
RFC-8785-Projektion aller spezifischen Felder außer Core und Signatur; die
Gateway-Signatur enthält ausschließlich `keyRef`, `signedAt`, `nonce`,
`tombstoneCoreSha256` und `signature`. Der Eintrag wird erst nach dem
Accepted-Checkpoint erzeugt und ist erst nach seinem eigenen Vollquorum-
Checkpoint wirksam. Im vollständigen Logpräfix darf es höchstens einen
Tombstone je `operationCorrelationId`, `providerIdempotencyKeySha256`,
`providerMarkerRef` und `providerRequestSha256` geben; jede dieser vier
Eindeutigkeiten gilt einzeln. Transparenzappend und create-only Insert dieser
vier Schlüssel in den externen persistenten Uniqueness-Index sind eine atomare
Transaktion; konkurrierender Insert, unbestätigter Fsync oder nicht
rekonstruierbarer Index ist fail-closed. Engine, Schema und Policy dieses Index
sind Bestandteil von `bootstrapTrustProtocolSha256` und des extern gepinnten
Transparenzdienstes; bei jedem Start wird der Index aus dem vollständigen
checkpointeten Logpräfix rekonstruiert und bytegleich verglichen. Der Tombstone
läuft nie ab, wird nie gelöscht und
bleibt auch nach Failure, Abort, Completion, Ref-Rückkehr oder
Provider-Marker-Verlust verbraucht. Damit ist die extern witness-
checkpointierte Transparenzfolge selbst der vom Repository und Provider
getrennte immutable Idempotenzspeicher. Kein Gateway, Monitor oder Validator
darf für einen vorhandenen Tombstone ein zweites Egress-Intent oder einen
weiteren Sendversuch autorisieren.

Nach dem Tombstone-Checkpoint erzeugt der unabhängige Egress-Monitor nach
`recovery-egress-intent.schema.json` genau einen spezifischen Payload
`entryKind: "recovery-egress-intent"` mit ausschließlich `egressIntentId`,
`leaseId`, `operationCorrelationId`, `recoveryIdempotencyTombstoneRef`,
`recoveryIdempotencyTombstoneSha256`,
`recoveryIdempotencyTombstoneCheckpointSha256`,
`recoveryIdempotencyTombstoneCheckpointTreeSize`,
`gatewayAcceptedReceiptRef`, `gatewayAcceptedReceiptSha256`,
`gatewayAcceptedCheckpointSha256`, `gatewayAcceptedCheckpointTreeSize`,
`authorizationEntrySha256`, `claimedLeaseEntrySha256`,
`providerIdempotencyKeySha256`, `branch`, `expectedRefOid`, `targetRefOid`,
`providerInstallationIdentitySha256`, `providerCredentialIdentitySha256`,
`providerApiOrigin`, `providerEndpointSha256`, `providerRequestSha256`,
`providerMarkerRef`, `providerMarkerTargetOid`, `controlPlaneHandleSha256`,
`networkNamespaceSha256`, `networkPolicySha256`,
`providerByteCounterIdSha256`, `initialProviderBytesSent: 0`,
`providerSocketOpened: false`, `oneShotEgressTokenSha256`, `provisionedAt`,
`expiresAt`, `monitorServiceIdentity`, `monitorKeyRef`, `monitorImageDigest`,
`monitorPolicySha256`, `monitorPermissionsSha256`,
`monitorTrustedTimeSourceSha256`, `intentCoreSha256` und `monitorSignature`.
Core und geschlossene Signatur folgen der Monitorform und werden gegen den
externen Pre-Ledger-Pin geprüft. Das Intent ist erst nach seinem eigenen
Vollquorum-Checkpoint wirksam und läuft spätestens mit Lease und Authorization
ab. Der Monitor provisioniert ein exklusives, zunächst geschlossenes
Netzwerk-Namespace samt write-once Bytecounter; die Gateway-Credential kann nur
über dieses Handle verwendet werden. Host-, Gateway- und Container-Egress sind
für DNS, Proxy, IPv4, IPv6, Unix-Socket und jede fremde Namespace-/Credential-
Kopie default-deny; ein nicht vollständig mess- und testbarer Bypass hält das
Gate `red`. Weder Socket noch Providerroute werden
vor dem checkpointeten `dispatch-started` und dessen challenge-frischen
Witness-Floors geöffnet. Danach validiert und verbraucht der Monitor den vorab
gehashten Token atomar höchstens einmal und nur für genau diesen Request. Pro Tombstone,
Control-Plane-Handle, Namespace, Counter und Token ist in der gesamten
Logfolge jeweils höchstens ein Intent zulässig; Kollision, Austausch oder
fehlender Vorgänger setzt alle Recovery-Gates `red`. Tombstone, Intent und
Accepted-/Dispatch-Started-Receipt führen Authorization, Claim, Lease,
Operation, Providerrequest, Installation, Credential, Branch, OIDs und Marker
bytegleich.

Der Zero-Byte-Beleg enthält nach
`recovery-egress-closure.schema.json` ausschließlich `schemaVersion`,
`repositoryId`, `closureId`, `closureReason:
"pre-dispatch-expiry"|"post-dispatch-zero-byte"`, `leaseId`,
`operationCorrelationId`, `recoveryIdempotencyTombstoneRef`,
`recoveryIdempotencyTombstoneSha256`, `recoveryEgressIntentRef`,
`recoveryEgressIntentSha256`, `recoveryEgressIntentCheckpointSha256`,
`recoveryEgressIntentCheckpointTreeSize`,
`gatewayDispatchStartedEntrySha256`,
`gatewayDispatchStartedCheckpointSha256`,
`gatewayDispatchStartedCheckpointTreeSize`, `providerApiOrigin`,
`providerEndpointSha256`, `providerRequestSha256`,
`providerInstallationIdentitySha256`, `providerCredentialIdentitySha256`,
`providerMarkerRef`, `controlPlaneHandleSha256`,
`networkNamespaceSha256`, `networkPolicySha256`,
`providerByteCounterIdSha256`, `oneShotEgressTokenSha256`,
`oneShotEgressTokenConsumed`, `providerSocketOpened: false`,
`initialProviderBytesSent: 0`, `finalProviderBytesSent: 0`,
`firstProviderByteAt: null`, `counterSealedAt`, `namespaceDestroyedAt`, `closedAt`,
`monitorServiceIdentity`, `monitorKeyRef`, `monitorImageDigest`,
`monitorPolicySha256`, `monitorPermissionsSha256`,
`monitorTrustedTimeSourceSha256`, `closureCoreSha256` und `monitorSignature`.
Core und Monitor-Signatur folgen den geschlossenen Formen der übrigen
Monitorbelege und werden gegen den externen Pre-Ledger-Pin geprüft. Der
getrennte Egress-Monitor hält den versiegelten Netzwerk-Namespace und
write-once Bytecounter vom Egress-Intent bis zur atomaren Credential-/Namespace-
Sperre; erst danach darf er ausschließlich bei exakt null Bytes den Closure-
Beleg signieren. Bei `pre-dispatch-expiry` sind alle drei Dispatch-Started-
Felder `null` und `oneShotEgressTokenConsumed: false`; bei
`post-dispatch-zero-byte` sind sie non-null und binden den exakten
Vollquorum-Checkpoint. Alle übrigen Egress-Identitäten sind in Intent,
Dispatch-Started und Closure bytegleich. Gateway-Selbstaussage, ein Closure für
ein anderes Handle oder Namespace, fehlender
Counterpräfix, offener Socket, unbekannter Counterstand oder eine nur
nachträgliche Prozessinspektion genügt nicht.

Jeder branchändernde Normal-Rollback und jede Emergency-Recovery verwendet die
nach `recovery-app-attestation.schema.json` geschlossene App-Attestation. Sie
enthält ausschließlich `schemaVersion`, `repositoryId`, `attestationId`,
`operationType: "tcb-rollback"|"tcb-emergency-recovery"`, `appIdentity`,
`appKeyRef`, `appImageDigest`, `appPolicySha256`, `appPermissionsSha256`,
`providerInstallationIdentitySha256`, `authorizationEntrySha256`,
`authorizationCheckpointSha256`, `authorizationCheckpointTreeSize`,
`authorizationCheckpointIssuedAt`, `authorizationExpiresAt`,
`recoveryOperationLeaseId`,
`recoveryOperationLeaseSha256`, `leaseCheckpointSha256`,
`leaseCheckpointTreeSize`, `leaseCheckpointIssuedAt`, `leaseExpiresAt`,
`floorChallengeNonce`, `witnessFloorResponses`, `branch`,
`expectedRefOid`, `targetRefOid`,
`operationCorrelationId`, `providerIdempotencyKeySha256`,
`providerInstallationIdentitySha256`, `providerCredentialIdentitySha256`,
`providerApiOrigin`, `providerEndpointSha256`,
`providerMarkerRef`, `providerMarkerTargetOid`,
`gatewayAcceptedReceiptRef`, `gatewayAcceptedReceiptSha256`,
`gatewayAcceptedCheckpointSha256`, `gatewayAcceptedCheckpointTreeSize`,
`recoveryIdempotencyTombstoneRef`, `recoveryIdempotencyTombstoneSha256`,
`recoveryIdempotencyTombstoneCheckpointSha256`,
`recoveryIdempotencyTombstoneCheckpointTreeSize`,
`recoveryEgressIntentRef`, `recoveryEgressIntentSha256`,
`recoveryEgressIntentCheckpointSha256`,
`recoveryEgressIntentCheckpointTreeSize`,
`controlPlaneHandleSha256`, `networkNamespaceSha256`,
`networkPolicySha256`, `providerByteCounterIdSha256`,
`oneShotEgressTokenSha256`,
`gatewayDispatchStartedReceiptRef`, `gatewayDispatchStartedReceiptSha256`,
`gatewayDispatchStartedCheckpointSha256`,
`gatewayDispatchStartedCheckpointTreeSize`,
`gatewaySettledReceiptRef`, `gatewaySettledReceiptSha256`,
`gatewaySettledCheckpointSha256`, `gatewaySettledCheckpointTreeSize`,
`observedRefOidBefore`, `observedRefOidAfter`, `observedProviderMarkerOid`,
`providerReceiptRef`,
`providerReceiptSha256`,
`operationStartedAt`, `operationCompletedAt`, `result: "succeeded"|"failed"`,
`attestedAt`, `nonce`, `attestationCoreSha256` und `signature`. App-/Key-/Image-/Policy-/
Berechtigungs-/Providerfelder müssen bytegleich zu Pre-Ledger und externen Pins
sein. Der Core ist die RFC-8785-Projektion aller Felder außer Core und
Signatur; die App signiert ihn mit dem gepinnten Key. Der Authorization-Eintrag
muss vollständig im gebundenen Vollquorum-Checkpoint liegen; die Claimed-
Lease, der Tombstone und das Egress-Intent müssen vollständig in ihren
gebundenen, strikt aufeinanderfolgenden Vollquorum-Checkpoints liegen.
`floorChallengeNonce` ist pro Operationsversuch global einmalig.
`witnessFloorResponses` ist das nach `witnessId` sortierte Vollquorum mit
ausschließlich `witnessId`, `keyRef`, `floorId`, `floorSha256`,
`minimumTreeSize`, `minimumCheckpointSha256`, `floorChallengeNonce`,
`respondedAt` und `responseSignature`. Jeder Witness signiert die
RFC-8785-Projektion aus Repository, App-Attestation-ID, Lease-ID/-Hash,
Challenge, Floor-ID/-Vollhash/-Größe/-Checkpoint und `respondedAt`; Floor und
Response werden gegen seinen externen Pin geprüft. Jede Floor-Größe liegt
mindestens beim Lease-Checkpoint, nennt keine spätere Failed-/Abort-/Terminal-
Sicht für diese Lease, und jede Antwort liegt höchstens fünf Sekunden vor der
Gateway-Akzeptanz. Alte Responses sind wegen der neuen Challenge nicht
wiederverwendbar. Die Accepted-/Dispatch-Started-/Settled-Gateway-Receipts und der
Providerbeleg binden exakt Authorization, Claim-Vollhash/-Checkpoint,
Operationskennung, Branch und OIDs dieser Attestation. Es gilt
`authorizationCheckpointIssuedAt < leaseCheckpointIssuedAt <
operationStartedAt <= gatewayAcceptedAt < tombstoneCheckpoint.issuedAt <
egressIntentCheckpoint.issuedAt < gatewayDispatchStartedAt <=
operationCompletedAt <=
min(leaseExpiresAt, authorizationExpiresAt)`; beim Normal-Rollback ersetzt
`rollbackValidUntil` die Authorization-Grenze.
Nur `succeeded` mit `observedRefOidBefore == expectedRefOid` und
`observedRefOidAfter == targetRefOid` sowie `observedProviderMarkerOid ==
targetRefOid` darf Completion oder Rollback stützen;
der Validator prüft den providerseitigen Operationsbeleg unabhängig nach. Bei
Normal-Rollback ist `authorizationExpiresAt == rollbackValidUntil`, bei
Emergency bytegleich zur Authorized-Phase; `leaseExpiresAt` ist bytegleich zur
Claimed-Lease.

Der providerseitige Beleg ist ein getrennt nach
`provider-ref-update-receipt.schema.json` geschlossenes Artefakt. Er enthält
ausschließlich `schemaVersion`, `repositoryId`, `providerReceiptId`,
`providerName: "github"`, `providerApiOrigin`, `providerEndpointSha256`,
`providerInstallationIdentitySha256`, `providerCredentialIdentitySha256`,
`providerIdempotencyKeySha256`,
`operationCorrelationId`, `authorizationEntrySha256`,
`authorizationCheckpointSha256`, `leaseId`, `claimedLeaseEntrySha256`,
`leaseCheckpointSha256`, `gatewayAcceptedReceiptRef`,
`gatewayAcceptedReceiptSha256`, `recoveryIdempotencyTombstoneRef`,
`recoveryIdempotencyTombstoneSha256`,
`recoveryIdempotencyTombstoneCheckpointSha256`,
`recoveryIdempotencyTombstoneCheckpointTreeSize`,
`recoveryEgressIntentRef`, `recoveryEgressIntentSha256`,
`recoveryEgressIntentCheckpointSha256`,
`recoveryEgressIntentCheckpointTreeSize`, `controlPlaneHandleSha256`,
`networkNamespaceSha256`, `networkPolicySha256`,
`providerByteCounterIdSha256`, `oneShotEgressTokenSha256`,
`oneShotEgressTokenConsumedAt`, `finalProviderBytesSent`,
`gatewayDispatchStartedReceiptRef`,
`gatewayDispatchStartedReceiptSha256`,
`gatewayDispatchStartedCheckpointSha256`,
`gatewayDispatchStartedCheckpointTreeSize`, `dispatchFloorChallengeNonce`,
`dispatchWitnessFloorResponses`, `providerMarkerRef`,
`providerMarkerTargetOid`, `providerPrimitive:
"github-graphql-updateRefs-beforeOid"`, `providerRequestId`,
`providerRequestRef`, `providerRequestSha256`, `providerResponseRef`,
`providerResponseSha256`, `tlsTranscriptRef`, `tlsTranscriptSha256`,
`providerCertificateChainSha256`, `operationType: "compare-and-swap-ref"`,
`branch`, `expectedRefOid`, `targetRefOid`, `observedRefOidBefore`,
`observedRefOidAfter`, `observedProviderMarkerOid`,
`result: "succeeded"|"failed"`,
`providerRequestStartedAt`, `providerAcceptedAt`, `providerCompletedAt`,
`providerObservedAt`, `verificationStartedAt`, `verificationCompletedAt`,
`verifierServiceIdentity`, `verifierKeyRef`, `verifierImageDigest`,
`verifierPolicySha256`, `trustedTimeSourceSha256`, `nonce`,
`receiptCoreSha256` und `signature`. Core und
Signatur folgen derselben geschlossenen RFC-8785-Projektion wie die App-
Attestation; Service, Key, Image, Policy, Trusted-Time-Digest und Failure-Domain werden gegen den
extern gepinnten unabhängigen Provider-Ref-Verifier geprüft. Response- und
Requestidentität werden zusätzlich gegen den Gateway-Pin geprüft:
`providerInstallationIdentitySha256` und
`providerCredentialIdentitySha256` sind exakt die non-null Werte des aktiven
Gateway-Pins; der Verifier übernimmt oder besitzt die Schreibcredential nicht.
Response- und
Request-/TLS-Artefaktrefs sind revisionsfest und ihre Vollbyteshashes offline
nachprüfbar. Die rohe `operationCorrelationId` ist bytegleich zu Lease,
Gateway und App, global einmalig und wird als Provider-`clientMutationId`
übertragen; `providerRequestId` ist non-null und im provider-authentifizierten
Responseheader als GitHub-Request-ID belegt. `providerRequestSha256` ist
bytegleich in Registered-, Accepted-, Tombstone-, Egress-Intent- und
Dispatch-Started-Artefakt. Providerinstallation, Credentialidentität,
Handle, Namespace, Policy, Counter und Token sind bytegleich in Intent,
Dispatch-Started, Providerbeleg und späterer App-Attestation; der im
TLS-Transcript belegte erste Providerbyte stammt aus genau diesem Namespace,
und `finalProviderBytesSent` entspricht dem versiegelten write-once Counter.
Die Primitive muss `beforeOid == expectedRefOid` und
`afterOid == targetRefOid` in den exakten Requestbytes tragen. Konkret enthält
`UpdateRefsInput` genau zwei atomare `RefUpdate`-Objekte: erstens `name ==
"refs/heads/" + branch`, `beforeOid == expectedRefOid`, `afterOid ==
targetRefOid` und das für den exakt gebundenen Restore erforderliche `force:
true`; zweitens `name == providerMarkerRef`, `beforeOid ==
"0000000000000000000000000000000000000000"`, `afterOid == targetRefOid` und
`force: false`. `providerMarkerRef` ist exakt
`"refs/heads/aurelia-recovery-markers/" + SHA-256-hex(operationCorrelationId)`
und darf nach der AURELIA-Policy niemals gelöscht oder wiederverwendet werden;
`providerMarkerTargetOid == targetRefOid`. `clientMutationId` ist
ausschließlich der rohe Korrelationswert, keine behauptete Provider-
Idempotenzgarantie. Die dokumentierte Atomizität und die create-only-
Vorbedingung schützen den Branchupdate providerseitig, solange der Marker
besteht. Die epochenübergreifende Wiederholungsfestigkeit beruht jedoch nicht
auf einer unbeweisbaren lückenlosen Ref-Historie: Der vorherige externe
Idempotenz-Tombstone bleibt selbst bei unbemerktem Delete/Recreate des
Provider-Markers vorhanden und verhindert einen zweiten Egress für dieselbe
Operation oder denselben Request nach einer Ref-Folge `A→B→A`. Trotzdem ist
nach dem irreversiblen `dispatch-started` kein
automatischer Sendewiederholungsversuch zulässig. Diese
CAS-/Atomizitätssemantik und die Feldnamen sind gegen die aktuelle offizielle
[GitHub-GraphQL-Git-Referenz](https://docs.github.com/en/graphql/reference/git#updaterefs)
zu verifizieren. Kann die dokumentierte Semantik oder Antwortkorrelation nicht
verifiziert werden, ist kein Receipt erzeugbar und die Operation bleibt
fail-closed.
`succeeded`
verlangt `observedRefOidBefore == expectedRefOid` und
`observedRefOidAfter == targetRefOid` sowie `observedProviderMarkerOid ==
targetRefOid`; `failed` verlangt unabhängig vom Grund
`observedRefOidAfter == observedRefOidBefore`,
`observedProviderMarkerOid: null` und einen
provider-authentifizierten Response, der die CAS-Ablehnung abschließend
belegt; bloßer Verbindungsabbruch, Timeout oder verlorener Response bleibt
`executing`. `providerRequestStartedAt` ist
der durch das Gateway-Journal und den TLS-Transcript belegte Zeitpunkt des
ersten Outbound-Bytes; `providerAcceptedAt` und `providerCompletedAt` sind die
im provider-authentifizierten TLS-/Responseartefakt belegten ersten und letzten
Responsezeitpunkte. Die anschließende Ref-Beobachtung und die unabhängige
Verifikation sind trusted-time-gestempelt. `dispatchFloorChallengeNonce` ist
global einmalig; `dispatchWitnessFloorResponses` besitzt die oben geschlossene,
nach `witnessId` sortierte Vollquorum-Form und signiert hier Repository,
Provider-Receipt-ID, Lease-ID, Dispatch-Started-Entry-Ref/-Vollhash/-Checkpoint,
Operationskennung, Challenge und Floor-Vollzustand. Jeder Floor liegt
mindestens beim Dispatch-Started-Checkpoint, damit auch nach Tombstone- und
Egress-Intent-Checkpoint, enthält keinen späteren
Cancel-/Failure-State und jede Response liegt höchstens fünf Sekunden vor dem
ersten Providerbyte. Vollständig gilt
`claimCheckpoint.issuedAt < operationStartedAt <= gatewayAcceptedAt <=
gatewayAcceptedEntry.loggedAt <= gatewayAcceptedCheckpoint.issuedAt <
tombstone.createdAt <= tombstoneEntry.loggedAt <=
tombstoneCheckpoint.issuedAt < egressIntent.provisionedAt <=
egressIntentEntry.loggedAt <= egressIntentCheckpoint.issuedAt <
gatewayDispatchStartedAt <= gatewayDispatchStartedEntry.loggedAt <=
gatewayDispatchStartedCheckpoint.issuedAt <=
oneShotEgressTokenConsumedAt <= providerRequestStartedAt <= providerAcceptedAt
<= providerCompletedAt <=
operationCompletedAt <= providerObservedAt <= verificationStartedAt <=
verificationCompletedAt <= gatewaySettledAt <=
gatewaySettledEntry.loggedAt <= gatewaySettledCheckpoint.issuedAt <=
attestedAt <= min(leaseExpiresAt, authorizationExpiresAt)`;
beim Normal-Rollback ersetzt `rollbackValidUntil` die letzte Grenze.
Zwischen `operationStartedAt` und `gatewayAcceptedAt`, zwischen
Dispatch-Started-Checkpoint und `providerRequestStartedAt`, zwischen letzter
App-Witness-Response und Gateway-Akzeptanz, zwischen letzter Dispatch-Witness-
Response und erstem Providerbyte sowie zwischen `providerCompletedAt` und
`operationCompletedAt` liegen jeweils höchstens fünf Sekunden. Dieser Skew ist
fest codiert, weder konfigurierbar noch rückwirkend erweiterbar. Ein App-
Statement ohne diesen Beleg, falsche
Provideridentität, zurückdatierte App-Zeit oder nur ein nicht auflösbarer
Operation-ID-Hash ist ungültig.
Ein erfolgreicher oder providerabschließend fehlgeschlagener Receipt verlangt
`finalProviderBytesSent > 0`; null Bytes gehören ausschließlich in den
unabhängigen Closurepfad und dürfen niemals als Provider-Receipt umetikettiert
werden.
In Rollback beziehungsweise Completion sind Provider-Receipt-Ref/-Hash und
Gateway-Accepted-/Dispatch-Started-/Settled-Receipt-Ref/-Hash bytegleich zur
App-Attestation;
`compareAndSwapOperationIdSha256` ist exakt SHA-256 der rohen global einmaligen
`operationCorrelationId`.

Beim Normal-Rollback ist `operationCompletedAt == rolledBackAt`; zusammen mit
der obigen Rollbackordnung muss somit auch der wirksame Checkpoint vor
`rollbackValidUntil` liegen. Bei Emergency Completion gilt vollständig
`authorizedAt <= authorizationEntry.loggedAt <=
authorizationCheckpointIssuedAt < leaseCheckpointIssuedAt <
operationStartedAt <= gatewayAcceptedAt <= operationCompletedAt <= completedAt
<= completionEntry.loggedAt <= completionCheckpoint.issuedAt <=
authorizationExpiresAt`.
Eine App-Attestation vor dem gebundenen Authorization-Checkpoint oder ein
gemeinsamer erst nachträglicher Checkpoint über Authorization und Completion
ist ungültig.

Der in allen Controller-Signaturen verwendete `keyRef` muss bytegleich dem
durch Pre-Ledger, Genesis und externe Pins gebundenen
`validatorControllerKey.keyRef` sein; jede Signatur wird gegen genau dessen
Fingerprint geprüft. Dieser Controller-Key bleibt in G0 immutable. Verlust oder
Kompromittierung hält alle Gates `red`; vor Pilot-Green ist deshalb ein separat
freigegebener und praktisch getesteter Controller-Key-Recoveryvertrag Pflicht.
Der neue TCB darf keinen Controller-Key selbst einführen.
Neu eingeführte Reviewer-/Operator-Keys können weder die erforderliche
Offline-Root- noch Custodian-Signatur ersetzen. Für den allerersten G0-Import
übernimmt ein unabhängig
bereitgestellter, vor Repositoryausführung extern gepinnter Bootstrap-
Validator diese Vorgängerrolle; Image-, Policy-, Workflow-, Schema-Set- und
Trust-Protokoll-Digest werden
zusätzlich im doppelt signierten Pre-Ledger-Bundle gebunden. Niemals bestätigt
PR-Code seine eigene Abschwächung.

`check:governance-remote` ist für `GATE-G0` verpflichtend, aber kein Teil
offline reproduzierbarer Unit-Tests. Fehlende App, API-/Logfehler,
Digestabweichung oder unzureichende Berechtigung liefert `unknown` und hält
das Gate `red`. Der Check verifiziert zusätzlich die create-only geschützte
Marker-Ref-Namespace-Policy: nur das gepinnte Gateway darf einen neuen Marker
anlegen; Update, Delete, Force-Update und jeder Bypass sind gesperrt. Jeder
fehlende oder veränderte erwartete Marker setzt Remote-Control auf `red`;
Wiederanlage heilt den Befund nicht. Diese periodische Kontrolle behauptet
keine lückenlose Provider-Ref-Historie und trägt deshalb nicht die
Idempotenzgarantie. Diese liegt ausschließlich beim vollständigen externen
Tombstone-Logpräfix: vor jedem Recovery-Egress muss der Remote-Validator dessen
frischen Vollquorum-Checkpoint und die Eindeutigkeit von Operation, Marker und
Request prüfen. Selbst ein zwischen zwei Snapshots verborgenes Delete/Recreate
autorisiert niemals einen zweiten Egress. Jeder
Gate-/Release-Head benötigt eine höchstens eine Stunde
alte Remote-Control-EVID; bei Branchschutz- oder Bypass-Änderung schreibt das
externe Monitoring ausschließlich einen neuen
append-only Branch-Policy-Transition-Eintrag im Transparenzlog. Alle Receipts
der bisherigen Branch-Policy-Epoch und ihre historischen EVID bleiben
unverändert, dürfen ab diesem Logindex aber kein Gate mehr stützen.

### 6.4 Kryptografische Artefaktverträge

Die folgenden reinen Draft-2020-12-Schemata sind verpflichtend und setzen auf
jeder Ebene `additionalProperties: false`:

- `docs/governance/schemas/trust-roots.schema.json`;
- `docs/governance/schemas/event-attestation.schema.json`;
- `docs/governance/schemas/pre-ledger-trust-bundle.schema.json`;
- `docs/governance/schemas/final-design-approval.schema.json`;
- `docs/governance/schemas/acceptance-receipt.schema.json`;
- `docs/governance/schemas/branch-policy-transition.schema.json`;
- `docs/governance/schemas/transparency-checkpoint.schema.json`;
- `docs/governance/schemas/transparency-bundle.schema.json`;
- `docs/governance/schemas/validator-promotion-request.schema.json`;
- `docs/governance/schemas/validator-activation.schema.json`;
- `docs/governance/schemas/validator-activation-bundle.schema.json`;
- `docs/governance/schemas/validator-rollback-authorization.schema.json`;
- `docs/governance/schemas/validator-rollback-record.schema.json`;
- `docs/governance/schemas/emergency-tcb-recovery.schema.json`;
- `docs/governance/schemas/recovery-app-attestation.schema.json`;
- `docs/governance/schemas/recovery-operation-lease.schema.json`;
- `docs/governance/schemas/provider-ref-update-receipt.schema.json`;
- `docs/governance/schemas/recovery-write-ahead-receipt.schema.json`;
- `docs/governance/schemas/recovery-idempotency-tombstone.schema.json`;
- `docs/governance/schemas/recovery-egress-intent.schema.json`;
- `docs/governance/schemas/recovery-egress-closure.schema.json`;
- `docs/governance/schemas/transparency-key-transition.schema.json`;
- `docs/governance/schemas/transparency-equivocation-report.schema.json`;
- `docs/governance/schemas/transparency-witness-floor.schema.json`;
- `docs/governance/schemas/external-model-request-envelope.schema.json`;
- `docs/governance/schemas/external-model-request-receipt.schema.json`;
- `docs/governance/schemas/external-model-response-envelope.schema.json`;
- `docs/governance/schemas/egress-dispatcher-contract.schema.json`;
- `docs/governance/schemas/network-enforcement-verification.schema.json`;
- `docs/governance/schemas/egress-dispatch-attestation.schema.json`;
- `docs/governance/schemas/egress-enforcement-lease.schema.json`;
- `docs/governance/schemas/egress-transport-profile.schema.json`;
- `docs/governance/schemas/egress-transport-receipt.schema.json`;
- `docs/governance/schemas/custodian-pin-transition.schema.json`;
- `docs/governance/schemas/reasoning-approval.schema.json`;
- `docs/governance/schemas/collector-contract.schema.json`;
- `docs/governance/schemas/collector-protected-state.schema.json`;
- `docs/governance/schemas/input-manifest.schema.json`;
- `docs/governance/schemas/subject-manifest.schema.json`;
- `docs/governance/schemas/provider-due-diligence.schema.json`;
- `docs/governance/schemas/sanitization-report.schema.json`.

Alle Artefakte sind UTF-8 ohne BOM. Signierte Payloads werden nach RFC 8785
kanonisiert; SHA-256 ist kleingeschriebenes Hex, Ed25519-Public-Keys sind
32 Byte und Signaturen 64 Byte als Base64url ohne Padding. Zeitpunkte sind
UTC `YYYY-MM-DDTHH:mm:ss.sssZ`. IDs erfüllen `^KEY-[A-Z0-9]+(?:-[A-Z0-9]+)*$`,
`^KEYREV-[0-9]{6}$`, `^RECEIPT-[0-9]{12}$`,
`^POLICYTRANS-[0-9]{12}$`, `^TCBACT-[0-9]{12}$`,
`^TCBRB-[0-9]{12}$`, `^TCBREC-[0-9]{12}$`,
`^RECAPP-[0-9]{12}$`, `^RECLEASE-[0-9]{12}$`,
`^PROVREC-[0-9]{12}$`, `^RECTOMB-[0-9]{12}$`,
`^RECEGRESS-[0-9]{12}$`, `^RECCLOSE-[0-9]{12}$`,
`^EGRESS-[0-9]{6}$`,
`^EGRESSAT-[0-9]{12}$`, `^NETVERIFY-[0-9]{6}$`,
`^PINTRANS-[0-9]{12}$`, `^MODELREQ-[0-9]{12}$`,
`^KEYTRANS-[0-9]{12}$`, `^WFLOOR-[0-9]{12}$` und
`^EQUIV-[0-9]{12}$`; Nonces sind 32 zufällige Byte als
Base64url und global einmalig.
`repositoryId` ist in allen G0-Kryptoartefakten exakt
`redshift-three67/aurelia`; Alias, Fork oder umbenanntes Repository benötigt
eine neue formal freigegebene Vertrauensbaseline.

Kanonische Bootstrap-Pfade sind:

- `docs/governance/bootstrap/pre-ledger-trust-bundle.json`;
- `docs/governance/bootstrap/final-design-approval.json`.

Das Pre-Ledger-Bundle enthält ausschließlich `schemaVersion`,
`repositoryId`, `designBaselineCommit`, `designCommit`, `designSpecPath`,
`designSpecSha256`, `governanceImplementationCommit`, `operatorKey`,
`recoveryRootKey`, `orchestratorKey`, `validatorControllerKey`,
`recoveryApp`, `recoveryWriteAheadGateway`, `providerRefVerifier`,
`egressEnforcementMonitor`,
`transparencyInstanceKey`,
`witnessKeys`, `finalApprovalPath`,
`finalApprovalSha256`, `bootstrapValidatorImageDigest`,
`bootstrapValidatorPolicySha256`, `bootstrapWorkflowSha256`,
`bootstrapSchemaSetSha256`, `bootstrapTrustProtocolSha256`,
`genesisEventIds`, `issuedAt`, `nonce`,
`operatorSignature` und `recoveryRootSignature`. Operator-, Recovery- und
Orchestrator-Key-Objekte
enthalten ausschließlich `keyRef`, `roleRef`, `assigneeRef`,
`algorithm: "ed25519"`, `publicKeyBase64url` und `fingerprintSha256`.
`validatorControllerKey` enthält ausschließlich `keyRef`,
`controllerIdentity`, `algorithm: "ed25519"`, `publicKeyBase64url` und
`fingerprintSha256`.
`recoveryApp` enthält ausschließlich `appIdentity`, `keyRef`,
`algorithm: "ed25519"`, `publicKeyBase64url`, `fingerprintSha256`,
`imageDigest`, `policySha256`, `permissionsSha256` und
`providerInstallationIdentitySha256`. Seine Berechtigung ist auf das Lesen des
gebundenen Refs sowie das signierte Einreichen exakt gebundener Operationen
beim Write-ahead-Gateway beschränkt; es besitzt weder Providercredential noch
direkten Provider-Egress. Repositoryinhalte, Secrets, Workflows, Issues und
andere Refs sind nicht zugreifbar.
`recoveryWriteAheadGateway`, `providerRefVerifier` und
`egressEnforcementMonitor` enthalten jeweils
ausschließlich `serviceIdentity`, `keyRef`, `algorithm: "ed25519"`,
`publicKeyBase64url`, `fingerprintSha256`, `imageDigest`, `policySha256`,
`permissionsSha256`, `providerInstallationIdentitySha256: string|null`,
`providerCredentialIdentitySha256: string|null`, `trustedTimeSourceSha256` und
`failureDomain`. Alle drei sind von Recovery-App,
Dispatcher, Validator-Controller und Transparenzinstanz getrennt. Nur das
Write-ahead-Gateway besitzt die eng begrenzte, durch den einzigen non-null
`providerCredentialIdentitySha256` gepinnte Provider-Ref-Schreibcredential
für den exakt autorisierten Branch und create-only
`refs/heads/aurelia-recovery-markers/*`; Löschen, Überschreiben oder ein
anderer Ref ist unzulässig.
Der geheime Credentialwert liegt nicht exportierbar in einem vom
`egressEnforcementMonitor` kontrollierten Credential-Broker. Der Gatewayprozess
erhält niemals dessen Rohbytes und kann die Credential nur über das im
checkpointeten Egress-Intent benannte Handle mit dem dort gehashten atomaren
One-shot-Token verwenden; der Monitor kann die Credential weder lesen noch
selbst als Provideridentität benutzen. Broker-Image, Policy, Tokenverbrauch und
Bypass-Negativtests sind durch Monitor- und Gateway-Pins gebunden.
Recovery-App, Gateway und Provider-Verifier binden dieselbe non-null
Providerinstallation; Provider-Verifier und Egress-Monitor führen für die
Credentialidentität `null`.
Der Provider-Verifier besitzt nur Audit-/Ref-Leserechte; beim Egress-Monitor
ist das Feld `null`, und er besitzt ausschließlich Host-/Netzwerk-/Prozess-
Control-Plane-Rechte ohne Provider-Credential.
`transparencyInstanceKey` enthält ausschließlich `keyRef`, `logId`,
`keyEpoch: 1`, `algorithm: "ed25519"`, `publicKeyBase64url` und
`fingerprintSha256`. `witnessKeys` enthält mindestens zwei nach `witnessId`
sortierte Objekte mit ausschließlich `witnessId`, `keyRef`,
`operatorIdentity`, `failureDomain`, `algorithm: "ed25519"`,
`publicKeyBase64url` und `fingerprintSha256`; Identitäten, Fehlerdomänen, Keys
und Fingerprints sind paarweise verschieden.
Bootstrap-Validator-, Recovery-App-, Recovery-Write-ahead-Gateway-,
Provider-Ref-Verifier- und Egress-Enforcement-Monitor-Image-Digest erfüllen jeweils
`^sha256:[0-9a-f]{64}$`; Policy-, Workflow-, Schema-Set-, Berechtigungs- und
Trust-Protokoll-Digests sind jeweils 64 kleingeschriebene Hexzeichen.
`genesisEventIds` ist exakt
`["EVT-000001","EVT-000002","EVT-000003"]`; `finalApprovalPath` ist der oben
festgelegte Pfad. Operator und getrennt offline verwahrter Recovery-Root
signieren unabhängig dieselbe RFC-8785-Payload aus allen Feldern außer den
beiden Signaturfeldern. Der
Validator erhält Operator-, Recovery-, Validator-Controller-, Recovery-App-,
Recovery-Write-ahead-Gateway-, Provider-Ref-Verifier-, Egress-Enforcement-Monitor-,
Transparenzinstanz- und alle Witness-
Fingerprints aus geschützten, nicht vom PR änderbaren externen Pins und
akzeptiert ausschließlich für EVT-000001 dieses Bundle als Pre-State-
Verifikationsquelle.

Die finale Designfreigabe enthält ausschließlich `schemaVersion`,
`repositoryId`, `approvalText`, `designCommit`, `designSpecPath`,
`designSpecSha256`,
`approvalScope: "AURELIA-G0-GOVERNANCE-DESIGN"`, `operatorIdentity`,
`operatorRole: "ROLE-OPERATOR"`,
`operatorKeyRef`, `operatorKeyFingerprint`, `method: "ed25519"`, `issuedAt`,
`nonce` und `signature`. Sie wird vor
Genesis erzeugt, signiert alle Felder außer `signature`, liegt am festen Pfad
und wird im Genesis-Anchor durch Pfad und Dateihash referenziert. Sie ist nie
eine EVT-Attestationsdatei und erzeugt daher keinen Self-Hash-Kreis.

Alle externen Kontrollakten bilden eine einzige append-only Logfolge. Jeder
Eintrag besitzt neben seinem unten geschlossenen Payload exakt die gemeinsamen
Felder `schemaVersion`, `entryKind`, `repositoryId`, `logId`,
`transparencyLogIndex`, `previousLogEntrySha256`, `loggedAt`,
`instanceKeyRef`, `instanceKeyEpoch`, `method: "ed25519"`, `entryCoreSha256`
und `instanceSignature`. Der Core ist die RFC-8785-Projektion des vollständigen
Eintrags ohne `entryCoreSha256` und `instanceSignature`; die Instanz signiert
exakt den Core. `instanceSignature` enthält ausschließlich `keyRef`, `signedAt`,
`nonce`, `entryCoreSha256` und `signature`; `keyRef` ist bytegleich
`instanceKeyRef`. Der Logindex beginnt bei `0` und ist lückenlos;
`previousLogEntrySha256` ist dort `null` und danach der SHA-256 der
vollständigen kanonischen, signierten Vorgängerbytes. Zulässige Entry-Kinds
sind ausschließlich `acceptance-receipt`, `branch-policy-transition`,
`tcb-activation`, `tcb-rollback`, `tcb-emergency-recovery`,
`recovery-operation-lease`, `recovery-write-ahead-receipt`,
`recovery-idempotency-tombstone`, `recovery-egress-intent`,
`transparency-key-transition`,
`external-model-request-receipt` und
`custodian-pin-transition`. Nur die unten geschlossene Recovery-Ausnahme einer
kompromittierten Transparenzinstanz darf `instanceSignature: null` führen und
benötigt stattdessen die vollständige externe Recovery-Schwelle.

Jeder Entry-Kind mit zusätzlicher Payloadautorisierung besitzt einen im
jeweiligen Schema benannten `*CoreSha256`. Dieser Payload-Core ist ausnahmslos
der Hash der RFC-8785-Projektion aller spezifischen Payloadfelder außer exakt
dem benannten Core selbst und den in diesem Payloadschema abschließend
aufgezählten Payload-Signaturfeldern; die erst beim Append vergebenen
gemeinsamen Logfelder `schemaVersion`, `entryKind`, `repositoryId`, `logId`,
`transparencyLogIndex`, `previousLogEntrySha256`, `loggedAt`, `instanceKeyRef`,
`instanceKeyEpoch`, `method`, `entryCoreSha256` und `instanceSignature` gehören
niemals hinein. Insbesondere gilt diese eine Regel ohne Gateway-Ausnahme für
`receiptCoreSha256` des Recovery-Write-ahead-Payloads. Jeder zugehörige Signatureintrag
enthält ausschließlich den schemafesten Purpose, Signerrolle oder Witness-ID,
Signeridentität soweit rollenbezogen, KeyRef, `signedAt`, global einmalige
Nonce, exakt diesen Core-Digest und Ed25519-Signatur. Danach bindet der
`entryCoreSha256` einschließlich aller Payloadsignaturen zusätzlich den
vollständigen Logkontext. So gibt es weder Zukunftsindex- noch Signaturhash-
Fixpunkte; die Schematests verwenden pro Entry-Kind feste RFC-8785-Bytes.

Für jeden erstmals akzeptierten Head entsteht ein
`entryKind: "acceptance-receipt"`-Eintrag. Sein spezifischer Payload enthält
ausschließlich `receiptId`, `branch`, `headCommit`, `headTreeOid`, `events`,
`validatorImageDigest`, `validatorPolicySha256`, `workflowSha256`,
`schemaSetSha256`, `trustProtocolSha256`, `tcbStateEpoch`,
`tcbStateEntryId`, `tcbStateEntrySha256`, `branchRulesSha256`,
`branchPolicyEpoch`, `acceptedAt`, `oidcIssuer`, `oidcAudience`, `oidcSubject`
und `runId`. In Bootstrap-Epoch `1` sind State-ID/-Hash `null` und der TCB-Satz
bytegleich zum Pre-Ledger-Bundle; danach binden sie den vollständigen aktiven
TCB-State-Logeintrag. `events` ist nach `eventId` sortiert; jeder Eintrag
besitzt ausschließlich `eventId`, `eventSha256` und `attestations`. Dessen nach
`attestationPurpose,keyRef` sortierte Attestationen besitzen ausschließlich
`attestationPurpose`, `keyRef`, `envelopeSha256` und `nonceSha256`. Jede EVT-
Attestation erscheint exakt einmal. Envelope-/Nonce-Digests und Eventhash
werden neu berechnet.

Eine Branchregeländerung erzeugt genau einen
`entryKind: "branch-policy-transition"`-Eintrag mit spezifisch ausschließlich
`policyTransitionId`, `branch`, `observedHeadCommit`,
`previousBranchRulesSha256`, `observedBranchRulesSha256`,
`previousBranchPolicyEpoch`, `branchPolicyEpoch` exakt um eins erhöht,
`invalidatesThroughLogIndex`, `reason` und `observedAt`.
`invalidatesThroughLogIndex` ist der unmittelbar vorherige Logindex. Ab diesem
Eintrag darf keines der früheren Acceptance-Receipts dieses Branches mit dem
alten Regelhash oder der alten Policy-Epoch ein Gate stützen. Jedes spätere
Receipt muss den im Replay aktuell wirksamen Regelhash und die neue Epoch
tragen; auch eine spätere Rückkehr zu denselben Regelbytes erzeugt eine weitere
Epoch und reaktiviert nie alte Receipts.

`tcb-activation`, `tcb-rollback` und alle drei Phasen von
`tcb-emergency-recovery` folgen den geschlossenen Payloads aus Abschnitt 6.3.
Nur Activation, Rollback und die abgeschlossene Recovery erzeugen einen neuen
aktiven State; deren `tcbStateEpoch` steigt strikt um eins und jede
`previousTcbStateEntrySha256`-Kante zeigt auf die vollständigen Bytes des
unmittelbar vorher aktiven TCB-State-Eintrags. Die autorisierte Recoveryphase
reserviert genau diese nächste Epoch, wird selbst aber nie aktiver State; bis
zum passenden Completion- oder Abort-Checkpoint blockiert sie jeden Receipt
und jede weitere TCB-Transition. Abort löst nur die Reservierung, ändert den
aktiven State nicht und reaktiviert keine Gates. Jede Promotion-Request-ID ist
höchstens einmal verbrauchbar. Es
kann deshalb weder eine zweite gültige Activation vom selben Request noch
einen verzweigten aktiven Controllerzustand geben. Ein Receipt ist für aktuelle
Gate-/Releaseentscheidungen nur verwendbar, wenn State-Epoch, State-ID/-Hash
und vollständiger TCB-Satz exakt dem an seinem Logindex aktiven Zustand
entsprechen und keine spätere Rollback-/Recovery-Transition diese Epoch
verworfen hat.

Die Instanz veröffentlicht Checkpoints mit ausschließlich `schemaVersion`,
`repositoryId`, `logId`, `checkpointKind: "regular"|"key-recovery-floor"`,
`treeSize`, `rootSha256`, `issuedAt`, `previousCheckpointSha256`,
`instanceKeyRef`, `instanceKeyEpoch`, `keyTransitionSha256`,
`method: "ed25519"`, `checkpointCoreSha256`, `instanceSignature`,
`recoveryAuthorizationSignatures` und `witnessSignatures`. Der Merklebaum folgt
RFC-6962-Domänentrennung: Blatt `SHA256(0x00 || RFC8785(entry))`, innerer Knoten
`SHA256(0x01 || left || right)`. Der Checkpoint-Core umfasst alle Felder außer
Core-Digest, Instanz-, Recovery- und Witness-Signaturen. `regular` verlangt die
aktive Instanzsignatur und leere Recovery-Signaturen. Die Instanzsignatur
enthält ausschließlich `keyRef`, `signedAt`, `nonce`,
`checkpointCoreSha256` und `signature`. `key-recovery-floor` ist nur bei
`compromise|loss` zulässig, besitzt `instanceSignature: null` und die unten
vollständige Recovery-Schwelle. Deren nach `purpose,keyRef` sortierte
Rollensignaturen enthalten ausschließlich `purpose`, `signerRole`,
`signerIdentity`, `keyRef`, `signedAt`, `nonce`, `checkpointCoreSha256` und
`signature`; erforderlich sind Operator, Recovery-Root,
Validator-Controller und nach erstmaligem Pilot-Green beide Custodians. Jeder
Checkpoint benötigt zusätzlich alle im Pre-Ledger beziehungsweise durch
vollständig aktivierte Transitionen konfigurierten Witness-Signaturen; jeder
Eintrag enthält ausschließlich `witnessId`, `keyRef`, `signedAt`, `nonce`,
`checkpointCoreSha256` und `signature`. `treeSize` ist positiv und über die
Checkpointkette nicht fallend;
gleiche Größe/Root ist ausschließlich beim ersten Checkpoint einer neuen
Key-Epoch zulässig. Beim ersten Bootstrap-Checkpoint ist
`previousCheckpointSha256: null`; danach bindet es lückenlos die vollständigen
Vorgängerbytes. `keyTransitionSha256` ist außer beim Recovery-Floor und ersten
regulären Checkpoint einer neuen Key-Epoch `null`.

Das exportierte Transparency-Bundle enthält ausschließlich `schemaVersion`,
`repositoryId`, `entries`, `checkpoints` und `witnessFloors`. `entries` ist das
vollständige Präfix mit exakt den Indizes `0..latest.treeSize-1`;
`checkpoints` ist die vollständige Hashkette vom ersten bis zum frischen
letzten Checkpoint, `witnessFloors` die vollständigen unten definierten
Witness-Floor-Ketten. Der Validator berechnet Loghashkette und jede Merkle-Root
aus dem Vollpräfix neu. Redundante Inclusion-/Consistency-Proofs sind verboten;
die Konsistenz zu jedem früher vertrauten Checkpoint wird direkt aus dessen
Präfixgröße und Root neu berechnet. Eine aktuelle Gate-/Releaseprüfung verlangt
zusätzlich einen höchstens eine Stunde alten letzten Checkpoint und frisch von
allen Witnesses bezogene Floors. Ist ein Witness-Floor größer als der
Bundle-Checkpoint oder nennt er bei gleicher Größe einen anderen
Checkpointhash, ist das Bundle stale beziehungsweise equivok und alle Gates
sind `red`.

Jeder Witness führt und veröffentlicht nach
`transparency-witness-floor.schema.json` eine monotone Kette. Ein Floor enthält
ausschließlich `schemaVersion`, `repositoryId`, `floorId`, `logId`,
`witnessId`, `keyRef`, `minimumTreeSize`, `minimumCheckpointSha256`,
`instanceKeyEpoch`, `observedAt`, `previousFloorSha256`, `nonce` und
`signature`; die Signatur umfasst alle übrigen Felder. Größe und Key-Epoch
fallen nie, die vorherige Kante bindet die vollständigen signierten Bytes.
Jeder co-signierte Key-Transition-Floor muss unmittelbar als neuer Floor
publiziert und zwischen Witnesses gegossipt werden; damit kann ein alter,
formal noch frischer Checkpoint die Transition nicht verbergen.

Eine Equivokationsmeldung enthält ausschließlich `schemaVersion`,
`repositoryId`, `reportId`, `logId`, `witnessId`, `witnessKeyRef`, `reason`,
`firstProposal`, `secondProposal`, `previousWitnessObservationSha256`,
`observedAt`, `nonce`, `reportCoreSha256` und `signature`.
`reportCoreSha256` ist der Hash der RFC-8785-Projektion aller Felder außer Core
und Signatur; die Signatur bindet exakt diesen Digest. `witnessId`,
`witnessKeyRef` und Signatur werden gegen den zu diesem Observation-Zeitpunkt
aktiven, extern gepinnten Witness-Key geprüft. Jede Proposal enthält den vollständigen
`checkpointCore`, `checkpointCoreSha256`, `instanceSignature` und
`witnessSignatures`. `checkpointCore` besitzt exakt die oben genannten
Checkpointfelder ohne Core-Digest und alle drei Signaturfelder und hat
`checkpointKind: "regular"`; Digest und geschlossene Instanzsignatur werden
neu geprüft. `witnessSignatures` ist die nach `witnessId,keyRef` sortierte,
duplikatfreie, möglicherweise leere Teilmenge der oben geschlossenen Witness-
Signaturen;
ein Vollquorum ist ausdrücklich nicht erforderlich. `reason` ist
`same-size-different-root`, `decreasing-tree-size` oder
`inconsistent-successor`. So ist bereits die Aufteilung von Proposal X an
Witness A und Proposal Y an Witness B meldbar. Jede gültige Meldung setzt alle
Gates `red`; zwei Split Views können kein gültiges Vollquorum erhalten.

Der Transparenzinstanzkey ist durch Pre-Ledger, Genesis und externe Pins an
`logId` und Epoch `1` gebunden. Ein Wechsel ist selbst ein
`entryKind: "transparency-key-transition"`-Logeintrag. Sein spezifischer
Payload enthält ausschließlich `transitionId`, `transitionReason`,
`fromKeyRef`, `fromKeyEpoch`, `fromKeyFingerprint`, `toKey`,
`lastCheckpointSha256`, `lastTreeSize`, `lastRootSha256`,
`activationMode: "after-witness-floor"`, `transitionCoreSha256` und
`authorizationSignatures`. `toKey` enthält ausschließlich `keyRef`,
`keyEpoch` exakt `fromKeyEpoch + 1`, `algorithm: "ed25519"`,
`publicKeyBase64url` und `fingerprintSha256`. Der Transition-Core umfasst
den spezifischen Payload ohne Core-Digest und Autorisierungssignaturen; die
gemeinsamen Logfelder bindet erst die Instanz-Entry-Signatur. Bei normaler
`rotation` authentifiziert die gemeinsame Instanzsignatur den alten
Instanzkey; Operator und Recovery-Root sowie nach erstmaligem Pilot-Green beide
Custodians autorisieren den Wechsel zusätzlich.
Bei `compromise|loss` signieren Operator, Root, nach Pilot beide Custodians,
Validator-Controller und sämtliche Witnesses; nur dann darf die Logentry-
Instanzsignatur `null` sein. Rollen-Signatureinträge sind nach
`purpose,keyRef` sortiert und enthalten ausschließlich `purpose`,
`signerRole`, `signerIdentity`, `keyRef`, `signedAt`, `nonce`,
`transitionCoreSha256` und `signature`. Witness-Einträge enthalten
ausschließlich `purpose: "witness"`, `witnessId`, `keyRef`, `signedAt`, `nonce`,
`transitionCoreSha256` und `signature`; beide Formen sind im Schema als
disjunktes `oneOf` geschlossen.

Der jüngste alte Checkpoint muss exakt durch Hash, Größe und Root gebunden sein.
Nach Append der Transition erzeugt die alte Instanz bei Rotation einen letzten
alten Vollquorum-Checkpoint; bei Verlust/Kompromittierung entsteht stattdessen
der `key-recovery-floor`. Er trägt bereits `toKey.keyRef` und dessen Epoch,
bindet `keyTransitionSha256` an den vollständigen Transition-Logentry und wird
durch die oben definierte Recovery-Schwelle sowie alle Witnesses signiert. Alle
Witnesses veröffentlichen diesen Floor monoton. Der erste reguläre Checkpoint
der neuen Epoch übernimmt identische Loggröße/Root, bindet als
`previousCheckpointSha256` den Floor und als `keyTransitionSha256` den
vollständigen Transition-Logentry-Hash. Erst danach werden externe Pin-Caches
auf den neuen Key aktualisiert. Ab dem publizierten Floor sind alle Gates
abgeleitet `red`; alte Checkpoints darunter scheitern am live abgefragten
Witness-Floor. Erneutes Green verlangt neue Reviews und Gatefreigaben. Verlust
eines Witness-, Root- oder Controller-Keys hält G0 fail-closed; ihre genehmigten
und praktisch getesteten Recovery-/Rotationsverträge sind ausdrücklich
Voraussetzung für `GATE-PILOT green`.

## 7. Rollen und Funktionstrennung

| Rollen-ID | Verantwortungsbereich | Besetzung im Pilot |
|---|---|---|
| `ROLE-OPERATOR` | Betreiber, Product Owner, finale Release- und Restrisikoentscheidung | Repository-Inhaber `redshift-three67` |
| `ROLE-ORCHESTRATOR` | Planung, Kontextpakete, Integration und Evidenzzusammenführung | agentischer Orchestrator; keine eigene finale Freigabe |
| `ROLE-EXTERNAL-REVIEW-RUNNER` | lokaler, attestierter Transport und Capture externer Modellantworten | Service; Ausgabe bleibt unvertrauenswürdige EVID, keine Reviewerfreigabe |
| `ROLE-IMPLEMENTER` | Umsetzung eines freigegebenen, begrenzten Tasks | pro Task frisch benannter Agent oder Entwickler |
| `ROLE-SPEC-REVIEWER` | unabhängiger Soll-/Ist-Abgleich | vom Implementer getrennt |
| `ROLE-QUALITY-SECURITY-REVIEWER` | Qualität, Fehlermodi und technische Sicherheit | vom Implementer getrennt |
| `ROLE-FINAL-REVIEWER` | unabhängige integrierte Gesamtprüfung | von Implementer, Orchestrator, Spec- und Quality/Security-Reviewer getrennt |
| `ROLE-PRIVACY-REVIEWER` | Datenschutzprüfung, DSFA-Zuarbeit und Betroffenenrechte | unbesetzt; Art.-9-Gate bleibt `red` |
| `ROLE-LEGAL-REVIEWER` | unabhängige rechtliche Prüfung von Zweck, Rechtsgrundlagen, Verträgen und Claims | unbesetzt; Art.-9- und Claim-Gates bleiben `red` |
| `ROLE-PENTESTER` | unabhängiger Web-/API-Penetrationstest | unbesetzt; Pilot-Release-Gate bleibt `red` |
| `ROLE-HARDWARE-REVIEWER` | Emitter-, Sensor- und elektrische Betriebssicherheit | unbesetzt; Hardware-Gates bleiben `red` |
| `ROLE-A11Y-CLAIMS-REVIEWER` | Barrierefreiheit und nichtmedizinische Claim-Grenze | unbesetzt; finales Release-Gate bleibt `red` |
| `ROLE-RECOVERY-ROOT` | offline verwahrte kryptografische Co-Autorisierung für geschlossene recovery-kritische Trust-Operationen | in Genesis extern gepinnt; kein Online- oder Alltagskey |
| `ROLE-RECOVERY-CUSTODIAN-A` | erste menschliche Break-glass-Freigabe für Betreiberwiederherstellung | vom Betreiber und zweiten Custodian getrennt; zunächst unbesetzt |
| `ROLE-RECOVERY-CUSTODIAN-B` | zweite menschliche Break-glass-Freigabe für Betreiberwiederherstellung | vom Betreiber und ersten Custodian getrennt; zunächst unbesetzt |

Der Betreiber kann mehrere accountable Rollen im kontrollierten Pilot tragen,
aber Implementierung und unabhängige technische Verifikation dürfen für
denselben Scope nicht durch dieselbe Instanz freigegeben werden. KI-Systeme
dürfen Evidenz vorbereiten und Findings aussprechen, jedoch weder rechtliche
noch datenschutzrechtliche, Penetrations-, Hardware- oder Betreiberfreigaben
ersetzen.

`GATE-ART9` benötigt getrennte genehmigte REV-Akten von
`ROLE-PRIVACY-REVIEWER` und `ROLE-LEGAL-REVIEWER`. Keine der beiden Rollen
ersetzt die andere. Beide Rollen müssen durch hierfür qualifizierte Menschen
besetzt sein; KI-Ausgaben können nur Zuarbeit oder Evidenzanhang sein.

Für Reviews gilt die folgende geschlossene Mindestmatrix; `reviewerRole` und
`approvedByRole` müssen exakt passen, `independentFrom` enthält mindestens die
genannten Rollen und die aufgelösten Assignees sind für denselben Scope
paarweise verschieden:

| `reviewType` | `reviewerRole` | `approvedByRole` bei `approved` | zwingend getrennt von |
|---|---|---|---|
| `spec` | `ROLE-SPEC-REVIEWER` | `ROLE-OPERATOR` | `ROLE-IMPLEMENTER`, `ROLE-ORCHESTRATOR` |
| `quality-security` | `ROLE-QUALITY-SECURITY-REVIEWER` | `ROLE-OPERATOR` | `ROLE-IMPLEMENTER`, `ROLE-ORCHESTRATOR`, `ROLE-SPEC-REVIEWER` |
| `final` | `ROLE-FINAL-REVIEWER` | `ROLE-OPERATOR` | `ROLE-IMPLEMENTER`, `ROLE-ORCHESTRATOR`, `ROLE-SPEC-REVIEWER`, `ROLE-QUALITY-SECURITY-REVIEWER` |
| `operator` | `ROLE-OPERATOR` | `ROLE-OPERATOR` | `ROLE-IMPLEMENTER`, `ROLE-ORCHESTRATOR` des Subjects |
| `privacy` | `ROLE-PRIVACY-REVIEWER` | `ROLE-OPERATOR` | `ROLE-IMPLEMENTER`, `ROLE-ORCHESTRATOR`, `ROLE-LEGAL-REVIEWER` |
| `legal` | `ROLE-LEGAL-REVIEWER` | `ROLE-OPERATOR` | `ROLE-IMPLEMENTER`, `ROLE-ORCHESTRATOR`, `ROLE-PRIVACY-REVIEWER` |
| `pentest` | `ROLE-PENTESTER` | `ROLE-OPERATOR` | `ROLE-IMPLEMENTER`, `ROLE-ORCHESTRATOR`, `ROLE-QUALITY-SECURITY-REVIEWER` |
| `hardware` | `ROLE-HARDWARE-REVIEWER` | `ROLE-OPERATOR` | `ROLE-IMPLEMENTER`, `ROLE-ORCHESTRATOR` |
| `a11y-claims` | `ROLE-A11Y-CLAIMS-REVIEWER` | `ROLE-OPERATOR` | `ROLE-IMPLEMENTER`, `ROLE-ORCHESTRATOR` |

Jede in der letzten Spalte genannte Trennung steht symmetrisch in den
`separationFromRoleRefs` beider ROLE-Records; fehlende Rückkanten sind
ungültig. Zusätzliche Trennungen dürfen die Mindestmatrix nur verschärfen,
niemals ersetzen.

Die Identität von Reviewer und Approver ist außer bei `reviewType: "operator"`
immer verschieden. Auch dort darf der Operator weder Subject-Implementer noch
-Autor sein. Ein P0- oder P1-Finding darf nur in einer genehmigten
Nachfolgerreview desselben Typs verworfen werden: `dismissedByRole` ist deren
fachlich vorgeschriebene Reviewerrolle, der gespeicherte Assignee ist der
tatsächliche Nachfolgerreviewer und `approvedByRole` ist zusätzlich
`ROLE-OPERATOR`. Implementer oder Orchestrator können ein P0/P1 niemals allein
schließen. P2/P3 folgen mindestens derselben fachlichen Reviewerrolle.

Die beiden Recovery-Custodians führen jeweils `ROLE-OPERATOR` und die andere
Custodian-Rolle in `separationFromRoleRefs`; alle drei Assignees und aktiven
Key-Fingerprints sind paarweise verschieden. Diese Trennung ist symmetrisch
und kann nicht durch eine Mehrfachrolle desselben Menschen erfüllt werden.
`ROLE-RECOVERY-ROOT` besitzt ausschließlich den extern gepinnten Offline-Key
und keine Netzwerk-Credential. Seine geschlossenen Autorisierungszwecke sind
exakt Genesis-Bootstrap, geplanter Operator-Handover, Operator-Recovery,
TCB-Promotion samt vorab autorisiertem Rollback sowie erstmalige Besetzung und
Rotation eines Recovery-Custodians und Transparenzinstanz-Key-Transition. Er besitzt kein Online-, Alltags-, Gate-
oder fachliches Freigaberecht; alle anderen Envelopes und Artefaktzwecke werden
abgewiesen.
Assignee, Key und externer Pin dieser Rolle sind in G0 und Pilot immutable;
normale ROLE-Events, Operatorhandlungen oder Repositoryänderungen dürfen sie
weder rotieren noch widerrufen. Verlust oder Kompromittierung hält alle Gates
`red`. Eine geplante spätere Rotation müsste durch den bisherigen Root und die
dann geltende Custodian-Schwelle autorisiert werden; für tatsächlichen Verlust
oder Kompromittierung behauptet G0 ausdrücklich keinen Notweg, der die nicht
mehr vertrauenswürdige Root-Signatur voraussetzt. Pilot-Green bleibt deshalb
gesperrt, bis ein separater physischer Multi-Party-Recoveryvertrag mit eigener
extern gepinnter Vertrauenswurzel, Re-Pinning-Transparenz und praktischem
Verlusttest genehmigt ist.

## 8. Reasoning- und Modell-Eskalation

Reasoning wird nach Auswirkung, nicht nach Dateianzahl oder scheinbarer
Mechanik gewählt. Unterstützte Stufen können vom ausgewählten Modell abhängen.

| Stufe | Geeigneter Umfang |
|---|---|
| `medium` | Repository-Recherche, klar begrenzte Dokumentation, risikoarme mechanische Änderungen und Standardtests |
| `high` | mehrteilige Implementierung, Datenmodelle, API-Verträge, Integrationen und schwierige Fehleranalyse |
| `xhigh` | Threat Model, Tenant-Isolation, RLS, Schlüsselhierarchie, Datenschutzdatenfluss, Restore, Incident Response und Gesamtarchitektur |
| `max`/`ultra` | nur bei widersprüchlichen Sicherheitsanforderungen, ungeklärten Releaseblockern, divergierenden Reviews oder besonders kritischer Gesamtfreigabe, sofern unterstützt |

Vor jeder Änderung der Stufe nennt der Orchestrator:

1. bisherige und empfohlene Stufe;
2. betroffenen Arbeitsschritt;
3. konkrete Risikobegründung;
4. vorgesehenen Rückkehrpunkt.

Die Arbeit auf der neuen Stufe beginnt erst nach ausdrücklicher Bestätigung des
Betreibers. Auch eine Herabstufung wird angekündigt und bestätigt. Während
eines laufenden Hochrisiko-Tasks wird nicht aus Token- oder Zeitgründen
herabgestuft. Im REV-Protokoll werden Modellrolle, Modellbezeichnung,
bestätigte Stufe, Scope und Ergebnis erfasst, niemals interne Gedankengänge.

Der Orchestrator kann die UI-Einstellung nicht als technisch erzwungen
behaupten. Die Betreiberbestätigung dokumentiert die beabsichtigte Einstellung.

Tokenoptimierung ist nur über kleinere kanonische Kontextpakete, gezielte
Diffs, risikogerechte Modellwahl und das Vermeiden wiederholter Vollscans
zulässig. Sie darf keine Akzeptanzkriterien, Sicherheitsinvarianten,
Negativtests, Evidenzen oder Reviewstufen entfernen. Bei Unsicherheit gewinnt
Vollständigkeit vor Tokenersparnis.

## 9. Subagent-Driven- und Reviewprozess

Jeder Implementierungstask verwendet ein kuratiertes Kontextpaket mit:

- Taskziel und vollständigen Akzeptanzkriterien;
- geltenden REQ-, CTRL-, RISK- und GATE-IDs;
- erlaubten Dateien und ausdrücklich genannten Nicht-Zielen;
- Abhängigkeiten und Sicherheitsinvarianten;
- erwarteten Tests und Evidenzen;
- bekannten Findings aus vorherigen Reviews.

Die Reihenfolge ist verbindlich:

1. freigegebene Spezifikation und Implementierungsplan;
2. frischer Implementer, testgetriebene Umsetzung und Selbstprüfung;
3. unabhängige Spec-Review;
4. Korrektur und erneute Spec-Review bis `approved`;
5. unabhängige Quality/Security-Review;
6. Korrektur; anschließend erneute Spec- und Quality/Security-Review für den
   betroffenen Scope;
7. sequenzielle Verifikationsgates und Evidenzaufnahme;
8. unabhängige Gesamt-Review;
9. Betreiberfreigabe oder dokumentierte Ablehnung.

Nur ein Implementer bearbeitet zur selben Zeit dieselbe Dateioberfläche.
Parallele Arbeit ist nur in isolierten Worktrees mit nicht überlappender
Dateihoheit zulässig. Der Orchestrator integriert erst einen sauberen Diff mit
grünen Tests und abgeschlossener Reviewkette.

## 10. Externe LLM-Zuarbeit

Ein über Kimi Code CLI gesteuertes Modell wie die vom Betreiber bezeichnete
Variante `gemini-flash-3-7` darf als schnelle unabhängige Gegenprobe für
begrenzte Konsistenz-, Vollständigkeits- oder Diffprüfungen dienen. Es ist
keine alleinige Security-, Privacy-, Kryptografie- oder Releaseinstanz.

Vor nichtöffentlichem Kontext werden Anbieter/Endpoint, tatsächliche
Modellbezeichnung und -version, Datenverarbeitung, Region, Aufbewahrung und
Trainingseinstellung als verifizierte `provider-due-diligence`-EVID festgehalten. Diese Due Diligence
erweitert niemals den zulässigen Kontext: Externe LLMs erhalten ausnahmslos nur
synthetische, öffentliche oder minimal erforderliche, lokal sanitierte
**Nicht-Produktionsausschnitte** des Repositories.

Nie übermittelt werden:

- Secrets, Tokens, Schlüssel oder Zugangsdaten;
- personenbezogene oder Art.-9-Daten;
- sämtliche produktionsabgeleiteten Konfigurationen, Dumps, Logs,
  Telemetriedaten, Topologien oder Recovery-Artefakte, auch auszugsweise;
- aktuelle oder geplante Produktions-, Betriebs-, Architektur-, Security-,
  Recovery-, Deployment- oder Serverkonzepte, auch sanitierte Ausschnitte;
- reale Hostnamen, IP-Adressen, Tenant-, Client-, User- oder Geräte-IDs;
- Netzwerk-, Server-, Backup-, Schlüssel- oder Mandantendetails aus der realen
  Zielumgebung, selbst wenn sie für eine Prüfung nützlich erscheinen;
- das vollständige private Repository; externe Prüfobjekte bleiben immer auf
  den kleinsten sanitierbaren Ausschnitt begrenzt.

Eine erste Gegenprobe erfolgt möglichst ohne die Schlussfolgerung des
Orchestrators. Jeder Befund muss Priorität, Behauptung, Datei/Zeile,
reproduzierbares Szenario, betroffene Invariante, Korrektur, Verifikationstest,
Konfidenz und geprüften Umfang nennen. Ausgaben externer Modelle gelten als
unvertrauenswürdige Empfehlungen und werden lokal verifiziert.

Ein externes Modell wird niemals als EVT-Akteur oder `reviewerRole` geführt,
weil es keinen AURELIA-Trust-Root besitzt. `ROLE-EXTERNAL-REVIEW-RUNNER`
attestiert ausschließlich Transport, Provider-Response-Digest und unveränderte
Capture-EVID. Erst ein intern oder menschlich besetzter, nach Abschnitt 7
getrennter Reviewer bewertet diese EVID und signiert die REV-Akte in eigener
Verantwortung.

## 11. M-G1-Zugriffs- und In-place-Härtungsstrategie

Der M-G1 ist ab jetzt ausschließlich für AURELIA vorgesehen. Installiert ist
Debian Linux mit Desktop Environment; derzeit laufen lediglich
Entwicklungsumgebungen. Welche Dienste tatsächlich aktiv sind, ist noch nicht
verifiziert.

Die bestehende Partitionierung bleibt erhalten. Eine Neuinstallation oder
Neupartitionierung gehört nicht zum Normalverfahren. Sie ist nur zulässig,
wenn ein dokumentierter Befund belegt, dass Verschlüsselung,
Datenträgerintegrität oder eine zwingende Sicherheitsgrenze anders nicht
erreichbar ist, der Betreiber ausdrücklich freigibt und Fachpersonal die
Arbeit vor Ort mit gesichertem Rückroll- oder Wiederherstellungsweg ausführt.

Zugriff erfolgt stufenweise:

1. **G0 und frühes Design:** lokales Repository, kein Serverzugriff.
2. **Collector-Bootstrap:** Noch vor dem ersten Netzwerk-Audit führt
   Fachpersonal vor Ort oder über eine abgesicherte Konsole einen separat
   signierten privilegierten Change-Plan aus. Er nennt Ausgangshashes, exaktes
   Write-Set für Binaries, Konfiguration, `authorized_keys`, sshd-/systemd-
   Drop-ins und Auditregeln, vollständige Dateiinhalte/-modi/-Owner,
   Sicherungen, atomare Installationsschritte, Rollback und Nachprüfung. Ein
   ungeplanter Write oder Hashfehler bricht vor SSH-Aktivierung ab.
3. **Nach verifiziertem Bootstrap und vor Einfrieren des Threat Models:** kein
   allgemeiner Shellzugang. Der signierte Inventurcollector läuft als
   SSH-Forced-Command mit fester
   Argument-Allowlist, ohne PTY, Agent-/X11-/Port-Forwarding, beliebige
   Argumente oder ausgehende Verbindungen. Der fest gehashte Dispatcher
   startet ausschließlich den Collector über eine fest konfigurierte
   Systemd-Service-Unit mit dem schema-validierten `collectorContract`; die
   SSH-Sitzung erbt die Sandbox nicht nur implizit. `ProtectSystem=strict`,
   `ReadOnlyPaths=/`, unzugängliche `/tmp`-/`/var/tmp`- und Control-Socket-
   Pfade, `IPAddressDeny=any`, keine erlaubte Address Family, ein Verbot aller
   Network-I/O-Syscalls, vollständiger Capability-Drop und Prozess-/CPU-/
   Speicherlimits werden nach dem Lauf aus Unit-Properties verifiziert.
   Listener-, Verbindungs- und Socketinventar entsteht ausschließlich durch
   lesendes Parsen von `/proc/net/*` und Prozess-FD-Inodes; der Collector öffnet
   selbst keinen Socket. Ein
   dedizierter UID/GID ohne Supplementary Groups und ohne Docker-, Container-,
   Journal- oder Administrationsgruppe ist Pflicht. Ein normaler Nicht-Root-SSH-Account wird
   ausdrücklich nicht als „read-only“ bezeichnet oder akzeptiert.
4. **Vor Provisionierungsfreigabe:** physische Konsole oder abgesicherte
   Remote-Konsole für UEFI, Secure Boot, TPM, LUKS-Boot, Datenträger-, GPU-,
   Netzwerk-, Stromversorgungs- und Recovery-Prüfung.
5. **Pilotinstallation:** zeitlich begrenzte, personenbezogene Privilegierung
   ausschließlich gegen einen signierten Change-Plan. Dieser bindet
   Basiszustand, exakte `argv`-Arrays ohne Shellinterpretation, Binärdateihash,
   Zeitfenster, Backup-/Restore-Evidenz, erwarteten Zustand, Rückrollschritte
   und Verifikationsbefehle. Editoren, Pager, Shells, Interpreter, Plugin-
   Loader und frei ergänzbare Argumente sind verboten; ein pauschaler
   `sudo`-Account oder nur textlich „vorab freigegebener Befehl“ genügt nicht.
6. **Vor Art.-9- und Hardwaregates:** praktischer isolierter Restore sowie
   physische GPU-/USB-/Emitter-/Sensor- und Notabschaltungsprüfung.

Die erste Inventur erfasst mindestens:

- Debian-Version, Kernel, Paketquellen und Patchstand;
- Benutzer, Gruppen, sudo-Regeln, SSH und interaktive Sitzungen;
- systemd-Dienste, Sockets, Timer, Cron, Desktop-Autostarts und Display Manager;
- Container, virtuelle Umgebungen und lokale Entwicklungsserver;
- lauschende Ports, Firewall, DNS, Routing und ausgehende Verbindungen;
- Dateisysteme, Mounts, LUKS, Swap, SMART/NVMe-Zustand und freien Speicher;
- GPU-, CUDA- und USB-Treiber sowie tatsächlich erkannte Geräte;
- Secretspeicher, Backups, Logs und Recovery-Möglichkeiten;
- USV/Stromversorgung und vorhandene Remote-Management-Funktionen.

Vor einer Bereinigung werden Konfiguration und benötigte Daten gesichert.
Jeder Fund erhält `keep`, `isolate`, `disable`, `remove` oder `investigate`,
mit Begründung, Abhängigkeiten, Rückrollbefehl und Verifikation. Die
Desktop-Umgebung wird nicht pauschal entfernt; ihre spätere Startart und
Angriffsfläche werden anhand des Threat Models entschieden.

Collector-Quelltext, Buildprovenienz, Signatur, erlaubte Kommandos und die
Redaktionsregeln für Secrets werden vor dem ersten Lauf reviewed. Die Ausgabe
wird lokal gehasht, vor Übernahme auf Secrets geprüft und als
`audit-artifact` erfasst. Jeder Schreibversuch, unerwartete Prozessstart,
Netzwerkzugriff oder Ressourcenlimitverstoß beendet die Inventur fail-closed
und hält `GATE-PROFILE` sowie `GATE-PILOT` `red`.

## 12. Registerverträge

Jeder JSON-Block besitzt genau die Pflichtfelder `schemaVersion` mit dem
konstanten String `aurelia-governance-v1`, `registerType` mit einem der Werte
`traceability`, `risk`, `data-processing`, `gate` sowie ausschließlich die für
diesen Typ in Abschnitt 6.2 festgelegten Arrays. Alle anderen Top-Level-Felder
sind verboten.

Alle Records besitzen die gemeinsamen Pflichtfelder:

| Feld | JSON-Typ und Regel |
|---|---|
| `id` | nichtleerer String; passendes ID-Pattern aus der folgenden Tabelle |
| `title` | nichtleerer String |
| `status` | nichtleerer String; Enum des jeweiligen Recordtyps |
| `ownerRole` | ROLE-ID |
| `sourceRefs` | Array aus mindestens einem eindeutigen Source-Locator |
| `reviewOn` | String `YYYY-MM-DD` |
| `exceptionProvenanceRefs` | eindeutiges Array aus EXC-IDs; abgeleitete, monotone Ausnahmeprovenienz |

Ein Source-Locator ist entweder `repo:<pfad>#L<start>-L<ende>`,
`repo:<pfad>#<export>` oder `approval:<REV-ID>`. Repository-Pfade sind relativ,
verwenden `/`, dürfen kein `..` enthalten und müssen existieren. Datumswerte
verwenden `YYYY-MM-DD`, Zeitpunkte RFC 3339 und Commit-Baselines ausschließlich
vollständige 40-stellige Git-SHAs. Strings sind nichtleer, Arrays enthalten
eindeutige Werte. `null` ist nur bei ausdrücklich als nullable bezeichneten
Feldern zulässig. `additionalProperties` ist auf jeder Ebene `false`.

REQ, CTRL, PROFILE, ROLE, COMP, RISK, DATA, FLOW, GATE und EXC besitzen
zusätzlich die Pflichtfelder `supersedesRecordRef: string | null` und
`supersededByRecordRef: string | null`. Beide verweisen ausschließlich auf
eine andere ID derselben Recordfamilie. Eine Nachfolge ist bidirektional,
kreisfrei und genau 1:1. Der neue Record verweist beim initialen Event auf den
bereits existierenden Vorgänger; anschließend wechselt der Vorgänger in
derselben Transaktion auf seinen Familienterminalstatus und verweist zurück:
`retired` für REQ/CTRL/PROFILE/ROLE/COMP/DATA/FLOW, `closed` für RISK,
`expired` für GATE sowie `revoked|expired` für EXC. Ein RISK mit Nachfolger
darf nicht wieder geöffnet, ein GATE mit Nachfolger nicht wieder auf `red`
gesetzt werden. Der `baseCommit` des initialen Nachfolger-EVT muss ein
Git-Nachfolger des letzten Vorgänger-EVT-`baseCommit` sein. REV und EVID verwenden
stattdessen ihre bereits spezialisierten Supersession-Felder. Ein Record ohne
Nachfolger führt beide generischen Felder als `null`; eine einseitige oder
familienfremde Nachfolge ist ungültig.

Genau zwei Lifecycle-Schreibausnahmen bestehen: Nur das `fromStatus: null`-
Event des Nachfolgers darf `supersedesRecordRef` einmal von `null` auf den
Vorgänger setzen. Nur der unmittelbar danach folgende Familienterminal-
Übergang des Vorgängers darf `supersededByRecordRef` einmal von `null` auf den
Nachfolger setzen. Während des ersten Events wird die reziproke
Cross-Reference-Prüfung bis zum zweiten Event derselben Transaktion
aufgeschoben; am Transaktionsende müssen beide Seiten exakt passen. Danach
sind beide Felder unveränderlich.

`exceptionProvenanceRefs` wird nicht frei behauptet. Der Validator berechnet
für jeden Replayzustand den kleinsten Fixpunkt aus allen direkten
Governance-Referenzen eines Records: Jede direkt referenzierte genehmigte EXC
und die gespeicherte Provenienz jedes referenzierten Records wird vereinigt.
Bei EXC selbst wird die eigene ID nicht aufgenommen. Ein einmal in einem
Record gespeicherter Provenienzeintrag ist monoton und darf durch Widerruf,
Ablauf, Amendment oder Supersession der Ausnahme nicht entfernt werden.
Der Übergang einer referenzierten EXC zu `approved` ist nur in einer atomaren
Transaktion gültig, die alle direkt und transitiv abhängigen Records per
zulässigem Event um die neue Provenienz ergänzt; andernfalls schlägt die
Genehmigung fehl.
Capture-/Review-/Gate-Historie behält damit sichtbar, dass sie unter einer
Ausnahme entstand. Ein No-Waiver-Gate muss selbst und über den vollständigen
REQ-/CTRL-/PROFILE-/ROLE-/COMP-/RISK-/DATA-/FLOW-/GATE-/REV-/EVID-/EXC-
Referenzgraphen eine leere Provenienz besitzen; andernfalls bleibt es `red`.

Formale ID-Patterns:

| Familie | Pattern |
|---|---|
| Produkt | `^(?:D|C|X|U)[0-9]{2}$`, `^K[1-8]$`, `^L0[1-9]$`, `^H[1-8]$`, `^O(?:0[1-9]|10)$`, `^WV0[1-6]$` |
| REQ | `^REQ-(?:[0-9]{3}|HR-[0-9]{2}|GOV-[0-9]{3})$` |
| CTRL/RISK/DATA/FLOW/GATE/REV/EVID/PROFILE/ROLE/COMP | `^(?:CTRL|RISK|DATA|FLOW|GATE|REV|EVID|PROFILE|ROLE|COMP)-[A-Z0-9]+(?:-[A-Z0-9]+)*$` |
| EXC | `^EXC-[0-9]{3}$` |
| EVT | `^EVT-[0-9]{6}$` |
| KEY | `^KEY-[A-Z0-9]+(?:-[A-Z0-9]+)*$` |
| KEYREV | `^KEYREV-[0-9]{6}$` |
| RECEIPT | `^RECEIPT-[0-9]{12}$` |
| POLICYTRANS | `^POLICYTRANS-[0-9]{12}$` |

Referenzfelder besitzen feste Zielmengen:

| Feldfamilie | Zulässiges Ziel |
|---|---|
| `productDecisionRefs` | bestehender Produktkanon D/C/X/U/K/L/H/O/WV |
| `requirementRefs` | REQ |
| `controlRefs`, `compensatingControlRefs` | CTRL |
| `riskRefs` | RISK |
| `dataRefs` | DATA |
| `componentRefs`, `sourceComponentRef`, `targetComponentRef` | COMP |
| `profileRefs` | PROFILE |
| `roleRefs`, `*ByRole`, `*Role`, `*RoleRefs`, `independentFrom`, `separationFromRoleRefs` | ROLE |
| `gateRefs`, `blockedGateRefs` | GATE |
| `reviewRefs`, `supersedesReviewRef`, `supersededByReviewRef` | REV |
| `evidenceRefs`, `evidenceSubjectRefs`, `requiredEvidenceRefs`, `qualificationEvidenceRefs`, `resolutionEvidenceRefs`, `assignmentEvidenceRef`, `reasoningApprovalEvidenceRef`, `externalReviewEvidenceRefs`, `sanitizationEvidenceRef`, `dueDiligenceEvidenceRef`, `egressDispatcherContractEvidenceRef`, `networkEnforcementEvidenceRef`, `installationChangePlanEvidenceRef`, `operatorSignatureEvidenceRef`, `promotionEvidenceRef` | EVID |
| `derivationRefs` | jeder statusbehaftete Governance-Record aus REQ, CTRL, PROFILE, ROLE, COMP, RISK, DATA, FLOW, GATE, REV, EVID oder EXC; niemals EVT |
| `exceptionRefs` | EXC |
| `subjectIds`, `scopeIds` | jede existierende Produkt- oder Governance-ID außer inline Findings |
| `invariantRefs` | REQ, CTRL oder GATE |
| `supersedesEvidenceRef`, `supersededByEvidenceRef` | EVID |
| `supersedesRecordRef`, `supersededByRecordRef` | dieselbe Recordfamilie wie der Quellrecord, ausgenommen REV/EVID/EVT |
| `attestationKeyRefs`, `keyRef`, `operatorKeyRef`, `recoveryRootKeyRef`, `orchestratorKeyRef`, `validatorControllerKeyRef`, `oldControllerKeyRef`, `instanceKeyRef`, `witnessKeyRef` | vorhandener, für den jeweiligen Vertrag extern oder im Replay verankerter `KEY-*`-Eintrag |
| `recordRef` | jeder statusbehaftete Governance-Record außer EVT |
| `operatorAttestationRef` | kanonischer detached Pfad `docs/governance/attestations/<EVT-ID>--approver--<KEY-ID>.json`; EVT, Purpose und Key müssen zur Reasoning-Approval-EVID passen |

`implementationPaths`, `subjectPaths` und `artifactPathOrUri` sind keine
ID-Referenzen. Repository-Pfade folgen der Source-Pfadregel; externe
Artefakt-URIs sind nur für EVID zulässig und müssen zugriffskontrolliert sein.
Systemkomponenten werden ausschließlich über COMP-Records referenziert;
Freitext-, Host-, Provider-, IP-, Tenant- oder Clientbezeichner sind in
Component-Referenzfeldern ungültig. Cross-References müssen existieren und –
bei wechselseitigen Beziehungen – auf beiden Seiten übereinstimmen.

Produkt-IDs werden nicht mit einem zweiten manuellen Statusfeld dupliziert.
Der Validator erzeugt zur Laufzeit einen read-only `productDecisionIndex` aus
den bestehenden Kanonquellen:

| Familie | Kanonquelle | Statusableitung |
|---|---|---|
| D | `src/lib/concept/decisions.ts#DECISIONS` | Feld `lock`, abgeglichen mit `CANONICAL_DECISION_LOCKS` |
| C | `src/lib/concept/freigabe.ts#C_GESETZT` | Konstante `gesetzt` |
| X | `src/lib/concept/freigabe.ts#X_KATALOG` | `X_STATUS.stand` plus Zeilenfeld `kategorie` |
| U | `src/lib/concept/freigabe.ts#U_GESETZT` | Konstante `gesetzt` |
| K | `src/lib/concept/kozyrev-labor.ts#KOZYREV_OPTIONAL` | Feld `lock` |
| L | `src/lib/concept/lovable-nutzen.ts#LOVABLE_NUTZEN` | Feld `urteil` |
| H | `src/lib/concept/standalone.ts#HYBRID_ALTERNATIVEN` | Feld `lock` |
| O | `src/lib/concept/offen.ts#OFFEN` | Felder `lage` und `gruppe` |
| WV | `src/lib/concept/wiedervorlage.ts#WIEDERVORLAGE` | Konstante `wiedervorlage` plus `phase` und `wann` |

Der Index enthält intern genau `id`, `sourcePath`, `exportName` und den
abgeleiteten Status. Er wird nicht gespeichert. Jede `productDecisionRef` wird
gegen ihn aufgelöst; der Coverage-Bericht nennt Quelle und aktuellen Status
direkt aus dem Produktkanon.

### 12.1 Requirements, Controls, Profile, Rollen und Komponenten

Ein REQ-Record im Traceability-Register enthält zusätzlich die Pflichtfelder
`sourceQuote: string`, `sourceQuoteSourceRef: string`,
`sourceQuoteSha256: string`, `normalizedRequirement: string`,
`productDecisionRefs: string[]`, `profileRefs: string[]`,
`dataRefs: string[]`, `componentRefs: string[]`, `roleRefs: string[]`,
`controlRefs: string[]`, `riskRefs: string[]`, `gateRefs: string[]`,
`verificationMethod: string`, `evidenceRefs: string[]` und
`acceptanceCriteria: string[]` mit mindestens einem Eintrag. Nur
`productDecisionRefs`, `profileRefs`, `dataRefs`, `componentRefs`, `roleRefs`,
`controlRefs`, `riskRefs` und `evidenceRefs` dürfen bei `proposed` leer sein;
ein `approved`-REQ benötigt mindestens ein Gate und einen Control.

`sourceQuoteSourceRef` ist exakt ein in `sourceRefs` vorhandener
`repo:<pfad>#L<start>-L<ende>`-Locator. Der Validator prüft vorhandene
Zeilengrenzen, liest den Git-Blob aus dem Ziel-/`--head`-Tree des erzeugenden
oder ändernden EVT, normalisiert nur
Zeilenenden auf LF und verlangt Bytegleichheit des vollständigen Ausschnitts
mit `sourceQuote` ohne angehängten Schlusszeilenumbruch. `sourceQuoteSha256`
ist SHA-256 über genau diese UTF-8-Bytes. Freie Paraphrasen stehen
ausschließlich in `normalizedRequirement`; Quote, Locator und Digest können
nicht unabhängig voneinander geändert werden.
Da ein EVT-Commit nach Abschnitt 12.5 keine Fachquelle ändern darf, muss der
Zielblob bereits im Basiscommit vorhanden und bytegleich sein. Source- und
REQ-Änderungen werden deshalb bewusst in zwei Commits getrennt: zuerst die
fachlich reviewte Quelle, danach der reine Governance-Event.

Ein CTRL-Record enthält zusätzlich die Pflichtfelder
`controlType: "technical" | "organizational" | "mixed"`, `objective: string`,
`requirementRefs: string[]`, `riskRefs: string[]`, `profileRefs: string[]`,
`implementationPaths: string[]`, `verificationMethod: string`,
`evidenceRefs: string[]`, `failureBehavior: string` und `gateRefs: string[]`.
Requirements und Gates enthalten mindestens je einen Eintrag. Implementation
und Evidenz dürfen nur bei `proposed` leer sein; `verified` benötigt beides.

Ein PROFILE-Record enthält zusätzlich die Pflichtfelder `purpose: string`,
`maximumDataClass: "synthetic" | "public" | "control" | "art9"`,
`identityAuthority: "none" | "preview-gate" | "debian-local"`,
`allowedCapabilities: string[]`, `forbiddenCapabilities: string[]`,
`secretDataRefs: string[]`,
`serverAccessLevel: "none" | "read-only-audit" | "privileged-planned" |
"runtime-only"`, `requirementRefs: string[]` und `gateRefs: string[]`.
Purpose, mindestens eine verbotene Fähigkeit, Requirements und Gates sind
nie leer. `PROFILE-PREVIEW` darf weder `art9` noch `debian-local`,
`privileged-planned` oder produktive Secret-Referenzen verwenden.
`read-only-audit` bezeichnet ausschließlich den Forced-Command-Collector aus
Abschnitt 11 und niemals einen interaktiven SSH- oder Shellaccount.

Ein ROLE-Record enthält zusätzlich die Pflichtfelder `requiredHuman: boolean`,
`assigneeKind: "human-account" | "human-person" | "agent" | "service" |
"unassigned"`, `assigneeRef: string | null`,
`attestationKeyRefs: string[]`,
`operatorEpoch: integer | null`,
`qualificationRequirements: string[]`,
`qualificationEvidenceRefs: string[]` und
`separationFromRoleRefs: string[]`. Bei `unassigned` sind Kind und Status
`unassigned`, `assigneeRef` ist `null` und Qualifikationsevidenz leer. Bei
`unassigned` sind auch `attestationKeyRefs` leer. Bei `assigned` sind
`assigneeRef` und mindestens ein im Trust-Root-Register aktiver,
rollen-/assigneegebundener `attestationKeyRef` gesetzt. Eine Rolle mit `requiredHuman: true`
akzeptiert nur `human-account` oder `human-person`; sobald
`qualificationRequirements` nichtleer ist, benötigt jedes grüne Gate mit
dieser Rolle mindestens eine verifizierte Qualifikationsevidenz. Ein Gate darf
getrennte Rollen gemeinsam als Verifier oder Approver verlangen und muss dies
für unabhängige Reviews sogar tun. Verboten ist, dass zwei für denselben Scope
getrennte Rollen nach Auflösung des Rollenregisters dieselbe `assigneeRef`
besitzen. Der Validator enthält hierfür einen negativen Test mit identischem
Assignee und einen positiven Test mit zwei verschiedenen Assignees.

Nur `ROLE-OPERATOR` besitzt eine positive `operatorEpoch`, initial `1`; alle
anderen Rollen führen `null`. Handover und Recovery erhöhen sie exakt um eins.
Jedes normale EVT speichert die unmittelbar vor seinem Replay gültige Epoch.
Im atomaren Handover-/Recovery-Bündel tragen Gate-Resets die alte und der
abschließende ROLE-Wechsel die neue Epoch; danach ist ausschließlich die neue
Epoch gültig. Reviews, Evidenzen,
Ausnahmen, Risikoakzeptanzen und Gates wirken nur, wenn ihre autorisierenden
Events zur aktuellen Epoch gehören. Eine Epoch-Rotation entwertet sie als
aktive Freigabe ohne historische REV-/EVID-Records umzuschreiben.

Eine Trust-Root-Ergänzung ist nur zusammen mit dem EVT zulässig, das dieselbe
Rolle erstmalig zuweist, per Handover, Recovery oder Custodian-Rotation rotiert
oder einen Schlüssel widerruft. Der Event-Envelope bindet den vollständigen
neuen Public-Key-Eintrag. Der neue Schlüssel darf dieses Ereignis nicht selbst
autorisieren. Der eingehende Operator-Key wird beim geplanten Handover durch
ausgehenden Operator und Offline-Recovery-Root, bei Recovery vor Pilot durch
Offline-Recovery-Root und nach erstmaligem Pilot-Green zusätzlich durch beide
Custodians autorisiert; in allen Fällen attestiert der eingehende Operator
separat die Schlüsselannahme, ohne damit die alte Autorisierungsschwelle zu
erfüllen. Dadurch ist `trust-roots.json` eine streng aus ROLE-Ereignissen
abgeleitete, append-only Verifikationsquelle. Einzige Bootstrap-Ausnahme ist
der in Abschnitt 12.5 exakt festgelegte EVT-000001-Delta aus initialem
Operator- und Recovery-Root-Key; beide externen Pins und beide Signaturen des
Pre-Ledger-Bundles müssen vor dessen Annahme stimmen.

Ein COMP-Record enthält zusätzlich die Pflichtfelder
`componentKind: "browser" | "edge" | "control-plane" | "data-store" |
"compute-worker" | "identity" | "backup" | "export" | "delete"`,
`trustZone: "client" | "public-edge" | "control" | "sensitive-data" |
"compute" | "backup" | "lifecycle"`, `profileRefs: string[]`,
`requirementRefs: string[]`, `controlRefs: string[]`,
`implementationPaths: string[]` und `gateRefs: string[]`. Profile,
Requirements, Controls und Gates sind nie leer. Implementation darf bei
`proposed` oder `approved` leer sein, bei `implemented` nicht. Ein COMP-Record
enthält keine Provider-, Host-, IP-, Tenant- oder Clientfelder; zusätzliche
Properties sind durch das Schema verboten.

REQ-, CTRL- und PROFILE-Beziehungen sind bidirektional: Nennt ein REQ einen
CTRL, muss der CTRL das REQ nennen. Dasselbe gilt für Profile, Risiken, Gates
und Evidenzen, soweit beide Seiten ein Referenzfeld besitzen. Gate-Approver und
-Verifier werden gegen das Rollenregister auf Besetzung, Human-Pflicht,
Qualifikation und Trennung geprüft.

### 12.2 Risiken

Ein RISK-Record enthält zusätzlich:

- `scenario: string`, `dataRefs: string[]`, `profileRefs: string[]`,
  `componentRefs: string[]`, `cause: string`, `threatOrFailure: string`;
- `likelihood`, `impactSecurity`, `impactPrivacy`, `impactOperations`,
  `impactProduct` jeweils als Enum `low`, `medium`, `high`, `critical`;
- `inherentRating` und `residualRating` mit demselben Enum sowie
  `controlRefs: string[]`;
- `treatment` mit `avoid`, `mitigate`, `transfer` oder `accept`;
- `dueOn: string`, `requirementRefs: string[]`, `gateRefs: string[]`;
- `acceptedByRole: string | null`, `acceptanceScope: string | null` und
  `acceptanceExpiresOn: string | null`.

Mindestens eine der drei Assetmengen `dataRefs`, `profileRefs` oder
`componentRefs` ist nichtleer. Requirements und Gates sind nie leer. Ein
`closed`-Risiko benötigt verifizierte Controls; ein `accepted`-Risiko benötigt
`treatment: "accept"`.

Die drei Akzeptanzfelder sind bei `treatment: "accept"` zwingend und sonst
`null`. Restrisikoakzeptanz darf ausschließlich `ROLE-OPERATOR` erklären und
ist ohne Scope oder Ablaufdatum ungültig.

### 12.3 Datenobjekte und Datenflüsse

Ein DATA-Record enthält zusätzlich:

- `dataSubjectGroups: string[]`, `fields: string[]`,
  `classification: "public" | "control" | "art9" | "secret" | "audit" |
  "backup"`, `purpose: string`;
- `plannedLegalBasis: string | null`, `controllerRole: string`,
  `processorNames: string[]`;
- `storageLocations: string[]`, `regions: string[]`,
  `encryptionAtRest: string`, `keyOwnerRole: string`;
- `accessRoleRefs: string[]`, `retentionRule: string`, `backupRule: string`,
  `exportRule: string`, `deletionRule: string`,
  `prohibitedDestinations: string[]` und `gateRefs: string[]`.

Purpose, Felder, Speicherorte, Regionen, verbotene Ziele und Gates sind nie
leer. Betroffenengruppen dürfen nur bei `public`, `secret`, `audit` oder
`backup` leer sein. `plannedLegalBasis` darf nur bei diesen vier Klassen
`null` sein. Controller, Key Owner und Access Roles werden gegen ROLE geprüft.

Ein FLOW-Record enthält zusätzlich:

- `dataRefs: string[]`, `purpose: string`, `sourceComponentRef: string`,
  `targetComponentRef: string`;
- `trustBoundary: string`, `profileRefs: string[]`,
  `transportProtection: string`;
- `authentication: string`, `authorization: string`, `loggingRule: string`;
- `processorNames: string[]`, `regionPath: string[]`,
  `controlRefs: string[]`, `riskRefs: string[]` und `gateRefs: string[]`.

Data, Zweck, Trust Boundary, Profile, Regionen, Controls, Risiken und Gates
sind nie leer. Source und Target werden gegen das COMP-Register aufgelöst.
Bei `active` dürfen Transport,
Authentifizierung oder Autorisierung nicht `planned`, `none` oder leer sein.

Eine als geplant geführte Rechtsgrundlage ist keine Legal-Freigabe. Ein
Art.-9-Datenobjekt oder -Flow ohne Retention, Löschweg, Key Owner,
Privacy-/Legal-Gate und verbotene Ziele ist ungültig.

### 12.4 Gates, Reviews, Evidenz und Ausnahmen

Ein GATE-Record enthält zusätzlich:

- `entryCriteria: string[]`, `exitCriteria: string[]`,
  `requiredEvidenceRefs: string[]` jeweils mit mindestens einem Eintrag;
- `noWaiver: boolean`, `verifierRoleRefs: string[]`,
  `approverRoleRefs: string[]`, beide nie leer;
- `baselineCommit: string | null`, `reviewRefs: string[]`,
  `exceptionRefs: string[]` und `expiresOn: string | null`.

Bei `red` oder `amber` darf `baselineCommit` `null` sein. `green` verlangt
vollständige Baseline, mindestens eine genehmigte Review, ausschließlich
verifizierte Pflichtevidenzen, besetzte qualifizierte Verifier/Approver und
kein abgelaufenes Datum. Die autorisierenden EVT sämtlicher Reviews,
Pflichtevidenzen, Risikoakzeptanzen und der Gate-Freigabe müssen außerdem zur
aktuellen `ROLE-OPERATOR.operatorEpoch` gehören; ältere Epochen bleiben
Historie, sind aber keine aktive Stütze. Bei REV/EVID umfasst dies sämtliche
für den aktiven Zustand erforderlichen Creation-, Capture-/Execution- und
Decision-/Verification-EVT, nicht nur den letzten Statuswechsel.
`exceptionRefs` muss bei
`noWaiver: true` leer sein.
Zusätzlich muss die in Abschnitt 12 berechnete transitive
`exceptionProvenanceRefs`-Menge des Gates und jedes über Requirements,
Controls, Profile, Rollen, Komponenten, Risiken, Datenobjekte, Flows,
Hilfsgates, Reviews, Evidenzen oder Ausnahmen erreichbaren Records leer sein.
Der Validator traversiert dieselbe vollständige Typmenge wie
`derivationRefs` bis zum Fixpunkt; eine direkte Leerprüfung von
`exceptionRefs` genügt ausdrücklich nicht.

Ein REV-Record enthält zusätzlich:

- `reviewType: "spec" | "quality-security" | "final" | "operator" |
  "privacy" | "legal" | "pentest" | "hardware" | "a11y-claims"`;
- `subjectIds: string[]`, `subjectPaths: string[]`, `scope: string`,
  `evidenceSubjectRefs: string[]`, `reviewerRole: string`,
  `independentFrom: string[]`;
- `reviewerAssigneeSnapshot: string | null`,
  `independentAssigneeSnapshots: string[]`,
  `subjectActorSnapshots: object[]`;
- `reviewerExecution: "human" | "internal-agent"`,
  `modelName: string | null`,
  `reasoningLevel: "medium" | "high" | "xhigh" | "max" | "ultra" | null`,
  `promptDigest: string | null` mit 64 hexadezimalen Zeichen,
  `reasoningApprovalEvidenceRef: string | null`,
  `externalReviewEvidenceRefs: string[]`;
- `baselineCommit: string`,
  `createdEpoch: integer`, `decisionEpoch: integer | null`,
  `verdict: "approved" | "changes-required" | "rejected" | null`,
  `findings: object[]`, `evidenceRefs: string[]`;
- `approvedByRole: string | null`, `performedAt: string | null` und
  `approvedByAssigneeSnapshot: string | null`, `expiresOn: string | null`,
  `supersedesReviewRef: string | null`,
  `supersededByReviewRef: string | null` und
  `supersededFromStatus: "approved" | "changes-required" | null` und
  `findingResolutions: object[]`.

Mindestens eine der Mengen `subjectIds` oder `subjectPaths` ist nichtleer.
Subject-Pfade existieren in der Review-Baseline. Scope und sämtliche
Assignee-Snapshots sind nichtleere Strings, sobald sie gesetzt sind.
`createdEpoch` wird beim `null→requested`-Event aus der aktuellen Operator-
Epoch gesetzt. `decisionEpoch` ist bei `requested` `null`; der Übergang zu
`approved` oder `changes-required` ist nur innerhalb derselben weiterhin
aktuellen Epoch zulässig und setzt `decisionEpoch` auf denselben Wert. Ein
Epochwechsel kann eine alte angeforderte Review daher niemals nachträglich
aktivieren.

`reviewerExecution: "human"` verlangt Modell, Reasoning, Prompt-Digest und
Reasoning-Freigabe als `null`. `internal-agent` verlangt
Modell, beabsichtigte Reasoning-Stufe, Prompt-Digest und eine vor
Taskbeginn und vor `performedAt` erzeugte `reasoning-approval`-EVID in
`reasoningApprovalEvidenceRef`. `externalReviewEvidenceRefs` ist bei beiden
Ausführungsarten ein eindeutiges Array; jeder Eintrag ist eine vom lokalen
Runner erfasste `external-model-output`-EVID. Sie kann eine Review informieren,
aber weder Reviewer- noch Approver-Snapshot ersetzen.

Die Reasoning-Approval-Evidenz ist vom Operator kryptografisch attestiert,
existiert vor Taskbeginn und bindet Task-/Review-Scope, Modell, bisherige und
genehmigte beabsichtigte Stufe, Freigabezeit und Ablauf. Sie behauptet nicht,
die UI-Einstellung technisch gemessen zu haben. Bei Modell-, Scope- oder
Stufenwechsel ist eine neue Evidenz erforderlich. Alle Preflight-Evidenzen
stehen zusätzlich in `evidenceRefs`.

Jeder Subject-Actor-Snapshot besitzt ausschließlich `subjectRef: string`,
`roleRef: string`, `assigneeRef: string` und `assignmentEvidenceRef: string`.
`subjectRef` ist entweder eine ID aus `subjectIds` oder
`path:<repo-relative-subjectPath>`. Jeder fachliche Subject besitzt genau einen
primären Snapshot, weitere oder fremde Subjects sind verboten. Die
Assignment-Evidenz ist zum Reviewzeitpunkt `captured` oder `verified` und
belegt Taskübergabe beziehungsweise Autorenschaft. Damit wird nicht
`ownerRole`, sondern der tatsächliche Implementer oder Autor historisch
festgehalten. Jede `assignmentEvidenceRef` muss zusätzlich in den
`evidenceRefs` derselben Review stehen. `evidenceSubjectRefs` ist eine
eindeutige Teilmenge von `evidenceRefs` und darf leer sein, solange die Review
keine EVID selbst verifiziert, invalidiert oder supersediert.

Jedes inline Finding besitzt ausschließlich die Pflichtfelder
`findingId: string` mit Pattern `^F-[A-Z0-9]+(?:-[A-Z0-9]+)*$`,
`priority: "P0" | "P1" | "P2" | "P3"`, `assertion: string`,
`evidencePath: string`, `lineStart: integer | null`,
`lineEnd: integer | null`, `scenario: string`, `invariantRefs: string[]`,
`correction: string`, `verificationTest: string`,
`confidence: "low" | "medium" | "high"`. Linien sind gemeinsam `null` oder
positive Ganzzahlen mit `lineEnd >= lineStart`. Finding-IDs sind über alle
Reviews eindeutig. Findings sind unveränderliche Befunde; ihr Zustand wird
nicht im Ursprungsrecord überschrieben.

Jede Finding-Resolution besitzt ausschließlich die Pflichtfelder
`findingRef: string` im Format `<REV-ID>#<findingId>`,
`disposition: "resolved" | "dismissed"`, `resolution: string`,
`resolutionEvidenceRefs: string[]`, `dismissedByRole: string | null` und
`dismissedByAssigneeSnapshot: string | null`. Sie darf nur in einer anderen,
neueren Review stehen, deren `supersedesReviewRef` auf die Ursprungsreview oder
eine lückenlose Nachfolgerkette zurückführt. Subject-IDs, Subject-Pfade und
Scope sind identisch; die neue Baseline ist ein anderer, per
`git merge-base --is-ancestor` nachgewiesener Nachfolger der alten Baseline.
Der neue Reviewer-Assignee unterscheidet sich von allen gespeicherten
Subject-Actor-Assignees der Ursprungsreview. Evidenz-Subjects sind hiervon
getrennt: `evidenceSubjectRefs` darf neue Korrekturevidenzen enthalten und wird
bei der Gleichheitsprüfung der fachlichen Subjects nicht verglichen.

`resolved` verlangt mindestens eine `captured` oder `verified`, scope- und
baselinegebundene Korrekturevidenz; Dismissal-Felder sind `null`. `dismissed`
verlangt dieselbe Evidenz, einen nichtleeren Grund, exakt die für den
Reviewtyp vorgeschriebene fachliche Reviewerrolle und deren historischen
Assignee-Snapshot. Bei P0/P1 muss die Nachfolgerreview außerdem genehmigt und
separat durch `ROLE-OPERATOR` attestiert sein. Ein Finding darf in der aktiven Reviewkette
genau einmal aufgelöst werden. Ein Review mit Verdict `approved` darf keine
neuen P0–P2-Findings enthalten und muss alle noch offenen P0–P2-Findings seiner
Supersede-Kette mit gültigen Finding-Resolutions schließen.

Nach Genehmigung der Re-Review wechseln ihre Capture-Evidenzen über dieselbe
zweistufige Regel zu `verified`. Für ein grünes Gate gilt eine Finding-
Resolution erst dann als geschlossen, wenn alle ihre Evidenzen `verified`
sind; dadurch entsteht kein Review/Evidenz-Kreis.

Scope und Baseline jeder Resolutionsevidenz entsprechen exakt der neuen
Re-Review. `dismissedByAssigneeSnapshot` entspricht dem fachlichen
Reviewer-Snapshot der Nachfolgerreview und unterscheidet sich von allen
Subject-Actor-Assignees der Ursprungsreview. Die Re-Review besitzt
denselben `reviewType` wie die Ursprungsreview. Selbstreferenzen oder
sachfremde Finding-Refs sind ungültig.

Bei einer agentisch besetzten Reviewerrolle sind die zur
`reviewerExecution` passenden Modell-, Reasoning-, Prompt- und
Preflight-Felder zwingend; bei einer menschlichen Rolle sind sie `null`.
Bei Abschluss werden `reviewerAssigneeSnapshot`,
`independentAssigneeSnapshots`, `subjectActorSnapshots` und gegebenenfalls
`approvedByAssigneeSnapshot` aus dem zu diesem Zeitpunkt gültigen
Rollenregister kopiert. `independentAssigneeSnapshots` ist positionsgleich zu
`independentFrom`. Der Reviewer-Snapshot muss sich von jedem Independent- und
Subject-Actor-Snapshot unterscheiden. Die Snapshots bleiben auch nach einer späteren
Rollenumbesetzung unverändert und sind für historische Unabhängigkeitsprüfungen
maßgeblich.

Der Schema-Zustandsautomat ist verbindlich:

- `requested` verlangt Verdict, Zeitpunkt, Approver, Reviewer-/Approver-
  Snapshots, beide Supersede-Referenzen und `supersededFromStatus` als `null`, leere Independent- und
  Subject-Actor-Arrays sowie leere Findings und Finding-Resolutions;
  `createdEpoch` ist aktuell und `decisionEpoch` `null`;
  `evidenceRefs` enthält ausschließlich die nach Ausführungsart erforderliche
  Reasoning-Approval und bereits erfasste externe Output-Evidenzen;
- `changes-required` verlangt Verdict `changes-required` oder `rejected`,
  Zeitpunkt, Reviewer-/Independent-/Subject-Actor-Snapshots, mindestens eine
  `captured` oder `verified` Evidenz und mindestens ein Finding;
  Creation-/Decision-Epoch sind identisch und aktuell;
  `approvedByRole`, Approver-Snapshot und `supersededByReviewRef` sind `null`;
  `supersededFromStatus` ist `null`;
- `approved` verlangt Verdict `approved`, Zeitpunkt, Evidenz und einen
  Reviewer-/Independent-/Subject-Actor-Snapshot, mindestens eine Evidenz und einen
  besetzten `approvedByRole` samt Snapshot; alle referenzierten Evidenzen sind
  `captured` oder `verified`, niemals `expected`, `invalidated` oder
  `superseded`; `supersededByReviewRef` und `supersededFromStatus` sind `null`;
  Creation-/Decision-Epoch sind identisch und aktuell;
- `superseded` verlangt eine existierende neuere Review in
  `supersededByReviewRef`; diese verweist über `supersedesReviewRef` zurück und
  prüft identische Subjects, Scope und Reviewtyp auf einer anderen, per
  `git merge-base --is-ancestor` nachgewiesenen Nachfolger-Baseline. Beide
  Reviews dürfen weder sich selbst noch einen Kreis referenzieren.
  `supersededFromStatus` nennt den unmittelbar vorherigen Zustand. Der gesamte
  Payload muss weiterhin dessen vollständige `approved`- beziehungsweise
  `changes-required`-Bedingungen erfüllen; nur `status`,
  `supersededFromStatus` und `supersededByReviewRef` dürfen sich beim Übergang
  ändern. Diese historischen Vorzustandsbedingungen werden gegen die im alten
  Record unverändert gespeicherte `createdEpoch`/`decisionEpoch` und die damals
  gültigen Rollen-Snapshots geprüft; die sonst für eine aktive
  `approved`-/`changes-required`-Review geltende Forderung nach aktueller Epoch
  wird auf den Vorgänger nicht erneut angewendet. Nur die neue Nachfolgerreview
  muss vollständig in der aktuellen Epoch erzeugt und entschieden sein.
  Supersession ändert die alte Epoch nicht, macht den Vorgänger niemals wieder
  gatewirksam und erlaubt keine spätere Reaktivierung.
  In einer atomaren Transaktion setzt zuerst deren
  `requested→approved|changes-required`-Event einmalig
  `supersedesReviewRef`, anschließend der alte Supersession-Event die
  reziproke Referenz; nur zwischen diesen beiden Events ist die Rückkante
  aufgeschoben.
  Eine REV darf nie direkt als `superseded` angelegt werden.

Nur `status: "approved"` und `verdict: "approved"` kann ein Gate speisen. Nur
`ROLE-OPERATOR` kann eine Betreiber-Review formal genehmigen. Eine genehmigte
Review mit einem `expiresOn` vor dem Validierungsdatum bleibt historische
Evidenz, darf aber kein grünes Gate speisen.

Ein EVID-Record enthält zusätzlich:

- `evidenceType: "command-output" | "test-report" | "design-commit" |
  "review-report" | "approval-record" | "audit-artifact" |
  "qualification" | "reasoning-approval" | "collector-contract" |
  "network-enforcement-verification" | "egress-dispatcher-contract" |
  "validator-promotion-request" |
  "external-model-output" | "provider-due-diligence" |
  "sanitization-report"`;
- `artifactPathOrUri: string | null`, `sha256: string | null` mit 64
  hexadezimalen Zeichen, `producerRole: string`,
  `producerAssigneeSnapshot: string | null`;
- `producedAt: string | null`, `baselineCommit: string | null`,
  `captureBaseCommit: string | null`,
  `subjectIds: string[]`, `subjectPaths: string[]`,
  `subjectManifestPath: string | null`, `subjectManifestSha256: string | null`,
  `scope: string`, `command: string`, `result: string | null`;
- `derivationRefs: string[]`, `inputManifestPath: string | null`,
  `inputManifestSha256: string | null`;
- `governanceChangeDigests: string[]` aus eindeutigen SHA-256-Werten;
- `reasoningApproval: object | null`, `collectorContract: object | null`,
  `networkEnforcementVerification: object | null`,
  `egressDispatcherContract: object | null`,
  `externalModelOutput: object | null`,
  `providerDueDiligence: object | null`,
  `sanitizationReport: object | null`;
- `retentionRule: string`, `verifiedByRole: string | null` und
  `verifiedByAssigneeSnapshot: string | null`, `reviewRefs: string[]`,
  `stateReason: string | null`, `supersedesEvidenceRef: string | null` und
  `supersededByEvidenceRef: string | null`,
  `supersededFromStatus: "captured" | "verified" | "invalidated" | null`,
  `createdEpoch: integer`, `captureEpoch: integer | null` und
  `decisionEpoch: integer | null`.

Der Evidenz-Zustandsautomat ist verbindlich:

- `expected`: Artefakt, SHA-256, Zeitpunkt, `baselineCommit`,
  `captureBaseCommit`, Subject- und Inputmanifest, Ergebnis, spezialisierte
  Payloads, Verifier,
  Producer-/Verifier-Snapshot, State-Reason, Vorgänger und Nachfolger sind `null`;
  Reviewrefs sind leer; `createdEpoch` ist aktuell, Capture-/Decision-Epoch
  sind `null`;
- `captured`: Artefakt, SHA-256, Zeitpunkt, vollständige Subject-Baseline,
  `captureBaseCommit`, beide Manifestpfade/-hashes, Ergebnis sowie Producer-
  Snapshot sind gesetzt; abhängig vom `evidenceType` ist exakt das unten
  vorgeschriebene spezialisierte Objekt gesetzt, alle anderen bleiben `null`;
  Verifier, Verifier-Snapshot,
  State-Reason, Vorgänger, Nachfolger und `supersededFromStatus` sind `null`;
  `createdEpoch` und `captureEpoch` sind identisch und aktuell,
  `decisionEpoch` ist `null`;
- `verified`: alle Artefakt- und Capture-Bindungsfelder, ein besetzter und erforderlichenfalls vom
  Producer getrennter `verifiedByRole` samt historischem Assignee-Snapshot
  sowie mindestens eine genehmigte, nicht abgelaufene `reviewRef` sind
  gesetzt; `decisionEpoch` entspricht Creation, Capture und aktueller Epoch;
  State-Reason, Nachfolger und `supersededFromStatus` sind `null`;
  `supersedesEvidenceRef` darf ausschließlich als Teil der unten normierten
  Supersession gesetzt werden;
- `invalidated`: alle Artefakt- und Capture-Bindungsfelder, Verifier, genehmigte Review und eine
  nichtleere `stateReason` sind gesetzt; Creation, Capture und
  `decisionEpoch` sind identisch, Nachfolger und `supersededFromStatus` sind
  `null`;
- `superseded`: der vollständige vorherige `captured`-, `verified`- oder
  `invalidated`-Payload bleibt erhalten; ausschließlich Status,
  `supersededFromStatus`, nichtleere `stateReason` und eine existierende
  neuere EVID-ID in `supersededByEvidenceRef` kommen hinzu. Eine fehlende
  Verifier-/Reviewbelegung aus einem zuvor nur `captured` Record wird nicht
  nachträglich erfunden. Die historischen Vorstatusbedingungen werden gegen
  die unverändert gespeicherten Creation-/Capture-/Decision-Epochen und
  damaligen Rollen-Snapshots geprüft; ihre sonstige Aktualitätsforderung gilt
  nicht erneut für den Vorgänger. Nur die neue Nachfolger-EVID muss vollständig
  in der aktuellen Epoch erfasst und verifiziert sein. Der alte Record bleibt
  historisch und kann nie reaktiviert werden.

`producerRole`, `scope`, `command`, `derivationRefs`,
`governanceChangeDigests` und `retentionRule` bleiben in jedem Status Pflicht.
Mindestens eine der Mengen `subjectIds` oder `subjectPaths` ist nichtleer.
`baselineCommit` bezeichnet ausschließlich den fachlichen Commit, gegen den
Artefakt und Subjectmanifest erzeugt wurden. `captureBaseCommit` ist der
bereits existierende EVT-`baseCommit` von `null|expected→captured`; er ist
keine ID des entstehenden Capture-Commits und erzeugt daher keine
Git-Selbstreferenz. Das Digest-Array darf leer
sein, solange die Evidenz keinen Governance-Event autorisiert. Sobald ein EVT
sie in `evidenceRefs` verwendet, muss sie den exakten `changeDigest` dieses
Events enthalten; ausgenommen ist ausschließlich der in Abschnitt 12.5
normierte eigene EVID-Lebenszyklus-Event. Da Scope, Baseline und Digests nach `captured` nicht mehr
per Amendment änderbar sind, ist die fachliche Evidenz unveränderlich an den
konkreten Recordwechsel gebunden. So kann ein Gate erwartete Evidenz
referenzieren, ohne ihre Existenz vorzutäuschen. Nur `verified` darf ein grünes
Gate speisen.

Bei `null→captured` werden `createdEpoch` und `captureEpoch` gemeinsam aus der
aktuellen Epoch gesetzt. `expected→captured` ist nur zulässig, wenn die
gespeicherte `createdEpoch` weiterhin aktuell ist; `captureEpoch` übernimmt
denselben Wert. `captured→verified|invalidated` verlangt ebenfalls eine
unveränderte aktuelle Creation-/Capture-Epoch und setzt `decisionEpoch`
identisch. Ein Epochwechsel verlangt deshalb neue REV- und EVID-IDs mit
vollständig neuer Capture-, Review- und Freigabekette. Alte Records dürfen in
der neuen Epoch ausschließlich historisch unverändert bleiben oder durch eine
vollständig in der neuen Epoch erzeugte Nachfolgerakte formal `superseded`
werden; ein Supersession-Event reaktiviert den Vorgänger nicht.

Das nach `subject-manifest.schema.json` validierte Subjectmanifest enthält
ausschließlich `schemaVersion`, `manifestId`, `evidenceRef`,
`baselineCommit`, `subjectIds`, `subjectPaths` und `entries`. IDs und Pfade
sind exakt die EVID-Felder; sie dürfen weder erweitert noch verkleinert
werden. Jeder sortierte Entry ist diskriminiert: Ein File-Entry enthält
ausschließlich `kind: "file"`, `path`, `fileMode: "100644"|"100755"` und
`sha256`; ein Record-Entry ausschließlich `kind: "record"`, `recordRef`,
`registerPath` und `recordSha256`; ein Product-Decision-Entry ausschließlich
`kind: "product-decision"`, `productDecisionRef`, `sourcePath`, `exportName`,
`sourceBlobSha256` und `derivedStatusSha256`. Für jede Product-ID berechnet der
Validator am `baselineCommit` den `productDecisionIndex`, liest den
Source-Blob aus diesem Tree und bildet `derivedStatusSha256` als SHA-256 der
RFC-8785-Darstellung von ausschließlich `{ "id", "sourcePath", "exportName",
"status" }`. Die vier Werte müssen bytegleich zum Indexeintrag sein; ein
manuell behaupteter oder aus dem aktuellen Working Tree gelesener Status ist
ungültig. Dateien werden aus dem
`baselineCommit`-Tree gelesen, Verzeichnisse vollständig rekursiv expandiert,
Symlinks und Submodule fail-closed abgewiesen; jeder Subjectpfad und jede
Subject-ID erscheint mit genau einem passenden File-, Record- oder
Product-Decision-Entry in der Coverage. Jede als Subject genannte Product-ID
verlangt exakt einen Product-Decision-Entry; fehlende, doppelte oder durch einen
File-/Record-Entry maskierte Produktentscheidungen sind ungültig. Zusätzliche
ungeprüfte, fehlende oder aus einer anderen Baseline stammende Subjects sind
ungültig.
Der kanonische Pfad ist
`docs/governance/manifests/<EVID-ID>--subject.json`.

Das davon getrennte, nach `input-manifest.schema.json` validierte
Ableitungsmanifest enthält
ausschließlich `schemaVersion`, `manifestId`, `evidenceRef`,
`subjectBaselineCommit`, `generatedAt` und `entries`. Jeder nach
`pathOrUri` sortierte `entries`-Eintrag enthält ausschließlich
`pathOrUri`, `fileMode: "100644"|"100755"|null`, `sha256`,
`dataClassification: "public"|"synthetic"|"sanitized-non-production"|
"internal-control"|"art9"|"secret"`, `derivationRefs` und die vollständigen
`exceptionProvenanceRefs`. Die Liste
ist vollständig; Duplikate, Globs, nicht revisionsfeste URIs und fehlende
rekursiv gelesene Inputs sind ungültig.
Repositorypfade verlangen einen Mode, revisionsfeste externe URIs zwingend
`fileMode: null`.
Der kanonische Pfad ist
`docs/governance/manifests/<EVID-ID>--inputs.json`.
Jeder Eintrag, dessen Inhalt aus einem Governance-Record entsteht oder dessen
Semantik verwendet, nennt diesen Record in `derivationRefs`; der Validator
löst dabei sämtliche oben erlaubten Recordfamilien auf. Capture übernimmt
monoton die Ausnahmeprovenienz aller Ableitungsrecords und ihrer transitiven
Referenzgraphen.
Eine unabhängige Review bestätigt Inputvollständigkeit und Erzeugungsweg;
Evidenz ohne verifiziertes Manifest darf kein No-Waiver-Gate speisen. Eine
neue EVID ohne Referenz auf tainted Inputs kann deren Provenienz somit nicht
waschen.

Bei `evidenceType: "reasoning-approval"` ist ausschließlich
`reasoningApproval` non-null und besitzt ausschließlich `taskScope`, `modelName`,
`previousReasoningLevel`, `approvedReasoningLevel`, `approvedAt`, `expiresAt`
und `operatorAttestationRef`; die sechs anderen Spezialobjekte sind `null`.
Das Capture-EVT dieser EVID enthält zwingend eine zusätzliche
`attestationPurpose: "approver"`-Signatur des aktuellen Operators; ist dieser
zugleich Akteur, bleiben Actor- und Approver-Envelope purpose- und
noncegetrennt.
Bei `collector-contract` ist ausschließlich `collectorContract`, bei
`network-enforcement-verification` ausschließlich
`networkEnforcementVerification`, bei
`egress-dispatcher-contract` ausschließlich `egressDispatcherContract`, bei
`external-model-output` ausschließlich `externalModelOutput` non-null. Bei
`provider-due-diligence` ist ausschließlich `providerDueDiligence`, bei
`sanitization-report` ausschließlich `sanitizationReport` non-null. Bei allen
anderen Evidenztypen sind alle sieben spezialisierten Objekte `null`.

`networkEnforcementVerification` ist nur bei
`evidenceType: "network-enforcement-verification"` non-null und besitzt nach
`network-enforcement-verification.schema.json` ausschließlich
`verificationId`, `dispatcherServiceIdentity`, `dispatcherImageDigest`,
`dispatcherBinarySha256`, `networkPolicySha256`, `tokenStorePolicySha256`,
`allowedEndpointIdentifierSha256`, `observedDnsPolicySha256`,
`allowedTransportProfileSha256s`,
`observedProxyPolicySha256`, `observedIpv4PolicySha256`,
`observedIpv6PolicySha256`, `deniedServiceIdentitiesSha256`,
`positiveTestSetSha256`, `bypassNegativeTestSetSha256`, `observedAt`,
`expiresAt`, `verifierRole`, `verifierAssigneeSnapshot` und `result: "passed"`.
Producer/Verifier sind von Runner und Dispatcher-Assignee getrennt. Das Objekt
besitzt selbst keine EVID-Referenz und kann daher weder sich selbst noch den
später erzeugten Dispatchervertrag referenzieren. Es muss bereits `verified`,
nicht abgelaufen, in derselben Baseline und demselben Scope liegen, bevor der
Vertrag erfasst wird; die Graphprüfung verbietet direkt und transitiv jeden
Zyklus.

`egressDispatcherContract` ist nur bei
`evidenceType: "egress-dispatcher-contract"` non-null und besitzt nach
`egress-dispatcher-contract.schema.json` ausschließlich `contractId`,
`dispatcherServiceIdentity`, `dispatcherImageDigest`,
`dispatcherBinarySha256`, `dispatcherKeyRef`, `transparencyLogId`,
`networkPolicySha256`, `tokenStorePolicySha256`,
`allowedEndpointIdentifierSha256`, `allowedMethods: ["POST"]`,
`allowedTransportProfileSha256s`,
`tokenConsumptionMode: "atomic-single-use-before-egress"`,
`maxReceiptAgeSeconds`, `bypassPaths: []`, `networkEnforcementEvidenceRef`,
`verifiedAt`, `expiresAt`, `contractCoreSha256` und `signature`. Der Contract-
Core ist die RFC-8785-Projektion aller Felder außer Core und Signatur; der
geprüfte Dispatcher-Key signiert exakt diesen Digest. Der referenzierte
Netzwerkbeleg muss exakt die oben geschlossene, bereits verifizierte
`network-enforcement-verification`-EVID sein und weist nach, dass
alle anderen Serviceidentitäten, Container, Benutzer und Hostprozesse am
Provider-Egress fail-closed gesperrt sind; DNS-/Proxy-/IPv4-/IPv6- und direkte
IP-Pfade gehören zur Policy. Nur der gehashte Dispatcher darf den exakt
gebundenen Endpoint mit der einzigen Methode erreichen. Sein geschützter
Tokenstore verbraucht Receipt-ID, Envelopehash und Token atomar vor dem ersten
Netzwerkbyte und lehnt Retry, Parallelverbrauch, abgelaufene Receipts sowie
einen anderen Endpoint ab. Contract-, Netzwerk- oder Binary-Digestabweichung,
ein nichtleeres `bypassPaths`, direkter Runner-/Host-Egress oder ein nur als
`audit-artifact` typisierter Beleg ist ungültig und hält alle betroffenen Gates
`red`.
`maxReceiptAgeSeconds` liegt zwischen 1 und 900; Contract-`expiresAt` liegt
nicht nach dem `expiresAt` des Netzwerkbelegs. Contract und Netzwerkbeleg haben
verschiedene EVID-IDs, identische Baseline/Subjects/Scope und der Beleg muss im
Vorgänger-Replayzustand bereits `verified` sein.
`allowedTransportProfileSha256s` ist in beiden Objekten dieselbe sortierte,
duplikatfreie, non-empty Liste bereits geprüfter Profil-Vollhashes. Jeder
Request-, Lease-, Attestations- und Transportbeleg muss exakt einen Listeneintrag
verwenden; ein nachträglich eingeführtes oder permissiveres Profil ist
ungültig.

`externalModelOutput` ist nur bei `evidenceType: "external-model-output"`
non-null und besitzt ausschließlich `providerName`, `endpointClass:
"public-cloud-api"|"enterprise-private"|"local-runtime"`, `modelVersion`,
`endpointIdentifierSha256`, `processingRegion`, `retentionPolicy`, `trainingUse:
"disabled"|"contractually-disabled"`, `inputArtifactSha256`,
`inputClassification: "public"|"synthetic"|"sanitized-non-production"`,
`sanitizerRole`, `sanitizerAssigneeSnapshot`, `sanitizationEvidenceRef`,
`dueDiligenceEvidenceRef`, `runnerRole: "ROLE-EXTERNAL-REVIEW-RUNNER"`,
`runnerAssigneeSnapshot`, `egressDispatcherContractEvidenceRef`,
`expectedEvidenceRecordSha256`, `requestDescriptorSha256`,
`providerApplicationRequestRef`, `providerApplicationRequestSha256`,
`providerRequestBodySha256`, `providerApplicationHeadersSha256`,
`transportProfileRef`, `transportProfileSha256`,
`providerResponseSha256`, `providerRequestIdSha256`, `requestReceiptId`,
`requestReceiptSha256`, `requestSentAt`, `responseReceivedAt`,
`dispatchAttestationRef`, `dispatchAttestationSha256`,
`egressEnforcementLeaseRef`, `egressEnforcementLeaseSha256`,
`egressTransportReceiptRef`, `egressTransportReceiptSha256`,
`wireRequestTranscriptSha256`, `tlsTranscriptSha256`,
`requestEnvelopeRef`, `requestEnvelopeSha256`, `responseEnvelopeRef` und
`responseEnvelopeSha256`. Due-Diligence, Sanitisierung und der Egress-
Dispatcher-Vertrag sind
nachweislich vor dem externen Preflight `verified`; der Runner attestiert nur
Reihenfolge, Transport und Bytecapture, niemals fachliche Richtigkeit oder eine
Revieweridentität.

Der Request-Envelope liegt kanonisch unter
`docs/governance/external-model/<EVID-ID>--request.json` und enthält
ausschließlich `schemaVersion`, `repositoryId`, `externalOutputEvidenceRef`, `providerName`,
`endpointClass`, `endpointIdentifierSha256`, `modelVersion`,
`processingRegion`, `retentionPolicy`, `trainingUse`, `inputArtifactSha256`,
`inputClassification`, `sanitizerRole`, `sanitizerAssigneeSnapshot`,
`dueDiligenceEvidenceRef`, `egressDispatcherContractEvidenceRef`,
`dueDiligenceVerificationEventHash`, `sanitizationEvidenceRef`,
`sanitizationVerificationEventHash`,
`egressDispatcherContractVerificationEventHash`,
`expectedEvidenceRecordSha256`, `subjectIds`, `subjectPaths`, `scope`,
`command`, `providerApplicationRequestRef`, `providerApplicationRequestSha256`,
`providerRequestBodySha256`, `providerApplicationHeadersSha256`,
`transportProfileRef`, `transportProfileSha256`,
`allowedHeaderNames`, `authorizationCredentialSha256`,
`requestDescriptorSha256`, `preparedAt`, `runnerRole`,
`runnerAssigneeSnapshot`, `runnerKeyRef`, `nonce` und `signature`. Seine
Runner-Signatur bindet alle Felder außer `signature`. Die drei Eventhashes
müssen auf bereits extern quittierte `captured→verified`-Events der exakt
referenzierten DD-, Sanitization- und Egress-Dispatcher-Contract-EVID-Akten
zeigen.
`externalOutputEvidenceRef` bezeichnet eine schon in einem früher quittierten
Head vorhandene `expected`-EVID. `expectedEvidenceRecordSha256` ist ihr
vollständiger kanonischer Recordhash. `requestDescriptorSha256` ist der Hash
der RFC-8785-Projektion aus EVID-ID/-Recordhash, `subjectIds`, `subjectPaths`,
`scope`, `command`, Inputhash, Provider-/Endpoint-/Modellfeldern und den drei
Verification-Eventhashes sowie Application-Request-Ref/-Vollhash, Body-/
Application-Headerhash, Transportprofil-Ref/-Vollhash,
`allowedHeaderNames` und Credential-Digest. Eine spätere
Änderung auch nur eines dieser Felder macht Envelope und Folgekette stale.
`providerApplicationRequestRef` verweist auf ein verschlüsselt,
revisionsfest verwahrtes, RFC-8785-kanonisches JSON-Artefakt mit ausschließlich
`schemaVersion`, `method: "POST"`, `scheme: "https"`, `authority`,
`pathAndQuery`, `transportProfile: "http/1.1"|"h2"`,
`transportProfileRef`, `transportProfileSha256`, `streaming: false`,
`applicationHeaders`, `bodyBase64url` und `bodySha256`. Die nach Headername
sortierten Application-Header enthalten ausschließlich Namen aus dem
sortierten, schemafesten `allowedHeaderNames`: `accept`, `content-type`,
`authorization`, `idempotency-key` und providerpflichtige Versionsheader.
Alle Namen sind lowercase und eindeutig; jeder erlaubte Name erscheint genau
einmal oder wird durch das providerspezifische geschlossene Profil explizit
als optional ausgewiesen.
`Host`, Request-Line, HTTP/2-Pseudoheader, Framing- und Connection-Header sind
keine Application-Header, sondern werden transportprofilspezifisch im späteren
Wire-Transcript gebunden. Vollhash, Bodyhash und Application-Headerhash werden
getrennt neu berechnet. Der geheime Authorizationwert wird nie geloggt, sein
Digest ist jedoch in `authorizationCredentialSha256` gebunden; zusätzliche
Application-Body-/Header-/Query-Daten sind unzulässig.

Das revisionsfeste `transportProfileRef` liegt kanonisch unter
`docs/governance/transport-profiles/<profileId>.json`, erfüllt
`egress-transport-profile.schema.json` und enthält ausschließlich
`schemaVersion`, `profileId`, `kind: "http/1.1"|"h2"`,
`connectionReuse: false`, `singleRequest: true`, `streaming: false`,
`exactApplicationHeaderNames`, `orderedWireHeaderNames`,
`duplicateHeaderNamesAllowed: []`, `framingMode: "content-length"`,
`trailers: []`, `maxBodyBytes`, `tlsAlpn`, `http1` und `http2`. Genau eines der
beiden diskriminierten Spezialobjekte ist non-null. Jeder Headername ist
lowercase; `orderedWireHeaderNames` enthält jeden tatsächlich zulässigen
regulären Wire-Header genau einmal. Header, Trailer, Transfer-Encoding,
Connection-Reuse oder ein paralleler Request außerhalb dieses geschlossenen
Profils sind unzulässig.

Bei `kind: "http/1.1"` ist `tlsAlpn: "http/1.1"`; `http1` enthält
ausschließlich `protocolVersion: "HTTP/1.1"`, `requestTargetForm: "origin"`,
`hostHeaderSource: "authority"`, `contentLengthRequired: true`,
`connectionHeader: "close"`, `transferEncoding: null` und
`mandatoryHeaderOrder`. `mandatoryHeaderOrder` ist eine Teilfolge von
`orderedWireHeaderNames` und enthält exakt `host`, `content-length` und
`connection`. Bei `kind: "h2"` ist `tlsAlpn: "h2"`; `http2` enthält
ausschließlich `connectionMode: "fresh-exclusive"`, `connectionPreface:
"PRI * HTTP/2.0\\r\\n\\r\\nSM\\r\\n\\r\\n"`, `streamId: 1`,
`maxConcurrentStreams: 1`, `hpackDynamicTableSize: 0`, `hpackHuffman: false`,
`pseudoHeaderOrder: [":method",":scheme",":authority",":path"]`,
`clientSettings`, `serverSettingsPolicyRef`, `serverSettingsPolicySha256`,
`settingsAckRequired: true`
und `goawayAfterResponse: true`. `host`, `connection`, `transfer-encoding` und
andere HTTP/2-verbotene Header sind ausgeschlossen. Jeder Dispatch öffnet eine
frische TLS-/H2-Verbindung, verwendet ausschließlich Stream 1, setzt die HPACK-
Tabelle mit `SETTINGS_HEADER_TABLE_SIZE: 0` auf Größe null, setzt
`SETTINGS_MAX_CONCURRENT_STREAMS: 1` und `SETTINGS_ENABLE_PUSH: 0`, wartet vor
dem Requestheaderblock auf die zugehörigen ACKs, akzeptiert keinen fremden
Stream und schließt nach der Response. Der vollständige Connection-Preface-/SETTINGS-/ACK-Präfix wird im
Transportbeleg gebunden; es existiert keine frühere dynamische Tabellenhistorie.
`clientSettings` ist exakt die nach numerischer HTTP/2-Identifier sortierte
Liste dieser drei geschlossenen `{ "identifier", "value" }`-Objekte. Die
revisionsfeste Server-Settings-Policy ist über Ref und Vollhash gebunden und
weist zusätzliche, fehlende oder außerhalb ihrer exakten Wertebereiche liegende
Settings fail-closed ab.

Vor jedem Providerdispatch sendet der nicht umgehbare, extern nach
`egressDispatcherContractEvidenceRef` attestierte Egress-Dispatcher den Request-Envelope
an die Transparenzinstanz. Diese prüft, dass DD-, Sanitization- und
Egress-Dispatcher-Contract-Receipts im bisherigen Logpräfix liegen und erzeugt vor
Netzwerkversand einen `entryKind: "external-model-request-receipt"`-Eintrag.
Dessen spezifischer Payload enthält ausschließlich `requestReceiptId`,
`externalOutputEvidenceRef`, `expectedEvidenceRecordSha256`,
`requestDescriptorSha256`, `requestEnvelopeSha256`,
`providerApplicationRequestSha256`, `providerRequestBodySha256`,
`providerApplicationHeadersSha256`, `allowedHeaderNames`,
`transportProfileRef`, `transportProfileSha256`,
`authorizationCredentialSha256`,
`dueDiligenceAcceptanceReceiptId`, `sanitizationAcceptanceReceiptId`,
`egressDispatcherContractAcceptanceReceiptId`,
`dueDiligenceAcceptanceReceiptLogIndex`,
`sanitizationAcceptanceReceiptLogIndex`,
`egressDispatcherContractAcceptanceReceiptLogIndex`,
`preflightAcceptedAt`, `dispatchTokenSha256` und `expiresAt`. Das einmalige
Dispatch-Token ist an Requesthash und Frist gebunden; `preflightAcceptedAt` ist
bytegleich zum vertrauenswürdigen `loggedAt` des Eintrags. Netzwerkpolicy erlaubt
Provider-Egress ausschließlich diesem gehashten Dispatcher; er verweigert
Versand ohne gültiges, unverbrauchtes Token und exakt übereinstimmenden
Preflight-Receipt. Damit liegt ein extern signierter Zeitanker zwingend vor dem
physischen Request.

Der Receipt allein erlaubt noch keinen Versand. Erst nachdem er in einem
frischen Vollquorum-Checkpoint liegt, installiert der unabhängige Egress-
Enforcement-Monitor im getrennten Control Plane atomar eine unveränderliche,
pro Dispatch geschlossene Enforcement-Lease nach
`egress-enforcement-lease.schema.json`. Sie enthält ausschließlich
`schemaVersion`, `repositoryId`, `enforcementLeaseId`, `requestReceiptId`,
`requestReceiptSha256`, `requestCheckpointSha256`,
`requestCheckpointTreeSize`, `requestCheckpointIssuedAt`,
`dispatchTokenSha256`, `dispatcherContractEvidenceRef`,
`dispatcherContractSha256`, `dispatcherContractExpiresAt`,
`networkEnforcementEvidenceRef`, `networkEnforcementEvidenceSha256`,
`networkEnforcementExpiresAt`, `dispatcherServiceIdentity`,
`dispatcherImageDigest`, `dispatcherBinarySha256`, `dispatcherKeyRef`,
`monitorServiceIdentity`, `monitorKeyRef`, `monitorImageDigest`,
`monitorPolicySha256`, `monitorPermissionsSha256`,
`monitorTrustedTimeSourceSha256`, `networkPolicySha256`, `tokenStorePolicySha256`,
`floorChallengeNonce`, `witnessFloorResponsesSha256`,
`endpointIdentifierSha256`, `providerApplicationRequestSha256`,
`providerRequestBodySha256`, `providerApplicationHeadersSha256`,
`transportProfileRef`, `transportProfileSha256`,
`allowedHeaderNames`, `authorizationCredentialSha256`,
`controlPlaneHandleSha256`, `policyEpoch`, `activatedAt`, `expiresAt`,
`leaseIntentSha256`, `leaseCoreSha256` und `monitorSignature`. Lease-Core und geschlossene
Monitor-Signatur werden gegen den externen Pin geprüft; die Signatur enthält
ausschließlich `keyRef`, `signedAt`, `nonce`, `leaseCoreSha256` und
`signature`. Der Monitor versiegelt Netzwerk-Namespace, cgroup-/eBPF-/Firewall-
Handle, DNS, Proxy, IPv4/IPv6, Zielauthority, Methode, Tokenstore und
Credential-Zugriff in derselben atomaren Transaktion. Nur der gebundene
Dispatcherprozess kann innerhalb dieser Lease den gebundenen Request senden.
Der Policyhandle bleibt bis zum letzten Responsebyte referenzgehalten und
unveränderlich; ein privilegierter Änderungsversuch wird entweder vor Commit
abgewiesen oder trennt atomar den Transport und verhindert einen gültigen
Transport-Receipt. Eine bloße Vorabinspektion ohne diese Control-Plane-
Eigenschaft ist nicht ausreichend.
Vor der Installation berechnet der Monitor `leaseIntentSha256` als SHA-256 der
RFC-8785-Projektion aller Leasefelder außer
`witnessFloorResponsesSha256`, `activatedAt`, `leaseIntentSha256`,
`leaseCoreSha256` und
`monitorSignature`; Challenge, vorgesehene Frist, Policyepoch und vorbereiteter
Control-Plane-Handle sind damit bereits gebunden. Die Witnesses signieren
dieses Intent und nicht den erst danach konstruierbaren Lease-Vollhash. Nach
Vollquorum installiert der Monitor die Policy, setzt `activatedAt`, bindet den
Arrayhash der Responses und signiert den vollständigen Lease-Core. Ein
Vollhash in seiner eigenen Vorbedingung oder ein Zukunftshash ist unzulässig.

Nach Installation erzeugt der Monitor nach
`egress-dispatch-attestation.schema.json` die pro Dispatch geschlossene
Attestation. Sie enthält ausschließlich `schemaVersion`, `repositoryId`,
`attestationId`, `requestReceiptId`, `requestReceiptSha256`,
`requestCheckpointSha256`, `requestCheckpointTreeSize`,
`requestCheckpointIssuedAt`, `floorChallengeNonce`, `witnessFloorResponses`,
`dispatcherContractEvidenceRef`, `dispatcherContractAcceptanceReceiptId`,
`dispatcherContractAcceptanceReceiptLogIndex`, `dispatcherServiceIdentity`,
`dispatcherImageDigest`, `dispatcherBinarySha256`, `dispatcherKeyRef`,
`monitorServiceIdentity`, `monitorKeyRef`, `monitorImageDigest`,
`monitorPolicySha256`, `monitorPermissionsSha256`,
`monitorTrustedTimeSourceSha256`, `networkPolicySha256`, `tokenStorePolicySha256`,
`endpointIdentifierSha256`, `providerApplicationRequestRef`,
`providerApplicationRequestSha256`, `providerRequestBodySha256`,
`providerApplicationHeadersSha256`, `transportProfileRef`,
`transportProfileSha256`, `allowedHeaderNames`,
`authorizationCredentialSha256`, `enforcementLeaseRef`,
`enforcementLeaseSha256`, `leaseIntentSha256`, `observedAt`, `expiresAt`,
`attestationCoreSha256` und `monitorSignature`. Core und Signatur folgen der
gleichen geschlossenen Form. Witness-Responses sind challengegebunden,
umfassen alle Witnesses, binden Repository, Attestation-ID, Receipt,
`leaseIntentSha256`,
Challenge und Floor-Vollzustand, liegen höchstens zehn Sekunden vor
`activatedAt` und niemals danach; ihr RFC-8785-Arrayhash ist bytegleich
`enforcementLease.witnessFloorResponsesSha256` und ihre Floors mindestens beim
Request-Checkpoint. Binary,
Serviceidentität, Policy-, Endpoint-, Token- und Application-Request-Digests
müssen bytegleich zu Vertrag, Netzwerkbeleg, Envelope, Receipt und
Enforcement-Lease sein. Attestation-`expiresAt` liegt höchstens 30 Sekunden
nach `observedAt`; die Enforcement-Lease höchstens 900 Sekunden nach
`activatedAt` und nicht nach Receipt-, Contract- oder Netzwerkbeleg-Frist.
Zusätzlich gilt `preflightAcceptedAt <= requestCheckpointIssuedAt <=
activatedAt <= observedAt`, die Differenz zwischen Checkpoint und `observedAt`
überschreitet Contract-`maxReceiptAgeSeconds` nicht und vollständig gilt
`observedAt < attestation.expiresAt <= requestReceipt.expiresAt` sowie
`activatedAt < enforcementLease.expiresAt <= min(requestReceipt.expiresAt,
dispatcherContract.expiresAt, networkEnforcementVerification.expiresAt)`.
Erst Attestation, versiegelte Lease und unverbrauchtes Dispatch-Token
autorisieren das erste Netzwerkbyte; der Tokenstore verbraucht Token,
Receipt-, Attestations- und Leasehash atomar. Split View, Digest-Drift,
abgelaufener Contract/Netzwerkbeleg oder Policywechsel scheitert vor Egress.

Nach Ende oder Abbruch jedes Transports erzeugt der Monitor den geschlossenen
`egress-transport-receipt.schema.json`-Beleg mit ausschließlich
`schemaVersion`, `repositoryId`, `transportReceiptId`, `requestReceiptId`,
`requestReceiptSha256`, `dispatchAttestationRef`,
`dispatchAttestationSha256`, `enforcementLeaseRef`,
`enforcementLeaseSha256`, `dispatchTokenSha256`,
`providerApplicationRequestSha256`, `providerRequestBodySha256`,
`providerApplicationHeadersSha256`, `transportProfile:
"http/1.1"|"h2"`, `transportProfileRef`, `transportProfileSha256`,
`connectionIdSha256`, `wireRequestTranscriptRef: string|null`,
`wireRequestTranscriptSha256: string|null`,
`mandatoryTransportFieldsSha256: string|null`,
`tlsTranscriptRef: string|null`, `tlsTranscriptSha256: string|null`,
`providerResponseSha256: string|null`, `firstRequestByteAt: string|null`,
`lastRequestByteAt: string|null`, `firstResponseByteAt: string|null`,
`lastResponseByteAt: string|null`, `controlPlaneHandleSha256`, `policyEpochAtStart`,
`policyEpochAtEnd`, `networkPolicySha256AtStart`,
`networkPolicySha256AtEnd`, `tokenStorePolicySha256AtStart`,
`tokenStorePolicySha256AtEnd`, `transportResult: "completed"|"aborted"`,
`monitorServiceIdentity`, `monitorKeyRef`, `monitorImageDigest`,
`monitorPolicySha256`, `monitorPermissionsSha256`,
`monitorTrustedTimeSourceSha256`,
`transportCodecImageDigest`, `transportCodecPolicySha256`,
`http1Evidence: object|null`, `http2Evidence: object|null`,
`receiptCoreSha256` und `monitorSignature`. Das verschlüsselt revisionsfest
verwahrte Wire-Artefakt bindet die tatsächlichen HTTP/1.1-Octets oder
HTTP/2-Frame-/HPACK-Bytes unmittelbar vor TLS sowie den vollständigen
TLS-Transcript; Decoder-Image und -Policy sind mitgebunden. Bei `completed` ist
genau eines von `http1Evidence` und `http2Evidence` passend zum Transportprofil
non-null und vollständig; beim `aborted`-Schema darf es nur ohne erstes
Requestbyte `null` bleiben, andernfalls bindet die diskriminierte Abortvariante
den vollständig verfügbaren Präfix.
`http1Evidence` enthält ausschließlich `requestLineSha256`,
`orderedHeaderMultimap`, `headerBlockSha256`, `contentLength`,
`transferEncoding: null`, `connection: "close"`, `trailers: []` und
`connectionReuse: false`. Jeder Multimap-Eintrag enthält ausschließlich
`ordinal`, `name`, `valueSource`, `valueLength` und `valueSha256`; die
Ordnung und vollständige Namensmenge sind bytegleich zum Profil, `host` ist
einmalig und bytegleich zur Authority. `http2Evidence` enthält ausschließlich
`connectionPrefaceRef`, `connectionPrefaceSha256`, `clientSettingsRef`,
`clientSettingsSha256`, `serverSettingsRef`, `serverSettingsSha256`,
`settingsAckRef`, `settingsAckSha256`, `streamId: 1`,
`exclusiveSingleStream: true`, `hpackDynamicTableSizeAtStart: 0`,
`hpackDynamicTableSizeAtEnd: 0`, `hpackInitialStateSha256`,
`hpackFinalStateSha256`, `orderedPseudoHeaders`, `orderedHeaderMultimap`,
`headerBlockSha256`, `dataFramesSha256`, `trailers: []` und
`connectionReuse: false`. Initial-/Final-HPACK-State sind exakt der
schemafesten leeren Tabelle; der vollständige SETTINGS-/ACK-Präfix und alle
Frames der frischen Connection werden neu gehasht, ausschließlich Stream 1 ist
zulässig, und `:authority` erscheint genau einmal. Jeder Pseudo-/Regelheader-
Eintrag besitzt dieselben geschlossenen `ordinal`, `name`, `valueSource`,
`valueLength` und `valueSha256` wie bei HTTP/1.1. Identische Headerblockbytes
mit abweichendem HPACK-State, ein fremder Stream, Zusatz-/Doppelheader oder
Trailer sind ungültig.
`mandatoryTransportFieldsSha256` ist der SHA-256 der RFC-8785-Projektion des
jeweiligen vollständigen diskriminierten Evidence-Objekts. Methode, Scheme,
Authority, Pfad/Query, Body und Application-Header müssen aus dem kanonischen
Application-Request ohne semantische Änderung ableitbar sein; es gibt keine
transportseitigen Felder außerhalb von Profil, Evidence und Wire-Transcript.
Start-/End-Epoch, Policy- und Handle-Digests müssen
identisch sein. Bei `completed` sind alle nullable Felder non-null. Bei
`aborted` ist ein Artefakt-/Zeitfeld genau dann `null`, wenn das zugehörige Byte
nie auftrat; andernfalls bindet es den vollständig erfassten Präfix, und kein
Abortbeleg darf eine Output-EVID stützen. Ein Wechsel nach der Attestation, zwischen Tokenverbrauch und
erstem Byte oder während des Transports erzwingt `aborted`; nur `completed`
mit `firstRequestByteAt <= lastRequestByteAt <= firstResponseByteAt <=
lastResponseByteAt <= enforcementLease.expiresAt` darf eine Output-EVID
stützen.

Der Response-Envelope liegt kanonisch unter
`docs/governance/external-model/<EVID-ID>--response.json` und enthält
ausschließlich `schemaVersion`, `repositoryId`, `externalOutputEvidenceRef`,
`expectedEvidenceRecordSha256`, `requestDescriptorSha256`,
`requestEnvelopeSha256`, `requestReceiptId`, `requestReceiptSha256`,
`dispatchTokenSha256`, `dispatchAttestationRef`, `dispatchAttestationSha256`,
`egressEnforcementLeaseRef`, `egressEnforcementLeaseSha256`,
`egressTransportReceiptRef`, `egressTransportReceiptSha256`,
`providerApplicationRequestSha256`, `providerRequestBodySha256`,
`providerApplicationHeadersSha256`, `wireRequestTranscriptSha256`,
`transportProfileRef`, `transportProfileSha256`, `tlsTranscriptSha256`,
`providerRequestIdSha256`,
`providerResponseSha256`,
`requestSentAt`, `responseReceivedAt`, `runnerRole`, `runnerAssigneeSnapshot`,
`runnerKeyRef`, `nonce` und `signature`. Auch er wird über alle Felder außer `signature` mit
dem zum Request und Response aktiven, rollen-/assigneegebundenen Runner-Key
signiert. Request- und Response-Nonce sind verschieden. Es gilt
`preflightAcceptedAt <= requestCheckpointIssuedAt <= dispatchAttestation.observedAt
<= requestSentAt <= responseReceivedAt <= producedAt` sowie
`requestSentAt < dispatchAttestation.expiresAt <= requestReceipt.expiresAt` und
`requestSentAt <= dispatcherContract.expiresAt <=
networkEnforcementVerification.expiresAt`; der vollständige Transport liegt
innerhalb der versiegelten Enforcement-Lease. Zusätzlich sind `requestSentAt
== transportReceipt.firstRequestByteAt`, `responseReceivedAt ==
transportReceipt.lastResponseByteAt` und `transportResult == "completed"`.
Envelope-/Receipt-/Descriptor-/
Application-Request-/Attestations-/Lease-/Transporthashes,
Provider-/Inputfelder und Runner-Snapshots sind bytegleich zu
`externalModelOutput`; `requestReceiptSha256` ist der Hash der vollständigen
kanonischen, instanzsignierten Logentry-Bytes. Der `sha256` des erfassten
Output-EVID-Artefakts ist
zwingend bytegleich `providerResponseSha256`; Parsing, Normalisierung oder
Extraktion erzeugt eine separate abgeleitete EVID mit vollständigem
Inputmanifest. Fehlender Preflight, Dispatch vor Receipt, Token-Reuse,
post-Receipt-Amendment oder Output-Substitution ist ungültig.

`providerDueDiligence` besitzt ausschließlich `providerName`,
`endpointClass: "public-cloud-api"|"enterprise-private"|"local-runtime"`,
`endpointIdentifierSha256`, `modelVersion`, `processingRegion`,
`retentionPolicy`, `trainingUse: "disabled"|"contractually-disabled"`, `termsVersionSha256`,
`assessedAt`, `expiresAt`, `assessorRole` und `assessorAssigneeSnapshot`.
Providername, Endpointklasse/-identifier, Modellversion, Region, Retention und TrainingUse
müssen bytegleich zu `externalModelOutput` sein; die Assessment-EVID ist vor
`preflightAcceptedAt` verifiziert, zum Requestzeitpunkt nicht abgelaufen und in
`dueDiligenceEvidenceRef` exakt referenziert.

`sanitizationReport` besitzt ausschließlich `sourceArtifactSha256`,
`sanitizedArtifactSha256`, `inputClassification:
"public"|"synthetic"|"sanitized-non-production"`, `sanitizerRole`,
`sanitizerAssigneeSnapshot`, `sanitizerVersionSha256`, `rulesetSha256`,
`producedAt`, `secretFindings`, `personalDataFindings` und
`disposition: "passed"`. `externalModelOutput.inputArtifactSha256` ist
bytegleich `sanitizedArtifactSha256`; Inputklassifikation, Sanitizerrolle und
-Snapshot stimmen ebenfalls exakt überein. Die Report-EVID ist vor
`preflightAcceptedAt` verifiziert und in `sanitizationEvidenceRef` exakt referenziert.
Beide Findingfelder sind nichtnegative Integer; nur `passed` mit jeweils dem
Wert `0` ist zulässig. Der unsanitisierte Quellhash wird
niemals an den Provider übertragen.

`collectorContract` ist nur bei `evidenceType: "collector-contract"`
non-null und besitzt ausschließlich `dispatcherPath`, `dispatcherSha256`,
`collectorPath`, `collectorSha256`, `configPath`, `configSha256`,
`protectedStateManifestPath`, `protectedStateManifestSha256`,
`allowedSupervisorDeltas`, `allowedArgv: string[][]`, `runtimeWriteSet: []`,
`runAsUid`, `runAsGid`, `supplementaryGroups: []`,
`unixSocketPaths: []`, `netlinkProtocols: []`,
`systemCallAllowlist: string[]`, `networkSyscallDenylist: string[]`,
`inaccessiblePaths: string[]`, `installationChangePlanEvidenceRef`, `pty: false`,
`agentForwarding: false`, `x11Forwarding: false`, `portForwarding: false`,
`outboundNetwork: false`, `restrictAddressFamilies: []`,
`systemdProperties: string[]`, `cpuQuota`, `memoryMax`, `tasksMax`,
`timeoutSeconds`, `expiresAt` und `operatorSignatureEvidenceRef`. Die
Systemd-Liste enthält mindestens `ProtectSystem=strict`,
`ProtectHome=read-only`, `ReadOnlyPaths=/`, `NoNewPrivileges=yes`, leere
`CapabilityBoundingSet`/`AmbientCapabilities`, `PrivateTmp=no`,
`PrivateDevices=yes`, `RestrictAddressFamilies=none`,
`IPAddressDeny=any`, eine positive `SystemCallFilter`-Allowlist, die sämtliche
Network-I/O-Syscalls ausschließt, und
`InaccessiblePaths` mindestens für `/tmp`, `/var/tmp`,
`/run/docker.sock`, `/run/containerd/containerd.sock` und
`/run/dbus/system_bus_socket`. `runtimeWriteSet: []` bedeutet keine
persistente oder volatile Dateisystemänderung im Namespace des Collectors;
auch temporäre Dateien sind verboten. `networkSyscallDenylist` enthält
mindestens `socket`, `socketpair`, `connect`, `bind`, `listen`, `accept`,
`accept4`, `sendto`, `sendmsg`, `sendmmsg`, `recvfrom`, `recvmsg`, `recvmmsg`,
`setsockopt`, `getsockopt`, `shutdown` und `io_uring_setup`; der technische
Negativtest versucht jede verfügbare Address Family und diese Aufrufe und
erwartet ausnahmslos die Sandboxverweigerung. AF_UNIX, Netlink, D-Bus und
lokale Control-Sockets sind vollständig gesperrt. Freie Shells,
Editoren, Pager, Interpreter, Pluginloader, Umgebungsargumente und Globs sind
schemawidrig.

`RestrictAddressFamilies=none` setzt systemd mindestens Version 249 voraus.
Bootstrap und Lauf prüfen tatsächliche systemd-Version, Kernel-Seccomp sowie
die für `IPAddressDeny` erforderliche cgroup-v2/eBPF-Unterstützung; eine nur
syntaktisch akzeptierte, aber nicht wirksame Direktive ist `unknown` und bricht
den Collectorlauf ab. Die Seccomp-Verweigerung von `socket`/`socketpair` ist
die primäre No-Socket-Grenze, `RestrictAddressFamilies` und `IPAddressDeny` sind
unabhängige zusätzliche Schichten.

Das referenzierte `collector-protected-state`-Manifest enthält ausschließlich
`schemaVersion`, `baselineCapturedAt`, `fileEntries`, `serviceEntries` und
`allowedSupervisorDeltas`. Jeder nach `path` sortierte File-Entry enthält
ausschließlich `path`, `entryType: "file"|"directory"`, `fileMode`, `uid`,
`gid` und `sha256`; bei Dateien ist dies der Hash der Bytes, bei Verzeichnissen
der Hash des RFC-8785-kanonischen, vollständig rekursiven
Descendant-Manifests. Symlinks und unlesbare Einträge schlagen fail-closed fehl.
Jeder nach `unitName` sortierte Service-Entry enthält ausschließlich
`unitName`, `fragmentSha256`, `dropInSha256s`, `loadState`, `activeState`,
`unitFileState` und `mainPid` vor dem Lauf. Erfasst werden mindestens
Collector/Dispatcher/Config, SSH-/Systemd-/Audit-Konfiguration,
`authorized_keys`, Paketdatenbank, AURELIA-Pfade und alle aktiven oder
aktivierten Services. `allowedSupervisorDeltas` ist in Contract und Manifest
bytegleich und exakt
`["append-only-audit-journal","systemd-invocation-accounting"]`. Nach dem Lauf
müssen alle geschützten File- und Servicefelder bytegleich sein. Zulässig sind
nur die außerhalb des Collector-Namespace vom Supervisor erzeugten, explizit
auditierten Journal- und Invocation-Accounting-Einträge; neue/gelöschte
Dateien, Unitänderungen, Paketänderungen oder ein anderer Dienstzustand schlagen
fehl. Damit behauptet die Prüfung keine unmögliche globale Bytegleichheit von
Journal und Systemd-Laufzeit, sondern eine exakt abgegrenzte Nichtmutation des
geschützten Serverzustands.

„Erforderlichenfalls getrennt“ ist maschinenlesbar: Verschiedene Assignee-Refs
sind zwingend, wenn eine der Rollen die andere in `separationFromRoleRefs`
nennt oder `evidenceType` `review-report`, `qualification` oder
`audit-artifact` ist. Für alle Pflichtevidenzen eines No-Waiver-Gates gilt die
Trennung ebenfalls zwingend.

`producerAssigneeSnapshot` wird bei `null|expected → captured` aus
`producerRole` kopiert; `verifiedByAssigneeSnapshot` beim Übergang zu `verified` aus
`verifiedByRole`. Beide bleiben
bei späterer Rollenumbesetzung unverändert. Die Trennungsprüfung verwendet
diese Snapshots, nicht die aktuelle Rollenbelegung.

Eine Review darf eine `captured` Evidenz prüfen und genehmigen. Erst danach
wird die Evidenz unter Verweis auf diese Review `verified`; eine Review darf
also nicht `expected`, wohl aber `captured` als Input verwenden. Damit ist der
Bootstrap ausdrücklich `captured → approved review → verified evidence` und
enthält keinen Statuskreis.

Für den G0-Start wird `EVID-G0-DESIGN-COMMIT` zunächst mit dem realen
Design-Commit als `captured` angelegt. `REV-G0-DESIGN-APPROVAL` dokumentiert
danach den bereits erteilten Betreiberwortlaut gegen genau diese Evidenz und
wird durch `ROLE-OPERATOR` genehmigt. Erst anschließend wechselt die Evidenz
unter Rückverweis auf diese Review zu `verified`. Dasselbe Muster gilt für
Baseline-Tests, Spec-/Quality-Reviews und finale Gates.

Jede Review, die eine Evidenz verifiziert oder invalidiert, enthält deren
EVID-ID in `evidenceSubjectRefs` und `evidenceRefs`, exakt denselben `scope`
und dieselbe Baseline. `evidenceSubjectRefs` ist stets eine Teilmenge von
`evidenceRefs` und wird nicht in die Gleichheitsprüfung der fachlichen Subjects
einer Re-Review einbezogen. Bei einer späteren Invalidation darf die Review-Baseline stattdessen
ein nachgewiesener Git-Nachfolger sein. Eine sachfremde Review ist ungültig.

Supersession ist bidirektional: Die alte EVID nennt
`supersededByEvidenceRef`, die neue nennt `supersedesEvidenceRef`. Beide haben
denselben `evidenceType` und Scope; die neue Evidenz besitzt einen späteren
`producedAt`-Zeitpunkt und eine andere, per `git merge-base --is-ancestor`
nachgewiesene Nachfolger-Baseline. Die genehmigte Supersession-Review nennt
beide EVID-IDs als `evidenceSubjectRefs` und die neue Baseline. In derselben
atomaren Transaktion wechselt zuerst die bereits `captured` neue EVID auf
`verified` und setzt einmalig `supersedesEvidenceRef`; unmittelbar danach
wechselt die alte EVID aus ihrem gespeicherten Vorstatus auf `superseded`,
setzt `supersededFromStatus` und verweist zurück. Die reziproke Prüfung darf
nur zwischen diesen beiden Events aufgeschoben werden und muss am
Transaktionsende exakt passen. Kein Record darf sich selbst oder einen Kreis
referenzieren.

`artifactPathOrUri` darf keine Secrets enthalten. Externe URLs benötigen einen
zugriffskontrollierten, revisionsfesten Ablageort; flüchtige Chat- oder
Terminalausgabe allein genügt nicht als Freigabeevidenz.

Ein EXC-Record enthält zusätzlich:

- `scopeIds: string[]`, `justification: string`,
  `compensatingControlRefs: string[]`;
- `requestedByRole: string`, `approvedByRole: string | null`,
  `requestedAt: string`, `expiresAt: string`;
- `revokedAt: string | null`, `evidenceRefs: string[]` und
  `blockedGateRefs: string[]`.

Scope, kompensierende Controls und blockierte Gates sind nie leer. `approved`
verlangt `ROLE-OPERATOR`, mindestens eine verifizierte Evidenz und ein in der
Zukunft liegendes Ablaufdatum. `requested` hat `approvedByRole: null`;
`revoked` benötigt `revokedAt`, alle anderen Statuswerte setzen es `null`.

Ausnahmen benötigen Betreiberfreigabe und ein festes Ablaufdatum. Abgelaufene
oder widerrufene Ausnahmen setzen betroffene Gates auf `red`.

Alle neun initialen Gates sind No-Waiver:

- `GATE-G0`, `GATE-DATAFLOW`, `GATE-PROFILE`, `GATE-ART9`;
- `GATE-MODULE`, `GATE-CUDA`, `GATE-HARDWARE`, `GATE-PILOT`;
- `GATE-24X7`.

Künftige waivable Gates müssen dies ausdrücklich begründen. Eine Ausnahme
darf niemals direkt oder indirekt ein initiales No-Waiver-Gate grün machen.

### 12.5 Append-only Transition-Ledger

`transitions` enthält EVT-Objekte; für sie gelten nicht die gemeinsamen
Recordfelder. Ein EVT besitzt ausschließlich:

- `id: string`,
  `eventKind: "transition" | "amend" | "handover" | "recovery" |
  "custodian-rotation"`,
  `recordRef: string`, `fromStatus: string | null`, `toStatus: string`;
- `previousRecordSha256: string | null`, `resultingRecordSha256: string`;
- `changeDigest: string`, `trustRootDeltaSha256: string`;
- `actorRole: string`, `actorAssigneeSnapshot: string`,
  `operatorEpoch: integer`, `occurredAt: string`, `baseCommit: string`;
- `evidenceRefs: string[]`, `previousEventHash: string | null`,
  `eventAuthorizationPayloadSha256: string`, `eventHash: string`;
- `authorizationAttestations: object[]`;
- `genesisAnchor: object | null`.

Alle Hashfelder besitzen 64 kleingeschriebene hexadezimale Zeichen. Record-
Hashes sind SHA-256 über die UTF-8-Bytes der RFC-8785-kanonischen
JSON-Darstellung des vollständigen Records. `changeDigest` ist auf dieselbe
Weise der Hash über genau das Objekt `{ "recordRef", "eventKind",
"previousRecordSha256", "resultingRecordSha256" }` in dieser
RFC-8785-Kanonisierung. Damit bleibt ein vorab geprüfter Beleg trotz späterer
reiner Evidenz-Commits verwendbar, kann aber weder auf einen anderen Record
noch einen anderen Vorher-/Nachherzustand übertragen werden.
`eventAuthorizationPayloadSha256` ist SHA-256 über die UTF-8-Bytes der
RFC-8785-Darstellung des vollständigen EVT ohne
`eventAuthorizationPayloadSha256`, `authorizationAttestations` und
`eventHash`; dieser gemeinsame Event-Core ist für alle Mitzeichner bytegleich.
`eventHash` ist SHA-256 über die UTF-8-Bytes der RFC-8785-Darstellung des
vollständigen EVT ohne `eventHash` und bindet dadurch Core-Digest und alle
Attestationen.

Jede Authorization-Attestation besitzt ausschließlich `method: "ed25519"`,
`attestationPurpose: "actor" | "approver" | "incoming-operator" |
"recovery-root" | "custodian-a" | "custodian-b" |
"incoming-custodian-a" | "incoming-custodian-b"`, `keyRef: string`,
`signerIdentity: string`, `signerRole: string`, `signedAt: string`,
`nonce: string`, `envelopeSha256: string` und `signature: string`. Die Nonce
ist repositoryweit einmalig. Der signierte RFC-8785-/UTF-8-Envelope enthält
exakt `schemaVersion`, `repositoryId`, `method`, `attestationPurpose`, `keyRef`,
`signerIdentity`, `signerRole`, `signedAt`,
`eventAuthorizationPayloadSha256` und `nonce`. Er enthält weder Signatur noch
`envelopeSha256`. Alle EVT-Sicherheitsfelder einschließlich ID, Zustände,
Recordhashes, Change-/Trust-Root-Digest, Actor, Epoch, Zeit, Basiscommit,
Evidenzrefs, Genesis-Anchor und vorherigem Eventhash liegen im gemeinsam
gebundenen Event-Core. Jeder Mitzeichner besitzt einen eigenen Purpose-, Key-,
Identitäts-, Zeit- und Nonce-spezifischen Envelope über exakt denselben
`eventAuthorizationPayloadSha256`.
Der Delta-Hash ist SHA-256 über das RFC-8785-kanonische
Array der diesem Event zugeordneten hinzugefügten oder widerrufenen Trust-Root-
Einträge; ohne Änderung ist er der Hash von `[]`.
`envelopeSha256` und detached Signatur werden offline gegen den unmittelbar
vor dem Event aktiven `keyRef` aus `trust-roots.json` geprüft. Key-Role,
Key-Assignee, `signerRole` und `signerIdentity` müssen übereinstimmen. Nur bei
`attestationPurpose: "actor"` müssen sie zusätzlich EVT-Akteur und Rollen-
Snapshot entsprechen; `approver`, Recovery-Root, Custodians und eingehender
Operator werden gegen ihre jeweils geschlossene Sollrolle geprüft. Aktive
identische Public Keys oder Fingerprints für verschiedene Assignees/Rollen
sind verboten. Ein repositoryintern behaupteter String oder eine
korrekte Hashkette ohne gültige externe Signatur authentifiziert niemanden.
Zusätzliche Annahmesignaturen eines eingehenden Handover-/Recovery-Operators
oder Custodians sind ausschließlich Besitz- und Annahmenachweis, keine
autorisierende Selbsteinführung. Der Kandidatenkey wird kryptografisch geprüft,
aber erst durch die operationseigene alte Autorisierungsschwelle zum aktiven
Trust Root. Beim geplanten Handover sind das
ausgehender Operator und Offline-Recovery-Root; bei Recovery vor Pilot der Root
und nach erstmaligem Pilot-Green zusätzlich beide Custodians; bei initialer
Custodian-Besetzung Operator und Root, bei Rotation Root und verbleibender
Custodian; der eingehende Custodian belegt jeweils nur Besitz und Annahme.

Jeder normale EVT besitzt genau eine passende Akteurattestation. Ausgenommen
sind ausschließlich Handover-/Recovery-/Custodian-Rotations-EVTs und ihre
atomaren Gate-Resets;
dort gelten die unten vollständig aufgezählten Zwecke, und eine
`recovery-root`-Attestation erfüllt bei `actorRole: "ROLE-RECOVERY-ROOT"`
zugleich die Akteurauthentifizierung. Verlangt der
resultierende Record zusätzlich einen vom Akteur getrennten Approver, enthält
das EVT eine zweite Attestation dieser Rolle über denselben Event-Core; bei
`reviewType: "operator"` kann dieselbe Operatorattestation beide Funktionen
erfüllen. Handover und Recovery besitzen die unten geforderte
Mehrfachattestation; die Custodian-Rotation folgt ihrer unten geschlossenen
Schwelle. Änderungen an
Trust-Roots werden gegen den vor der Transaktion aktiven Schlüsselzustand
geprüft; ein im selben Commit neu eingeführter oder ausgetauschter Schlüssel
kann seine eigene Einführung niemals autorisieren. Einzige Ausnahme ist die
EVT-000001-`actor`- und -`recovery-root`-Attestation: Beide werden gegen ihre
separaten externen Pins und dasselbe doppelt signierte Pre-Ledger-Bundle
geprüft, bevor ihre Keys in den Replayzustand gelangen. Der geschützte CI-Check
erhält initialen Operator- und Recovery-Root-Fingerprint als zwei nicht aus
dem Pull Request änderbare geschützte Pins. Ohne beide externe Pins bleibt jeder
Bootstrap ungültig.

EVT-IDs sind eine einzige globale, lückenlose Sequenz: Der erste Eintrag ist
`EVT-000001`, jeder folgende numerische Wert ist exakt um eins größer. Das
Array ist ausschließlich in dieser Reihenfolge sortiert. `previousEventHash`
ist beim ersten EVT `null` und entspricht danach stets `eventHash` des global
unmittelbar vorherigen Arrayeintrags. `occurredAt` ist über das gesamte Array
nicht fallend und für denselben `recordRef` strikt steigend. Ein neu
angehängtes Event darf daher weder eine frühere ID noch einen früheren
Zeitpunkt einschieben.

Zeitmonotonie allein genügt nicht. Jede `signedAt`-Zeit liegt höchstens fünf
Minuten vor oder nach `occurredAt`. Nur bei der erstmaligen Aufnahme neuer
Events muss `signedAt` zwischen 24 Stunden vor und fünf Minuten nach der
extern vertrauenswürdig attestierten CI-Annahmezeit liegen. Zukunftswerte
werden abgewiesen. Die externe Instanz speichert danach das in Abschnitt 6.4
definierte immutable Acceptance-Receipt. Historische Replays prüfen Receipt,
damalige Keygültigkeit, Envelope und Logkette; sie verlangen niemals eine
Änderung oder Neuattestation alter EVT-Dateien. Die Working-Tree-Prüfung nutzt
lokale UTC nur vorläufig und kann kein Gate grün machen. So sperrt weder ein
2099-Event noch eine nach 24 Stunden zwangsläufig veraltete Historie das
Ledger.

Das erste EVT eines Records verwendet `fromStatus` und
`previousRecordSha256` als `null`. Jedes weitere EVT dieses Records übernimmt
den Status und vollständigen Recordhash seines zeitlich letzten Vorgängers.
`baseCommit` ist der vollständige Git-Commit, auf dessen Zustand die gesamte
Working-Tree- oder Commit-Transaktion angewendet wird. Innerhalb derselben
Transaktion ist je `recordRef` exakt höchstens ein neues EVT zulässig. Dadurch
kann der Validator den einen resultierenden Record aus dem Zielregister
verwenden; nicht rekonstruierbare Zwischenrecords sind ausgeschlossen.

Jeder Commit mit neuen EVT-Einträgen ist ein strikt nachgelagerter
Governance-only-Commit. Sein Diff darf ausschließlich die vier Register,
`trust-roots.json`, schema-konforme Bootstrap-/Attestations-/Evidenzartefakte
und keine Validator-, Schema-, Workflow-, Direktiven-, Source-, Code-, Test-,
Konfigurations- oder sonstige Fachdatei ändern. Der Validator vergleicht
Pfad, Dateimodus und SHA-256 jedes Zielblobs; die externe Acceptance-Receipt
bindet anschließend tatsächlichen Head-Commit und vollständige Tree-OID.
Fachänderung, Review/Evidenzerzeugung und Governance-Freigabe sind daher
mindestens drei getrennte Commits. Ein Gate kann im selben Commit weder
ungeprüften Code einschleusen noch seinen Validator abschwächen.

`genesisAnchor` ist außerhalb der nachfolgend exakt definierten drei
Bootstrap-Events immer `null`. Dort besitzt es ausschließlich:

- `elaborationApprovalText: "G0-Design freigegeben"`;
- `elaborationApprovalSha256:
  "b90981b47509d7349d1ccc476e8cb6b35f4a56d1b791ba94a396f1454f5d06bd"`;
- `designSpecPath:
  "docs/superpowers/specs/2026-08-24-aurelia-g0-governance-design.md"`;
- `designSpecSha256: string` als SHA-256 der unveränderten Git-Blob-Bytes aus
  `git show <designCommit>:<designSpecPath>`;
- `designBaselineCommit:
  "b20ee873347c5fd767e2089c993f1cf93a625def"`;
- `designCommit: string` als vollständiger Commit, der exakt diese
  geprüfte Datei enthält;
- `governanceImplementationCommit: string` als vollständiger, separat
  reviewter Commit mit Validator, Schemas und Direktiven, auf den Genesis
  angewendet wird;
- `finalApprovalText: string` exakt nach dem Muster
  `AURELIA G0-Spezifikation <designCommit> mit Dateihash
  <designSpecSha256> final freigegeben`;
- `finalApprovalScope: "AURELIA-G0-GOVERNANCE-DESIGN"`;
- `finalApprovalSha256: string` als SHA-256 der vollständigen unveränderten
  Bytes des folgenden Freigabeartefakts,
  `finalApprovalRef:
  "docs/governance/bootstrap/final-design-approval.json"`;
- `preLedgerTrustBundleRef:
  "docs/governance/bootstrap/pre-ledger-trust-bundle.json"`,
  `preLedgerTrustBundleSha256: string`;
- `bootstrapValidatorImageDigest: string`,
  `bootstrapValidatorPolicySha256: string`,
  `bootstrapWorkflowSha256: string`, `bootstrapSchemaSetSha256: string`,
  `bootstrapTrustProtocolSha256: string`;
- `operatorKeyRef: string`, `operatorKeyFingerprint: string`,
  `recoveryRootKeyRef: string`, `recoveryRootKeyFingerprint: string`,
  `orchestratorKeyRef: string`, `validatorControllerKeyRef: string` und
  `validatorControllerKeyFingerprint: string`;
- `transparencyLogId: string`, `transparencyInstanceKeyRef: string`,
  `transparencyInstanceKeyFingerprint: string`,
  `transparencyInstanceKeyEpoch: 1` und
  `witnessKeyFingerprints: string[]` in derselben sortierten Reihenfolge wie
  `witnessKeys` im Pre-Ledger-Bundle.

Alle drei Genesis-Events tragen ein bytegleiches Anchor-Objekt,
`baseCommit` gleich `governanceImplementationCommit`, `operatorEpoch: 1` und
denselben `occurredAt`-Zeitpunkt. Der
Validator weist nach, dass `designCommit` ein Nachfolger von
`designBaselineCommit` ist, der Git-Blob-Hash stimmt und der Diff zwischen
diesen beiden Commits ausschließlich die Designspezifikation enthält. Der
Implementierungscommit ist ein separat durch den im Pre-Ledger-Bundle und
extern identisch gepinnten Bootstrap-/Vorgängervalidator sowie die
vorgeschriebene Reviewkette akzeptierter Nachfolger des Designcommits. Der
alte Ausarbeitungswortlaut ist nur an `designBaselineCommit` gebunden. Die
separate finale Freigabesignatur wird gegen den extern gepinnten
`operatorKeyFingerprint` geprüft und bindet dagegen den exakten
`repositoryId`, `designCommit`, Dateihash und den bytegleichen konstanten
`approvalScope`. Das Pre-Ledger-Bundle bindet zusätzlich
Implementierungscommit, die Keys von Operator, Offline-Recovery-Root,
Orchestrator, Validator-Controller und Transparenzinstanz sowie sämtliche
Witness-Keys.
Alle drei Genesis-Anchor
müssen diese `logId`-, Epoch- und Fingerprintwerte bytegleich wiederholen; der
Validator vergleicht sie zusätzlich mit den extern geschützten Pins.
Zulässig sind genau und
in dieser Reihenfolge:

1. `EVT-000001`: `eventKind: "transition"`, `ROLE-OPERATOR`,
   `null→assigned`, Akteur und Snapshot
   `ROLE-OPERATOR`/`redshift-three67`, leere `evidenceRefs`, ein
   `trustRootDeltaSha256` über exakt initialen Operator- und Offline-Recovery-
   Root-Key sowie gültige `actor`- und `recovery-root`-Attestationen;
2. `EVT-000002`: `eventKind: "transition"`, `ROLE-ORCHESTRATOR`,
   `null→assigned`, Akteur und Snapshot
   `ROLE-OPERATOR`/`redshift-three67`, leere `evidenceRefs`, ein Delta über
   exakt den Orchestrator-Key und eine gültige Operatorattestation, die
   Assignee und Key bindet;
3. `EVT-000003`: `eventKind: "transition"`,
   `EVID-G0-DESIGN-COMMIT`, `null→captured`, Akteur
   `ROLE-ORCHESTRATOR`, Snapshot und Producer-Snapshot
   `codex-orchestrator`, `createdEpoch: 1`, `captureEpoch: 1`,
   `decisionEpoch: null`, `baselineCommit: designCommit`,
   `captureBaseCommit: governanceImplementationCommit`, Subjectpfad der
   Designspezifikation sowie schema- und hashgültige getrennte Subject-/
   Inputmanifeste, leere `evidenceRefs` und eine mit dem in EVT-000002
   autorisierten Orchestrator-Key erzeugte Attestation; der Trust-Root-Delta
   ist der Hash von `[]`.

Die drei Events werden als unteilbares Bündel geprüft. Nur EVT-000001 löst
Rolle und Assignee aus der kryptografischen finalen Betreiberfreigabe statt
einer bereits abgespielten Rollenbelegung auf. EVT-000002 verwendet bereits die Belegung
aus EVT-000001; EVT-000003 diejenige aus EVT-000002 und zusätzlich den realen
Artefakt- und Dateihash. Keine weitere genesisbedingte Ausnahme, Rolle,
Evidenzbefreiung, Reihenfolge oder abweichende Besetzung ist zulässig; die
separat normierten leeren Planungsübergänge bleiben davon unberührt.

Zulässige Übergänge sind vollständig geschlossen:

| Record | Übergänge |
|---|---|
| REQ | `null→proposed`, `proposed→approved|retired`, `approved→implemented|retired`, `implemented→verified|retired`, `verified→retired` |
| CTRL | `null→proposed`, `proposed→implemented|retired`, `implemented→verified|retired`, `verified→retired` |
| COMP | `null→proposed`, `proposed→approved|retired`, `approved→implemented|retired`, `implemented→retired` |
| PROFILE | `null→proposed`, `proposed→approved|retired`, `approved→active|retired`, `active→retired` |
| ROLE | `null→unassigned|assigned`, `unassigned→assigned|retired`, `assigned→unassigned|suspended|retired`, `suspended→assigned|retired` |
| RISK | `null→open`, `open→treated|accepted|closed`, `treated→open|accepted|closed`, `accepted→open|closed`, `closed→open` |
| DATA/FLOW | `null→catalogued`, `catalogued→planned|retired`, `planned→active|retired`, `active→retired` |
| GATE | `null→red`, `red→amber|green|expired`, `amber→red|green|expired`, `green→red|expired`, `expired→red` |
| REV | `null→requested`, `requested→changes-required|approved`, `changes-required→superseded`, `approved→superseded` |
| EVID | `null→expected|captured`, `expected→captured`, `captured→verified|invalidated|superseded`, `verified→invalidated|superseded`, `invalidated→superseded` |
| EXC | `null→requested`, `requested→approved|revoked|expired`, `approved→revoked|expired` |

`ROLE assigned→assigned` ist kein allgemeiner Tabellenübergang, sondern nur als
vollständig validiertes `handover`, `recovery` oder `custodian-rotation` nach
den jeweils geschlossenen Schwellen dieses Abschnitts zulässig.

Initiale Planungsübergänge zu `expected`, `requested`, `proposed`,
`unassigned`, `red`, `catalogued` oder `open` dürfen leere `evidenceRefs`
besitzen. Ein normaler EVID-Übergang zu `captured`, `verified`, `invalidated`
oder `superseded` nennt in `evidenceRefs` exakt seine eigene EVID-ID; der
Validator prüft den vollständigen resultierenden EVID-Payload einschließlich
Artefakthash, Rollen-Snapshots und gegebenenfalls genehmigter Review. So
entsteht keine unendliche Evidenzkette. Für diesen Selbstverweis gilt die
`governanceChangeDigests`-Pflicht ausdrücklich nicht; damit enthält der
resultierende EVID-Hash keinen kryptografischen Fixpunkt. Seine
Lebenszyklusgültigkeit folgt ausschließlich aus Artefakt-/Payloadhash,
Attestation, Rollen-Snapshots und Review-Verweisen.

Jeder andere Übergang, `handover`, `recovery`, `custodian-rotation` und jedes
`amend` benötigt
mindestens eine EVID, die im unmittelbar vorherigen Replayzustand bereits
`captured` oder `verified` ist, den EVT-`changeDigest` in
`governanceChangeDigests` enthält und deren `scope` exakt
`governance-change:<recordRef>:<eventKind>:<previousRecordSha256-or-null>:<resultingRecordSha256>`
entspricht. Einzige Ausnahme sind die Gate-Reset-EVTs einer TCB-Promotion:
Sie konsumieren gemeinsam die in Abschnitt 6.3 exakt definierte
Transaktions-EVID, sofern ihr eigener Change-Digest genau einmal im signierten
`gateResetPlan` steht und Plan sowie aktueller Gatezustand vollständig
übereinstimmen. Der String enthält keine Leerzeichen oder Zeilenumbrüche. Ihre vollständige Baseline ist gleich
oder Vorfahr der EVT-Basis. `baselineCommit` und Subjectmanifest binden dabei
den unveränderten Fachstand; `captureBaseCommit` bindet den bereits
existierenden Replayzustand, in dem die Capture-Transaktion beginnt. Für jeden
Commit zwischen beiden Baselines und Konsum beweist der Validator in First-
Parent-Reihenfolge zusätzlich eine gültige externe Acceptance-Receipt und den
Governance-only-Vertrag dieses Abschnitts. Vorhandene REV-/EVID-Records dürfen
nur über ihre geschlossenen Transitionen – insbesondere
`requested→approved|changes-required`, `captured→verified|invalidated` und die
beiden reziproken Supersession-Lebenszyklen – fortgeschrieben werden; bereits
fixierte Capture-, Review- und Semantikfelder bleiben unverändert. Ein
dazwischenliegender Code-, Rollen-, Gate-, Control-, REQ-, Risiko-, Daten-,
Profil-, Ausnahme-, Trust-Root-, Schema-, Workflow- oder Validatorwechsel
macht die Evidenz stale und verlangt Re-Capture/Re-Review. Die für den
konsumierenden Übergang erforderliche Fachänderung liegt daher vor der
Evidenzbaseline, nie zwischen Evidence-Capture und Freigabe-Event.

Jede in einem nicht-EVID-EVT genannte EVID muss diese Bedingungen erfüllen;
sachfremde Belege dürfen nicht dekorativ mitgeführt werden. EVID-Scope,
Change-Digest und Baseline sind nach Capture unveränderlich.
Schema-Zustandsbedingungen gelten zusätzlich.

Für `eventKind: "transition"` müssen `fromStatus` und `toStatus` verschieden
sein und der Wechsel in der geschlossenen Tabelle stehen. Für
`eventKind: "amend"` sind beide Statuswerte identisch. Ein Amendment ändert
genau einen bestehenden Record, aber keinen Lebenszykluszustand. Es ist nur in
folgender geschlossener Matrix erlaubt; der Validator vergleicht die
geänderten Top-Level-Felder mit der Feldfreigabe:

| Record | Erlaubte Zustände | Änderbare Felder zusätzlich zu `title`, `sourceRefs`, `reviewOn`, `ownerRole` |
|---|---|---|
| REQ/CTRL/COMP/PROFILE | `proposed` | alle typspezifischen Felder, soweit sie nicht unten unveränderlich sind |
| ROLE | `unassigned` | `qualificationRequirements`, `separationFromRoleRefs` |
| RISK | `open`, `treated` | alle typspezifischen Felder außer Akzeptanzfeldern |
| DATA/FLOW | `catalogued`, `planned` | alle typspezifischen Felder, soweit sie nicht unten unveränderlich sind |
| GATE | `red`, `amber` | `entryCriteria`, `exitCriteria`, `requiredEvidenceRefs`, `verifierRoleRefs`, `approverRoleRefs`, `expiresOn` |
| REV | `requested` | `subjectIds`, `subjectPaths`, `scope`, `evidenceSubjectRefs`, `reviewerRole`, `independentFrom`, `reviewerExecution`, `modelName`, `reasoningLevel`, `promptDigest`, `reasoningApprovalEvidenceRef`, `externalReviewEvidenceRefs`, `evidenceRefs`, `expiresOn` |
| EVID | `expected` | `evidenceType`, `producerRole`, `subjectIds`, `subjectPaths`, `scope`, `command`, `derivationRefs`, `governanceChangeDigests`, `retentionRule` |
| EXC | `requested` | `scopeIds`, `justification`, `compensatingControlRefs`, `requestedByRole`, `expiresAt`, `evidenceRefs`, `blockedGateRefs` |

Für ROLE sind `ownerRole`, für REV und EVID die gemeinsamen Felder nur dann
änderbar, wenn sie in der Tabelle ausdrücklich vorkommen; die pauschale
Common-Feldfreigabe gilt für diese drei Typen nicht. Während eines `amend`
sind immer unveränderlich
`id`, `status`, Rollenbelegung und Assignee-Snapshots, Zeitpunkte, Commit-
Baselines, Creation-/Capture-/Decision-Epochen, Artefaktpfad und -hash,
Verdict, Findings und Finding-Resolutions,
Risikoakzeptanzfelder, Gate-`noWaiver`, Gate-Baseline, Gate-Review- und
Ausnahmereferenzen, Ausnahmegenehmigung/-widerruf sowie alle Supersession-
Referenzen. Die zwei ausdrücklich normierten Supersession-Lifecycle-Events
sind keine Amendments. REV, EVID oder andere finalisierte beziehungsweise aktive Records
können nicht amendiert werden; fachliche Änderungen benötigen einen neuen
Record mit formaler Supersession oder einen ausdrücklich erlaubten
Lebenszyklusübergang.

`exceptionProvenanceRefs` ist kein frei änderbares Amendmentfeld. Der
Validator darf bei einem ansonsten zulässigen Event ausschließlich die von
ihm neu berechnete monotone Mengenvergrößerung verlangen; Entfernen oder
manuelles Hinzufügen scheitert.

`handover` und `recovery` gelten ausschließlich für `ROLE-OPERATOR` mit
`assigned→assigned`; sie sind keine Amendments. Handover speichert im EVT den
ausgehenden Operator als Akteur/Snapshot und benötigt getrennte gültige
Attestationen mit den Zwecken `actor`, `recovery-root` und
`incoming-operator` des ausgehenden Operators, des extern gepinnten Offline-
Recovery-Roots und des eingehenden Operators über denselben Event-Core in
jeweils eigenen Envelopes. Der
Zielrecord enthält neuen Assignee, neuen Key und `operatorEpoch` exakt
`alte Epoch + 1`; Identitäts- und Übergabeevidenz sind `verified`. Der
ausgehende Operator kann damit eine geplante Übergabe anstoßen, aber weder
allein einen Nachfolger einsetzen noch den Offline-Root umgehen.

Recovery ist nur zulässig, wenn der reguläre Operator nach dokumentiertem
Incident nicht verwendbar oder kompromittiert ist. `actorRole` ist
`ROLE-RECOVERY-ROOT`; dessen `recovery-root`-Attestation erfüllt für dieses
Sonderereignis zugleich die Akteurauthentifizierung. Vor dem ersten jemals
grünen `GATE-PILOT` sind exakt Recovery-Root und eingehender Operator
erforderlich. Sobald `GATE-PILOT` historisch einmal `green` war, sind
zusätzlich die beiden bereits vorher `assigned`, qualifizierten, paarweise
verschiedenen menschlichen `ROLE-RECOVERY-CUSTODIAN-A/B` mit den Zwecken
`custodian-a` und `custodian-b` erforderlich. Der Zielrecord setzt Assignee,
Key und `operatorEpoch` exakt auf `alte Epoch + 1`. Weder der kompromittierte
Operator noch ein einzelner Custodian kann Recovery autorisieren.

Die erstmalige Besetzung eines Custodians ist ausschließlich vor dem ersten
Pilot-Green als `unassigned→assigned`-Transition zulässig. Akteur ist der
aktuelle Operator; erforderlich sind getrennte Attestationen `actor`,
`recovery-root` und – passend zur Zielrolle – `incoming-custodian-a` oder
`incoming-custodian-b` über denselben Event-Core. Kandidatenidentität und -key
sind von Operator, Root und anderem Custodian verschieden, die geforderte
Qualifikations- und Identitätsevidenz ist `verified`, und der Kandidat signiert
seine Annahme mit dem einzuführenden Key. Nur Operator und Root autorisieren;
die eingehende Signatur ist Besitz-/Annahmenachweis. Eine reine
Operatorzuweisung genügt nicht.

Sobald `GATE-PILOT` jemals grün war, dürfen beide Custodian-Rollen durch normale
Transitionen oder Amendments weder `unassigned`, `suspended`, `retired` noch
umgeschlüsselt werden. Geplanter Austausch genau eines Custodians erfolgt
ausschließlich als `custodian-rotation` mit `assigned→assigned`. Akteur ist der
Offline-Recovery-Root. Beim Austausch von A sind die Zwecke `recovery-root`,
`custodian-b` und `incoming-custodian-a`, beim Austausch von B entsprechend
`recovery-root`, `custodian-a` und `incoming-custodian-b` erforderlich. Der
verbleibende und der eingehende Custodian sind getrennte qualifizierte Menschen;
alle Assignees, Public Keys und Fingerprints bleiben paarweise verschieden. Die
Transaktion setzt zuvor sämtliche grünen Gates ausschließlich mit
Recovery-Root und verbleibendem aktiven Custodian auf `red`; der Kandidatenkey
darf diese früheren Events nicht signieren. Erst das abschließende ROLE-EVT
wird durch Root und verbleibenden Custodian autorisiert und enthält zusätzlich
den nicht autorisierenden Besitz-/Annahmenachweis des Kandidaten. Es bindet
verifizierte Identitäts-, Qualifikations- und Übergabeevidenz, fügt den neuen
Key hinzu und widerruft den alten Key.

Erstbesetzung und Rotation werden extern durch einen
`entryKind: "custodian-pin-transition"`-Eintrag abgeschlossen. Dessen
spezifischer Payload enthält ausschließlich `pinTransitionId`,
`custodianRole`, `transitionKind: "initial-assignment"|"rotation"`,
`previousPinEpoch`, `pinEpoch` exakt um eins erhöht, `previousAssigneeRef`,
`previousKeyRef`, `previousKeyFingerprint`, `nextAssigneeRef`, `nextKeyRef`,
`nextKeyFingerprint`, `roleEventId`, `roleEventSha256`, `acceptanceReceiptId`,
`headCommit`, `headTreeOid`, `effectiveAfterCheckpoint: true`,
`pinTransitionCoreSha256` und `transitionSignatures`. Der Core umfasst alle
spezifischen Payloadfelder außer sich selbst und `transitionSignatures`. Bei
Erstbesetzung sind `previousPinEpoch: 0`, `pinEpoch: 1` und
die drei Previous-Identitäts-/Keyfelder `null`; Operator, Root sowie Kandidat signieren.
bei Rotation signieren Root, verbleibender aktiver Custodian und Kandidat. Die
nach `purpose,keyRef` sortierten Einträge enthalten ausschließlich `purpose`,
`signerRole`, `signerIdentity`, `keyRef`, `signedAt`, `nonce`,
`pinTransitionCoreSha256` und `signature`; der Kandidaten-Purpose lautet
`incoming-custodian-a|b` und bleibt ein Annahmenachweis, während nur die in der
jeweiligen alten Schwelle liegenden Purposes autorisieren. Event-, Receipt-,
Head-/Tree- und Keydaten müssen bytegleich zur Repositorytransaktion sein.

Der neue externe Pin wird erst aus dem vollständigen Logpräfix ab dem ersten
Vollquorum-Checkpoint über diesen Eintrag wirksam. Bis dahin ist die ROLE trotz
Repositorytransition extern `pending`, darf keine Recovery-/TCB-Schwelle
erfüllen und hält alle Gates `red`. Verifier leiten aktuelle Custodian-Pins und
Pin-Epochen ausschließlich aus Genesis plus Log ab; opaque, einseitig
aktualisierte Pin-Caches oder gesplittete Sichten sind ungültig. Erst neue
Reviews und Evidenzen dürfen Gates wieder aktivieren.
Sind beide Custodians verloren oder nicht unabhängig verfügbar, bleibt das
System fail-closed; G0 definiert keine Einpersonen- oder Operator-Umgehung und
verlangt vor jeder Wiederaufnahme einen separat freigegebenen physischen und
governance-seitigen Recovery-Vertrag.

Handover und Recovery sind atomare Mehrfachrecord-Transaktionen. Ebenso ist die
oben definierte Custodian-Rotation ein atomarer Sonderübergang. Vor dem
ROLE-Wechsel wird jedes aktuell grüne Gate mit einem eigenen, zum selben
atomar validierten Git-Commit gehörenden EVT auf `red` gesetzt. Beim Handover
attestieren ausgehender Operator und Recovery-Root jeden Reset; bei Recovery
der Recovery-Root und, nach erstmaligem Pilot-Green, beide Custodians. Erst
danach folgt der ROLE-Wechsel mit Key-Ergänzung und Widerruf des alten
Operator-Keys. Handover verlangt verifizierte Identitäts- und
Übergabeevidenz. Recovery verlangt mindestens eine bereits `captured`, an
Incident, Kandidatenkey, Scope und changeDigest gebundene Evidenz mit
vollständigem Inputmanifest; nach erstmaligem Pilot-Green müssen zusätzlich
zwei getrennte, von Custodian A beziehungsweise B erzeugte und attestierte
`approval-record`-EVID vorliegen. Fehlt ein erforderlicher Reset, eine Attestation, die
jeweils vorgeschriebene Evidenz oder die exakte Epoch-Erhöhung, schlägt
der gesamte Commit fehl. Alte Reviews, Evidenzen, Ausnahmen,
Risikoakzeptanzen und Freigabe-Events werden niemals umgeschrieben oder
physisch invalidiert; ihre frühere Epoch macht sie lediglich als aktive
Stütze unwirksam. Vor erneutem Gate-Green sind neue Reviews, Evidenzen und
Betreiberfreigaben in der neuen Epoch erforderlich.

`ROLE-OPERATOR` darf außerhalb von Genesis, Handover oder Recovery weder
`unassigned`, `suspended` noch `retired` werden; ein irreversibler
Ein-Operator-Lockout ist damit ungültig. `ROLE-RECOVERY-ROOT` muss bereits vor
`GATE-G0 green` getrennt vom Operator `assigned`, mit dem im Pre-Ledger-Bundle
gebundenen aktiven Key extern gepinnt und offline wiederherstellbar sein.
Beide Recovery-Custodians müssen vor jedem Pilot-Green paarweise getrennt
besetzt und mit extern gepinnten aktiven Keys versehen sein. Recovery-Root und
Custodians sind Break-glass-Identitäten ohne Online- oder Normalbetriebsrecht.

Für jeden normalen EVT wird `actorRole` gegen den Replayzustand unmittelbar
vor dem Event aufgelöst. Die Rolle muss `assigned` sein und
`actorAssigneeSnapshot` muss bytegleich ihrer damaligen `assigneeRef` sein.
Zusätzlich gilt die geschlossene Autorisierungsmatrix:

| Record/Operation | Zulässiger Akteur |
|---|---|
| ROLE `null→unassigned` | `ROLE-ORCHESTRATOR` oder `ROLE-OPERATOR` |
| `ROLE-RECOVERY-ROOT null→assigned` | ausschließlich einmalig im initialen Seed, `ROLE-OPERATOR` plus `recovery-root`-Attestation gegen den bereits durch EVT-000001 aktiven Pre-Ledger-Key |
| Custodian `unassigned→assigned` vor erstem Pilot-Green | `ROLE-OPERATOR`; zusätzliche Attestationen von `ROLE-RECOVERY-ROOT` und eingehendem Ziel-Custodian |
| Custodian-Rotation `assigned→assigned` | `ROLE-RECOVERY-ROOT`; der verbleibende Custodian co-autorisiert, der eingehende attestiert nur Annahme; alle grünen Gates werden zuvor von Root plus verbleibendem Custodian atomar zurückgesetzt |
| ROLE-Handover | ausgehender `ROLE-OPERATOR`; zusätzliche Attestationen von `ROLE-RECOVERY-ROOT` und eingehendem Operator |
| ROLE-Recovery | `ROLE-RECOVERY-ROOT`; zusätzliche Attestation des eingehenden Operators sowie nach erstmaligem Pilot-Green beider Custodians |
| sonstige ROLE-Übergänge/Amendments | `ROLE-OPERATOR`; für `ROLE-OPERATOR`, `ROLE-RECOVERY-ROOT` und nach erstmaligem Pilot-Green beide Custodian-Rollen selbst verboten |
| GATE nach `green` | ausschließlich `ROLE-OPERATOR` |
| GATE nach `red`, `amber` oder `expired` | `ROLE-OPERATOR` oder eine im Ziel-Gate genannte Verifierrolle; im Handover-Bündel Operator plus Recovery-Root, im Recovery-Bündel Recovery-Root und nach erstmaligem Pilot-Green beide Custodians, bei Custodian-Rotation ausschließlich Recovery-Root plus verbleibender aktiver Custodian |
| REV `null→requested` oder Amendment | `ROLE-ORCHESTRATOR` oder `ROLE-OPERATOR` |
| REV nach `changes-required` oder `approved` | exakt `reviewerRole` der Ziel-Review |
| REV nach `superseded` | `ROLE-ORCHESTRATOR` oder `ROLE-OPERATOR` |
| EVID `null→expected` oder Amendment | Ziel-`producerRole`, `ROLE-ORCHESTRATOR` oder `ROLE-OPERATOR` |
| EVID nach `captured` | exakt `producerRole` der Ziel-Evidenz |
| EVID nach `verified` oder `invalidated` | exakt `verifiedByRole` der Ziel-Evidenz |
| EVID nach `superseded` | `ROLE-ORCHESTRATOR` oder die gespeicherte Verifierrolle |
| EXC `null→requested` oder Amendment | `ROLE-ORCHESTRATOR` oder `ROLE-OPERATOR` |
| EXC nach `approved`, `revoked` oder `expired` | ausschließlich `ROLE-OPERATOR` |
| RISK nach `accepted` | ausschließlich `ROLE-OPERATOR` |
| RISK sonst | Ziel-`ownerRole`, `ROLE-ORCHESTRATOR` oder `ROLE-OPERATOR` |
| REQ/CTRL/COMP/PROFILE nach `approved`, `active` oder `verified` sowie DATA/FLOW nach `active` | ausschließlich `ROLE-OPERATOR` |
| sonstige REQ/CTRL/COMP/PROFILE/DATA/FLOW-Operation | Ziel-`ownerRole`, `ROLE-ORCHESTRATOR` oder `ROLE-OPERATOR` |

Die Matrix ersetzt keine fachliche Funktionstrennung: Gate-, Review-,
Qualifikations- und Snapshotregeln aus Abschnitt 7 und 12.4 gelten zusätzlich.
Der Betreiber kann einen Recordzustand setzen, aber keine fehlende unabhängige
Fachevidenz oder Pflichtrolle ersetzen.

Der Validator führt den Zeitvergleich normativ aus:

1. Für uncommittete lokale Änderungen ist die Basis `HEAD` und das Ziel der
   Working Tree. Für einen Commitcheck werden `--base <sha> --head <sha>`
   explizit übergeben.
2. Er liest die Register der Basis mit `git show <base>:<path>`. Vorhandene
   EVT-Objekte müssen im Ziel nach RFC-8785-Kanonisierung identisch und in
   derselben Reihenfolge als Präfix erhalten bleiben; nur Anhängen ist erlaubt.
3. Beim Erstimport existieren in der Basis keine Governance-Register. Dann
   sind ausschließlich vollständige Seed-Records mit je einem
   `fromStatus: null`-EVT und dem exakt dreiteiligen Genesis-Bündel zulässig.
4. Er prüft zunächst globale ID-, Array-, Zeit- und Eventhashkette. Danach
   spielt er neue Events in Arrayreihenfolge ab, prüft pro Transaktion die
   Ein-Event-je-Record-Regel, erlaubten Übergang oder Amendment,
   kryptografische Attestations- und Trust-Root-Kette, Akteurautorisierung,
   Evidenz-/Scope-/Baselinebindung, Ausnahmeprovenienz, Recordhash,
   Change-Digest und `baseCommit`. Handover, Recovery und Custodian-Rotation
   werden als atomare Sonderbündel geprüft. Der resultierende Record muss exakt dem kanonischen
   Zielrecord entsprechen.
5. Bei EVID `null|expected→captured` wird der Producer-Snapshot erstmals aus
   der unmittelbar vor diesem Event gültigen Rollenbelegung gesetzt und danach
   unveränderlich. Bei REV
   `requested→changes-required|approved` werden Reviewer-, Independent-,
   Subject-Actor- und Approver-Snapshots gesetzt und danach unveränderlich.
   Bei EVID `captured→verified` wird der Verifier-Snapshot gesetzt und danach
   unveränderlich. Der Validator vergleicht jeden Snapshot mit der unmittelbar
   vor dem jeweiligen Event gültigen, bereits abgespielten Rollenbelegung.
6. CI prüft jeden Commit eines vorgeschlagenen Bereichs in First-Parent-
   Reihenfolge einzeln. Ein Merge-Commit darf Governance-Register nicht
   verändern; solche Änderungen werden linear per Rebase oder Cherry-Pick
   integriert. Dadurch kann kein Zwischenübergang übersprungen werden.
7. Der geschützte CI-Lauf prüft zusätzlich den extern gepinnten Operator-
   Fingerprint, Branchschutz/Bypass-Konfiguration, signierte Commits,
   Attestationsnonces sowie die vertrauenswürdige Laufzeit. Er liest den
   tatsächlichen Head-Blob und -Tree, nicht nur einen vom PR deklarierten
   Basiscommit, und erzeugt erst nach vollständiger Prüfung das unveränderliche
   Acceptance-Receipt. Bei historischem Replay verifiziert der Offline-
   Validator das exportierte Transparency-Bundle gegen den extern gepinnten
   Genesis-Instanzkey, die vollständigen Entry-, Checkpoint- und Witness-Floor-
   Ketten sowie die daraus neu berechneten Loghashes, Merkle-Roots und
   Checkpointkonsistenzwerte. Separate Inklusions-/Konsistenzbeweise sind weder
   enthalten noch vertrauenswürdig. Zusätzlich werden Policy-/TCB-Transitions,
   Head-/Tree-OIDs sowie sämtliche Event-, Envelope- und Nonce-Digests geprüft.
   Bei aktueller Gateprüfung ist der letzte Vollquorum-Checkpoint höchstens
   eine Stunde alt und alle live abgefragten Witness-Floors sind frisch. Ein
   lokaler grüner Lauf ohne diese externen Inputs ist nur Vorprüfung.

Direktes `expected→verified`, direkte Erzeugung als `superseded`, Änderung
alter Snapshots, Eventlöschung, Eventumsortierung, ID-Lücke, Rückdatierung,
Hashneuberechnung ohne passenden Basiszustand, ein zweites Event desselben
Records in einer Transaktion, nicht autorisierte Akteure, ungebundene Evidenz,
ungültige oder fehlende Signaturen, Trust-Root-Selbsteinführung,
Zukunftszeit, stale Zwischencommits, unerlaubte Amendments und mehrere
Statussprünge in einem EVT werden abgewiesen.

### 12.6 Geschlossenes initiales G0-Manifest

Der Validator prüft die folgenden Seeds und Coverage-Regeln. Ein kleinerer
Satz ist kein gültiges G0:

1. `REQ-HR-01` bis `REQ-HR-22` bilden die 22 Hard Rules aus
   `AGENTS.project.md` einzeln und wortgetreu auf Requirements ab.
2. `REQ-GOV-001` bis `REQ-GOV-012` decken Quellenpräzedenz, Traceability,
   Funktionstrennung, Reasoning-Bestätigung, externe LLM-Sanitisierung,
   eingeschränkten Serverzugriff, No-Waiver, In-place-Härtung,
   kryptografische Akteurauthentifizierung, transitive Ausnahmeprovenienz,
   Operator-Recovery und vertrauenswürdige Zeit ab.
3. Initiale Controls sind `CTRL-GOV-SOURCE-PRECEDENCE`,
   `CTRL-GOV-TRACEABILITY`, `CTRL-GOV-INDEPENDENT-REVIEW`,
   `CTRL-GOV-REASONING-CONFIRMATION`,
   `CTRL-GOV-EXTERNAL-LLM-SANITIZATION`, `CTRL-GOV-SERVER-ACCESS`,
   `CTRL-GOV-NO-WAIVER`, `CTRL-GOV-VALIDATOR`,
   `CTRL-GOV-ACTOR-ATTESTATION`, `CTRL-GOV-BRANCH-PROTECTION`,
   `CTRL-GOV-EXCEPTION-PROVENANCE`, `CTRL-GOV-OPERATOR-RECOVERY` und
   `CTRL-GOV-INVENTORY-COLLECTOR`.
4. Initiale Profile sind `PROFILE-PREVIEW` und
   `PROFILE-DEBIAN-PILOT`. Preview erlaubt ausschließlich synthetische Daten
   und keine Produktionsidentität, Hardware oder produktiven Secrets.
5. Das Rollenregister enthält exakt alle Rollen aus Abschnitt 7.
   `ROLE-OPERATOR` ist `assigned`, `requiredHuman: true`,
   `assigneeKind: "human-account"`, `assigneeRef: "redshift-three67"` und
   `operatorEpoch: 1`.
   `ROLE-ORCHESTRATOR` ist als agentische Rolle gekennzeichnet. Taskbezogene
   technische Rollen dürfen bis zur Beauftragung `unassigned` bleiben.
   `ROLE-RECOVERY-ROOT` ist getrennt `assigned`, offline, ohne
   Normalbetriebsrecht und mit dem Pre-Ledger-/externen Pin-Key belegt; fehlt
   diese Belegung, bleibt bereits `GATE-G0` rot. Privacy, Legal, Pentest,
   Hardware, A11y/Claims und beide Recovery-Custodians sind
   `requiredHuman: true`, zunächst `unassigned` und halten
   ihre zugehörigen Gates `red`. Vor Pilot-Green sind beide Custodians
   getrennt zu besetzen und ihre Trust-Roots extern zu pinnen.
6. Das Komponentenregister enthält als zwingende G0-Teilmenge `COMP-BROWSER`, `COMP-EDGE`,
   `COMP-CONTROL`, `COMP-DATA`, `COMP-COMPUTE`, `COMP-BACKUP`,
   `COMP-IDENTITY`, `COMP-EXPORT` und `COMP-DELETE`. Die initialen G0-Flows
   verwenden nur diese kanonischen IDs. Zusätzliche Komponenten sind zulässig,
   benötigen aber vor ihrer Referenz
   einen genehmigten COMP-Record mit REQ-, CTRL- und GATE-Verknüpfung. Ein
   zusätzlicher `componentKind` oder eine zusätzliche Trust-Zone benötigt eine
   genehmigte Schema- und Spezifikationsänderung.
   Kind/Trust-Zone sind fest: Browser=`browser/client`, Edge=`edge/public-edge`,
   Control=`control-plane/control`, Data=`data-store/sensitive-data`,
   Compute=`compute-worker/compute`, Backup=`backup/backup`,
   Identity=`identity/control`, Export=`export/lifecycle` und
   Delete=`delete/lifecycle`.
7. Initiale Risiken sind `RISK-GOV-DRIFT`, `RISK-GOV-SELF-APPROVAL`,
   `RISK-GOV-EXTERNAL-DISCLOSURE`, `RISK-GOV-UNTRACEABLE-EXCEPTION`,
   `RISK-MG1-SINGLE-ORIGIN`, `RISK-MG1-INPLACE-CHANGE` und
   `RISK-REASONING-MISMATCH` sowie `RISK-GOV-FORGED-ACTOR`,
   `RISK-GOV-STALE-EVIDENCE`, `RISK-GOV-OPERATOR-LOCKOUT` und
   `RISK-GOV-TIME-POISONING`.
8. Initiale Datenobjekte sind `DATA-PUBLIC`, `DATA-CONTROL`, `DATA-ART9`,
   `DATA-SECRETS`, `DATA-AUDIT` und `DATA-BACKUP`.
9. Initiale Flows sind `FLOW-BROWSER-EDGE`, `FLOW-EDGE-CONTROL`,
   `FLOW-CONTROL-DATA`, `FLOW-DATA-COMPUTE`, `FLOW-DATA-BACKUP`,
   `FLOW-IDENTITY`, `FLOW-EXPORT` und `FLOW-DELETE`. Ihre Richtung ist
   fest: Browser→Edge, Edge→Control, Control→Data, Data→Compute, Data→Backup,
   Browser→Identity, Data→Export und Data→Delete.
10. Alle neun Gates aus Abschnitt 13 müssen als `red` gesät werden. G0 selbst
   darf erst nach vollständiger Implementierung und Review auf `green` wechseln.
11. Initiale Reviews sind `REV-G0-ELABORATION-AUTHORIZATION`,
   `REV-G0-DESIGN-APPROVAL`,
   `REV-G0-SPEC-REVIEW`, `REV-G0-QUALITY-REVIEW` und
   `REV-G0-FINAL-REVIEW`. Die Ausarbeitungsfreigabe bleibt historisch auf
   `designBaselineCommit` begrenzt; nur die separat signierte
    Designfreigabe darf den finalen Designcommit genehmigen. Nicht
    abgeschlossene Reviews bleiben `requested`; alle initialen REV führen
    `createdEpoch: 1`, unbeendete zusätzlich `decisionEpoch: null`.
12. Initiale Evidenzen sind `EVID-G0-BASELINE-GATES`,
    `EVID-G0-DESIGN-COMMIT`, `EVID-G0-FINAL-DESIGN-APPROVAL`,
    `EVID-G0-CONTRACT-TESTS` und `EVID-G0-FINAL-GATES`. Noch nicht erzeugte Evidenz wird als `expected` mit
    `createdEpoch: 1`, `captureEpoch: null`, `decisionEpoch: null` und den
    dafür erlaubten Nullfeldern geführt und kann kein Gate grün machen. Direkt
    erfasste Genesis-EVID setzt Creation/Capture auf `1`.
13. Das initiale `exceptions`-Array ist leer. Trust-Roots enthalten den extern
    gepinnten Operator-Key, den unabhängig extern gepinnten Offline-Recovery-
    Root-Key und den durch das doppelt signierte Pre-Ledger-Bundle
    autorisierten Orchestrator-Key; private Schlüssel sind ausgeschlossen. Die
    davon getrennten externen Kontroll-Pins enthalten exakt den Validator-
    Controller-Key sowie `logId`, Instanzkey mit Epoch `1` und sämtliche
    mindestens zwei Witness-Keys aus Pre-Ledger und Genesis; Repositorydaten
    allein dürfen keinen dieser Pins ersetzen.
14. Jeder Seed-Record besitzt genau ein initiales EVT mit fortlaufender
    sechsstelliger ID, `fromStatus: null`, passendem Zielstatus und
    `baseCommit` gleich dem Commit unmittelbar vor dem Erstimport. Die ersten
    drei Einträge sind exakt das Genesis-Bündel aus Abschnitt 12.5; alle
    übrigen Seeds folgen topologisch, sodass Akteurrollen und konsumierte
    Evidenzen im Replay bereits existieren. Die vollständige Eventmenge
    rekonstruiert alle vier Register ohne Rest.
15. Jede vorhandene Produkt-ID aus `D01–D24`, `C01–C12`, `X01–X20`,
    `U01–U12`, `K1–K8`, `L01–L09`, `H1–H8`, `O01–O10` und `WV01–WV06`
    muss mindestens einmal in `productDecisionRefs` vorkommen. Der Validator
    löst Quelle und aktuellen Status ausschließlich über den read-only
    `productDecisionIndex` auf und weist fehlende oder zusätzliche IDs ab.
16. Jede WV-ID nennt Owner, konkreten Trigger, benötigte Evidenz und das
    blockierte Gate. Jeder universelle Stop-Auslöser der
    Vorbereitungsspezifikation wird auf mindestens ein REQ, RISK und GATE
    abgebildet.
17. Jedes genehmigte REQ nennt mindestens einen CTRL oder einen ausdrücklich
    `proposed` Control mit rotem Gate; es darf keine scheinbar erfüllte
    Anforderung ohne Verifikation geben.

## 13. Initiale Stop-Gates

| Gate | Bedeutung |
|---|---|
| `GATE-G0` | Kein verbindlicher Threat-Model- oder Architektur-Sign-off ohne Quellenhierarchie, Rollen, IDs, Traceability, extern gepinnte Trust-Roots, signierte Events, Branchschutz und Baseline |
| `GATE-DATAFLOW` | Kein vollständiges Threat Model ohne DATA-/FLOW-Inventar und Trust Boundaries |
| `GATE-PROFILE` | Keine Produktionsidentität oder Secrets ohne belegte Trennung `preview-synthetic`/`debian-pilot` |
| `GATE-ART9` | Keine realen Daten ohne Backup-Ort, Restore, Privacy-/Legal-Prüfung, RLS-Negativtests, Grants, Retention, Löschung und Incident-Prozess |
| `GATE-MODULE` | Modul bleibt `executable: false`, bis Herkunft, Lizenz, Hash, Schemas, Testvektoren, Reproduzierbarkeit, Budget, CopyGuard und Passport geprüft sind |
| `GATE-CUDA` | CUDA bleibt aus, bis Tenant-/Client-/Job-Isolation, Budget, OOM, Reset und Attestation geprüft sind |
| `GATE-HARDWARE` | USB/Emitter/Sensor bleibt aus, bis Geräteprüfung, Lease-Arming-ACK, Abbruch, Rollen und Audit belegt sind |
| `GATE-PILOT` | Kein Pilot-Release bei rotem Claim-, A11y-, Restore-, Isolation-, Secret-, Migrations-, Recovery-, Collector- oder Qualitätsgate |
| `GATE-24X7` | Keine 24/7-Zusage ohne zweite EU-Fehlerdomäne und Failover-Nachweis |

Unabhängig von den tabellarischen Kriterien darf `GATE-G0` nur bei extern
gepinntem, offline wiederherstellbarem `ROLE-RECOVERY-ROOT`, gültigem
Validator-Controller-, Recovery-App-, Recovery-Write-ahead-Gateway-,
Provider-Ref-Verifier-, Egress-Enforcement-Monitor-, Transparenzinstanz- und vollständigen Witness-Pins,
gültigem Bootstrap-Validator-Receipt samt frischem co-signierten Checkpoint und
aktueller Operator-Epoch grün werden.
`GATE-PILOT` verlangt zusätzlich beide getrennten menschlichen Custodians mit
extern gepinnten Keys. Für Recovery-Root, Validator-Controller, Recovery-App,
Recovery-Write-ahead-Gateway, Provider-Ref-Verifier, Egress-Enforcement-Monitor,
Transparenzinstanz, jeden Witness, beide Custodian-Pins und die TCB-/Branch-
Wiederherstellung müssen jeweils geschlossene Rotations-, Verlust- und
Kompromittierungsverträge genehmigt, in einer isolierten Testumgebung praktisch
durchlaufen und durch aktuelle EVID-/REV-Akten belegt sein. Ein lediglich
dokumentierter, ungetesteter oder von einem ausgefallenen Schlüssel selbst
abhängiger Notweg hält `GATE-PILOT` `red`.

Die universellen Stop-Auslöser der Vorbereitungsspezifikation bleiben
zusätzlich bindend.

## 14. Initiale Kanonkorrekturen in G0

G0 korrigiert ausschließlich unmittelbar governance-relevante Drift:

- `docs/23-id-schema.md` führt `WV` und die neuen Governance-IDs auf und
  bezeichnet `X` nicht mehr als offene Prüfung;
- `docs/00-index.md` verlinkt die Governance-Artefakte und `docs/25-offen.md`;
- `docs/07-identity.md` unterscheidet ausdrücklich Preview-Identität von den
  erst auf dem M-G1 aktivierbaren Passkeys unter WV03;
- Freigaben nennen zukünftig REV-ID, Scope und Baseline statt nur Datum oder
  Chat-Wort;
- bestehende Wiedervorlagen werden in Traceability und Gate-Register mit
  Owner, Trigger, benötigter Evidenz und blockiertem Gate gespiegelt.

Fachliche Inhalte von D-, C-, X-, U-, K-, H-, O- oder WV-Entscheidungen werden
in G0 nicht neu entschieden.

## 15. Fehler- und Änderungsverhalten

Der Governance-Validator arbeitet fail-closed. Ein Struktur-, Referenz- oder
Statusfehler liefert einen ungleich null Exitcode und nennt Datei, Eintrag und
verletzte Regel. Er schreibt keine Dateien und ändert keinen Status selbst.

Jede Governance-Änderung enthält:

- betroffene IDs und Baseline;
- Grund und erwartete Wirkung;
- Reviewer und benötigte Evidenz;
- Migrations- oder Rückrollwirkung;
- neues Reviewdatum.

Registerhistorie wird nicht überschrieben. Korrekturen erzeugen eine neue
REV-Akte; frühere Akten werden `superseded`, bleiben aber nachvollziehbar.

## 16. Abnahme von G0

G0 gilt erst als bestanden, wenn:

1. alle vorgesehenen Direktiven und Register vorhanden und im Index verlinkt
   sind;
2. Quellenhierarchie, Rollen, Reasoning-, Review-, externe LLM- und
   Serverzugriffsregeln widerspruchsfrei dokumentiert sind;
3. alle initialen IDs eindeutig und alle Referenzen auflösbar sind;
4. bekannte unbesetzte Fachrollen die zugehörigen Gates sichtbar `red` halten;
5. No-Waiver-Regeln maschinenprüfbar sind;
6. Trust-Root-, Attestations-, Branchschutz-, Zeit- und Operator-Recovery-
   Verträge einschließlich Negativtests grün sind;
7. die governance-relevanten Kanonkorrekturen abgeschlossen sind;
8. Governance-Vertragstests zuerst rot und nach Implementierung grün
   nachgewiesen wurden;
9. Canon-Check, Governance-Check, Typecheck, Lint, vollständige Tests und
   Diff-Check sequenziell grün sind;
10. Spec-Review, Quality/Security-Review und Gesamt-Review keine offenen
   P0–P2-Befunde besitzen;
11. der Betreiber den konkreten vollständigen Design- und späteren G0-Commit
    jeweils mit Dateihash, Scope und extern gepinntem Schlüssel signiert
    freigibt.

Ein grünes `GATE-G0` erlaubt nur den Übergang zur gemeinsamen Ausarbeitung von
Debian-Pilotprofil, Threat Model und Datenschutzdatenfluss. Es erlaubt keine
Produktivdaten und keine Serveränderung.

## 17. Folgereihenfolge

Nach G0 werden die Pakete in dieser Reihenfolge spezifiziert:

1. vorläufiges `debian-pilot`-Profil und Threat Model gemeinsam;
2. Datenschutzdatenfluss und DSFA-Zuarbeit;
3. Identität, Sitzungen, Rollen, RLS, Schlüssel, Audit und Datenlebenszyklus;
4. Betrieb, Observability, Kapazität, Incident Response, Backup/Restore,
   Migration, Deployment und Rollback;
5. Lieferkette und nicht umgehbare Release-Gates;
6. Modulaufnahme über Kernel-ABI und Labor-Sandbox;
7. vollständige Claims-/CopyGuard- und Accessibility-Prüfung;
8. integrierte End-to-End-Gesamtprüfung.

Grundinvarianten für nichtmedizinische Claims, CopyGuard und WCAG gelten ab G0
und werden nicht bis zum siebten Paket aufgeschoben.
