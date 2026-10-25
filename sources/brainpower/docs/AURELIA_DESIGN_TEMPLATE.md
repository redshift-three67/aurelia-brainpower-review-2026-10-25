# Aurelia: Hermes-Design als visuelle Vorlage

Betreiberwunsch vom 24.09.2026: Das **Design-Template** der Hermes-/Governor-Oberfläche dient später als Vorlage für Aurelia und ihre Module. Dieser Auftrag überträgt ausschließlich die Gestaltung. Hermes-Routing, Datenmodelle, Freigaben und Bedienfunktionen werden daraus nicht auf Aurelia übertragen.

Quelle ist die bestehende Oberfläche in `governor_workbench/static/style.css` mit den Modi System, Hell und Dunkel. Wiederverwendbar sind Seitenraster, Navigation, Typografie, Karten/Tabellen, Formulare, Zustandsanzeigen, Fokusmarkierung, responsive Regeln und semantische Farbvariablen. Der gemeinsame Grundstil bleibt für Plattform und Module gleich.

Lesender Machbarkeitsabgleich am 25.09.2026: Aurelia besitzt bereits `src/styles.css` mit Tailwind-`@theme`-Variablen, eigener Typografie und semantischen Farben. Eine Übernahme ist deshalb als **Token- und Komponentenabbildung** umsetzbar; ein ungeprüftes Kopieren der Governor-CSS würde Aurelias bestehende Gestaltung und Komponenten überlagern. Welche vorhandenen Aurelia-Komponenten bestehen bleiben, entscheidet D0/D1 anhand ihres aktuellen Quellstands.

Jedes Modul erhält später eine **eigene Akzentpalette**, die der Nutzer wählen oder in einem begrenzten Farbschema definieren kann. Die Palette ändert nur semantische Akzenttokens für primäre Aktionen, aktive Navigation, Hervorhebung und Fokus. Hintergrund, Text, Warnung, Fehler und Status behalten gemeinsame Kontrast- und Bedeutungsregeln; dieselbe Akzentwahl braucht passende Hell- und Dunkelwerte. Eine Modulwahl darf andere Module und die Plattform nicht umfärben. Gespeicherte Auswahl wird nach Modulkennung getrennt; ein unbekanntes oder ungültiges Schema fällt auf den Aurelia-Standard zurück.

Vor der Umsetzung auf Aurelia: Bestandsaufnahme der dortigen UI, Token-Schnittstelle und Zuständigkeit für gespeicherte Nutzerpräferenzen; danach ein isoliertes Template mit Kontrast-, Tastatur-, Mobil- und Modulwechselprüfung. Hier ist noch **keine Aurelia-Oberfläche geändert** und kein Modul implementiert.

Zeitliche Einordnung: Nach der Hermes-Funktionsabnahme werden RadiWorks, Radi144, `morphic_v1` („Radimorphic“) und ein neues Modul mit eigenem Projektpfad einzeln lokal vorbereitet und live geprüft. Der Designvertrag und modulweise Akzentvarianten werden dabei soweit ohne Aurelia-Serverimplementierung möglich vorbereitet. Nach diesen Prototypen wird D0–D4 in den vollständigen Produkt-Matrixplan aufgenommen; die tatsächliche Aurelia-Integration und Plattformabnahme folgen erst nach dessen gesonderter Prüfung und den geltenden Server-/Produktgates. Die [beschlossene Reihenfolge](MODULUEBERGANG_UND_BETREIBERPRUEFUNG.md) ändert keine Gate-Zählung.

## Verbindliche Planungsstruktur für die Aurelia-Matrix

Diese Anforderung gehört in die Planung der **Aurelia-Plattform und jedes ihr zugeordneten Moduls**, auch bei später neu aufgenommenen Modulen. Sie ist ein eigener Gestaltungsstrang neben Funktions-, Schnittstellen-, Sicherheits- und Betriebsnachweisen. Die Anzeige als Planungsanforderung zählt nicht als abgenommener Governor-Gate-Schritt und erteilt keine Produktfreigabe.

| Phase | Plattform Aurelia | Jedes Modul |
|---|---|---|
| D0 · Bestand | Bestehende Aurelia-Oberfläche, verwendete Komponenten, Styles und Präferenzspeicher mit Quellenstand erfassen. | Eigene UI oder ausschließlich von Aurelia bereitgestellte Oberfläche ausdrücklich feststellen. |
| D1 · gemeinsamer Vertrag | Aus dem Hermes-/Governor-Design nur Layout, Navigation, Typografie, Komponenten und semantische Tokens als versioniertes, isoliertes Design-Template ableiten; die Zuständigkeit von Modul_Templates für Vertrags-/Tokenabgleich klären. | Gemeinsamen Vertrag übernehmen; Fachlogik, Kernengine und Modulverträge bleiben eigenständig. |
| D2 · Themenwahl | Aurelia-Standardpalette, System/Hell/Dunkel und sichere Rückfallwerte definieren. | Pro stabiler Modulkennung getrennte wählbare Akzentpalette und gegebenenfalls begrenzte benutzerdefinierte Kombination; bei Headless-Modulen gilt dies für ihre Aurelia-Oberfläche. |
| D3 · Prüfung | Kontrast, Fokus, Tastatur, responsive Ansicht und Zustandsfarben an realen Aurelia-Seiten prüfen. | Hell/Dunkel, Modulwechsel, Wiederladen und ungültige Wahl prüfen; eine Modulfarbe darf Plattform und andere Module nicht ändern. |
| D4 · Abnahme | Tatsächliche Aurelia-Implementierung und Betreiberabnahme erst nach ihren eigenen Produktgates. | Modulweise Live- und Integrationsprüfung mit eigener Freigabe; kein Schluss aus einem anderen Modul. |

Ein gruppenweiter Matrixplan muss D0–D4 für Aurelia und die betroffenen Module nachvollziehbar zuordnen. Bei einem Einzelplan bleibt die gemeinsame Template-Version als Abhängigkeit sichtbar. Neue Module erhalten diese Anforderung bei der Aufnahme, ohne automatisch dieselbe Farbpalette oder denselben Fertigstellungsstand zu erben. Bis ein versionierter Vertrag und tatsächliche Prüfbelege vorliegen, lautet der Status **Planung offen**; weder Kartenfarbe noch ein Review dürfen „umgesetzt“ suggerieren.

## Betreiber-Nachtrag und Modulvorbereitung, 04.10.2026

Dunkel wird für neue RadiWorks-Konfigurationen ohne ausdrückliche Nutzer-/Hostwahl vorbereitet; gültige Präferenzen bleiben erhalten. Ruhige Salbei-/Petrol-/Sandvarianten, lokale Schriftversorgung, sichtbarer Fokus und textlich erklärte Zahlenverläufe sind gemeinsame Gestaltungsziele. Keine Heilwirkungs- oder pauschale Barrierefreiheitsbehauptung. Das ist eine versionierte Vorbereitung; Aurelias laufende Oberfläche und die kanonischen Modul_Templates wurden hier nicht geändert.

Der [Delta-Vertrag v0.2](verification/RADIWORKS_AURELIA_TEMPLATE_DELTA_V02_2026-10-04.md) gleicht die vorhandenen Aurelia-Tokens/Schriftanforderungen mit der älteren Template-Referenz ab und beschreibt getrennte GV-2-, Kontext- und Experimentalverträge. D0 Quellenstand erfasst, D1 als Entwurf; D2/D3 zunächst am isolierten RadiWorks-Kandidaten, D4 weiterhin gesondertes Gate.

Plattformweite Betreibergrenze: Die stabilen bestehenden Algorithmen/Heuristiken bleiben die Grundlage aller aktuellen und zukünftigen Module. Semantische KI-Suche, neue Embeddings oder Ersatzalgorithmen nur nach ausdrücklicher vorheriger Besprechung. Der freigegebene [Radi144-Experimentalmodus](verification/RADIWORKS_VEKTOR_EXPERIMENT_V01_2026-10-04.md) bleibt getrennt und ist keine allgemeine Ersetzungsgenehmigung. Persönliche Felder, Suche und Zahlenheuristik haben getrennte Aufgaben; laufende Aufträge behalten ihren Kontextstand.
