# Goldwert-Harness — Regeneration

Der Goldwert belegt die bitexakte Übereinstimmung des Python-Ports mit dem
Original-Bytecode von `AnalysisService.analyseRateList`.

## Ablauf (einmalig bei Engine-Änderungen an der Analyse-Logik)

```bash
cd tools/gold
mkdir -p run classes

# 1. Compilieren (Classpath = Radiworks-Root mit de/isuret-Klassen + Jackson)
"C:/Users/Hubert111/.jdks/openjdk-24.0.1/bin/javac.exe" -encoding UTF-8 \
  -cp "C:/Users/Hubert111/Documents/Radiworks" -d classes GoldHarness.java

# 2. Original-Bytecode ausführen (cwd = leerer Ordner 'run', damit der
#    Settings-/Config-Zugriff sauberverläuft)
cd run
"C:/Users/Hubert111/.jdks/openjdk-24.0.1/bin/java.exe" \
  -cp "C:/Users/Hubert111/Documents/Radiworks;../classes" \
  GoldHarness 300 R 20260829 > ../gold_analysis_300.json 2>../gold_stderr.log

# 3. Goldwert an die Tests liefern
cp ../gold_analysis_300.json ../../../tests/gold/
```

## Parameter

| Arg | Bedeutung | Default |
|---|---|---|
| 1 | Anzahl Raten (300 → HashMap-Bins bleiben unter Treeify-Schwelle) | – |
| 2 | Raten-Präfix (`R0000` …) | `R` |
| 3 | Master-Seed der Zwei-Stufen-Entropie | `20260829` |

## Warum 300 Raten?

Die Selektionsphase wählt max(300/10, 120) = 120 Schlüssel; bei finaler
Tabellenkapazität 256 bleiben die Bins klein (< 8), sodass die
HashMap-Ordnungssimulation (`core/javahashmap.py`) ohne Treeify-Bäume auskommt.
Der Test bricht laut, falls die Annahme verletzt wird.

## Erwartete stderr-Meldung (harmlos)

`AnalysisService.<init>` versucht, `data/radionics/HOMEOPATHY/clarkeMateriaMedica.json`
zu laden und druckt bei Fehlen einen Stacktrace — das Original fängt die
Ausnahme ab und arbeitet ohne Materia Medica weiter.
