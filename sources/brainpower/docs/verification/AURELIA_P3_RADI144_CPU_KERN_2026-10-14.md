# P3 – Radi144: begrenzte CPU-Kernreferenz

Stand:14.10.2026, V10. **Begrenzte CPU-Kernreferenz bestanden: zwei unabhängige Läufe mit je14 Fallgruppen und81 geprüften Erwartungen; stabile Ergebnisobjekte vollständig gleich.** Gesamt-P3 und vollständige Produktabnahme bleiben offen. Der frühere Bootstrapblocker ist für diesen Umfang aufgelöst; historische Befunde unten gelten zu ihrem jeweiligen Zeitpunkt.

## Aktueller V10-Abschluss

Vier tatsächlich benötigte Torchgen-Module (`torchgen`, `torchgen.model`, `torchgen.utils`, `torchgen.code_template`) separat in der nativen Initialisierung gebunden. Vier Quellhashes und Dateigrößen stimmen mit dem gepinnten Torch-RECORD überein; zusätzlich METADATA, top_level und RECORD selbst hashgebunden. PathFinder bestätigt die exakten Quellursprünge ohne Paketinitialisierer. Dies belegt interne Installationskonsistenz, keine Herausgebersignatur, vollständige Wheel- oder Bytecodeprüfung. Andere Torchgen-Unterbereiche und functorch bleiben gesperrt. Die Bibliotheksinitialisierung führt ihren eigenen Code aus; ein DispatchKey-Fehlerzweig kann generierten Text ausgeben und RuntimeError auslösen. Kein Codegenerierungsauftrag gestartet.

Root-RED:39 Tests, genau zwei erwartete Assertionfehler vor Implementierung. Root-GREEN:39/39 erfolgreich und Controllerprüfung Exit0; eingefrorene Werkzeugbytes unverändert. Luna/max prüft den begrenzten Paketpfad lesend; Astra/medium prüft SPEC→QUALITY vor Ausführung und anschließend den tatsächlichen Ergebnisumfang. Zwei zusätzliche lesende Elternprüfungen zunächst mit falschem Helpernamen bzw. nicht angepasstem sys.path abgebrochen, danach korrekt mit den drei gebundenen Suchpfaden erfolgreich; kein nativer Versuch oder Ergebnisbeleg durch diese Fehlaufrufe erzeugt. Nachweis `ROOT-V10-FRESH-PREFLIGHT.json`.

| Lauf | Originalfallgruppen / Erwartungen | Controller / reine Fallzeiten | Ergebnis |
|---|---|---|---|
| cpu-run-6 | 14 /81 |56.063s /0.461159s|Exit0, kein Timeout, alle Erwartungen erfüllt|
| cpu-run-7 | 14 /81 |64.109s /0.097294s|Exit0, kein Timeout, gleiche stabilen Ergebnisobjekte|

Vollständige stabile Caseobjekte, Quellhashes, AST, Runtime, Werkzeug-/Bootstrap-/Paketbindung und Einschränkungen verglichen. Lediglich Laufkennung, Erstellzeit, Laufzeiten und Audit-Ereigniszähler sind getrennte Beobachtungen. Tensorwerte werden vollständig als kanonische JSON-Zahlen gehasht; Ergebnisbelege speichern Hash/Dimension/Datentyp/Min/Max und die Skalare, **keine Rohmatrixarrays**. Vergleichshash `2be0183a9a4faf33ad20d4de47b14a547fc1f194da225cf49261df8da6b8471d`. Die Suche prüft gleiche Seeds vollständig wiederholt; kein isolierter Vergleich nur unterschiedlicher Seeds bei sonst gleichen Suchparametern.

Tatsächliche Umgebung: Python3.11.12, Torch2.12.0+cpu, NumPy2.4.6, CPU, ein Rechen- und ein Interopthread, CUDA nicht initialisiert. Kandidaten64/96/160 für12/24/36; keine Vollpool- oder GPUabnahme. Vorher jeweils mindestens3.54GB physisch und8.97GB Commitreserve verfügbar. Zehn benannte Originalquellen, Werkzeugbytes, HEAD und benannter Gitstatus vor/nach gleich; zehn Paketpins danach erneut gleich. Kein insgesamt sauberer Repositoryzustand behauptet. Gate nach Verbrauch beider Laufkennungen geschlossen; kein weiterer nativer Lauf durch diese Bindung.

**Warnungsgrenze:** Beide Läufe enthalten je26 erhaltene UserWarnings aus Torch `_jit_internal`: JIT-Overload-Deklarationskörper konnten nicht inspiziert werden. Der Guard lehnt den von `ast.parse` standardmäßig verwendeten Dateinamen `<unknown>` ab; diese PermissionError-Unterklasse kann über den OSError-Fallback genau solche Warnungen auslösen. Die konkret verschluckte Exception ist nicht erhalten, ein fehlgeschlagener Quelldateizugriff daher nicht bewiesen. Die Overloadregistrierung läuft weiter; direkte geprüfte Tensoroperationen benötigen kein JIT. Astra bewertet dies für diesen Umfang ohne Ergebnisblocker. **Keine JIT-, vollständige Engine-/HTTP-/API-/UI-/CLI-/Stochastik-/Linux- oder klinische Abnahme.**

Charakterisierte Originalgrenzen bleiben sichtbar: Top-k größer als der speicherbedingt verfügbare Kandidatenpool führt zum Original-RuntimeError. Die kontrollierte Precision-Fehlerprobe verändert den Original-RNG-Zustand; Rücksetzen erfolgt hier durch das Harness, nicht nachgewiesen durch den Produktfehlerpfad. API-Amplifier-Rückgabe erhält die vorherige Datenreferenz, keine tiefe Kopie. Diese Beobachtungen werden weder repariert noch als Abnahme produktiver Parallelität ausgegeben.

### Konkreter Bedarf für P4

- Unveränderlicher Auftrag mit tatsächlichen Eingaben, Seed/Zufallsrezept, Quell-/AST-/Kontext-/Werkzeugrevision und tatsächlicher Runtime samt Thread-/Kandidatenparametern.
- Native Matrix-/Embeddingartefakte oder referenzierbare Originalwerte einschließlich Hash, Form, Datentyp; Score, Intensität und deren Berechnungsdefinition getrennt von GV/Original-EW speichern. Dieser Harness exportiert nur Matrixdigests, die spätere Produktspeicherung ist damit nicht implementiert.
- Rohfokus und normalisierte Suche getrennt: Originalembedding ist groß-/kleinschreibungs- und leerzeichenabhängig. Komponentenreihenfolge der Signatur wird normalisiert; Defaultfrequenz440.0 ist Teil des Rezeptes.
- Speicher-/Kandidatenpolitik, Fehlerphase, RNG-Besitz/-Wiederherstellung sowie Amplifier-ID und Inhaltsrevision getrennt dokumentieren. Ein gemeinsames globales RNG oder veränderliche Datenreferenz ist kein Nachweis isolierter paralleler Jobs.
- Warnungen und synthetische Grenzen als Nachweisbedingungen erhalten. Reproduzierbarkeit gilt für diese gebundene Umgebung, kein versions-/plattformübergreifendes Identitätsversprechen.

Belege im Paket `checkpoints/Aurelia-P3-Radi144-CPU-20261014`: `ROOT-CPU-TORCHGEN-SUMMARY.json`, beide Controllerbelege und `runs/cpu-run-{6,7}/output/p3-result.json`, RED/GREEN-Manifeste, Vor-/Ergebnisreviews und geschlossenes Gate. Lokaler Vorher-/Nachherpunkt `checkpoints/Aurelia-P3-Radi144-Torchgen-Status-20261014-205410Z`; tatsächlicher Abschluss und Umfang ausschließlich durch finalen Manifest-/Archiv-/Rücklesebeleg. Kein vollständiges Projekt-/F:-/Serverbackup und keine Produkt-/Live-/Routing-/normative Templateänderung.

## Zeitbezogener V9-Stand (durch V10 ergänzt)

Stand:14.10.2026, FortsetzungV9. **CPU-Prüfung am Abhängigkeitsbootstrap unterbrochen; keine CPU-Abnahme.** Die NumPy-Umgebungsbarriere ist überwunden. Versuch5 stoppt an der vorhandenen, bislang nicht freigegebenen PyTorch-Paketwurzel `torchgen`.37 Harnessproben und Controllerprüfung erfolgreich; alle14 geplanten Originalfallgruppen bleiben unausgeführt. Originalalgorithmen und Produktdateien unverändert. Frühere Abschnitte bleiben zeitbezogene Historie.

## Aktueller V9-Befund nach Versuch5

Nach erneuter Betreiberfreigabe genau `OPENBLAS_MAIN_FREE='1'` in der bereinigten Kindumgebung vorgegeben. Der Elternprozess und die Windows-Konfiguration bleiben unverändert. Der Parameter betrifft die Hauptthread-Affinität; die Threadzahl bleibt separat1. Guards, Originalmethoden und numerische Assertions unverändert. Frische Laufkennungen5/6; alte Belege erhalten.

Die neue Controllerregression erkennt die vorher fehlende Vorgabe korrekt (RED Exit1). Danach Controllerprüfung Exit0 und37/37 Harnessproben erfolgreich (10,514s); eingefrorene Werkzeugbytes vor/nach gleich. Astra/medium prüft die konkrete Fassung vor nativer Wiederholung; in diesem begrenzten V9-Schritt kein erneuter Luna-Arbeiter nötig.

Versuch5 dauert65,047s und scheitert ohne Timeout: Torch importiert über `functional`, `nn.modules.module` und `utils/_python_dispatch.py:13–14` die vorhandene Wurzel `torchgen` und `torchgen.model`. Der Guard verweigert sie korrekt, weil sie im bisherigen Runtimeumfang fehlt. Vorher3.36GB physisch frei und9.86GB Commitreserve; kein beobachteter Ressourcenfehler. Torch-Initialisierung unvollständig, kein Originalfunktionskörper aufgerufen. NumPy wurde weiter durchlaufen, ist aber nicht separat vollständig abgenommen. Zehn Quellen, Werkzeuge, HEAD und benannter Gitstatus vor/nach gleich; Quellenhashes und drei Paketpins danach erneut gleich.

Das gebundene Torch-Paket nennt in `torch-2.12.0.dist-info/top_level.txt` die Wurzeln `torch`, `torchgen` und `functorch`. Sieben konkrete Metadaten-/Quelldateien für die Diagnose hashgebunden; keine vollständige Importclosure oder Lieferkettenprüfung. Tatsächlich beobachtet ist der Bedarf an `torchgen`; `functorch` ist deklariert, sein Bedarf in diesem Bootstrap noch nicht belegt.

Wie vereinbart nach neuem Fehler gestoppt: kein Versuch6, keine zusätzliche Paketfreigabe, Gate geschlossen und geprüft. Astra bestätigt als nächsten konsolidierten Schritt die Herkunft und unmittelbar benötigte Importkette `torchgen.model → torchgen.utils → torchgen.code_template` aufzunehmen und den tatsächlich benötigten Paketumfang zusammenhängend zu prüfen. `functorch` dabei gesondert erfassen. Keine pauschale Freigabe aller installierten Pakete oder von Codegenerierungsfunktionen; noch nicht implementiert.

Belege: `ROOT-CPU-ENV-SUMMARY.json`, `ROOT-controller-cpu-run-5.json`, `ROOT-NATIVE-FAILURE-5-REVIEW.json`, `evidence/v9-env-red/manifest.json`, `evidence/v9-root-candidate-1/manifest.json`, `ROOT-controller-stdlib-check-v9.json`. Lokaler Punkt: `checkpoints/Aurelia-P3-Radi144-Env-Status-20261014-202421Z`; Umfang durch Manifest/Rücklesen, kein Projekt-/F:-/Serverbackup.

## Historischer V8-Befund nach Entwurfsabgleich

Der Betreiber genehmigt die empfohlene Fortsetzung. Luna/max prüft den begrenzten Importentwurf ausschließlich lesend; Root entwickelt die Korrektur und Tests, Astra/medium prüft eingefrorene Bytes vor Versuch4. Entwurf `../superpowers/specs/2026-10-14-radi144-bootstrap-import-design.md`.

- Fehlende unbekannte Importwurzeln werden ausschließlich während nativer Initialisierung gegen die drei gebundenen Suchpfade geprüft, ohne Paketinitialisierer. Vorhandene, Namespace-, geladene oder ausdrücklich verbotene Wurzeln bleiben gesperrt. Veränderte Suchpfade, Metafinder, Pfadhooks und nichtstandardmäßige gecachte PathEntryFinder verhindern einen Abwesenheitsnachweis. Bestehendes TQDM-Gate und übrige Rechte unverändert.
- Root-RED2:37 Tests mit genau zwei erwarteten Assertionfehlern; Root-GREEN:37/37 erfolgreich, Werkzeugbytes vor/nach gleich. Realer isolierter Standardbibliotheksimport fängt ModuleNotFoundError als ImportError; ein vorhandenes Paket mit absichtlich fehlschlagendem Initialisierer und ein Namespacepaket werden vor Ausführung abgewiesen. Bytes, Ausgabe und Exitcodes jeweils erhalten.
- Versuch4 nach Review und frischen Bindungen:34,922s, kein Timeout. Torch erreicht `storage.py` und NumPy `_core/__init__.py:20`. NumPy ruft bei fehlendem `OPENBLAS_MAIN_FREE` zunächst `os.putenv(..., '1')` auf; der Guard erlaubt nur den begrenzten Torch-PATH-Fallback und stoppt. Keine Originalfunktionskörper oder vollständige Torch-/NumPy-Initialisierung. Vorher rund3.25GB physisch frei und9.57GB Commitreserve; Quellen, Werkzeuge und benannter Gitstand vor/nach gleich, zehn Quellenhashes danach erneut gleich.
- Vereinbarter Stopp bei neuem tatsächlichem Fehler eingehalten. Kein Versuch5 und keine weitere Codekorrektur. Gate nach Versuch4 geschlossen und geprüft. Astra bestätigt als nächsten **noch nicht umgesetzten** Vorbereitungsschritt `OPENBLAS_MAIN_FREE='1'` ausschließlich in der bereinigten Kindumgebung. Dadurch überspringt der gebundene NumPy-Code Setzen und Entfernen dieser Variablen, ohne zusätzliche Guardausnahme. Der Wert bleibt im Kindprozess bestehen und betrifft die Hauptthread-Affinität; er ersetzt keine Threadzahlbegrenzung.

Aktuelle Belege: `ROOT-CPU-IMPORT-SUMMARY.json`, `ROOT-controller-cpu-run-4.json`, `ROOT-NATIVE-FAILURE-4-REVIEW.json`, `evidence/v8-root-red-2/manifest.json`, `evidence/v8-root-candidate-1/manifest.json`. Neuer lokaler Vorher-/Nachherpunkt: `checkpoints/Aurelia-P3-Radi144-Import-Status-20261014-200503Z`; Umfang erst durch Manifest/Rücklesen bestätigt. Frühere Abschnitte unten bleiben zeitbezogene Historie.

## Umfang und Vorbereitung

Referenz `C:/Users/Hubert111/Documents/Radi144`; zehn benannte Quell-/Test-/Konfigurationsdateien im Vorherbeleg gebunden. Eigene Gitwurzel und HEAD `b8ac33a1360f1cb56f06e602fcd37cbda2a9c641`; getrackter Status der zehn Pfade `A AGENTS.md`. Diese bereits vorgemerkte Datei bleibt erhalten. Keine Behauptung eines insgesamt sauberen Repositories oder gleicher HEAD-/Arbeitsbytes.

Geplant sind originale ausgewählte AST-Methoden mit echtem installiertem Torch unter kontrolliertem CPU-Zustand. Kein Produktmodul, Enginekonstruktor, Wissenskatalog oder echter Klient wird geladen. Höchstens64 Grundkandidaten beziehungsweise160 nach Originalskalierung; das ist keine Aussage über die großen Standardpools. Vollständiger erfolgreicher `calculate_resonance`-/HTTP-/UI-/CLI-/Linuxweg bleibt außerhalb dieses Teilpakets.

Die bestehende Python3.11.12-Umgebung startet mit `-I -S`. Paketmetadaten nennen Torch2.12.0 und NumPy2.4.6; Metadaten sind noch kein erfolgreicher Bibliotheksimport. Vor jedem nativen Kindlauf sind mindestens1GiB physisch frei und1.5GiB Commitreserve erforderlich. Ein eigener Kindprozess, bereinigte Umgebung, CPU/ein Thread und180Sekunden technische Zeitgrenze schützen den begrenzten Prüflauf; keine fachliche Zeitbegrenzung der Gesamtarbeit.

Äußerer Controller nach zwei Reviewbefunden korrigiert: ursprünglicher Fehler und unabhängige Nachprüffehler bleiben getrennt erhalten; tatsächliche Hash-/Gitbeobachtungen werden vor dem Vergleich gespeichert. `launch_attempted` bezeichnet nur einen Startversuch. Zwei negative Gateproben einschließlich `-O --reviewed`, Umgebungs-Allowlist und synthetische Mehrfachfehlerprotokollierung bestanden. V1 und deren Erstbeleg erhalten. Astra/medium bestätigt diese Controllerkorrekturen; die späteren Harnessreviews und tatsächlichen Versuche sind unten getrennt belegt.

## Tatsächliche Vorprüfungen und Anlaufgrenzen

- Eingefrorene V4: 31 synthetische Standardbibliothekstests bestanden; eigener Controller und Harness vorab unabhängig geprüft. Erster echter Versuch `cpu-run-1` scheiterte beim UTF-8-SIG-Dekodieren der gebundenen Quellen: Der Codec wollte unter bereits geschlossener Importphase nachladen. Weder Torch noch Originalfunktionskörper erreicht. Vollständige begrenzte Fehlerkette im Controllerbeleg erhalten; kein Timeout, Quellen-/Werkzeug-/Gitstand vor/nach unverändert.
- V5 löst den Codec-Registryeintrag vor Guardinstallation auf und berücksichtigt das tatsächlich gemessene AST-Kompilierereignis `(ast.Module, None)`. Die Kompilier-API erhält weiterhin einen echten Dateinamen; erst dessen Auditereignis meldet `None`. Ausnahme nur in Vorbereitung; Originalaufrufe bleiben für Datei-/Import-/Codezugriffe gesperrt. 33 frische Root-Werkzeugtests bestanden; kein nativer Import oder Originalaufruf.
- Astra fand danach eine weitere konkrete Vorbereitungsgrenze: Der vollständige ausgewählte Engine-Syntaxbaum benötigt 172.945 UTF-8-Bytes, die beiden API-Helper 6.098 Bytes. V5 erlaubt dafür nur 65.536 Bytes. Ausschließlich Parser-/Extraktions-/Dumpmessung, kein Kompilieren/Ausführen der Originaldefinitionen. V6 trennt dafür eine AST-Grenze von 196.608 Bytes ab; die native Grenze für erzeugten Stringcode bleibt unverändert. 34 frische Root-Werkzeugtests bestanden einschließlich tatsächlicher AST-Maße und Übergrößenablehnung. Astra bewertet den begrenzten Versuch nach erneuter Werkzeugbindung/Ressourcenprüfung positiv; kein nativer Erfolg daraus ableitbar.
- Versuch2 mit geprüfter V6 erreicht die Definitionsextraktion und den Torch-Import, scheitert jedoch bereits in der Windows-Standardbibliothek `ctypes`: `windll.kernel32.GetLastError` fordert den nackten Alias `kernel32` an. Guard erlaubt bislang nur `kernel32.dll`; auch der unmittelbar benötigte Symbolname fehlt. Kein Originalfunktionskörper erreicht, kein Timeout oder Ressourcenfehler; rund3.23GB physisch frei und10.92GB Commitreserve vor Start. Zehn Quellen, Werkzeuge, HEAD und benannter Gitstatus vor/nach gleich. Astra bestätigt die eng begrenzte Alias-/Symbolkorrektur als sachgerecht; geprüfte V7 und Versuch3 folgen unten. Fremdpfade und alle Aufrufphasenverbote bleiben erhalten.
- Fehlversuch1 wird nicht überschrieben. Weitere Läufe erst mit neuen Kennungen, eingefrorenen Werkzeugbytes und erneutem Review. Ein alter zusätzlicher synthetischer Controllerbeleg wurde versehentlich überschrieben; vorheriger Hash/Review und aktueller Ersatzbeleg sind erhalten, alte Belegbytes nicht. Dies betrifft weder den tatsächlichen Fehlversuch noch dessen Werkzeugfassungen; Details in `ROOT-ANCILLARY-EVIDENCE-NOTE.json`.

## Teilbefund nach Versuch3 und nachfolgend freigegebener Entwurf

V7 ergänzt ausschließlich den nackten Alias `kernel32` und das Symbol `GetLastError` in der nativen Initialisierungsphase. Fremde absolute/relative Pfade und die Aufrufphase bleiben gesperrt. Root friert die Werkzeugbytes selbst ein und bestätigt 35/35 Standardbibliothekstests; Astra prüft die konkrete Fassung vor Versuch3. Zwei fehlgeschlagene Worker-Snapshotpfade sind als einfache Testdateikopien erhalten; sie sind keine gültigen Snapshots und wurden nicht dafür verwendet. Korrekturbeleg `ROOT-V7-SNAPSHOT-ERROR-CORRECTION.json`; gültiger Root-Snapshot `evidence/v7-root-candidate-1`.

V7-RED-Bytekopien und vorhandene Ausgabe (35 Tests, vier Fehler zu Alias/Symbol/Freshlabel) separat nachträglich inventarisiert. Kein zeitnaher RED-Manifest-/Exitcodebeleg vorhanden; keine vollständig zeitgleich gebundene RED-Protokollierung behauptet. `ROOT-V7-RED-INVENTORY.json` trennt diese Grenze vom tatsächlich erhaltenen frischen Root-GREEN-Exit0.

| Versuch | Tatsächlich erreicht | Abbruch | Dauer Controller | Vorher/Nachher |
|---|---|---|---|---|
| 1 / V4 | Quelldekodierung, vor Definitionen/Torch | Codec-Nachladeimport gesperrt | 38,704s | Quellen, Werkzeuge und benannter Gitstand gleich |
| 2 / V6 | Definitionen, begonnener Torch-Import | Windows-Stdlib-Alias `kernel32` gesperrt | 32,938s | Gleich; keine Nachprüffehler |
| 3 / V7 | Torch → `_utils` → Standardbibliothek `pickle` | Optionale Jython-Importwurzel `org` abgewiesen | 40,156s | Gleich; keine Nachprüffehler |

Im dritten Versuch will `pickle.py:103` optional `org.python.core.PyStringMap` importieren und fängt `ImportError`. Der Guard liefert stattdessen `GuardViolation`. Damit ist erneut die Importsemantik des Prüfgerüsts betroffen, kein nachgewiesener Fehler einer Radi144-Rechnung. Vor Versuch3 waren rund3.05GB physisch und10.17GB Commitreserve frei; kein Timeout. Die drei benannten Initialisierer-/Metadatendateien bleiben hashgleich; keine vollständige DLL-Lieferkettenprüfung.

Nach drei Anlaufabbrüchen keine weitere Einzelkorrektur oder Wiederholung. Das aktuelle Ausführungsgate ist geschlossen, die vorherigen Bindungen bleiben erhalten. Astra bestätigt die Konsolidierung und folgenden **noch nicht implementierten** Entwurf: Nur in der nativen Bootstrap-Phase eine Importwurzel ohne Paketinitialisierung gegen exakt die gebundenen Suchpfade prüfen. Nachgewiesene Abwesenheit als normales `ModuleNotFoundError` behandeln; vorhandene unfreigegebene Pakete weiterhin abweisen. Keine Umdeutung von Fehlern innerhalb vorhandener Pakete, keine Erweiterung von Datei-/DLL-/Netz-/Prozess-/Aufrufrechten. Linux mit OS-Isolation bleibt später ein eigener Plattformnachweis, ist für den kleinen CPU-Vergleich nicht zwingend.

Belege: `ROOT-CPU-SUMMARY.json`, drei `ROOT-controller-cpu-run-*.json`, `ROOT-NATIVE-FAILURE-3-REVIEW.json`, eingefrorene Werkzeugfassungen. **Kein numerischer Ergebnisvergleich, keine vollständige Precision-Deterministik und keine Produktfreigabe.**

## Statische Grenzen für die Ergebnisbewertung

| Bereich | Bestehende Grenze | Bedeutung für den Nachweis |
|---|---|---|
| Fokus/Signatur | Eigene Torch-Generatoren; Fokus wird unverändert gehasht. | Großschreibung und Leerzeichen nicht still normalisieren; keine semantische KI. |
| Matrixsuche | Gemeinsamer Torch-RNG; Ergebnisse hängen vom Anfangszustand ab. | Gleiche CPU-Ergebnisse nur bei gleichen gebundenen Eingaben und Anfangszuständen prüfen. |
| Precision-Fehler | RNG-Rücksetzung steht am normalen Abschluss. | Einen frühen Fehler separat charakterisieren; nachträgliche Rücksetzung durch den Harness ist kein Originalfix. |
| Speicherhelper | Allgemeiner Exception-Fallback liefert ursprüngliche Kandidatenzahl. | Absolute kleine Prüfpools unabhängig vom Helper begrenzen. |
| API-Amplifier | Vorheriger Zustand besteht aus Objektreferenzen. | Fake-basierte Apply-/Restore-Probe ist keine tiefe Kopie, HTTP-/Parallelitäts- oder tatsächliche Amplifierabnahme. |
| Gesamtberechnung | Weitere Zeit-/HRV-/Signatur-/Hardware-/Wissensabhängigkeiten. | Zwei kleine CPU-Läufe belegen keine vollständige Precision-Deterministik oder Klientenreaktion. |

Python-Auditguards sind keine native Betriebssystem-Sandbox. Die installierten nativen Bibliotheken bleiben eine ausdrückliche Vertrauensvoraussetzung. Keine Garantie gegen native Umgehungen oder eine vollständige DLL-Lieferkettenprüfung.

## Für P4 vorbereiten, noch keine DB-Entscheidung

| Datenbezug | Zu unterscheidende Angaben |
|---|---|
| Auftrag und Kontext | Stabile Klienten-/Auftrags-/Versuchsidentität, unveränderlicher Eingabestand, unveränderter Fokus. |
| Rechenrezept | Originalverfahren und Quellrevision, Parameter/Gewichtung/Amplifierrevision, Seed und RNG-Geltungsbereich. |
| Umgebung | Bibliotheksversionen, Gerät, Threads und tatsächlicher Kandidatenumfang; nominale Profile getrennt. |
| Ergebnis | Matrixdimension und Originalwerte, Score und Intensität mit jeweiliger Definition; keine Umdeutung zu Original-EW/GV oder Messwerten. |
| Verlauf und Fehler | Versuch, Teilphase, Ergebnis-/Bestätigungszustand, Fehlerursache und Wiederholung getrennt. |
| Hoheit | Rechenzustand und persönlicher Kontext sind keine Zugriffsberechtigung; Tenant/Operator/Job/Artefakt separat. |

Gesamt-P3 bleibt offen. Danach vollständige siebenmodulige P4-Matrix einschließlich Aurelia und Modul_Templates, dann P5-Betreiberentscheidung zur zentralen Struktur. Normative Anpassung und Integration P6–P8/S4.8 bleiben getrennt. Rootserver, RadiFarben-Rohreferenzen, RadiWorks-Dauerinstanzen, Governor und Routing werden durch dieses Paket nicht verändert.

Plan: `../superpowers/plans/2026-10-14-aurelia-p3-radi144-cpu-kern.md`. Artefakte: `checkpoints/Aurelia-P3-Radi144-CPU-20261014`; lokaler Statuspunkt: `checkpoints/Aurelia-P3-Radi144-CPU-Status-20261014-174238Z`. Gesicherter Umfang ausschließlich nach erfolgreichem Manifest-/Rücklesenachweis, kein F:-Gesamtbackup. Tatsächliche Helfer: Luna/max Vorbereitung; Astra/medium unabhängiger Review. Keine Runtime-Modellumschaltung daraus ableiten.
