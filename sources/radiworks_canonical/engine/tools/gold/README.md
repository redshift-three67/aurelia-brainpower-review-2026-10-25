# Goldwert-Harness — Regeneration

Der Goldwert belegt Java-Orakelparität ausschließlich für den seeded
`POST /analysis`-Pfad mit 300 synthetischen Raten (`R0000`–`R0299`): Seed 42 bei
`max_hits=100`, Seed 20260829 bei `max_hits=100` und Seed 42 bei `max_hits=1000`
(JDK 24.0.1). Verglichen werden `generalVitality`, `numberOfTrials` und
`rateObjects`; andere Daten, Kataloggrößen/Treeify-Fälle, Laufzeitpfade und
`stochastic` sind nicht Teil dieser Aussage.

## Ablauf (einmalig bei Engine-Änderungen an der Analyse-Logik)

```bash
# Lokale Pfade nie einchecken: auf die eigene JDK-Installation und den
# Radiworks-Checkout setzen.
export JAVA_HOME="/pfad/zum/jdk"
export RADIWORKS_ROOT="/pfad/zum/Radiworks"

cd tools/gold
mkdir -p run classes

# 1. Compilieren (Classpath = Radiworks-Root mit de/isuret-Klassen + Jackson)
"${JAVA_HOME}/bin/javac.exe" -encoding UTF-8 \
  -cp "${RADIWORKS_ROOT}" -d classes GoldHarness.java

# 2. Original-Bytecode ausführen (cwd = leerer Ordner 'run', damit der
#    Settings-/Config-Zugriff sauberverläuft)
cd run
"${JAVA_HOME}/bin/java.exe" \
  -cp "${RADIWORKS_ROOT};../classes" \
  GoldHarness 300 R 20260829 > ../gold_analysis_300.json 2>../gold_stderr.log

# 3. Goldwert an die Tests liefern
cp ../gold_analysis_300.json ../../../tests/gold/

# Optional: REST-Resultat inklusive General Vitality als unabhängiges,
# seeded Java-Orakel erzeugen. Die Ausgabe anschließend unter einem
# seed-spezifischen Namen in tests/gold/ übernehmen.
"${JAVA_HOME}/bin/java.exe" \
  -cp "${RADIWORKS_ROOT};../classes" \
  GoldHarness 300 R 42 --rest > ../gold_rest_analysis_300_seed_42.json
```

## Parameter

| Arg | Bedeutung | Default |
|---|---|---|
| 1 | Anzahl Raten (300 → HashMap-Bins bleiben unter Treeify-Schwelle) | – |
| 2 | Raten-Präfix (`R0000` …) | `R` |
| 3 | Master-Seed der Zwei-Stufen-Entropie | `20260829` |
| 4 | Optional `--rest`: setzt anschließend den originalen General-Vitality-Zug | – |
| 5 | Optional `100` oder `1000`: ursprüngliche `analysis.very.high.max.hit`-Grenze | `100` |

## Warum 300 Raten?

Die Selektionsphase wählt max(300/10, 120) = 120 Schlüssel; bei finaler
Tabellenkapazität 256 bleiben die Bins klein (< 8), sodass die
HashMap-Ordnungssimulation (`core/javahashmap.py`) ohne Treeify-Bäume auskommt.
Der Test bricht laut, falls die Annahme verletzt wird.

## Erwartete stderr-Meldung (harmlos)

`AnalysisService.<init>` versucht, `data/radionics/HOMEOPATHY/clarkeMateriaMedica.json`
zu laden und druckt bei Fehlen einen Stacktrace — das Original fängt die
Ausnahme ab und arbeitet ohne Materia Medica weiter.
