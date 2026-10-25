# Apps/Web Konsolidierung - Phase 1 Design

Datum: 2026-06-30
Status: abgestimmt, zur Umsetzung und zum Flow-Test vorbereitet
Geltungsbereich: `apps/web/*` als einzige Ziel-Web-UI; `web_ui/*` und `web_app.py` bleiben nur temporaer bis zur Vollmigration bestehen

## Ziel

Die produktive Web-Oberflaeche wird konsequent in `apps/web/*` konsolidiert. Die fachliche Referenz ist `Run-MultiplexScan.ps1` bzw. der aktuelle CLI-Flow. Radi144 dient nur als Vorlage fuer UI/UX, Stepper, visuelle Fuehrung und Progressdarstellung.

Phase 1 fokussiert den kliententauglichen Produktivfluss:
- Klientendaten
- Fokus
- Personalprofil mit Templates
- Entropy-Mode
- optionale Bildauswahl
- Level-/Top-N-Auswahl ohne Top-10
- Start des produktiven Top-N-Scans
- sichtbare PS1-Steps/Substeps
- Berichte/Archivierung
- Harmonisierung als Session-Abschluss

Phase 2 folgt spaeter fuer:
- administrative Profilverwaltung
- Quellen-/Profilerweiterung
- aktivier-/deaktivierbare externe Wissensquellen

## Architekturgrundsatz

- `apps/web/*` wird die einzige Ziel-Web-UI.
- `web_ui/*` und `web_app.py` bleiben temporaer, bis alle benoetigten Features in `apps/web/*` angekommen und getestet sind.
- Die Kernengine (`core/*`, `services/*`) wird nicht destabilisiert.
- Die Web-UI startet keine fachlich abweichenden Sonderpfade, sondern orchestriert den produktiven CLI-/Report-Flow.

## Produktiver Web-Flow

Der Web-Flow bildet fachlich diesen Ablauf sichtbar ab:
1. Klient
2. Fokus
3. Parameter
4. Analyse starten
5. Screening aller Profile
6. Top-Profil-Auswahl
7. Vollanalysen der Top-Profile
8. Synergy/Remedy
9. Deutung/Trend
10. Harmonisierung
11. Archivierung
12. Berichte/Vorschau

Radi144 wirkt nur auf die Darstellung, nicht auf die Fachlogik.

## Scores und Rundung

### Ziel

Die Scores sollen kliententauglich, konsistent und besser entzerrt dargestellt werden, ohne die Kernengine zu veraendern.

### Design

- Interne Rohwerte bleiben erhalten als `raw_score`.
- Sichtbare Werte werden zentral als `display_score` berechnet.
- Die Entzerrung erfolgt an genau einer gemeinsamen Stelle fuer alle Berichtstypen.
- Alle sichtbaren Scores in Resonanz-, Synergy-, Remedy-, Deutungs- und Trendberichten werden auf **maximal 3 Nachkommastellen** begrenzt.

### Erwartetes Ergebnis

- weniger Score-Cluster im oberen Bereich
- konsistente Darstellung ueber alle Berichte hinweg
- keine widerspruechlichen Rundungen zwischen HTML, JSON, UI und Konsolidierungen

## Personalprofil mit Templates

### Ziel

Das Personalprofil wird in `apps/web/*` als gefuehrter Schritt erklaert und nicht nur als vier abstrakte Zahlenfelder.

### Basiswerte

- `emotion`
- `physisch`
- `mental`
- `astral`

### Templates Phase 1

Empfohlene Vorlagen:
- Ausgeglichen
- Emotional sensibel
- Koerperlich belastet
- Mental ueberaktiv
- Energetisch offen
- Regenerationsfokus
- Stress / Erschoepfung
- Schmerz / Regulation

### Verhalten

- Template setzt Startwerte
- Werte bleiben anschliessend manuell editierbar
- Kurze Textbeschreibung erklaert die Bedeutung je Vorlage

## Entropy-Mode

### Ziel

Die bisher implizite Auswahl soll in `apps/web/*` wieder explizit fuer den Nutzer steuerbar werden.

### Optionen

- `legacy`
- `enhanced`
- `hybrid`

### Grundsatz

- kein UI-Scheinwert
- Web uebergibt denselben Modus an den produktiven Flow, der auch im CLI/PS1 verwendbar ist

## Bildoption

### Ziel

Die Bildintegration bleibt erhalten, aber stabil und nachvollziehbar.

### Phase-1-Design

- ein sauberer optionaler **Klientenbildpfad** wird in `apps/web/*` integriert
- dieses Bild wirkt auf die Signatur, nicht als separater Fokuskanal

### Fokusbild

- wird nur vorbereitet, aber in Phase 1 nicht aktiv als zweiter Bildkanal eingefuehrt, sofern dies die Stabilitaet gefaehrdet
- kann in Phase 1.5 oder 2 als eigener Kontextkanal kommen

## Top-N

### Ziel

Top-10 wird entfernt, da es nicht benoetigt wird und die UI/Ergebnislage aufblaeht.

### Erlaubte Werte

- 3
- 5
- 7
- 9

## Berichtsordnerstruktur

### Ziel

Fuenf saubere Berichtswurzeln mit konsistenter Session-Struktur je Klient.

### Root-Bereiche

- `C:\Benutzer_Archive_Start`
- `C:\Benutzer_Synergy_Start`
- `C:\Benutzer_Remedies_Start`
- `C:\Benutzer_Deutung_Start`
- `C:\Benutzer_Trends_Start`

### Struktur

Unter jedem Root:
- ein uebergeordneter Klientenordner
- darunter pro Lauf ein Session-Ordner mit Zeitstempel

Beispiel:
- `...\Mustermann_Klaus_09041966_Augsburg\20260630_101500_TOP5_SESSION\...`

### Wichtige Regel

- Synergy- und Remedy-Berichte duerfen nicht mehr als falsch verschachtelte Sonderordner innerhalb des Archivbereichs auftreten
- die Web-UI muss diese Struktur sichtbar und verstaendlich machen

## Berichtsanzeige in der Web-UI

### Ziel

Alle Berichtstypen sollen nach Session sauber auffindbar, previewbar und oeffenbar sein.

### Bereiche

- Resonanz
- Synergy
- Remedies
- Deutung
- Trends

### Reihenfolge pro Bereich

- letzte Session oben
- HTML priorisiert
- danach JSON
- dann TXT
- PDF zusaetzlich direkt oeffnbar

### UI-Funktionen

- Inline-Vorschau
- Originaldatei oeffnen
- Session-bezogene Sortierung

## Adaptive Ergebnisbegrenzung

### Ziel

Die Berichte sollen nicht ueberfordern oder verunsichern.

### Default-Grenzen

- Resonanzuebersicht: 7
- pro Gruppe: 15-20
- Synergy-Kombinationen: 5-10
- Remedy-Hauptliste: 12-20
- Trend-Highlights: 5-10
- Deutungs-Kernbefunde: 5-8

### Zusatzregel

- erweiterte Listen nur optional ueber "Mehr anzeigen"
- Standardansicht bleibt kliententauglich und ruhig

## Harmonisierung in der Web-UI

### Ziel

Die Harmonisierung wird an `Run-MultiplexScan.ps1` ausgerichtet, nicht an Radi144.

### Anforderungen

- echte Modi aus PS1 sichtbar machen
- Modi kurz erklaeren
- Harmonisierung als Session-Abschluss integrieren
- Status und Fortschritt sichtbar machen

## Migration in `apps/web/*`

### Phase 1 Umsetzungskern

In `apps/web/*` werden integriert:
- Personalprofil + Templates
- Entropy-Mode
- Bildoption
- produktiver Job-Flow entlang PS1/CLI
- sichtbare Steps/Substeps
- saubere Berichtslisten und Vorschau
- konsistente Ordner-/Sessionlogik
- adaptive Ergebnisbegrenzung
- PS1-konforme Harmonisierungsauswahl

### Legacy-Behandlung

- `web_ui/*` und `web_app.py` bleiben waehrend der Uebergangszeit bestehen
- nach erfolgreicher Vollmigration und Testfreigabe werden sie entfernt

## Nicht anfassen / Stabilitaetsgrenze

Nicht unnoetig umbauen:
- `core/*`
- `services/*`
- produktive CLI-Fachlogik, ausser dort, wo fuer Berichts-/Pfadkonsistenz zwingend erforderlich

Bevorzugte Anpassungsorte:
- `apps/web/*`
- Berichtskatalog / Web-Reportzugriff
- Orchestrierung / Job-Status / Vorschau / UI-Steps

## Phase-1-Erfolgskriterien

Phase 1 gilt als erfolgreich, wenn:
- genau eine konsolidierte Ziel-Web-UI in `apps/web/*` vorhanden ist
- der Nutzer den produktiven Top-N-Flow komplett aus der Web-UI starten kann
- Berichte aller 5 Bereiche korrekt erzeugt und pro Session archiviert werden
- Berichte in der UI sichtbar, sortiert, previewbar und oeffenbar sind
- Harmonisierung gemaess PS1 sauber als Session-Abschluss funktioniert

## Phase-1 UX-/Berichtsverfeinerung (nachtraeglich abgestimmt)

### Ziel

Die klientenseitige Web-UI und die HTML-Berichte sollen deutlich ruhiger, lesbarer und professioneller wirken. Radi144 bleibt weiterhin nur eine visuelle UX-Vorlage; die fachliche Referenz bleibt `Run-MultiplexScan.ps1`.

### Berichtskatalog

- In der Klienten-UI werden nur noch **HTML-Berichte** sichtbar gelistet.
- PDF-, JSON- und TXT-Dateien werden weiterhin erzeugt, aber im Katalog ausgeblendet.
- Pro Session sollen die relevanten Berichtstypen untereinander klar angeordnet sein:
  1. Resonanz
  2. Synergy
  3. Remedies
  4. Deutung
  5. Trends
- In der Kataloganzeige werden nur Titel und ggf. Zeitinformation angezeigt, keine technischen Pfade.

### Session-/Titeldarstellung

- Dateinamen duerfen technisch stabil und sortierbar bleiben.
- Die UI zeigt lesbare, kliententaugliche Titel, z. B.:
  - `Deutung - 30.06.2026 21:24 - Deisenhofer Klaus`
  - `Synergy-Gesamtanalyse - 30.06.2026 20:53`
- Wenn sinnvoll, werden auch die Dateinamen vereinheitlicht, z. B. in der Form:
  - `deutung_2026_06_30_21_24_44_Deisenhofer_Klaus`

### Layout Berichtskatalog / Vorschau

- Die linke Session-/Katalogspalte wird auf ca. 24-28% Breite reduziert.
- Die Vorschau bekommt ca. 72-76% Breite.
- Auf kleineren Displays wird die Sessionliste einklappbar bzw. oberhalb der Vorschau dargestellt.

### Listenbegrenzung / Ueberforderung vermeiden

- Grosse Listen sollen nicht in voller Laenge direkt sichtbar sein.
- Standardregel fuer grosse Berichtslisten:
  - **maximal 21 sichtbare Eintraege**
  - bei mehr als 30 Eintraegen: Scrollcontainer mit begrenzter Hoehe
  - der Rest bleibt ueber Scrollen erreichbar
- Speziell fuer Remedy-Berichte gilt standardmaessig:
  - sichtbar nur die Top 21
- Dasselbe Prinzip gilt fuer Resonanz-, Synergy-, Trend- und Deutungslisten, sofern deren sichtbare Standardmenge zu gross wird.

### PDF-Darstellung

- PDF-Berichte bleiben im Dateisystem erhalten, werden aber in der Klienten-UI vorerst nicht prominent angezeigt.
- Die UI ist in Phase 1 **HTML-first**.
- PDFs koennen spaeter in einem Experten-/Admin-Kontext wieder sichtbar gemacht werden, sobald das PDF-Layout hochwertig genug ist.

### HTML-Berichtslayout

- Die HTML-Berichte sollen professioneller und besser lesbar werden durch:
  - klarere Zwischenueberschriften
  - mehr Weissraum / Abstaende
  - ruhigere Tabellenstruktur
  - konsistente Score-Darstellung
  - klarere Hervorhebung von Ebenen/Levels
  - Scrollcontainer fuer lange Ergebnislisten

### Barrierefreiheit / Responsivitaet

Bereits in Phase 1 mitzudenken:

- klare semantische Ueberschriftenstruktur
- ausreichende Kontraste
- sichtbare Fokuszustaende
- Tastaturbedienbarkeit
- keine rein farbbasierte Statuskommunikation
- responsive Darstellung fuer verschiedene Endgeraete
- sinnvolle Scrollcontainer und Zielgroessen fuer Interaktion
- vorbereitende Accessibility-Aspekte im Sinne spaeterer E-E-A-T-/Webqualitaetsanforderungen

### Umsetzungsreihenfolge fuer diese Zusatzrunde

1. Berichtskatalog HTML-only
2. Sessionliste schmaler / Vorschau breiter
3. Titel- und Session-Darstellung lesbarer machen
4. Listenbegrenzung + Scrollcontainer
5. HTML-Berichtslayout lesbarer machen
6. Barrierefreiheitsverbesserungen in der Web-UI-Grundstruktur
- Ergebnislisten kliententauglich begrenzt sind
- Scores konsistent entzerrt und auf 3 Nachkommastellen gerundet angezeigt werden

## Hinweis zum Git-Commit

Diese Spezifikation ist geschrieben, aber absichtlich **nicht committed**, da in diesem Projekt Commits nur auf ausdruecklichen Wunsch erstellt werden.
