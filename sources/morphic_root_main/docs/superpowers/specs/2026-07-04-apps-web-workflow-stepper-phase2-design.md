# Apps/Web Workflow Stepper Phase 2 Design

Datum: 2026-07-04
Status: abgestimmt, zur Planerstellung vorbereitet
Geltungsbereich: `apps/web/static/*`, gezielte Shell-Tests in `tests/test_web_shell.py`, spaeter fokussierter Browser-Durchlauf auf einem Port ungleich `8090`

## Ziel

Der bestehende Phase-1-Webflow in `apps/web` soll strukturell ehrlicher, linearer und naeher an der realen Nutzerfuehrung werden. Die heute bereits vorhandenen Bereiche `Berichtskatalog & Vorschau` und `Workflowabschluss & Harmonisierung` werden aus dem losen Nachlauf unterhalb von `Analysefreigabe` in den eigentlichen Wizard ueberfuehrt.

Das Ergebnis soll:

- den tatsaechlichen Arbeitsablauf als nummerierte Schritte zeigen,
- auf Desktop und kleineren Viewports stabiler lesbar sein,
- die vorhandene Analyse-, Bericht- und Harmonisierungstechnik weiterverwenden,
- die Systemstabilitaet schonen und keine riskanten Volltests erzwingen.

## Ausgangslage

Der aktuelle Wizard endet sichtbar bei Schritt 6 `Analysefreigabe`. Danach folgen im Seitenfluss:

- `Berichtskatalog & Vorschau`
- `Workflowabschluss & Harmonisierung`

Fachlich sind das bereits echte Workflowphasen. In der UI wirken sie aber wie ein Anhang. Das fuehrt zu mehreren Problemen:

- Der Fortschrittsbalken signalisiert Abschluss, obwohl noch zentrale Schritte folgen.
- Der Nutzer muss nach einem erfolgreichen Scan mental von einem gefuehrten Wizard in eine freie Nachbearbeitung wechseln.
- Die Report-Ansicht leidet bei langen Session- und Berichtstiteln unter Umbruch- und Breitenproblemen.
- Die sticky Topbar plus sticky Stepper nehmen auf kleineren Viewports zu viel vertikalen Raum ein.

Radi144 zeigt hier die staerkere UX-Idee: relevante Nachphasen werden als explizite Steps gefuehrt, nicht als optischer Anhang.

## Leitplanken

- Keine Aenderung an Port `8090`; spaetere Browser-Tests nutzen einen anderen Port.
- Kein Full-Pytest-Lauf in diesem Slice; die bestehende Vollsuite bleibt bewusst deferred.
- Fokus auf `apps/web/static/*` und gezielte Shell-/UI-Tests.
- Keine unnoetige Aenderung an CLI-, Report- oder Harmonisierungs-Fachlogik.
- Bestehende Jobs, Endpunkte und Payloads bleiben kompatibel.

## Entscheidungsbild

### Gewaehlter Ansatz

Der Wizard wird von 6 auf 8 sichtbare Schritte erweitert:

1. Preflight
2. Hinweise
3. Klientenaufnahme
4. Fokus
5. Scan-Profil
6. Analysefreigabe
7. Berichte
8. Harmonisierung

`Berichte` und `Harmonisierung` bleiben technisch auf denselben vorhandenen UI-Bausteinen aufgebaut, werden aber in eigene Wizard-Panels und Fortschrittslogik ueberfuehrt.

### Verworfene Alternativen

#### Nur optische Nachschaerfung

Nicht ausreichend, weil die strukturelle Unwahrheit des Flows bestehen bliebe. Der Nutzer wuerde weiterhin nach Schritt 6 in einen impliziten Nachbereich fallen.

#### Grosser Radi144-naeherer Umbau mit zusaetzlichen Zwischensteps

Fuer diesen sicheren Zwischenschritt zu gross. Ein sofortiger Ausbau Richtung EMF, Analyse, Matrix, Details und Export als eigene Steps wuerde Risiko, Testaufwand und Regressionsflaeche deutlich vergroessern.

## Ziel-Workflow

### Step 1 bis 6

Die ersten sechs Schritte bleiben fachlich wie bisher bestehen. Texte, Substeps und Aktionen koennen punktuell nachgeschaerft werden, aber das Verhalten bleibt bewusst stabil.

### Step 7: Berichte

Dieser Schritt wird aktiv, sobald der Analyse-Job erfolgreich abgeschlossen ist oder wenn vorhandene Reports bereits geladen werden koennen.

Er enthaelt:

- den Berichtskatalog,
- die Session-Gruppierung,
- die Inline-Vorschau,
- die Auswahl eines aktiven Berichts fuer den Abschluss.

Der Schritt ist die Bruecke zwischen Analyse und Harmonisierung.

### Step 8: Harmonisierung

Dieser Schritt enthaelt ausschliesslich den Abschlussbereich:

- Harmonisierungsparameter,
- Hardware-Auswahl inklusive `Driver Layer`,
- Start/Refresh/Stop,
- Status- und Fortschrittsdarstellung.

Der finale Schritt bleibt deaktiviert bzw. funktional eingeschraenkt, solange kein aktiver Bericht fuer den Abschluss gewaehlt wurde.

## Interaktionsmodell

### Navigation

- Der Stepper zeigt 8 Schritte.
- `Weiter` bewegt sich linear weiter, solange die Validierung des aktuellen Schritts erfolgreich ist.
- `Zurueck` bleibt unveraendert verfuegbar.
- Klicks auf spaetere Steps bleiben nur im bereits freigeschalteten Bereich erlaubt.

### Validierung

- Schritt 2: beide Compliance-Checkboxen erforderlich.
- Schritte 3 bis 5: bestehende Formularvalidierung bleibt.
- Schritt 7: fuer den Uebergang zu Schritt 8 muss ein Bericht aktiv in der Vorschau gewaehlt sein.
- Schritt 8: keine zusaetzliche Wizard-Validierung, aber bestehende Harmonisierungsformular-Checks bleiben vor dem Start aktiv.

### Automatische Uebergaenge

- Nach erfolgreichem Analyse-Job wird `loadReports(..., true)` weiter genutzt.
- Wenn ein erster Bericht automatisch erfolgreich vorgeladen werden kann, springt die UI in Schritt 7 `Berichte`.
- Wird anschliessend ein Bericht aktiv gewaehlt, kann der Nutzer kontrolliert in Schritt 8 wechseln.

Der Wizard bleibt fuehrend, ohne den Nutzer hart zu verriegeln, wenn bereits gueltige Zustandsdaten vorhanden sind.

## Layout- und UX-Design

### Report-Schritt

Der Berichts-Schritt bleibt zweispaltig auf Desktop, aber robuster:

- linke Katalogspalte etwas grosszuegiger und besser gegen lange Titel abgesichert,
- rechte Vorschau dominant, aber nicht erdrueckend,
- Session- und Dateititel mit stabilerem Zeilenverhalten,
- Aktionsbuttons sauber umbrechbar, ohne dass der Texteindruck kollabiert.

Die bestehende Sessiongruppierung bleibt erhalten, weil sie bereits zur Datei- und Reportstruktur passt.

### Sticky-Verhalten

- Die sticky Topbar bleibt grundsaetzlich erhalten.
- Der Stepper bleibt sticky, bekommt aber auf kleineren Viewports konservativere Offset-/Raumwerte.
- Die Report-Vorschau bleibt auf Desktop sticky, auf kleineren Breakpoints statisch.

Ziel ist, die Fuehrung sichtbar zu halten, ohne den Content auf kleineren Hoehen zu stark zu beschneiden.

### Responsivitaet

- Desktop: 8-Stepper horizontal scrollfaehig wie bisher.
- Tablet: Reports untereinander, Vorschau nicht sticky.
- Mobil: Wizard, Berichte und Harmonisierung in einer klar lesbaren Einspaltenstruktur.

## Technische Umsetzung

### HTML

`apps/web/static/index.html` wird so umgebaut, dass:

- der Wizard-Stepper 8 Buttons traegt,
- die Fortschrittsanzeige `1 / 8` bis `8 / 8` abbildet,
- `reports` ein `wizard-panel` mit `data-step="6"` wird,
- der Harmonisierungsbereich in ein eigenes `wizard-panel` mit `data-step="7"` verschoben wird,
- semantische Labels und bestehende Accessibility-Marker erhalten bleiben.

### JavaScript

`apps/web/static/app.js` bleibt das Fuehrungszentrum.

Anpassungen:

- `WORKFLOW_STEPS` wird auf 8 Eintraege erweitert.
- `updateProgress()` und `goToStep()` arbeiten auf der neuen Schrittzahl.
- `validateCurrentStep()` bekommt eine neue Regel fuer den Berichts-Schritt.
- Nach erfolgreichem Analyseabschluss springt die UI in den Berichts-Schritt.
- Die Aktivierung der Harmonisierung bleibt an `activeReportId` gekoppelt.

Es wird keine neue State-Architektur eingefuehrt; die bestehende Logik wird gezielt erweitert.

### CSS

`apps/web/static/app.css` wird nur dort angepasst, wo es die neue Struktur oder die Lesbarkeit verlangt:

- Stepper-/Workspace-Abstaende fuer 8 Schritte,
- robustere `reports-layout`-Breiten,
- stabilere `report-item`-Layouts bei langen Texten,
- kontrolliertere sticky Offsets auf kleineren Viewports.

Die bestehende Farb- und Formensprache bleibt erhalten.

## Teststrategie

Nur fokussierte, leichte Verifikation in diesem Slice:

- `tests/test_web_shell.py` erweitert fuer 8-Step-Markup, neue Wizard-Panels und neue Erwartungen an die Workflowstruktur.
- JS/CSS-String-Pruefungen werden auf die neue Schrittzahl und die getrennten Panels angepasst.
- Danach ein gezielter Browser-Durchklicktest auf einem anderen Port als `8090`.

Bewusst nicht Teil dieses Slices:

- Full Pytest Suite
- schwere Lasttests
- aggressive Multi-Process- oder Langlaufpruefungen

## Risiken

- Ein zu harter Auto-Sprung zwischen Analyse und Bericht kann fuer bestehende Nutzer unerwartet wirken. Deshalb soll nur nach erfolgreicher Report-Vorschau automatisch auf Schritt 7 umgestellt werden.
- Eine zu starke CSS-Aenderung koennte die bereits funktionierende Vorschau destabilisieren. Deshalb bleibt der Umbau auf die vorhandenen Klassen und Layoutachsen begrenzt.
- Zusaetzliche Schrittvalidierung darf das Nachladen alter Reports nicht blockieren. Vorhandene valide Reports muessen weiterhin direkt previewbar bleiben.

## Erfolgskriterien

Der Slice gilt als erfolgreich, wenn:

- der sichtbare Wizard 8 echte Schritte zeigt,
- `Berichte` und `Harmonisierung` als separate gefuehrte Panels erscheinen,
- ein erfolgreicher Analyse-Lauf kontrolliert in den Berichts-Schritt ueberleitet,
- der Report-Katalog auf Desktop bei langen Titeln stabil lesbar bleibt,
- die Harmonisierung weiter nur mit aktivem Bericht freigegeben ist,
- fokussierte Shell- und Browser-Checks auf einem Port ungleich `8090` bestehen,
- die Full Pytest Suite weiterhin explizit deferred bleibt.
