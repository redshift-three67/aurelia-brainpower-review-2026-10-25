# RadiWorks CopyGuard und Administrator Testmodus

Stand 11.10.2026. Betreiber fordert Erklärung, Berücksichtigung des Screenshots und einen Administrator-Bypass für Entwicklungstests. Die Ergänzung ist in der Restliste vorgemerkt; Schalter und neue Laufzeitdiagnostik sind noch nicht implementiert. P0–P3 behalten Vorrang. Produktcode, Liveinstanzen, laufende Aufträge und normative Modul_Templates bleiben unverändert.

## Aktuelle Prüfung

Der lokale CopyGuard ist eine DE/EN-Regelliste mit regulären Ausdrücken und ignorierter Groß-/Kleinschreibung. `check_text` meldet bei mindestens einem Treffer `block`, sonst `allow`. Beispiele sind „Heilung“, „Diagnose“, „cure“ und bestimmte Erfolgsversprechen. Die konkrete Regelliste ist ein Prototypausschnitt, kein vollständiger sprachlicher oder fachlicher Prüfer. Verneinung, Zitate und Kontext werden nicht verstanden: auch „Keine Diagnose“ ergibt einen Treffer. Keine lokale LLM-Stufe oder Cloudanfrage in dieser Lexikonprüfung; Aurelias zusätzliche Prüfstufe bleibt ein eigener Integrationspunkt.

| Weg | Aktuelle Wirkung |
|---|---|
| Auto-Broadcast | Nach Analyse und Kandidatenauswahl anhand Raten-/Fall-GV wird der Name der gewählten Rate geprüft. Ein Treffer beendet diese Auto-Generation, setzt Auto auf AUS und meldet `auto.error`, Phase `copyguard`, mit „CopyGuard blockt Auto-Broadcast“. Diese Meldung entspricht dem Betreiberbild. |
| Direkter Broadcast / Mix | Direkte Signatur beziehungsweise gewählte Raten werden vor Einreihung geprüft; ein Treffer sperrt den Auftrag. |
| Entwurf / Freigabe | Ratenbezeichnungen im Ergebnis werden geprüft; vor Promote erfolgt die Prüfung erneut. Ein bestätigter Prüfschritt allein hebt einen Block nicht auf. |
| Öffentliche Ausgabe | Gesperrte Strings werden in der HTTP-/Live-Projektion durch `[CopyGuard: Text zurückgehalten]` ersetzt. Interne Originaldaten und berechnete Werte werden dadurch nicht umgeschrieben. |
| Prüfdigest | SHA-256 über die sortierten geprüften Texte, getrennt durch ein festes Zeichen. Er bindet den Textstand; er ist keine Administratorberechtigung, Wirksamkeitsbewertung oder vollständige Regelversionsbindung. |

CopyGuard bewertet weder EW/GV noch Resonanz, Klientenreaktion oder Audiofrequenzen. Der Screenshot belegt den gemeldeten Auto-Fehler; aus ihm sind auslösende Originalrate, Regeltreffer und Port nicht bestimmt. Keine Liveursache aus anderen, früheren Recovery-/Stochastiksperren übernehmen. Der vorhandene interne `DraftStore.transition(force=...)`-Parameter ist kein bestätigter Adminschalter: der HTTP-Übergang erlaubt nur definierte Statuswerte, und der Promote-Vorbereitungspfad prüft CopyGuard erneut.

## Reihenfolge im gesicherten RadiWorks Wartungsblock

| Schritt | Geplanter Umfang und Abnahme |
|---|---|
| RW-C1 Ursache und verständliche Erklärung | Zusammen mit RW-F1/F2 Start-/Stopursachen unterscheiden. Sichere Fehlerkennung, Regel-ID und gebundene Rate/Index/Jobkennung anbieten; zurückgehaltenen Rohtext nicht über generische Browserfehler oder Logs ausgeben. Verständliche Hilfe: „Eine ausgewählte Ratenbezeichnung enthält eine durch die Textregeln gesperrte Formulierung. Die Automatik wurde angehalten.“ |
| RW-C2 Administrator Test-Bypass | Nach Ursachenaufnahme und Sicherung als ausdrücklich aktivierbare Fähigkeit einer isolierten lokalen Entwicklungstestinstanz entwerfen/prüfen. Standard AUS; serverseitige Adminberechtigung plus Entwicklungsprofil, synthetischer Test-Scope, Begründung und Befristung erforderlich. UI-Schalter allein genügt nicht; lokaler Windowsadminstatus darf nicht ungeprüft als RadiWorks-/Tenantberechtigung gelten. |
| RW-C3 Regression und Freigabe | Auto, Direkt-/Mix- und Draftwege in beiden Verfahren/Zufallsmodi prüfen, einschließlich Negativfälle, Restart, Widerruf, Ablauf, Parallelität und Kontextwechsel. Danach Betreiberabnahme; erst gesonderter Quell-/Adapter-/Modul_Templates-Abgleich und Versionierung. |

## Grenzen des geplanten Schalters

Empfohlen ist eine serverseitig gebundene Testausnahme für CopyGuard-Broadcastsperren. Eine globale Abschaltung würde auch öffentliche Ausgaben und normale Instanzen beeinflussen. Automatisches Überspringen gesperrter Raten wäre eine eigene Änderung des Auswahlverhaltens und ersetzt den gewünschten Testschalter nicht.

Der originale Guardbefund bleibt `block`; Testausnahme separat mit Bediener, Grund, Zeitpunkt, Scope, Regelversion/Textdigest und Auftrag dokumentieren. Keine falsche Umdeklaration zu `allow`, keine stillen Änderungen an Raten, Scores oder Algorithmen. Erfasste Aufträge behalten ihren Teststatus; Widerruf/Ablauf stoppt die betreffende Test-Automatik und verhindert neue Ausnahmeaufträge. Bereits laufende Test-Broadcasts behalten ihren gebundenen Auftrag und bleiben explizit stoppbar. Neustart reaktiviert die Testausnahme nicht automatisch.

Öffentliche Textprojektion, Eingabevalidierung, Fall-/Tenantgrenzen, Kontextbindung, Recovery-/Persistenzprüfung, Quotas und andere Sicherheitsstopps bleiben aktiv. Kein automatischer Bypass auf8103–8109, im regulären Start5 oder in Aurelia-Produktion. Die konkrete lokale Adminautorisierung muss vor Implementierung nachgewiesen werden; keine bestehende Rolle oder fertige Hostautorität aus diesem Plan ableiten. Später in P4–P8 Administrator-/Testrechte, Audit/Archiv, Adapter und Templates getrennt abstimmen.

## Quellen und Prüfgrenzen

Quelle: manifestgebundener R6-Release `runtime/rw-r6-release-20261008`. Alle200Produktdateien vor/nach diesem Nachtrag frisch hash-/größengeprüft; Manifest SHA256 `445ece8f8c826e1391fead34c9a4c9b271e3b13b6d59a7654f66f11ab77b6275`. Kein Nachweis aktuell geladener Bytes einer konkreten Liveinstanz.

- `engine/src/radiworks/copyguard.py`: Regelliste, Text-/Listenprüfung, Digest und unverändernde öffentliche Projektion.
- `engine/src/radiworks/core/automode.py:399–412`: CopyGuard-Kandidatensperre und Auto-Ende.
- `engine/src/radiworks/api/routes.py:2489–2511,2567`: HTTP-Statusgrenze, direkte/Mix-Broadcastsperre.
- `engine/src/radiworks/core/draft.py:87–89,293–338`: Draftprüfung, interner force-Parameter und erneute Promote-Prüfung.
- Bestätigter öffentlicher Ausgabevertrag: `docs/superpowers/specs/2026-09-29-radiworks-public-copyguard-design.md`.

Sieben rein synthetische Leseproben: sicherer Text, deutscher Treffer, englischer Treffer/Großschreibung, Verneinungsgrenze, gemischte Liste, Digest-Reihenfolge und unverändernde Projektion bestanden. Keine Auto-/HTTP-/Broadcast-/Browser-Laufzeitabnahme und keine Bypassfunktion daraus ableiten. Planpflege durch Leitung, keine zusätzlichen Helfer.
