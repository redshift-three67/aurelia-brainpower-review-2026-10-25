# Morphic V1 Web Workflow: Radi144-naehere UX-Angleichung

Datum: 2026-07-04
Status: abgestimmt, zur Planerstellung vorbereitet

## Ziel

Der bestehende Morphic V1 Workflow der Weboberflaeche soll in Bedienung, visueller Fuehrung und Informationsarchitektur deutlich naeher an die Radi144 Userexperience herangefuehrt werden. Die Anwendung bleibt ein produktiver Arbeitsbildschirm, keine Landingpage: Der Nutzer soll sofort im gefuehrten Workflow landen, den aktuellen Schritt klar erkennen, erledigte Schritte sehen und vor dem Start transparent verstehen, welche Daten in den produktiven Analysepfad gehen.

Die fachliche Backend- und CLI-Verkabelung bleibt grundsaetzlich erhalten. Der Umsetzungsplan darf den Workflow jedoch auf den vollen 10-Schritt-Radi144-Ablauf erweitern, echte Bildreferenz-Uploads einfuehren und eine explizit aktivierbare, browserlokale Speicherung personenbezogener Klientendaten vorsehen. Ziel ist keine neue Analyse-Engine, sondern eine konsistentere, ruhigere und vertrauensbildende Workflow-Erfahrung auf Basis der vorhandenen Funktionen plus klar abgegrenzter Komfortfunktionen.

## Klaerung zur Scan-Profil-Aussage

Die bisherige Aussage

> Profilwahl wird fuer den Phase-1 Launcher vorbereitet. Template, Entropie-Modus, Bildoption und Adaptive Limits werden transparent in der Vorschau angezeigt und an den produktiven CLI-Pfad uebergeben.

bedeutet fachlich:

- Das UI sammelt im Scan-Profil bereits `profile_template`, `entropy_mode`, optional `image_path` und `adaptive_limits`.
- Die Vorschau zeigt diese Auswahl transparent an.
- Der produktive Web-Launcher uebergibt diese Werte bereits an den CLI-Pfad.
- Fuer diese Aussage ist daher kein grosser Backend-Block offen.

Offen ist vor allem die UX-Formulierung: Der Text klingt nach "wird spaeter vorbereitet", obwohl der Handoff technisch bereits vorhanden ist. In der neuen UX soll das als bestaetigter Uebergabe-Snapshot formuliert werden, etwa:

> Uebergabe an Phase 1: Template, Entropie-Modus, Bildreferenz und adaptive Limits werden in die Analysevorschau uebernommen und beim Start an den produktiven Analysepfad uebergeben.

Die Bildoption wird im erweiterten Scope von einem reinen Pfadfeld zu einer echten Bildreferenz-Option ausgebaut. Der bestehende Pfad bleibt als Fallback oder technische Anzeige erhalten, aber der Nutzer soll im UI eine Datei auswaehlen koennen.

## Scope

In Scope:

- `apps/web/static/index.html`
- `apps/web/static/app.css`
- `apps/web/static/app.js`
- fokussierte Anpassungen in `tests/test_web_shell.py`
- lokale Browser-/Screenshot-Pruefung fuer Desktop und Mobile
- Erweiterung auf den vollen 10-Schritt-Radi144-Ablauf
- echte Datei-Uploads fuer Bildreferenzen im Scan-/Analyseprofil
- minimaler lokaler Upload-/Staging-Pfad, falls fuer den produktiven CLI-Handoff erforderlich
- explizit aktivierbares, browserlokales Speichern personenbezogener Klientendaten
- bestehende Feldnamen und CLI-Vertraege beibehalten; API-Erweiterungen nur eng fuer Upload/Staging

Nicht in Scope:

- breite Backend-Neuentwicklung ausserhalb eines minimalen Upload-/Staging-Pfads
- neue CLI-Flags, sofern der bestehende Bildpfad-/Profil-Handoff ausreicht
- automatische oder verdeckte Speicherung personenbezogener Daten ohne ausdrueckliche Nutzerentscheidung
- Cloud- oder Server-Synchronisierung personenbezogener Daten
- komplette Neustrukturierung der Web-App

## Referenzprinzipien aus Radi144

Die Morphic-Oberflaeche soll Radi144 nicht 1:1 kopieren, sondern dessen Bedienqualitaeten uebernehmen:

1. Klare Step-Navigation mit aktiven, erledigten und gesperrten Zustaenden.
2. Visuelle Verbinder zwischen Schritten, damit der Ablauf wie ein zusammenhaengender Prozess wirkt.
3. Schritt-Header mit Icon-Marker, Titel und kurzer Unterzeile.
4. Kartenbasierte Arbeitsbereiche mit kompakten Titelzeilen.
5. Auswahloptionen als Radio-/Toggle-Karten statt blosser Formularfelder, wo die Entscheidung fachlich wichtig ist.
6. Zusammenfassungs- und Snapshot-Karten vor kritischen Aktionen.
7. Ruhige, warme Farbwelt mit Sage/Ink/Sand/Terracotta-Akzenten, aber ohne dominante Einfarbigkeit.
8. Mobile Darstellung ohne Ueberlagerungen, mit horizontal scrollbarer Step-Navigation und stabilen Button-/Kartenbreiten.

## UX-Struktur

Der Workflow wird auf 10 Schritte erweitert und naeher an Radi144 ausgerichtet:

1. Willkommen & Systemstatus
2. Hinweise & Einwilligung
3. Klienten-Daten
4. Fokus & Intention
5. Analyse-Konfiguration
6. EMF-/Umfeld-Analyseprofil
7. Zusammenfassung & Start
8. Ergebnis-Matrix
9. Ergebnis-Details & Berichte
10. Harmonisierung, Export & Abschluss

Jeder Schritt erhaelt dieselbe Grundstruktur:

- Step-Header mit Symbol, Schrittzahl, Titel und kurzer Orientierung.
- Primaere Arbeitskarte mit den wichtigsten Eingaben oder Aktionen.
- Sekundaere Snapshot-/Hinweiskarte fuer Transparenz.
- Footer-Aktionen mit Zurueck, Weiter oder Start.
- Validierungsfeedback direkt am relevanten Feld oder direkt an der Aktion.

Die rechte oder untere Kontextflaeche soll nicht erklaeren, wie die App generell funktioniert. Sie soll konkrete aktuelle Daten spiegeln: Preflight-Status, gewaehlt Auswahl, Berichtsauswahl, Startbereitschaft.

## Step-spezifisches Design

### 1. Willkommen & Systemstatus

Der bisherige Preflight wird zum ruhigen Einstieg mit Systembereitschaft. API-Status, Quellenstatus und Workflow-Bereitschaft erscheinen als kompakte Statuskarten. Die Nutzerfuehrung soll eher "Bereit fuer Analyse" als "technischer Check" sagen. Fehler bleiben sichtbar und handlungsnah.

### 2. Hinweise & Einwilligung

Hinweise werden als Consent- und Kontextbereich aufgebaut. Der Nutzer sieht kurze Karten zu Zweck, lokaler Verarbeitung, Grenzen der Auswertung und Verantwortung. Die bestehende Bestaetigung bleibt erhalten, aber optisch als bewusst gesetzter Freigabeschritt.

### 3. Klienten-Daten

Klientendaten werden in einem Radi144-aehnlichen Formularraster dargestellt: Pflichtfelder klar markiert, optionale Felder ruhiger, Feldgruppen mit kleinen Abschnittstiteln. Eine Snapshot-Karte zeigt, welche Daten fuer die Analyseuebersicht verwendet werden. Eine zusaetzliche Datenschutzkarte erlaubt explizit, diese Daten browserlokal fuer spaetere Sitzungen zu speichern.

### 4. Fokus & Intention

Der Fokus-Schritt wird von einer reinen Texteingabe zu einem klaren Analyseziel-Schritt. Das Fokusfeld bleibt zentral. Top-K, Schwerpunkt und optionale Nuancen werden als kompakte Kontrollgruppe gestaltet. Spaetere Presets koennen visuell vorbereitet werden, aber ohne neue fachliche Logik in dieser Scheibe.

### 5. Analyse-Konfiguration

Die bisherigen Konfigurationsanteile werden aus dem Scan-Profil herausgeloest, soweit sie allgemeine Analyseparameter betreffen. Dazu gehoeren Template, Entropie-Modus, Top-K und Startrelevanz. Die Auswahl erfolgt ueber Radio-/Toggle-Karten und wird sofort in einem Konfigurations-Snapshot gespiegelt.

### 6. EMF-/Umfeld-Analyseprofil

Das bisherige Scan-Profil wird zur transparenten Profil- und Umfeldwahl:

- Template als Radio-Karten mit kurzer Wirkung.
- Entropie-Modus als Radio-Karten oder segmentierte Auswahl.
- Bildreferenz als echte Datei-Auswahl mit Statushinweis, Vorschau-Metadaten und Pfad-/Dateiname-Anzeige.
- Adaptive Limits als Toggle-Karte.
- Uebergabe-Snapshot mit exakt den Werten, die an Vorschau und CLI gehen.

Die bisherige "wird vorbereitet"-Formulierung wird ersetzt durch eine bestaetigende Uebergabeformulierung. Dadurch sieht der Nutzer: Diese Auswahl ist nicht Dekoration, sondern produktiver Input.

### 7. Zusammenfassung & Start

Dieser Schritt wird zur Radi144-aehnlichen Zusammenfassung vor dem Start. Er zeigt Klient, Fokus, Scan-Profil, adaptive Limits, Bildreferenz und CLI-relevante Kernwerte als kompakte Review-Karten. Der Startbutton ist die einzige dominante Aktion. Nach dem Start zeigt der Bereich Jobstatus, Fortschritt und Fehlermeldungen.

### 8. Ergebnis-Matrix

Die Ergebnis-Matrix wird als eigenstaendiger Ergebnisschritt gefuehrt. Sie zeigt verfuegbare Treffer, Scores, Status und visuelle Priorisierung in einer kompakten Matrix-/Listenansicht. Ist noch kein Ergebnis vorhanden, erscheint ein klarer leerer Zustand statt technischer Unruhe.

### 9. Ergebnis-Details & Berichte

Berichte bleiben als eigener Schritt erhalten, werden aber mit Ergebnisdetails gebuendelt. Der Bereich wird als Report-Katalog mit aktiver Auswahl, Verfuegbarkeit, kurzer Vorschau und Detailansicht gestaltet.

### 10. Harmonisierung, Export & Abschluss

Harmonisierung wird als Abschluss-/Weiterverarbeitungsschritt gestaltet. Die aktive Berichtsbasis, Hardware-/Timing-Optionen, Exportoptionen und der Jobstatus werden als kontrollierte Karten dargestellt. Der Schritt soll nicht wie ein Anhang wirken, sondern wie der fachliche Abschluss des Workflows.

## Datei-Uploads fuer Bildreferenzen

Der Upload soll als lokaler Bildreferenz-Flow gestaltet werden:

- Der Nutzer kann eine Bilddatei auswaehlen.
- Zulaessige Formate werden klar begrenzt, etwa PNG, JPG und JPEG.
- Die UI zeigt Dateiname, Groesse und optional eine kleine Vorschau oder Statuszeile.
- Der produktive Analysepfad erhaelt weiterhin einen Bildpfad oder eine aequivalente lokale Referenz.
- Wenn die bestehende Backend-/Launcher-Struktur keinen echten Multipart-Upload unterstuetzt, wird im Umsetzungsplan zuerst ein minimaler lokaler Upload-/Staging-Pfad definiert.
- Der alte Pfad-Eingabemodus bleibt als technischer Fallback verfuegbar, solange er fuer CLI-Kompatibilitaet noetig ist.

## Browserlokale PII-Speicherung

Die Speicherung personenbezogener Klientendaten wird nur als explizit aktivierbares Komfortfeature aufgenommen:

- Standard bleibt: keine persistente Speicherung.
- Der Nutzer muss die Speicherung bewusst einschalten.
- Die UI erklaert kurz, dass die Daten nur lokal im Browser dieses Geraets gespeichert werden.
- Es gibt eine sichtbare Loeschen-/Zuruecksetzen-Aktion.
- Gespeichert werden nur die fuer die Wiederaufnahme des Workflows notwendigen Felder.
- Keine Cloud-Synchronisierung, kein Server-Speicher, kein verstecktes Autosave.
- Tests muessen pruefen, dass ohne Opt-in keine PII im lokalen Speicher landet.

## Interaktionsmodell

- Navigation bleibt schrittbasiert und validiert.
- Erledigte Schritte erhalten einen Done-Zustand.
- Gesperrte Schritte bleiben erkennbar, aber nicht dominant.
- Zurueck/Weiter-Aktionen bleiben an einer stabilen Stelle.
- Kritische Aktionen wie Analyse starten und Harmonisierung starten erhalten eindeutige Primaerbuttons.
- Bestehende API-Aufrufe bleiben unveraendert.
- Browser-Speicherung fuer personenbezogene Daten wird nur nach explizitem Opt-in eingefuehrt.
- Nicht-sensitive UI-Zustaende duerfen lokal gemerkt werden, wenn keine Datenschutzimplikation entsteht.

## Visuelles System

Die bestehende Morphic-Farbwelt wird in Richtung Radi144 verfeinert:

- Hintergrund: warmes Off-White/Ivory statt hartem Weiss.
- Flaechen: helle Karten mit feinen Linien und wenig Schatten.
- Primaerakzent: Sage/Olive fuer Fortschritt, Validitaet und Startbereitschaft.
- Sekundaerakzent: Terracotta fuer Aufmerksamkeit und aktive Marker.
- Text: dunkles Ink/Charcoal fuer hohe Lesbarkeit.
- Keine grossen Hero-Flaechen, keine dekorativen Orbs, keine dominanten Verlaeufe.

Typografie bleibt technisch robust. Externe Google-Fonts werden nicht eingebunden. Falls keine lokale Font-Strategie vorhanden ist, nutzt die App systemnahe Serif/Sans-Kombinationen, die Radi144s Charakter naehern, ohne Offline- und Datenschutzverhalten zu verschlechtern.

## Technischer Ansatz

Die Umsetzung soll inkrementell im bestehenden Vanilla-HTML/CSS/JS erfolgen:

- HTML-Struktur auf zehn Panels erweitern, aber bestehende Feld-IDs und Datenvertraege soweit moeglich erhalten.
- CSS-Tokens fuer Farben, Flaechen, Stepper, Karten, Radio-Karten, Toggles und mobile Layouts ausbauen.
- JS dort anpassen, wo neue visuelle Zustaende, Uploadstatus, lokale Speicherung oder Snapshot-Texte aus bestehenden Daten entstehen.
- Bestehende IDs und Formfeldnamen moeglichst beibehalten, damit Tests und API-Handoff stabil bleiben.
- Keine neue Framework-Abhaengigkeit einfuehren.

## Tests und Verifikation

Automatisiert:

- `tests/test_web_shell.py` an neue Struktur, Texte und Marker anpassen.
- Bestehende Assertions fuer CLI-Handoff im Scan-Profil erhalten.
- Tests fuer 10 Schritte, Stepper-Zustaende, Upload-UI, lokale Speicher-Opt-in, Report-/Harmonisierungsschritte und neue Scan-Profil-Formulierung ergaenzen oder aktualisieren.

Manuell/Browser:

- Lokaler Webserver auf freiem Port.
- Desktop-Screenshot des kompletten Workflows.
- Mobile-Screenshot mit Stepper, Formularfeldern und Footer-Aktionen.
- Kurzer Interaktionstest: Willkommen bis Startfreigabe, Scan-/Umfeldprofil-Auswahl, Upload-Auswahl, lokaler Speicher-Opt-in/Reset, Vorschau/Handoff-Snapshot, Ergebnis-/Berichtsschritte, Harmonisierungsschritt.

Nicht geplant:

- komplette Gesamtsuite, sofern der UX-Schnitt keine Backend- oder Engine-Module beruehrt.

## Risiken

- Zu starke 1:1-Uebernahme von Radi144 koennte Morphic fachlich unscharf machen. Deshalb werden Prinzipien uebernommen, nicht Dateistrukturen kopiert.
- Zu viel UI-Umbau auf einmal koennte bestehende Tests brechen. Deshalb bleiben IDs und Datenvertraege stabil, und der Umsetzungsplan wird phasenweise aufgebaut.
- Ein scheinbarer Upload im Scan-Profil waere irrefuehrend, wenn technisch nur ein Pfadfeld existiert. Deshalb muss der Umsetzungsplan den Upload-Handoff explizit klaeren.
- Autosave fuer Klientendaten ist datenschutzsensibel. Deshalb wird PII-Persistenz nur mit Opt-in, sichtbarem Reset und Tests aufgenommen.
- Der Sprung auf 10 Schritte kann die Bedienung verlaengern. Deshalb muessen Schritte klarer, nicht nur zahlreicher werden.

## Akzeptanzkriterien

- Der Workflow zeigt genau 10 Schritte im Radi144-nahen Ablauf.
- Alle aktuellen fachlichen Schritte sind erreichbar und validiert.
- Der Stepper wirkt visuell und funktional naeher an Radi144: aktiv, erledigt, verbunden, mobil bedienbar.
- Jeder Schritt besitzt einen konsistenten Header und mindestens eine klare Arbeitskarte.
- Scan-/Umfeldprofil zeigt Template, Entropie-Modus, Bildreferenz und Adaptive Limits als produktive Uebergabewerte.
- Bildreferenzen koennen ueber einen echten Datei-Auswahlfluss eingebracht werden.
- Personenbezogene Klientendaten werden nur nach explizitem Opt-in browserlokal gespeichert und koennen sichtbar geloescht werden.
- Die alte missverstaendliche "wird vorbereitet"-Formulierung ist ersetzt.
- Die produktive CLI-Uebergabe fuer Scan-Profil bleibt testbar erhalten.
- Desktop und Mobile zeigen keine ueberlappenden Texte, Buttons oder Karten.
- `tests/test_web_shell.py` laeuft erfolgreich.

## Naechster Schritt

Nach Review dieser Spezifikation wird ein konkreter Implementierungsplan erstellt. Dieser Plan soll die Arbeit in kleine, pruefbare Schritte zerlegen:

1. Stepper/Workflow-Shell vereinheitlichen.
2. Workflow von 8 auf 10 Schritte migrieren.
3. Gemeinsame Karten-, Header- und Kontrollmuster einziehen.
4. Zehn Schritte einzeln auf Radi144-naehere UX ueberfuehren.
5. Datei-Upload fuer Bildreferenzen und produktiven Handoff klaeren.
6. Browserlokale PII-Speicherung mit Opt-in und Reset einfuehren.
7. Scan-/Umfeldprofil-Text und Uebergabe-Snapshot schaerfen.
8. Tests und Browser-Verifikation aktualisieren.
