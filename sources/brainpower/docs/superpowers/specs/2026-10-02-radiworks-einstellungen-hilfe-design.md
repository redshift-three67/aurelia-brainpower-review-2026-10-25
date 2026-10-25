# RadiWorks: verständliche Einstellungen

Stand: 02.10.2026. Der Betreiber hat die lokale Fokus-/Suchprobe bestätigt und verständliche Erklärungen der Einstellungen angefordert. Bestehende Schlüssel, Werte, Speicherroutine und Analyse-/Broadcast-Abläufe bleiben unverändert.

## Entscheidung

Die Einstellungen erhalten für jeden derzeit bekannten Schlüssel einen deutschen Namen, den technischen Schlüssel und einen kurzen Wirkungstext direkt am Bedienelement. Aktive Schalter werden als „Wirkt im Prototyp“ gekennzeichnet. Nur gespeicherte Original-Schalter werden als „Derzeit ohne Wirkung“ gekennzeichnet. Für unbekannte künftige Schlüssel steht ein konservativer generischer Hinweis. Der API-Vertrag bleibt unverändert; das Formular speichert weiterhin dieselben Boolean-/Integer-/String-Werte.

Aktiv nach Quellabgleich: `entropy.defaultMode` bestimmt den Modus für neue Aufträge mit „Einstellung (Server)“; `play.binaural.sound` schaltet den kurzen Browserton im Broadcast-Bereich; `broadcast.legacyMixMode` ermöglicht die ältere direkte Mix-Übernahme statt des getrennten Prüfen-/Freigeben-Schritts. Letzterer bleibt standardmäßig aus und erhält einen besonders klaren Hinweis. Alle anderen derzeit sichtbaren Boolean-Schlüssel werden zwar gespeichert, aber von keinem aktiven RadiWorks-Ablauf gelesen. Das UI darf daraus weder Wirksamkeit noch Originalparität ableiten.

## Oberfläche und Grenzen

Die drei vorhandenen Abschnitte bleiben erhalten. Jede Zeile erhält einen lesbaren Namen, einen Wirkungshinweis und einen Status. Die Rohschlüssel bleiben sichtbar, damit Betreiber und Entwickler denselben Wert identifizieren können. Die Entropiehilfe nennt `seeded` und `stochastic` und erklärt, dass ein aktiver Fall für Stochastic einen dauerhaft wiederherstellbaren Schlüssel benötigt. Es werden keine Einstellungen automatisch verändert oder gespeichert. Der UI-Test nutzt nur Lesen und Filtern; kein realer Fall und kein Broadcast wird für die Erklärung verändert.

Nach der UI-Prüfung folgen getrennt die bereits vorgesehenen S4.7-Arbeiten: eine additive Area-Vorschau neben dem bestehenden GV-Raster und eine explizite Peggotty-Kompatibilitätsentscheidung für doppelte Marken/eingerückte Befehle. Reale Kamera, Recovery-Schlüssel und Aurelia-Host bleiben gesonderte Gates.
