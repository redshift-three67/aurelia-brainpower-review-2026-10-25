# 03 - Engine, Algorithmen und Fachlogik

## 1. Präzise technische Einordnung

Der Kern von Radi144 ist ein generatives Auswahlverfahren für Ziffernmatrizen. Die Implementierung besteht aus:

1. heuristischer Reduktion von Identitäts-, Zeit-, Orts-, Bild- oder Gruppendaten auf skalare Werte,
2. deterministischer Abbildung dieser Werte und des Fokus auf pseudozufällige Vektoren,
3. Erzeugung vieler zufälliger Matrizen mit Ziffern 0 bis 9,
4. Projektion dieser Matrizen in einen 256- bis 512-dimensionalen Zufallsraum,
5. Auswahl der höchsten Kosinusähnlichkeiten,
6. optionaler Symmetrisierung, Farbgebung, EMF- und Amplifier-Metadaten.

Der Code enthält **kein trainiertes Machine-Learning-Modell**, keine gelernte semantische Einbettung, keine Ground-Truth-Daten und keine Scorekalibration.

## 2. Signaturbildung

### 2.1 Namensheuristik

`client_signature.py:117-129`, `:416-426`:

```text
Numerologie = Summe der Unicode-Codepunkte aller Buchstaben
Phonetik    = feste Vokalwerte oder 2 * Unicode-Codepunkt
Namewert    = ((Numerologie + Phonetik) / 2) mod 1000
```

Feste Vokalwerte:

| Buchstabe | Wert |
|---|---:|
| a | 440 |
| e | 330 |
| i | 550 |
| o | 220 |
| u | 165 |

**Bewertung:** Das ist eine nachvollziehbar implementierte Numerologie-/Zeichenheuristik, aber keine gemessene physikalische Frequenz und keine linguistisch trainierte Repräsentation. Umlaute, Schreibweisen und Unicode-Normalformen können stark abweichende Werte erzeugen.

### 2.2 Geburtsheuristik

`client_signature.py:304-347`, `:428-436`:

```text
Basis = Julianischer Tag mod 1000
Ort   = erste 16 Bit von MD5(normalisierter Ortsname), skaliert auf 0..1000
Zeit  = Minuten seit Mitternacht / 1,44
Wert  = 0,6 * Basis + 0,3 * Ort + 0,1 * Zeit
```

Fehler: `ClientBase.birth_time` ist ein `datetime.time` (`app/schemas/klienten.py:9-11`), die Berechnung ruft aber `birth_time.split(':')` auf (`client_signature.py:329-337`). Die Exception wird verschluckt. API-seitig hat die Geburtszeit deshalb regelmäßig keinen Effekt.

### 2.3 Organuhr

Die Organuhr fügt bei jeder Standardsignatur einen aktuellen, stundenabhängigen Wert hinzu (`client_signature.py:60-62`, `:349-373`). Dadurch ist selbst der „Precision“-Modus zeitabhängig.

Die Zuordnung `range(23, 25)` enthält Stunde 23 und 24; `datetime.hour` liefert jedoch nur 0 bis 23. Zwischen 00:00 und 00:59 greift deshalb der 440-Hz-Fallback statt der beabsichtigten 23-01-Uhr-Zuordnung.

### 2.4 Gewichtete Gesamtsignatur

Vorgesehene Gewichte (`client_signature.py:38-99`):

| Komponente | Gewicht |
|---|---:|
| Name | 0,15 |
| Geburt | 0,20 |
| Bild | 0,25 |
| Organuhr | 0,10 |
| Planetary | 0,15 |
| EMF-Korrektur | 0,05 |

Die Summe wird durch die Summe der tatsächlich vorhandenen Gewichte geteilt. Bei einem Standardclient ohne Bild, Planetary und EMF sind die effektiven relativen Anteile daher:

- Name: 33,3 Prozent,
- Geburt: 44,4 Prozent,
- Organuhr: 22,2 Prozent.

### 2.5 Gruppe

`generate_group_signature` berechnet das arithmetische Mittel der skalaren Mitgliedsfrequenzen (`client_signature.py:131-159`). Die Dokumentation spricht von Vektorinterferenz/Centroid; tatsächlich wird kein Vektorcentroid gebildet.

Zusätzlich:

- die Mitgliederreihenfolge fließt als `member_0`, `member_1`, ... in den späteren Hash ein,
- identische Gruppen in anderer Reihenfolge können andere Ergebnisse liefern,
- das Eingabedictionary wird bei `place` -> `birth_place` in-place verändert.

### 2.6 Bild

Die Bildsignatur kombiniert (`client_signature.py:161-247`):

- Datei-SHA-256,
- mittlere RGB-/HSV-Werte,
- Histogrammentropie,
- Dateibasename.

Bei Base64-Uploads wird eine zufällig benannte `.img`-Temporärdatei erzeugt (`app/api/resonance.py:231-252`). Ihr zufälliger Name fließt als Bildname mit 25 Prozent Gewicht in die Signatur ein. Derselbe Bildinhalt kann dadurch unterschiedliche Ergebnisse und temporär benannte Client-Registry-Einträge erzeugen.

Pillow ist optional im Code, aber nicht in `requirements.txt` deklariert. Ohne Pillow fällt die Bildanalyse still auf Hash plus Dateiname zurück.

### 2.7 Geo

`client_signature.py:250-266`:

```text
Geo = (abs(lat) * 111,32 + abs(lon) * 40,075) mod 1000
Geo += log10(radius + 1) * 7,83
```

Probleme:

- Nord/Süd und Ost/West werden durch `abs()` ununterscheidbar.
- API-Grenzen von ±90/±180 werden nicht geprüft.
- Längengradskalierung berücksichtigt den Breitengrad nicht.
- geographische Größen und als Hertz interpretierte Werte werden ohne physikalische Einheitentransformation gemischt.

### 2.8 Planetary

`client_signature.py:375-400`:

```text
Planetary = 100 * (1 + sin(2*pi*TagImJahr/365,25))
```

Der konkrete Planet und `geolocation` werden nicht verwendet. Die Funktion ist ein Jahrestag-Sinus, keine astronomische Ephemeridenberechnung.

### 2.9 DB-Vektorisierung

`vectorise_database_selection` liest den kompletten Text und prüft nur, ob der Fokus als Teilstring vorkommt (`client_signature.py:268-302`). Bei Treffer wird nicht der Kontext, sondern erneut der Fokus selbst durch die Zeichenheuristik transformiert. Strukturierte Raten oder fachliche Felder werden nicht geparst.

## 3. Client- und Fokusvektoren

### 3.1 Implementierung

`resonance_engine.py:1157-1187`:

```text
seed_client = erste 32 Bit von MD5(Frequenz + sortierte Komponenten)
client_vec  = torch.randn(256) mit seed_client

seed_focus  = erste 32 Bit von MD5(Fokustext)
focus_vec   = torch.randn(256) mit seed_focus
```

### 3.2 Konsequenzen

- Synonyme besitzen keine systematisch höhere Nähe.
- Ein Tippfehler erzeugt wegen des Hash-Avalanche-Effekts einen nahezu unabhängigen Vektor.
- „Semantische Einbettung“ im Kommentar `resonance_engine.py:387` ist technisch nicht zutreffend.
- MD5 dient hier nicht zur Sicherheit, sondern als Seedableitung. Das zentrale Problem ist die fehlende fachliche Semantik.

Biofrequenzen werden ebenso in MD5-seedete Zufallsvektoren übersetzt (`resonance_engine.py:559-564`). Gleiche Frequenzwerte ergeben identische Bio-Vektoren, unabhängig vom fachlichen Label.

## 4. Matrixsuche und Score

### 4.1 Kandidaten

Für Matrixgröße `n` werden Kandidaten erzeugt:

```math
M_i \in \{0,\ldots,9\}^{n^2}
```

Kandidatenzahl:

- CPU unter 15 GB RAM: 80.000,
- CPU ab 15 GB RAM: 150.000,
- CPU ab 31 GB RAM: 250.000,
- CUDA je nach VRAM: 200.000 bis 1.000.000.

Beleg: `resonance_engine.py:49-92`.

Bei 12x12 besitzt der theoretische Ziffernraum `10^144` Möglichkeiten. Selbst 1.000.000 Kandidaten entsprechen nur `10^-138` dieses Raums. Die README-Aussage „Computes resonance patterns across 10^144 possibilities“ (`README.md:7`) ist daher missverständlich. Der Code sampelt eine kleine Zufallsstichprobe und wählt daraus das Maximum.

### 4.2 Zielvektor

```math
t = v_{client} + w \cdot v_{focus}
```

Gewichte:

| UI-Wert | w |
|---|---:|
| Deaktiviert | 0,0 |
| Sanft | 0,4 |
| Normal | 1,0 |
| Stark | 1,5 |

Unbekannte Strings fallen still auf 1,0 zurück (`resonance_engine.py:1057-1063`).

Im Precision-Modus enthält der Masterseed den Fokus weiterhin (`resonance_engine.py:292-300`). Deshalb kann ein anderer Fokus selbst bei `Deaktiviert` zu einer anderen Matrix führen.

### 4.3 Zufallsprojektion

```math
P \sim \mathcal{N}(0,1)^{n^2 \times d}
```

```math
p_i = M_i P
```

```math
S_i = \frac{p_i \cdot t}{\|p_i\|\,\|t\|}
```

Beleg: `resonance_engine.py:1068-1092`.

Der Score ist mathematisch eine Kosinusähnlichkeit. Seine fachliche Bedeutung ist aber nicht validiert, weil:

- Client- und Fokusvektoren pseudozufällig sind,
- die Projektionsmatrix nicht gelernt oder versioniert ist,
- Kandidatenzahl und Hardware das beobachtete Maximum beeinflussen,
- keine Nullverteilung, Ground Truth oder Kalibration existiert,
- die UI den Wert dennoch als Prozent zeigt (`user_workflow.js:1207-1214`),
- das Nutzerhandbuch Schwellen als „Blockaden“ und „energetische Ausrichtung“ interpretiert (`USER_GUIDE_DE.md:11-14`).

### 4.4 Intensität

Die Intensität ist nur die Standardabweichung der Matrixziffern (`resonance_engine.py:1094-1108`). Sie ist keine biologische oder physikalische Intensität.

### 4.5 Top-10 und Memory Guard

`top_k` ist fest 10. Der Speicherschutz darf Kandidaten bis auf 1 reduzieren (`resonance_engine.py:999-1029`). Dann kann `torch.topk(..., 10)` scheitern.

Der Guard schätzt Float-Kandidaten, Projektionen und Similarities, berücksichtigt aber den Peak nicht vollständig:

- `torch.randint(...).float()` kann kurzzeitig Integer- und Floattensor parallel halten,
- die Projektionsmatrix selbst und weitere Temporärtensoren sind nicht vollständig budgetiert,
- `cosine_similarity` erzeugt weitere Allokationen,
- nur physisch freier RAM, nicht der Windows-Commit-/Pagefile-Spielraum wird betrachtet.

Aktueller Beleg: Der reale Engine-Test scheiterte bei `cosine_similarity` an einer zusätzlichen Allokation von 85.684.224 Byte; der Folgetest endete an derselben Stelle mit einer nativen Access Violation.

## 5. Precision und Reproduzierbarkeit

### 5.1 Positive Eigenschaft

Precision setzt aus Vorname, Geburtsdatum und Fokus einen festen Torch-Seed und restauriert den globalen RNG nach einem erfolgreichen Lauf (`resonance_engine.py:282-303`, `:481-484`). Lokale Generatoren für Client- und Fokusvektoren sind ebenfalls deterministisch.

### 5.2 Reproduzierbarkeitsgrenzen

| Einfluss | Wirkung |
|---|---|
| aktuelle Organuhr | Signatur ändert sich mit der Stunde |
| HRV-Simulation | verwendet unseeded `np.random` und Tageszeit |
| EMF | hängt von OS-Zufall, Timing, Last, GPU und Stunde ab |
| Hardware/RAM | Kandidatenzahl und Rechenpfad ändern sich |
| CUDA/TF32 | bitgenaue Gleichheit nicht garantiert |
| Bild-Base64 | zufälliger Tempdateiname fließt ein |
| Gruppenreihenfolge | Komponentenhash ändert sich |
| Exceptions | globaler RNG wird nicht in einem äußeren `finally` restauriert |
| Parallelität | globaler Torch-RNG und Enginezustand können kollidieren |

Die Dokumentationsaussage „bit-genau dieselbe Matrix, selbst Jahre später“ (`DEVELOPER_MASTER_GUIDE.md:65-69`) wird durch den Code nicht getragen.

## 6. Symmetrie

Horizontale oder Quadrantsymmetrie mittelt Spiegelzellen und rundet auf Ziffern 0 bis 9 (`resonance_engine.py:518-557`).

Korrektheitsproblem:

1. Score und Intensität werden an der unsymmetrischen Matrix berechnet.
2. Danach werden Bestmatrix und Top-10-Matrizen verändert.
3. Score und Intensität werden nicht neu berechnet.

Die ausgegebene Matrix besitzt deshalb nicht den ausgewiesenen Score. Behauptungen über eine „Score-Retention“ sind im Code nicht berechnet.

## 7. Bio- und Elemente-Logik

Die Engine erkennt Chakra-/Meridian-Schlüsselwörter als einfache Teilstrings (`resonance_engine.py:304-322`) und mischt den daraus erzeugten Zufallsvektor 50/50 in den Fokusvektor (`:390-393`).

Die angekündigte 5-Elemente-Validierung ist ein No-op und gibt Ergebnisse unverändert zurück (`resonance_engine.py:566-575`). Das widerspricht `BIO_RESONANCE_DOCS.md:13-16`.

`bio_knowledge.json` enthält Zuordnungen, aber keine belastbaren Felder für Quelle, Lizenz, Evidenzgrad, Reviewstatus oder Gültigkeitsbereich.

## 8. EMF-Modul

### 8.1 Tatsächlich gemessene Größen

Standardmäßig:

- CPU-Timing-Jitter,
- statistische Eigenschaften von `os.urandom`,
- CPU- und RAM-Auslastung,
- auf CUDA GPU-Laufzeitvarianz und numerische Drift,
- optional ein nicht standardmäßig verdrahtetes SDR-Backend.

Composite-Index (`emf_compensator.py:388-419`):

```math
EMF = 0{,}30(1-E) + 0{,}25J + 0{,}20L + 0{,}15G + 0{,}10A
```

mit Entropiescore `E`, Jitterabweichung `J`, Systemlast `L`, GPU-Noise `G` und RNG-Autokorrelation `A`.

### 8.2 Bewertung

Diese Größen können ein **Systemrausch-/Lastprofil** beschreiben. Ohne kalibrierten Feldsensor messen sie kein elektromagnetisches Feld, keine WLAN-/Bluetooth-/5G-Feldstärke und keine Exposition am Klientenort.

Die UI bezeichnet den Vorgang dennoch als Echtzeitmessung des elektromagnetischen Umfelds. Remote-Audio-, GPS- und HRV-Daten werden zwar global gespeichert (`app/api/resonance.py:1153-1200`), aber in `profile_environment` nicht zur Indexberechnung verwendet (`emf_compensator.py:388-456`).

### 8.3 Kompensation und Counter-Frequencies

Der Kompensationsvektor moduliert Client- und Fokusvektor elementweise. Die Richtung basiert auf Zufallsrauschen und dem Composite-Index, nicht auf gemessenen Frequenzbändern.

Counter-Frequencies enthalten Labels wie „DNA-Reparatur“ und „Schmerzlinderung“ (`emf_compensator.py:580-632`). Diese Bezeichnungen sind medizinisch/biologisch wirkungsnah, ohne dass der Code einen Wirksamkeitsnachweis enthält.

## 9. Amplifier

Das Amplifier-System bildet Registryeinträge in 12 Dimensionen ab, berechnet Cosinus- und Metadatenähnlichkeit und erzeugt Empfehlungen. Es beeinflusst hauptsächlich:

- Palettenmodulation,
- Empfehlungsausgabe,
- Audiofrequenzen,
- Metadaten der Analyse.

Es ändert den bereits berechneten Matrixscore nicht.

Ein konkreter Key-Drift besteht zwischen Signaturkomponente `name` (`client_signature.py:38-45`) und erwarteter Amplifierkomponente `name_frequency` (`amplifier.py:321-325`). Die Namensdimension kann dadurch wirkungslos bleiben.

## 10. Quantum und D-Wave

Codebefund (`resonance_engine.py:1113-1155`):

- `run_quantum_inspired_refinement` ist `pass`.
- Der D-Wave-Import ist auskommentiert.
- Bei Token wird `dwave_enabled=True` gesetzt und „Mock“ geloggt.
- `solve_with_dwave` gibt die Eingangsmatrix unverändert zurück.

Damit ist keine QPU-Kommunikation, kein QUBO und kein Quantum-Annealing implementiert. Produkt- oder Dokumentationstexte, die eine abgeschlossene D-Wave-Integration behaupten, sind sachlich falsch.

## 11. Harmonisierung und Audio

### 11.1 Python/Tkinter

Der Audio-Mix ist mono und kombiniert Grundton, Quinte, Solfeggio und Unteroktave (`dev_cli.py:1647-1697`). Das ist kein binauraler Stereobeat mit 10-Hz-Kanalunterschied, obwohl `BIO_RESONANCE_DOCS.md:20-23` dies behauptet.

Die Session sammelt alle PCM-Teile in einer Liste und verbindet sie am Ende mit `b"".join(...)` (`dev_cli.py:1458-1460`, `:1608-1627`). Lange Sitzungen können mehrere Gigabyte RAM und zusätzlichen Join-Peak benötigen.

### 11.2 Browser

Der Browser nutzt Web Audio und MediaRecorder. Auch dort werden Aufzeichnungsblöcke bis zum Export im Speicher gesammelt. Python- und Browser-Harmonizer haben unterschiedliche Defaults und Audioebenen.

### 11.3 Fachliche Grenze

Der Code erzeugt reale Töne und reale Farbdarstellungen. Aus der technischen Erzeugung folgt kein Nachweis für:

- DNA-Reparatur,
- Schmerzreduktion,
- Immunstärkung,
- EMF-Abschirmung,
- therapeutische Wirksamkeit,
- radionische Fernwirkung.

## 12. Claims versus Code

| Aussage | Tatsächlicher Codebefund |
|---|---|
| KI-gestützte Resonanzberechnung | kein trainiertes KI-/ML-Modell |
| semantisches Embedding | MD5-seedeter Zufallsvektor |
| Berechnung über `10^144` Möglichkeiten | Stichprobe bis maximal 1.000.000 Kandidaten |
| höchste/exakte Matrix | bestes Ergebnis der jeweiligen Zufallsstichprobe |
| 5-Elemente-Validierung | No-op |
| echtes D-Wave/QPU | Mock ohne Solveraufruf |
| bitgenau über Jahre | zeit-, hardware-, zustands- und speicherabhängig |
| Gruppen-Vektorcentroid | Mittelwert skalarer Frequenzen |
| kontextuelles DB-Embedding | Teilstringsuche und Fokus-Zeichenheuristik |
| EMF-/5G-Messung | überwiegend Systemtiming, Last und OS-RNG |
| binauraler 10-Hz-Beat | Python-Mono-Mix mit Quinte |
| 98,7 bis 99,2 Prozent Akkuranz | keine Ground Truth oder statistische Validierung |

## 13. Fachliche Gesamtempfehlung

Vor einer Planerstellung muss entschieden werden, welche ehrliche Produktklasse angestrebt wird:

1. **Generativer Wellness-/Meditations- und Visualisierungsgenerator:** Dann müssen Scores, Claims, EMF und Outputs klar als heuristisch/experimentell bezeichnet werden.
2. **Wissenschaftlich messendes Analysesystem:** Dann ist eine neue, mess- und validierbare Fachmethodik mit Ground Truth, Kalibration und Unsicherheitsmodell erforderlich.
3. **Medizinische/therapeutische Software:** Dann sind zusätzlich Zweckbestimmung, QMS, Risikomanagement, klinische Bewertung und regulatorische Konformität notwendig.

Der aktuelle Code kann die zweite oder dritte Positionierung nicht belegen.
