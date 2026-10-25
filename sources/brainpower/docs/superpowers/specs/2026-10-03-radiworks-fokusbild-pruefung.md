# RadiWorks: optionales Fokusbild und tatsächlicher Vektorbezug

Stand: Quellenprüfung und Integrationsvorschlag, 03.10.2026. Keine Bildfunktion implementiert oder freigegeben.

## Tatsächliche Eingänge

Der bestehende normale Analysevertrag verwendet `database`, `seed`, `mode` und `max_hits`. Die Berechnung verarbeitet Raten und Entropie. Fallname, Fokus und Sitzungsabsicht werden anschließend als Kontext im Draft festgehalten. Die freigegebene Fokus-Suchfunktion filtert nach bewusstem Klick die Datenbankauswahl; sie verändert nicht automatisch deren Inhalt, Rangfolge oder GV.

Die aktuelle Falloberfläche hat keine getrennten validierten Felder für Vorname, Nachname, Geburtsdatum und Ort. Die bisherigen freien Fallnamen können solche Angaben enthalten; das ist keine algorithmische Vektorverarbeitung. Der 3-Fall-Versuch nutzt ausschließlich erfundene Angaben in diesem vorhandenen Namensfeld und das vorhandene Fokusfeld.

Ein Fokusbild ist kein Eingang von `/analysis`; ein zusätzlicher Parameter wird mit HTTP 422 abgewiesen. Die vorhandenen Funktionen „Bild & Area“ sind separate Abläufe. Sie ersetzen keine Bindung eines Bilds an den Fall oder an eine normale Ratenanalyse. Die Testbilder des aktuellen Versuchs bleiben ausdrücklich nur als lokale Referenz und SHA-256 im Versuchsmanifest.

## Möglichkeiten

| Möglichkeit | Nutzen | Grenze |
| --- | --- | --- |
| Lokales optionales Kontextbild | Fall/Fokus für den Nutzer erkennbar machen | keine Auswirkung auf EW, Auswahl, Potenz, Level oder GV; nach Reload ohne gespeicherte Bildreferenz erneut wählen |
| Persistiertes, fallgebundenes Kontextbild | wiederholbare Zuordnung und Nachvollzug über Sitzungen | zusätzlich Bildspeicher, sichere Validierung, Rechte, Löschung und Wiederherstellung erforderlich |
| Bild-/Identitätsdaten in einen neuen Auswahlalgorithmus einbeziehen | eigenständiger neuer Analysemodus möglich | kein unverändertes Originalverfahren; künstliche Seedänderungen belegen keine bessere Fallpassung |

**Empfehlung:** Kontextbild getrennt ergänzen, mit überprüfbarer Fall-/Fokuszuordnung und ohne heimliche Änderung der bestätigten Originalberechnung. Persistenz erst mit sauberem eigenem Bildspeichervertrag. Eine neue fallbezogene Auswahlfunktion wäre separat zu spezifizieren und als zusätzlicher ausdrücklicher Modus zu prüfen.

## Konkreter vorgeschlagener Bildvertrag

- Freiwillig; ohne Bild bleibt der vollständige bisherige Ablauf unverändert.
- JPEG, PNG oder WebP; maximal 5 MiB und 16 Megapixel als vorgeschlagene Produktgrenzen. Tatsächlicher Decoderinhalt muss zum Format passen. SVG-Testdateien im Versuchsmanifest sind keine Freigabe dieses Formats für das Produkt.
- Neutrale Beschriftung und Vorschau; keine Dateinamen, EXIF-Informationen oder eingebetteten Texte in Logs, Passport oder Modellanfragen. Entfernen bleibt ausdrücklich möglich.
- Spätere Speicherung über eine servergenerierte opake Bildreferenz, gebunden an Scope und Fall. Kein frei gewählter Dateipfad oder externer Bild-URL als Speicheradresse.
- Speichern/Entfernen prüfen den erwarteten Fallverweis, damit ein Fallwechsel nicht unbemerkt das Ziel ändert. Der bestehende prozessgebundene Verweis reicht noch nicht für einen dauerhaften Wiederanlaufvertrag.
- Neue Drafts erhalten einen unveränderlichen Kontext-Snapshot aus Bildreferenz, Hash und Kennzeichnung `context-only`; alte Sitzungen ändern sich nicht bei späterem Bildwechsel.
- SHA-256 bestätigt Bytegleichheit, nicht die Zuordnung zu einer Person und keine Anonymisierung. Für normalisierte Bilddateien müssen Original- und gespeicherter Hash klar unterschieden werden.
- Keine automatische Kameraaufnahme, externe Modellübermittlung, Seedableitung oder Veränderung bestehender Analysewerte.

## Voraussetzungen für Umsetzung und Aurelia

Der vorhandene gemeinsame Analysevertrag bleibt erhalten. Ein eigener optionaler Fallbild-Vertrag müsste in RadiWorks und dem lokalen Modul_Templates-Profil ausdrücklich ergänzt werden; ein solcher Nachtrag ändert keine bereits genehmigte gemeinsame Host-ABI. Aurelia muss den späteren Bildspeicher nach Mandant/Nutzer/Fall berechtigen und Aufträge anhand unveränderlicher Snapshots isolieren. Die aktuelle lokale Engine besitzt weiterhin einen aktiven Fall je Prozess; mehrere Browserfenster sind kein Ersatz für getrennte Jobs.

Tests für eine spätere Umsetzung: fehlendes Bild, erlaubte/abgewiesene Typen und Größen, Fallwechsel während Speichern, Entfernung, Reload/Wiederanlauf, Cross-Scope-Zugriff, unveränderter alter Draft und bytegleiche numerische Analyse bei gleichem Seed/Katalog mit und ohne Bild.

## Noch zu konkretisieren vor Implementierung

- Animierte/mehrseitige Bilder: zulässige Frame-/Seitenzahl, gesamtes Decoderbudget und Normalisierung festlegen. Die allgemeinen Dateigrößen-/Pixellimits allein reichen nicht.
- Entfernen: Aufheben der aktuellen Fallzuordnung und tatsächliche Byte-Löschung getrennt definieren; Referenzen alter Sitzungen, Berechtigungen und Wiederherstellung berücksichtigen.
- Der abgeschlossene 21-Minuten-Versuch hat kein Fokusbild numerisch verarbeitet. Siehe `docs/verification/RADIWORKS_VEKTOR_FOKUSBILD_21MIN_2026-10-03.md`.
