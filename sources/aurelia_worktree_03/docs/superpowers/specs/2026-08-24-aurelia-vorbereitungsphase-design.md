# AURELIA – Design der Vorbereitungsphase vor der Gesamtplanung

Stand: 2026-08-24

Status: vom Betreiber freigegeben

Freigabe: 2026-08-24 im Codex-Chat (Wortlaut: „freigeben“)

Zielbranch: `codex/aurelia-vorbereitung`

## 1. Zweck

Diese Spezifikation definiert die notwendigen korrigierenden und ergänzenden
Arbeiten, bevor der vollständige Umsetzungsplan für AURELIA erstellt wird. Sie
verändert keine Produktfunktion, aktiviert keine Hardware und erlaubt keine
realen Klientendaten. Ihr Ergebnis ist ein widerspruchsfreier, prüfbarer Kanon
für Produkt, Sicherheit, Betrieb und Modulaufnahme.

Die Vorbereitungsphase gilt als abgeschlossen, wenn jede unten genannte
Lieferung ein eindeutiges Abnahmekriterium besitzt und der Betreiber den
bereinigten Kanon schriftlich freigegeben hat.

## 2. Bestätigte Leitentscheidungen

1. AURELIA startet als kontrollierter Praxis-Pilot und erhält in dieser Stufe
   keine 24/7-Verfügbarkeitszusage.
2. M G1 bleibt für den Pilot der souveräne Origin und der einzige Ort für die
   Verarbeitung sowie für produktiven Klartext von Klienten-, Analyse- und
   Harmonisationsdaten. Außerhalb liegen nur verschlüsselte, zweckgebundene
   EU-Sicherungen ohne laufende Verarbeitung.
3. Die Plattform wird als modularer Kern mit wenigen getrennten,
   privilegierten Diensten entworfen. Eine vollständige Microservice-Landschaft
   ist ausgeschlossen.
4. Altcode wird nicht als Gesamtanwendung übernommen. Prototypen werden einzeln
   geprüft und ausschließlich über die Kernel-ABI aufgenommen.
5. Video, WebRTC, WebUSB, Cloud-LLM für Akteninhalte und Lovable als Runtime
   bleiben ausgeschlossen.
6. Bis zur gesonderten Art.-9-Freigabe werden ausschließlich synthetische Daten
   verwendet. Das System muss beim Versuch realer Nutzung fail-closed reagieren.
7. Planung und Dokumentationsbereinigung benötigen weder ein GitHub-Token noch
   Serverzugriff. Remotezugriffe werden erst für klar begrenzte spätere Phasen
   freigegeben.

## 3. Zielarchitektur für den Pilot

```text
Browser / PWA
    |
Caddy: TLS, Request-Limits, Sicherheitsheader
    |
TanStack-Frontend + FastAPI-Control-Plane
    |
PostgreSQL ----- Redis ----- MinIO
    |
    +-- CopyGuard        CPU/RAM, unprivilegiert
    +-- aurelia-timerd   Zeit und Zustandsautomat
    +-- aurelia-gpud     exklusiver CUDA-Zugang
    +-- aurelia-emitterd exklusiver, stark beschränkter Hardwarezugang
```

Frontend, Fachlogik und Datenzugriff dürfen zunächst als modularer Monolith
betrieben werden. `timerd`, `gpud` und `emitterd` sind getrennte Prozesse mit
versionierten Verträgen. Nur `gpud` darf CUDA-Geräte öffnen; nur `emitterd` darf
den vorgesehenen seriellen Hardwarepfad öffnen. Worker besitzen keinen freien
Internetzugang.

Die Produktionsidentität auf Debian ist eine eigene Zielarchitektur. Grok-Gate,
Preview-Identität und Vercel-spezifische Annahmen gelten nicht als
Produktionsauthentifizierung.

## 4. Ein Server als Ausfallbereich

### 4.1 Bedeutung

Ein Ausfallbereich ist eine Menge von Komponenten, die durch ein einzelnes
Ereignis gleichzeitig unverfügbar oder unzuverlässig werden kann. Bei M G1 als
alleinigem Origin umfasst dieser Bereich nicht nur CPU und GPU, sondern auch:

- Mainboard, RAM, Netzteile und beide NVMe-Laufwerke;
- Betriebssystem, Kernel, Treiber und lokale Schlüssel;
- Rechenzentrumsrack, Stromversorgung und Netzwerkpfad;
- Firewall, DNS, Zertifikate und fehlerhafte Deployments;
- administrative Fehlbedienung, Schadsoftware und kompromittierte Zugänge.

RAID, redundante Netzteile oder zwei Netzwerkkarten reduzieren einzelne
Fehlerwahrscheinlichkeiten, schaffen aber keine zweite Fehlerdomäne. Ein Backup
stellt Daten wieder her; es übernimmt nicht automatisch den laufenden Dienst.

`RPO` (Recovery Point Objective) bezeichnet den maximal akzeptierten
Datenverlust gemessen als Zeitspanne. `RTO` (Recovery Time Objective) bezeichnet
die angestrebte Zeit bis zur Wiederherstellung des Dienstes. Beide Werte sind
erst belastbar, nachdem ein Wiederherstellungstest sie unter realistischen
Bedingungen nachgewiesen hat.

### 4.2 Betriebsziel P1 – kontrollierter Praxis-Pilot

Für P1 gelten verbindlich:

| Merkmal | Ziel |
|---|---|
| Verfügbarkeit | keine 24/7-Zusage; angekündigte Wartungsfenster zulässig |
| Aufnahmestopp | bei Sicherheits-, Integritäts- oder Backupzweifel sofort möglich |
| RPO Datenbank | höchstens 15 Minuten durch verschlüsselte externe WAL-Ablage |
| RPO Objekte | höchstens 60 Minuten durch verschlüsselte inkrementelle Sicherung |
| RTO | höchstens 8 Betriebsstunden, sofern freigegebene Ersatzkapazität verfügbar ist |
| Maximal tolerierte Unterbrechung | 24 Stunden; danach Pilot aussetzen und Betreiberentscheidung |
| Restore-Nachweis | vollständiger isolierter Restore vor erster Art.-9-Nutzung, danach quartalsweise |
| Notbetrieb | keine neue Analyse oder Harmonisierung; nur gesicherter Aufnahmestopp und Statuskommunikation |

Kann vor dem Pilot keine passende Ersatzkapazität nachgewiesen werden, ist das
RTO ein Zielwert ohne Verfügbarkeitszusage. Dieser Umstand muss in
Betriebsvereinbarung und Risikoregister ausdrücklich stehen.

### 4.3 Betriebsziel P2 – späterer 24/7-Regelbetrieb

P2 ist ein eigenständiges Ausbau-Gate und nicht Bestandteil des ersten Piloten.
Es erfordert mindestens:

- eine zweite, vertraglich und technisch unabhängige EU-Fehlerdomäne;
- einen warmen Standby für Control Plane und Datenbank;
- verschlüsselte, laufend überprüfte Replikation von WAL und Objekten;
- dokumentiertes DNS-/Routing-Failover ohne geteiltes Einzelgeheimnis;
- regelmäßig getesteten Failover und Rückwechsel;
- angestrebtes RPO von höchstens 5 Minuten und RTO von höchstens 60 Minuten;
- einen Bereitschafts-, Incident- und Kommunikationsprozess.

GPU- oder Emitterjobs dürfen beim Failover nicht als ununterbrochen dargestellt
werden. Sie werden abgebrochen oder aus dem letzten bestätigten Checkpoint mit
einem dokumentierten Gap neu aufgenommen. Ein Emitter wird niemals automatisch
auf einer Ersatzinstanz aktiviert.

## 5. Arbeitspakete der Vorbereitungsphase

### A. Kanon und Entscheidungsstatus bereinigen

Zu entfernen oder eindeutig als historisch zu markieren sind insbesondere die
verbliebenen WebRTC-/Video-Verweise in Architektur, Sicherheit, Live-Konzept,
Navigation und ID-Schema. D08, D10 und D12 müssen in allen Quellen denselben
Status tragen. Generierte oder doppelte Darstellungen müssen auf eine
kanonische Quelle verweisen.

**Abnahme:** Eine automatisierte Suche findet keinen produktiven WebRTC-/Video-
Plan mehr. Jede D-, C-, X-, U-, K-, H-, O- und WV-ID besitzt genau einen
kanonischen Status; abgeleitete Dokumente widersprechen ihm nicht.

### B. Entwicklungsplattform und Debian-Produktion trennen

Es werden zwei explizite Profile beschrieben:

- `preview-synthetic`: bestehende Vorschau, nur synthetische Daten, keine
  Hardware und keine Produktionsidentität;
- `debian-pilot`: Caddy, produktive Authentifizierung, Postgres, lokale Dienste,
  Secret-Verwaltung und streng abgeschaltete Hardware bis zum jeweiligen Gate.

**Abnahme:** Für jede umgebungsabhängige Funktion ist dokumentiert, ob sie in
Preview, Pilot oder beiden existiert. Kein Preview-Token und keine
Preview-Identität kann als Produktionsidentität akzeptiert werden.

### C. Sicherheits- und Datenschutzbasis spezifizieren

Benötigt werden Threat Model, Datenfluss- und Vertrauensgrenzendiagramm,
Rollen-/Grant-Matrix, Tenant-RLS-Regeln, Schlüsselhierarchie, Lösch- und
Exportjobs, Auditmodell, Retention-Matrix, Incident-Prozess und technische
Zuarbeit für die Datenschutz-Folgenabschätzung.

**Abnahme:** Für jede Art.-9-Datenbewegung sind Rechtsgrundlage, Zweck,
Speicherort, Schlüssel, Aufbewahrung, Rollen und Löschweg benannt. Negative
Isolationstests sind als ausführbare Abnahmetests spezifiziert.

### D. Betriebsdesign erstellen

Das Betriebsdesign umfasst Debian-Härtung, Paket- und Patchstrategie,
Firewall, TLS, Caddy, Dienstidentitäten, Prozessrechte, Secret-Verwaltung,
Monitoring, Alerting, Loghygiene, Backup/Restore, Kapazitätsgrenzen,
Deployment/Rollback und Notfallhandbuch.

**Abnahme:** Eine neue, freigegebene Ersatzmaschine kann aus versionierter
Konfiguration plus Secret-Wiederherstellungsverfahren aufgebaut werden. Ein
isolierter Restore erreicht die P1-Ziele und wird protokolliert.

### E. Qualitäts- und Lieferkette definieren

Pflicht-Gates werden: reproduzierbare Installation, Format, Lint, Typecheck,
Unit-, Integrations- und Browsertests, Migrationsprüfung, SBOM,
Abhängigkeitsscan, Secret-Scan, statische Sicherheitsprüfung, signierte
Artefakte, Last-/Soak-Tests und unabhängiger Web-/API-Penetrationstest.

**Abnahme:** Kein Release kann ein fehlgeschlagenes Gate umgehen. Ausnahmen
benötigen einen zeitlich begrenzten, vom Betreiber signierten Risikoeintrag;
Art.-9-, Isolations- und Hardware-Gates erlauben keine Ausnahme.

### F. Modulaufnahmevertrag vervollständigen

Jeder Prototyp benötigt Herkunft, Lizenz, unveränderlichen Hash,
Zweck/Nicht-Zweck, Schemas, Testvektoren, Reproduzierbarkeit, Ressourcenbudget,
Seiteneffekte, CopyGuard-Flächen, Fehlerverhalten und Passport-Zuordnung.
Unbekannte oder nicht nachweisbare Eigenschaften führen zu
`executable: false`.

**Abnahme:** Ein Modul kann vollständig als Laborartefakt geprüft werden, ohne
Produktionsdaten, Produktionskeys, freien Netzwerkzugang oder Hardwarezugriff
zu erhalten.

### G. Produkt- und Rechtsgrenzen operationalisieren

Die nichtmedizinische Zweckbestimmung wird nicht nur textlich, sondern in
Funktionen, Rollen, Reports, Suchmetadaten, Werbung und CopyGuard-Regeln
durchgesetzt. Barrierefreiheit wird mit WCAG 2.2 AA und EN 301 549 als
Release-Gate geplant.

**Abnahme:** Eine Funktions-/Claim-Matrix ordnet jede sichtbare Aussage und
jede Kernfunktion einer erlaubten Produktzweckbestimmung zu. Medizinische
Claims blockieren den Release.

## 6. Zugriffsmodell

| Phase | Erforderlicher Zugriff | Regel |
|---|---|---|
| Kanonbereinigung und Planung | lokales Repository | kein Token, kein Serverzugriff |
| Remote-Abgleich | GitHub read-only | bevorzugt bestehende Anmeldung oder kurzlebige, fein beschränkte Berechtigung; nie Token im Chat |
| Serverinventur | SSH read-only soweit technisch möglich | eigener Audit-Nutzer, keine Root-Shell, keine Secrets ausgeben |
| Provisionierungsdesign | Offline-Konfiguration/Testsystem | noch kein Produktionsschreiben |
| Pilotinstallation | zeitlich begrenzte, protokollierte Eskalation | Root nur für definierte Installationsschritte |
| Betrieb | rollengetrennte Dienst- und Betreiberkonten | kein gemeinsames Dauerkonto |

GitHub-Schreibzugriff und Serverzugriff sind voneinander unabhängig. Beide
werden erst dann beantragt, wenn Ziel, Befehle, Rückrollweg und Protokollierung
der jeweiligen Phase feststehen.

## 7. Reihenfolge und Stop-Gates

1. Diese Vorbereitungsspezifikation freigeben.
2. Kanon und Statuswidersprüche korrigieren.
3. Sicherheits-, Datenschutz- und Betriebsgrundlagen spezifizieren.
4. Den vollständigen Gesamtplan in phasenweise ausführbare Teilpläne zerlegen.
5. Phase 1 mit ausschließlich synthetischen Daten vervollständigen.
6. P1-Backup und Restore nachweisen.
7. Erst danach Phase 2 und die Art.-9-Freigabe vorbereiten.
8. Module einzeln in der Laborumgebung aufnehmen.
9. CUDA und Hardware jeweils über eigene Freigabegates aktivieren.
10. Nach erfolgreichem Praxis-Pilot über P2 entscheiden.

Ein Stop-Gate wird ausgelöst bei widersprüchlichem Kanon, ungeklärtem
Datenfluss, fehlendem Restore, nicht reproduzierbarem Modul, fehlgeschlagener
Tenant-Isolation, unklarer Messwertquelle, medizinischem Claim oder
unprotokollierter Hardwareaktivierung.

## 8. Nicht delegierbare externe Freigaben

Technische Planung und Umsetzung ersetzen nicht:

- die Betreiberentscheidung über Zweck, Risiko und Verfügbarkeit;
- die rechtliche Prüfung von Zweckbestimmung, Verträgen und Claims;
- den Rat des Datenschutzbeauftragten zur Datenschutz-Folgenabschätzung;
- den unabhängigen Penetrationstest;
- die fachkundige Prüfung des Emitter- und Sensorbetriebs;
- die dokumentierte Pilotabnahme durch reale, autorisierte Anwender.

## 9. Ergebnis der Vorbereitungsphase

Nach Abschluss liegen folgende freigegebene Grundlagen vor:

1. widerspruchsfreier Produkt- und Entscheidungskanon;
2. Produktionsarchitektur für `debian-pilot`;
3. Threat Model und Datenschutz-Datenfluss;
4. RLS-, Schlüssel-, Audit- und Grant-Konzept;
5. P1-Betriebs-, Backup-, Restore- und Notfallkonzept;
6. Qualitäts- und Freigabematrix;
7. Modulaufnahmevertrag;
8. phasenweise zerlegbare Grundlage für den Gesamtumsetzungsplan.

Erst die Freigabe dieser acht Ergebnisse erlaubt den Übergang in die
detaillierte Gesamtplanung und anschließend in die Implementierung.
