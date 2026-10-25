# AURELIA K1 – Kanonkonsolidierungsdesign

**Status:** Vom Betreiber am 2026-08-25 durch die Freigabe
`K1 – lokale Kanonkonsolidierung ab Commit 8706186` zur schriftlichen
Konsolidierung freigegeben. Diese Spezifikation autorisiert weder einen Push
noch Serverzugriff, Git-History-Rewrite, Produktivdaten, CUDA, USB oder eine
Änderung am M G1.

**Verbindliche Ausgangsbasis:**
`8706186af01e10e4253e25abb31bf3577110dae4`

**Lokaler Arbeitszweig:** `codex/aurelia-konsolidierung`

**Historische, unveränderte Referenzen:**

- Kanon-Implementierung: `b20ee873347c5fd767e2089c993f1cf93a625def`
- freigegebenes Governance-Design:
  `a6a8e7dca456d14a6748b204b787b235fdedf9be`
- Server-Ground-Zero-Planung: `8706186`

---

## 1. Zweck

K1 stellt einen einzigen lokal nachvollziehbaren AURELIA-Kanon her, ohne die
divergierenden Branches blind zu mergen. Der gültige Ubuntu-/Ground-Zero-Stand
aus `8706186` bleibt führend. Fachlich weiterhin gültige Bestandteile der
Kanon- und Governance-Linie werden selektiv, testgetrieben und mit eindeutiger
Provenienz neu übernommen.

K1 beseitigt insbesondere:

1. widersprüchliche Aussagen zu Video und WebRTC;
2. die Verwechslung zwischen gestarteter Phase-1-Schale und pausierter
   Produktarbeit;
3. Debian-, 2×1-TB- und veraltete Serverangaben in aktiven Quellen;
4. einen Kanonvalidator, der den inzwischen falschen Status erzwingen würde;
5. einen Windows-Testaufruf, der 149 vorhandene Tests als `0 tests` übersieht;
6. die nicht plattformübergreifende Vite-Prozessausführung;
7. noch vorhandene lokale Herkunftspfade in den V1-/V2-Manifesten;
8. die Namens- und Reihenfolgekollision zwischen Governance-G0 und
   Server-Ground-Zero.

## 2. Umfang und Nicht-Ziele

### 2.1 K1 umfasst

- einen neuen lokalen Branch und Worktree ab `8706186`;
- einen konsistenten Produkt- und Infrastrukturstatus in Konstitution,
  Dokumentation, UI-Texten und maschinenprüfbaren Regeln;
- No-Video-/No-WebRTC-Kanon;
- Ubuntu Server 24.04.4 LTS, 2×2-TB-SN850X und `G0-SRV-0…12`;
- Phase-1-Schale technisch vorhanden, Produktarbeit bis `G0-SRV-12` pausiert;
- Authentifizierung und Datenbank eingeschaltet, ausschließlich synthetische
  Daten;
- einen plattformübergreifenden, nicht false-green Testpfad;
- separate Abnahme der Vite-Portabilität und der bereits vorhandenen
  Lintbefunde;
- einen nicht-identifizierenden Provenienzverweis in den V1-/V2-Manifesten;
- eine neue, explizite Ergänzung zum unveränderten Governance-Design;
- dokumentierte Behandlung der nicht ausgeführten Governance-Planentwürfe;
- lokale statische, ausführbare und Browser-basierte Verifikation.

### 2.2 K1 umfasst ausdrücklich nicht

- Merge, Rebase, Reset oder Änderung der Historie bestehender Branches;
- Push, Pull Request, Merge nach `main` oder Änderung von GitHub-Einstellungen;
- Bereinigung bereits erreichbarer historischer Objekte auf GitHub;
- Serverzugriff, SSH, IPMI, Backupausführung oder Neuinstallation;
- Umsetzung der 14 Governance-Planentwürfe;
- Governance-Genesis, Schlüsselzeremonie, Signaturen oder externe Witnesses;
- produktive Authentifizierung, Datenmigration oder `npm run build`, solange
  dieser Befehl `db:migrate` ausführt;
- Rotation oder Entfernung eines Provider-Credentials ohne bestätigten
  Plattformvertrag;
- Produktfunktionen aus Phase 1 oder späteren Phasen.

## 3. Bewertete Integrationsansätze

### 3.1 Vollständiger Merge des Governance-Branches

Der Governance-Branch enthält den Kanon-Branch vollständig und würde die
Historie erhalten. Er enthält aber gleichzeitig veraltete Phase-1-, Debian-
und Validatorannahmen. Ein Git-Merge hätte nur drei Textkonflikte, könnte aber
zahlreiche semantische Widersprüche automatisch übernehmen.

**Entscheidung:** verworfen.

### 3.2 Alle Kanon-Commits cherry-picken

Das würde die Änderungen in kleinen historischen Einheiten übernehmen, aber
auch `b20ee87` und dessen heute falsche Aussage „Phase 1 gestartet“ mitsamt
unzureichender Validatorabdeckung importieren.

**Entscheidung:** verworfen.

### 3.3 Selektive, testgetriebene Neuübernahme auf `8706186`

Jeder weiterhin gültige Änderungskomplex erhält zuerst einen Test gegen den
aktuellen Ground-Zero-Kanon. Erst danach wird die minimale Implementierung
übernommen. Historische Commits werden in der Änderungsdokumentation genannt,
aber nicht als unkontrollierter Patch angewendet.

**Entscheidung:** verbindlicher Ansatz.

## 4. Quellenhierarchie für K1

Zwingendes Recht, Verträge und belegte technische Realität stehen stets über
Repositorydokumenten. Innerhalb des K1-Arbeitsstandes gilt:

1. ausdrückliche Betreiberfreigaben mit Scope und Commitbezug;
2. `AGENTS.project.md` und diese genehmigte K1-Spezifikation;
3. `docs/project-control/ground-zero/GATE-STATUS.md` für den aktuellen
   Server-Gatestatus;
4. `docs/STATUS.md` und `docs/09-roadmap.md`;
5. freigegebene Fachspezifikationen und historische Designs mit ihren
   dokumentierten Supersession-Grenzen;
6. maschinenlesbarer Produktkanon und Validatoren;
7. Tests;
8. UI-/Portaltexte und abgeleitete Darstellungen.

Ein Konflikt wird nicht automatisch aufgelöst. Der betroffene K1-Teil bleibt
rot, bis die höhere Quelle eindeutig umgesetzt ist.

## 5. Verbindliche Kanonmatrix

| Sachverhalt | K1-Zielzustand |
|---|---|
| Phase 0 | abgenommen |
| Phase 1 | Schale/Auth/Mandant technisch begonnen; Produktarbeit pausiert |
| Pausengrund | `G0-SRV-GROUND-ZERO` |
| Wiederaufnahme | erst nach dokumentiertem `G0-SRV-12` |
| Datenklasse | ausschließlich `synthetic` |
| Auth | an |
| Datenbank | an; keine produktive Migration durch K1 |
| Zielbetriebssystem | Ubuntu Server 24.04.4 LTS amd64 plus minimales GNOME |
| Storage | 2×2 TB WD_BLACK SN850X, geplantes RAID1/LUKS2/LVM |
| Video/WebRTC | vollständig ausgeschlossen; Phase 9 gestrichen |
| CUDA/USB/Art. 9 | gesperrt |
| Destruktive Serveraktionen | gesperrt, solange keine separate Freigabe nach `G0-SRV-0…2` vorliegt |
| Governance-G0 | historisches Designprogramm, in K1 als `GATE-GOV-0` bezeichnet |
| Server-Ground-Zero | eigenständiges Infrastrukturprogramm `G0-SRV-0…12` |

Die Formulierung „Phase 1 läuft“ ist ohne Qualifizierung verboten. Zulässig ist
nur die eindeutige Aussage, dass die Phase-1-Schale vorhanden ist, während die
weitere Produktarbeit bis zur Serverabnahme pausiert.

## 6. Branch- und Provenienzstrategie

K1 arbeitet ausschließlich in
`.worktrees/aurelia-konsolidierung` auf
`codex/aurelia-konsolidierung`. Die Branchspitzen `8706186`, `b20ee87` und
`a6a8e7d` werden nicht verändert.

Für jeden selektiv übernommenen Komplex dokumentiert der Implementierungsplan:

- historische Commitreferenz;
- weiterhin gültige fachliche Aussage;
- verworfene oder supersedierte Aussage;
- neue Tests gegen den gültigen K1-Kanon;
- resultierenden lokalen Commit.

Die lokalen Rohanalysen und `source/`-Ordner bleiben ignoriert. Kein `git add
-f` ist zulässig.

## 7. Arbeitspakete

### 7.1 K1-A – Sanitisierung und Projektsteuerung

Die absoluten lokalen Herkunftspfade in den Manifesten V1 und V2 werden durch
eine neutrale Herkunftskennung ersetzt. Die Berichte selbst und ihre
Zeitstempel bleiben unverändert. Das ist eine Tip-Bereinigung; die bereits auf
GitHub erreichbare Vorgängerversion bleibt ohne separat freigegebenes
History-Rewrite historisch sichtbar und wird daher nicht als vollständig aus
der Historie entfernt bezeichnet.

`docs/project-control` erhält einen K1-Status, der Branch, Baseline,
Schutzgrenzen, bekannte historische Offenlegung und fehlende Remote-Freigabe
eindeutig nennt.

### 7.2 K1-B – Toolchain- und Qualitätsbaseline

Der Testpfad darf keine Shell-Glob-Semantik voraussetzen. Ein Node-basierter
Runner ermittelt die freigegebenen Testdateien deterministisch, sortiert sie
und beendet sich rot, wenn eine erwartete Testgruppe leer ist. Er startet den
Node-Testprozess ohne Shell und propagiert Exitcode oder Signal.

Die am unveränderten `8706186` gemessene Baseline ist:

| Gate | Ausgangslage |
|---|---|
| `npm run typecheck` | grün |
| bisheriges `npm test` | irreführend grün; MJS-Gruppe `0 tests`, danach 24/24 TS-Tests |
| korrekt entdeckte `scripts/*.test.mjs` | 134/149 grün, 15 rot |
| `npm run lint` | 1 Fehler, 3 Warnungen |
| `npm run check:auth` ohne Dev-Server | bestimmungsgemäß unentscheidbar/rot |
| `npm run build:dev` | `spawn vite ENOENT` unter Windows |

Die 15 MJS-Fehler werden nicht pauschal durch Erwartungsänderungen beseitigt.
Sie werden nach Ursache getrennt:

1. veraltete Auth-off-Annahmen trotz verbindlichem Auth-on-Kanon;
2. repositoryabhängige PWA-Erwartungen, die AURELIA-`site.json` nicht isolieren;
3. Windows-Symlinktests ohne vorherige Capability-Prüfung;
4. veraltete Annahme, dass keine globbbaren Auth-/Tenantmigrationen existieren;
5. fehlende, ignorierte `public/__grok`-Plattformassets.

Tests verwenden danach synthetische temporäre Fixtures statt zufälligen
Workspacezustand. Ein nicht vorhandenes plattformverwaltetes Asset wird nicht
synthetisch erfunden: Entweder wird eine autoritative lokale Quelle belegt oder
das zugehörige Gate bleibt mit genauer Ursache rot.

Der Vite-Wrapper löst das installierte Vite-JavaScript-CLI paketbasiert auf und
startet es mit `process.execPath`, ohne Shell oder `.cmd`-Abhängigkeit. Die
Änderung wird unabhängig vom Kanon getestet.

Die bekannten Lintbefunde werden als separater, verhaltensneutraler Commit
bereinigt.

### 7.3 K1-C – Produktkanon, Dokumente und Portal

No-Video-/No-WebRTC-Aussagen aus der Kanonlinie werden neu übernommen. Dabei
bleiben die Ubuntu-Angaben aus `8706186` erhalten. Mindestens folgende aktiven
Quellen werden vollständig abgeglichen:

- `AGENTS.project.md`;
- `SECURITY.md`;
- `docs/STATUS.md`, `docs/02-architecture.md`,
  `docs/03-security-dsgvo.md`, `docs/09-roadmap.md`,
  `docs/11-llm-handoff.md`, `docs/14-hardware.md`, `docs/15-live.md`,
  `docs/20-freigabe.md`, `docs/23-id-schema.md`,
  `docs/24-standalone.md`, `docs/26-wiedervorlage.md`;
- `src/lib/concept/*` mit aktiven D-/C-/X-/U-/K-/H-/O-/WV-Aussagen;
- alle Portalrouten mit Phase-, Video-, Betriebssystem- oder Hardwaretexten.

Der neue Kanonvalidator prüft nicht nur einzelne Portalformulierungen. Er muss
mindestens fail-closed erkennen:

- fehlende oder falsche Phase-/Pausenmarker;
- Debian/Bookworm oder 2×1-TB-Angaben in aktiven Quellen;
- optionales oder nachrangiges WebRTC/Video;
- fehlende Ubuntu-24.04.4- und 2×2-TB-Zielwerte;
- fehlende `G0-SRV-0`-Destruktionssperre;
- fehlende Rohquellen-Ausschlussregeln;
- unvollständige oder doppelte Produkt-ID-Familien;
- eine UI-Aussage, die der Produktkonstitution widerspricht.

Historische Analysen und ausdrücklich als superseded bezeichnete Designs
werden nicht textuell umgeschrieben und durch Pfadregeln von aktiven
Kanonprüfungen getrennt.

### 7.4 K1-D – Governance-Ergänzung

`a6a8e7d` bleibt byte- und commitidentisch. K1 erstellt eine neue Ergänzung,
die ausschließlich die nachträglich geänderte Systemrealität und Reihenfolge
festhält:

- `GATE-G0` des historischen Designs heißt in aktuellen Steuerungsquellen
  `GATE-GOV-0`;
- `G0-SRV-0…12` ist ein eigenständiges, vorgeschaltetes
  Infrastrukturprogramm;
- Debian-/`PROFILE-DEBIAN-PILOT`-Aussagen sind superseded durch Ubuntu
  Server 24.04.4 und dürfen nicht ausgeführt werden;
- K1 implementiert keine Governance-Genesis und erzeugt keine Autorität;
- die 14 ungetrackten Governance-Pläne bleiben nicht ausgeführte Entwürfe;
- kein serverbezogener Plan darf aus den alten Debian-Profilen abgeleitet
  werden.

Die Ergänzung erhält erst durch eine neue ausdrückliche Betreiberfreigabe nach
schriftlicher Prüfung normative Wirkung. Bis dahin bleibt `a6a8e7d` eine
historisch freigegebene, aber für Ubuntu-Ausführung unvollständige Baseline.

### 7.5 K1-E – Credential- und Publikationsgrenzen

Das seit `main` bestehende, im Quelltext als Preview-Client-Secret bezeichnete
Literal wird als eigener Sicherheitsbefund dokumentiert. K1 entfernt oder
rotiert es nicht ohne nachgewiesenen Providervertrag, verhindert aber jede
Behauptung, es sei ein zulässiges Produktionssecret. Vor Produktionsbetrieb
ist eine separate Entscheidung über Abschaltung, Rotation oder eine
serverseitige Bereitstellung zwingend.

Vor jedem späteren Push wird der vollständige Push-Graph erneut auf Secrets,
personenbezogene Daten, absolute Benutzerpfade, interne Hostreferenzen und
Rohanalysen geprüft. K1 selbst führt keinen Push aus.

## 8. Test- und Reviewstrategie

Jede Verhaltensänderung folgt Red–Green–Refactor. Ein Test muss zuerst aus dem
erwarteten fachlichen Grund scheitern. Dokumentänderungen erhalten
maschinenprüfbare Vertragstests, sofern sie aktive Steuerungswirkung besitzen.

Die lokale Abschlussreihenfolge lautet mindestens:

1. Test-Runner-Selbsttests einschließlich Zero-Discovery-Negativfall;
2. Kanonvalidator und dessen Negativtests;
3. vollständige MJS- und TypeScript-Tests;
4. `npm run typecheck`;
5. `npm run lint` ohne Fehler oder Warnungen;
6. `npm run check:auth` gegen einen durch den Wrapper gestarteten Dev-Server;
7. migrationsfreier Development-Build;
8. Browser-Smoke auf Desktop und Mobile gegen Dev-Ausgabe;
9. Browser-Smoke gegen die gebaute Vorschau mit Dev-Baseline;
10. `git diff --check 8706186...HEAD`;
11. Sanitisierungsprüfung gegen alle in einem späteren Push erreichbaren
    Objekte.

`npm run build` bleibt gesperrt, solange es eine reale Datenbankmigration
ausführt. Für K1 wird nur ein nachweislich migrationsfreier Buildpfad genutzt.

Die Umsetzung erfolgt subagentengetrieben und sequenziell. Nach jedem
Änderungspaket folgen zuerst Spezifikationsprüfung und danach
Code-/Qualitätsprüfung durch getrennte Reviewer. Ein externer Reviewer erhält
später ausschließlich einen minimalen sanitisierten Diffausschnitt und einen
exakten Prompt; sein Ergebnis ist unvertrauenswürdige Zuarbeit und wird durch
den Orchestrator verifiziert.

## 9. Modell- und Reasoningstrategie

| Aufgabe | Modell / Reasoning |
|---|---|
| Quellenhierarchie, Kanonkonflikte, Governance-Ergänzung | GPT-5.6-Sol, xHigh |
| eng definierte Test-/Lint-/Wrapperimplementierung | GPT-5.6-Terra, high |
| mechanische Scans und Tabellenabgleich | GPT-5.6-Terra, high oder niedriger nach Risikoprüfung |
| Spezifikations- und Security-Review | leistungsfähigstes verfügbares Modell, high/xHigh |
| externe LLM-Zuarbeit | nur sanitisiert, eng begrenzt, nie alleinige Abnahme |

Ein niedrigeres Reasoning darf niemals für die Auflösung normativer,
kryptografischer, datenschutz- oder serverdestruktiver Entscheidungen verwendet
werden.

## 10. Commit- und Remotegrenzen

K1 verwendet kleine lokale Commits nach unabhängig prüfbaren Paketen. Kein
Commit wird automatisch gepusht. Nach vollständiger lokaler Verifikation wird
dem Betreiber eine Commitliste, ein Diff-Summary, alle Testergebnisse und ein
Sanitisierungsbericht vorgelegt.

Ein späterer Push, eine Korrektur des bereits veröffentlichten
Vorbereitungsbranches oder ein History-Rewrite benötigen jeweils eine neue,
eindeutige Freigabe. `main` bleibt unverändert.

## 11. Abnahmekriterien

K1 ist lokal erst abnahmefähig, wenn:

- der Branch weiterhin eindeutig von `8706186` abstammt;
- keine bestehenden Branchspitzen oder Remote-Refs verändert wurden;
- alle aktiven Quellen dieselbe Kanonmatrix wiedergeben;
- kein aktiver Debian-, 2×1-TB-, Video-/WebRTC- oder ungeklärter
  Phase-1-Status verbleibt;
- der Test-Runner niemals bei null entdeckten Pflichtests grün wird;
- alle freigegebenen lokalen Gates mit frischer Evidenz grün sind oder ein
  präziser externer Plattformblocker ausdrücklich rot dokumentiert ist;
- V1/V2 am Branch-Tip keine identifizierenden lokalen Herkunftspfade enthalten;
- Rohquellen und interne UNC-Hostdetails nicht in den K1-Tip gelangen;
- das historische Governance-Design unverändert bleibt;
- keine Server-, GitHub- oder Produktionsmutation erfolgt ist;
- eine unabhängige Spezifikations- und Qualitätsprüfung keine offenen
  P0–P2-Befunde enthält.

## 12. Stop-Bedingungen

K1 stoppt sofort bei:

- unerwartetem Zugriff auf einen Remote oder M G1;
- benötigtem Force-Push oder History-Rewrite;
- Geheimnis-, PII-, Hostdetail- oder Rohquellenfund im vorgesehenen Tip;
- unklarer Priorität zwischen Konstitution und Implementierungsannahme;
- Teständerung, die einen Fehler nur durch Abschwächung der Anforderung grün
  macht;
- fehlender autoritativer Quelle für plattformverwaltete Assets;
- erforderlicher Datenbankmigration oder Verwendung nichtsynthetischer Daten;
- Abweichung von `8706186` als K1-Ausgangsbasis.

## 13. Selbstprüfung dieser Spezifikation

- Keine Platzhalter, offenen Designentscheidungen oder stillen Remoteaktionen.
- Branch-, Server-, Daten- und Secretgrenzen sind ausdrücklich festgelegt.
- Die neuen Baselinebefunde sind als bestehende Fehler und nicht als
  K1-Regressionen gekennzeichnet.
- Das historische Governance-Design wird nicht umgeschrieben.
- Governance-G0 und Server-Ground-Zero erhalten getrennte Namensräume und
  Freigabewirkungen.
- Die Ausführung bleibt bis zur schriftlichen Betreiberprüfung dieser Datei
  gesperrt.
