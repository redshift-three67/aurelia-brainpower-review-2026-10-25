# Radi144 – Exakter, präziser und vollständiger Wortlaut für den Start einer neuen Session

Stand: 2026-06-03 23:46:48
Projekt: Radi144
Branch: `wellenreiter`
Commit-Basis: `eec781a`

## Normative Hauptfassung

```text
Radi144 – Start einer neuen Analyse-Session

Bitte wählen Sie den Typ der neuen Session.
Danach werden die zugehörigen Vektordaten, Fokus-Themen und Analyseparameter vollständig erfasst.
Anschließend wird die Analyse berechnet, dokumentiert und im Session-Kontext archiviert.
```

## Vollständige operative Langfassung

```text
Radi144 – Start einer neuen Analyse-Session

Bitte wählen Sie den Typ der neuen Session.
Diese Auswahl legt fest, welche Vektorquelle verwendet, welche Eingabedaten erfasst und welche Analysepfade aktiviert werden.

Verfügbare Session-Typen:
[1] Einzelklient – Analyse auf Basis einer einzelnen Person
[2] Gruppen-Analyse – Analyse einer Gruppe bzw. eines gemeinsamen Gruppenvektors
[3] Geo-Resonanz – Analyse eines Ortes, Grundstücks oder räumlichen Koordinatenpunkts
[4] Bild-Resonanz – Analyse einer Bilddatei als Vektorquelle

Im nächsten Schritt werden die für den gewählten Session-Typ erforderlichen Eingabedaten vollständig aufgenommen.
Danach folgen Fokusdefinition, Konfigurationswahl, Berechnung, Berichtserstellung, Session-Archivierung und optional die Harmonisierung.
```

## Präziser Wortlaut je Session-Typ

### Einzelklient

```text
Neue Session: Einzelklient

Bitte erfassen Sie jetzt die Klientendaten für diese Session.
Erforderlich sind Vorname, Nachname, Geburtsdatum und Geburtsort.
Ein Geburtsplanet kann optional ergänzt werden.
Diese Angaben bilden den Klientenvektor für die nachfolgende Analyse.
```

### Gruppen-Analyse

```text
Neue Session: Gruppen-Analyse

Bitte wählen Sie jetzt die Eingabemethode für die Gruppenmitglieder.
Sie können eine JSON-Datei importieren, eine TXT-Liste übernehmen oder die Mitglieder manuell erfassen.
Die erfassten Personendaten werden zu einem gemeinsamen Gruppenvektor zusammengeführt.
```

### Geo-Resonanz

```text
Neue Session: Geo-Resonanz

Bitte erfassen Sie jetzt die Koordinaten, den optionalen Radius und eine eindeutige Bezeichnung für den Ort.
Diese Angaben definieren den Geo-Vektor für die nachfolgende Analyse-Session.
```

### Bild-Resonanz

```text
Neue Session: Bild-Resonanz

Bitte wählen Sie jetzt eine Bilddatei als Vektorquelle für diese Session.
Unterstützt werden JPG, PNG, BMP und TIFF.
Die ausgewählte Datei wird als Bildvektor in den weiteren Analyseablauf übernommen.
```

## Übergang nach der Typwahl

```text
Die Session-Grundlage wurde festgelegt.
Bitte vervollständigen Sie jetzt die Vektordaten und den fachlichen Fokus dieser Analyse.
Im Anschluss werden Konfiguration, Berechnung, Berichtserstellung und optional Harmonisierung ausgeführt.
```

## Wortlaut für den Fokus-Start

```text
Bitte definieren Sie jetzt den Fokus dieser Session.
Sie können einen einzelnen Fokus, mehrere Fokus-Themen in Sequenz oder vorbereitete Fokus-Vorschläge verwenden.
Die Fokusdefinition steuert die nachfolgende Resonanzberechnung und die spätere Berichtsstruktur.
```

## Wortlaut für den Konfigurationsübergang

```text
Die fachlichen Eingabedaten dieser Session sind vollständig erfasst.
Bitte legen Sie nun die Analysekonfiguration fest.
Dazu gehören insbesondere Matrixgröße, Berechnungsmodus, Gewichtung, Palette sowie optionale Module wie Planetarisch, EMF, HRV, Verstärker und Symmetrie.
```

## Wortlaut für den eigentlichen Berechnungsstart

```text
Die neue Session ist vollständig vorbereitet.
Radi144 startet jetzt die Berechnung mit der gewählten Vektorgrundlage, den definierten Fokus-Themen und der aktuellen Analysekonfiguration.
Die Ergebnisse werden anschließend dokumentiert, exportiert und im Session-Kontext abgelegt.
```

## Kurzfassung für spätere UI-/CLI-Harmonisierung

```text
Radi144 – Neue Session
Bitte wählen Sie den Analyse-Typ und erfassen Sie anschließend die vollständigen Vektordaten, Fokus-Themen und Analyseparameter.
Nach Abschluss der Eingaben wird die Session berechnet, dokumentiert und archiviert.
```

## Empfohlene Standardfassung

Wenn genau eine einzige zentrale Formulierung als Standard verwendet werden soll, ist diese Fassung die empfohlene Referenz:

```text
Radi144 – Start einer neuen Analyse-Session
Bitte wählen Sie den Typ der neuen Session. Danach werden die zugehörigen Vektordaten, Fokus-Themen und Analyseparameter vollständig erfasst. Anschließend wird die Analyse berechnet, dokumentiert und im Session-Kontext archiviert.
```
