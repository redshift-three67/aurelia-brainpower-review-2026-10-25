# P3 â€“ Radi144: Anfrage und tatsÃ¤chlich wirksame Einstellungen

## Betreiberentscheidung zur Fortsetzung

Der Betreiber bestätigt am14.10.2026 die Empfehlung: Original unverändert erhalten, die drei Requestoptionen im untersuchten Pfad als bekannte Vertragslücke führen und P3 fortsetzen. Keine neue auftragsbezogene CUDA-/Quantum-/Iterationssteuerung implementiert. Folgeschritt ist eine begrenzte synthetische Übergabecharakterisierung; Wunschwerte, übergebene Parameter und beobachtete Antwortwerte getrennt. Der folgende Haltbefund bleibt als zeitbezogener Ausgangsstand erhalten. Neuer Nachweisbereich `checkpoints/Aurelia-P3-Radi144-API-Parameter-20261014-213342Z`; noch keine Originalausführung/Abnahme daraus ableiten.

Stand14.10.2026. **Quelllokale VertragslÃ¼cke bestÃ¤tigt; weitere AusfÃ¼hrung wie vom Betreiber gewÃ¼nscht angehalten.** Keine neue API-/Engineprobe, keine Originalreparatur. Der bestandene CPU-Teilnachweis bleibt erhalten.

Nach Abschluss der beiden begrenzten CPU-LÃ¤ufe wurden drei unverÃ¤nderte Originaldateien per AST geprÃ¼ft. Dies ist eine statische Verbindung zwischen Requestschema, konkretem API-Caller, dessen untersuchten Vorbereitungshilfen, Engine-Signatur und gespeicherter Sitzungskonfiguration. Keine vollstÃ¤ndige App-/CLI-/WebSocket-Abdeckung, Live-Reproduktion oder HTTP-Abnahme.

| Einstellung | Deklariert / gespeichert | Im untersuchten API-Analysepfad belegt | Bedeutung |
|---|---|---|---|
| `calculation_mode` | Schema default `quantum`; Session `mode` | Wird an `calculate_resonance` weitergereicht; Engine unterscheidet `precision` | TatsÃ¤chlich Ã¼bergebener Modus. Kein Nachweis aller Laufzeitkombinationen durch diesen AST-Abgleich. |
| `use_cuda` | Schema default true; Session speichert Requestwert | Nicht im Berechnungsaufruf oder untersuchten vorbereitenden Helpern genutzt. Globale Engine beim Modulstart zunÃ¤chst `use_cuda=True`, Fehlerfallback false; Konstruktor berÃ¼cksichtigt GerÃ¤teverfÃ¼gbarkeit. | Request false erzwingt im geprÃ¼ften Weg nicht nachweislich CPU. Der gespeicherte Wunschwert ist kein GerÃ¤tenachweis. TatsÃ¤chliche Hardware wird getrennt aus dem Ergebnis Ã¼bernommen. |
| `use_quantum` | Schema default true; Session speichert Requestwert | Nicht im Berechnungsaufruf oder untersuchten vorbereitenden Helpern genutzt | Von `calculation_mode`, Enginezustand `quantum_active` und `dwave_enabled` trennen. Kein Beleg fÃ¼r eine wirkende Umschaltung durch dieses Requestflag. |
| `iterations` | Schema default1000, Minimum100 | Nicht weitergereicht; `calculate_resonance` besitzt keinen entsprechenden Parameter. Nicht in der untersuchten Sessionkonfiguration gespeichert. | Keine belegte Steuerung der Rechenanzahl in diesem Pfad. Daraus keine Aussage Ã¼ber andere Einstiege ableiten. |

**Konkrete Quellen:** `app/schemas/resonance.py:8â€“29`, `app/api/resonance.py:28â€“34` (globale Engine), `:90â€“125` (Sessionmirror), `:299â€“389` (Vorbereitung), `:414â€“466` (Analyseroute, Rechenaufruf ab441), `app/algorithms/resonance_engine.py:40â€“70` (Konstruktor), `:243â€“303` (Berechnung/Precisionzweig). Zeilennummern gelten ausschlieÃŸlich fÃ¼r die drei gebundenen Hashes im Nachweis.

| Originaldatei | SHA-256 |
|---|---|
| app/schemas/resonance.py |7179f3a5f34d356ecc4f9751fdb51c227bb2a3857d44ba8d1624c33d4000349c|
| app/api/resonance.py |a161551637e4149d3c8962cf870bca075d337f43cc798979a53b7c94ca538983|
| app/algorithms/resonance_engine.py |2aef926e2885adaee5a0724aaea827daf03d4363f07ed399d08d5e2c31333a09|

HEAD `b8ac33a1360f1cb56f06e602fcd37cbda2a9c641`; Status genau dieser drei getrackten Pfade leer und Quellhashes nach Aufnahme gleich. Keine Aussage Ã¼ber ein insgesamt sauberes Repository; bestehendes vorgemerktes AGENTS.md bleibt erhalten.

## Konsequenz und empfohlene Entscheidung

FÃ¼r P4/P5 drei Ebenen getrennt fÃ¼hren: **angefordert**, **wirksam angenommen**, **tatsÃ¤chlich beobachtet**. UnverÃ¤nderliche Requestkonfiguration, wirksames Rechenrezept und Runtimebeobachtung dÃ¼rfen einander nicht ersetzen. Der vorhandene separate Hardware-Ergebniswert bleibt relevant; diese Aufnahme behauptet keine falsche Hardwareausgabe.

Empfehlung: Den unverÃ¤nderten Originalstand als Referenz erhalten und die drei Optionen zunÃ¤chst als bekannte VertragslÃ¼cke einordnen. Vor neuen API-Funktionsreferenzen festlegen, welche Optionen echte auftragsbezogene Steuerung werden sollen und welche nur Legacy-/KompatibilitÃ¤tsfelder sind. Eine neue Verdrahtung, Entfernung oder Umbenennung im Original ist keine Routinekorrektur dieses Nachweises und wurde nicht vorgenommen. Eine solche ProduktÃ¤nderung benÃ¶tigt ihren eigenen versionierten Umfang und passende Regressionen; keine neue Formel oder Plattformentscheidung ableiten.

Astra/medium bestÃ¤tigt Befund und Aussagegrenzen durch rein lesenden Quellen-/AST-/Hashreview. Root erzeugt den maschinenlesbaren AST-Abgleich und prÃ¼ft danach Quellen/HEAD/benannten Status erneut. Keine Anfrage an echte Dienste oder Klienten, kein Bibliotheks-/Engine-/Modulstart. Der Befund stoppt weitere AusfÃ¼hrung; reine Konsolidierung und Sicherung werden abgeschlossen.

Beleg und lokaler Dokumentenpunkt: `checkpoints/Aurelia-P3-Radi144-Parameter-20261014-211126Z/PARAMETER-CONTRACT.json`, `SOURCE-READBACK.json`, `INDEPENDENT-REVIEW.json`. VollstÃ¤ndiger gesicherter Umfang ausschlieÃŸlich durch `FINAL-MANIFEST.json` und `FINAL-READBACK.json`. Keine F:-/Server-/Gesamtprojektsicherung. Gesamt-P3, P4-Siebenermatrix einschlieÃŸlich Aurelia/Modul_Templates und P5-Entscheidung bleiben offen. Keine Live-/Produkt-/Template-/RoutingÃ¤nderung.
