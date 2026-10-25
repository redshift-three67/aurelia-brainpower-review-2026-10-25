# Design- und Modulvertrag: vorbereiteter Delta v0.2 — 04.10.2026

**Status: Entwurf zur Vorbereitung; keine Änderung der Aurelia-Plattform oder kanonischen Modul_Templates.** Der isolierte RadiWorks-Kandidat runtime/rw-gv2-20261004 setzt einen Teil lokal um; seine Abnahme ist kein Plattformnachweis. Quellenstände und Hashes stehen in REFERENCE_SOURCES.json desselben Kandidaten.

## Abgleich

Aurelia docs/08-ui-a11y.md und src/styles.css sehen selbst gehostete Fraunces/Source Sans 3, semantische Tokens, Salbei/Pergament, 44px Ziele, Fokus und reduzierte Bewegung vor. Modul_Templates/standards/UI_DESIGN_STANDARD.md enthält einen älteren Token-/Overridevertrag. Governor-Design bleibt Vorlage für Raster, Navigation, Formulare, Tabellen und Zustandsanzeige; Fachlogik, Routing und Datenmodelle werden nicht kopiert.

Betreiber-Nachtrag: Dunkel ist die Rückfallpräferenz bei fehlender ausdrücklicher Wahl. Gültige Nutzer-/Hostpräferenz hat Vorrang. Modulakzente separat nach Modulkennung, kontrastfähige Hell-/Dunkelwerte. Ruhige Salbei-/Petrol-/Sandvarianten sind Gestaltung, keine nachgewiesene Heilwirkung. Ein gemeinsamer Theme-Vertrag und migrationsfreier Präferenzscope müssen vor Plattformübernahme entschieden werden. Bestehende Systeme haben unterschiedliche Tokenbezeichner; deshalb Mapping statt CSS-Kopie.

## Prüfbare Ziele

- Semantische Rollen: Hintergrund/Fläche, Text/Hinweis, Aktion, Fokus, Fehler/Warnung, neutrale/steigende/fallende Zahlen. Modulakzent darf Statusbedeutung nicht umdeuten.
- Textkontrast 4,5:1 für normalen und 3:1 für großen Text; Bedienelement-/Fokuskontrast prüfen, Tabellenziffern bündig und tabular, Text/Pfeile ergänzen Farbe.
- Tastatur, sichtbarer Fokus, 320/390px Reflow, Zoom, Fehler-/Leer-/Offlinezustände und Theme-/Modulwechsel prüfen. Lokale Einzelproben sind keine pauschale WCAG-2.2-AA-Zertifizierung.
- Schriftdateien nur lokal und mit Lizenz, robuste Fallbacks; kein externer Fontabruf. Quellen/Grenzen/Nachvollziehbarkeit dienen E-E-A-T, das keine Farb- oder Barrierefreiheitszertifizierung ist.

## Neue getrennte Modulverträge

**GV-2 v1**: Explizite Beobachtung pro aktivem gebundenem Promotions-Broadcast. Eigene OS-Entropie, verschlüsseltes Journal, 1260s, Neustart aus. Unveränderlicher Scope/Fall/Session/Ratenbezug; keine Wiederzuordnung an den aktuell geöffneten Fall. Direct/Auto bleiben unverändert und ohne erfundene Bindung ausgeschlossen. Historie hat 1000 Zeilen pro Broadcast, 256 Dateien und 1MiB pro Datei als aktuelle Grenzen; UI zeigt höchstens 200 jüngste Zeilen mit Kürzungshinweis. Delta ab 200 ist reine Anzeigegrenze. Raten-, Fall- und Broadcastbeobachtung nicht vermischen.

**VF-2/VF-3/EXP-1**: strukturierter persönlicher Kontext und versionierter Auftragssnapshot; erklärbare Suche mit Nutzerbestätigung; zusätzlich autorisierter eigener Radi144-Experimentalmodus. Siehe RADIWORKS_VEKTOR_EXPERIMENT_V01_2026-10-04.md. VF2-A/B und VF3 sind inzwischen im isolierten Kandidaten implementiert; EXP1 ist offen. Keine kanonische Produktions-/Aurelia-Übernahme. Siehe aktuelle Abschlussberichte.

## Zuständigkeit und offene Plattformpunkte

Aurelia muss Tenant/Client/Job aus Hostautorität bereitstellen, Berechtigung/CSRF/Lifecycle/Quoten/Archivierung über Adapter festlegen und Scopegrenzen testen. Lokale feste Prozessscopes sind kein Nachweis von Mehrmandantensicherheit. Scope-/Fallbezug und Präferenzisolierung müssen je Modul implementiert werden. APIs/Schemas/Adaptermanifest der gemeinsamen Referenzen sind vor einer Freigabe versioniert zu ergänzen, danach Consumer-Vertragstests. G0-SRV-GROUND-ZERO und eigene Integrationsentscheidung bleiben geschlossen. D0 Quellenabgleich erfolgt; D1 Vertrag als Entwurf; D2/D3 nur lokaler Kandidat; D4 keine Integrationsfreigabe.

Quellen: WCAG 2.2 https://www.w3.org/TR/WCAG22/ ; Kontrast https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html ; Google hilfreiche Inhalte https://developers.google.com/search/docs/fundamentals/creating-helpful-content .


## Plattformweite Betreibergrenze — 04.10.2026

Bestehende stabile Algorithmen und Heuristiken bleiben die Grundlage für RadiWorks und sämtliche aktuellen/künftigen Aurelia-Module. Keine semantische KI-Suche, neuen Embeddings oder anderen Analyseverfahren ohne ausdrückliche vorherige Besprechung. VF-3 nutzt erklärbare Katalog-/Wort-/Themenheuristik; EXP-1 bleibt der ausdrücklich genehmigte, getrennte Radi144-Heuristikmodus. Nicht automatisch auf andere Module ausweiten. Änderungen ergänzen bestätigte Funktionen; keine verdeckte Ersetzung.

## VF2-B-Delta — lokal geprüft, kanonische Übernahme offen
VF2-A/B im Kandidaten abgeschlossen: feste Fall-ID/Kontextversion, unveränderlicher Session-/Draft-Snapshot und Promote-Referenz; explizite zugängliche persönliche Felder und normalisiertes Fokusbild. Der partielle Patch verlangt erwarteten Fallverweis/Version, erhält unberührte Originalwerte und fängt Fallwechsel vor Antwortübernahme ab.

Lokale POST/GET /context-images speichern begrenztes CRC/Raster/SHA-geprüftes PNG pro festem Prozessscope. Keine Originaldateinamen/Bildmetadaten und keine Originalgewichtung. Bildinhalt bleibt gegebenenfalls personenbezogen. Historische Referenzen verlangen Assets im Backup; Entkopplung bedeutet kein sofortiges Löschen. Der Produktionsadapter muss Hostautorität, private Assetrechte, Quoten, Archivierung, Löschregeln und Exporte festlegen. Keine Aurelia-API-/Mehrmandantenfreigabe. VF3/EXP1 offen. Nachweise im VF2-B-Bericht; 8103–8110 unverändert.


## VF3-Delta — Kandidatenvertrag, 05.10.2026
Zwei zusätzliche read-only POST-Routen: /database-suggestions und /database-suggestions/confirm. Nur gespeicherter Fokus und explizite Themen, höchstens zwölf normalisierte Wörter und acht Vorschläge. Persönliche Identität/Bild ausgeschlossen; regelbasierte Wortübereinstimmung, keine KI-Semantik/Originalgewichtung. Jede Auswahl wird bewusst bestätigt und als exakte .txt-Datenbank gewählt; kein Analyse-/Broadcast-Auftrag durch die Suchhilfe.
Erwarteter Fallverweis und Kontextversion binden die Suche. Regelversion catalog-lexical-v1 und Dateisnapshot-Digest belegen den damaligen Quellenstand. Bestätigung liest/prüft erneut; keine zukünftige Ausführungslease. Release-Dateien vollständig innerhalb der dokumentierten Quoten hashgeprüft; Änderungen/fehlende Quellen kontrolliert abgewiesen. Originalleser-UTF8-Ersatz wird mit Dateianzahl sichtbar gemeldet. Kein automatischer Charsetwechsel, Upload oder Modellaufruf.
Adapterbedarf: Hostautorität/Scope, Berechtigungen, Request-/Katalogquoten, Datenschutz für Fokus/Themen, Quellenfrische und explizite Auswahl erhalten. Querytext nicht in URLs, Browserpersistenz oder Anwendungslogs ablegen. Lokale Prozess-/Fallbindung ist weiterhin kein Nachweis der Aurelia-Mehrmandantenrechte. Kanonische Modul_Templates-/Aurelia-Übernahme bleibt offen.
