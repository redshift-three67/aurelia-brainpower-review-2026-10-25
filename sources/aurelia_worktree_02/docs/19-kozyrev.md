# Kozyrev-Kerne (D19, D22, D23 gesetzt)

Zwei verschiedene Personen, zwei verschiedene Ansprüche. Die Anhänge vermischen sie.

| Name | Was es ist | Produkt |
|---|---|---|
| **S. V. Kozyrev** (Steklov, 2002, Comm. Math. Phys. 229:199–219) | p-adische Wavelets, Eigenbasis des Vladimirov-Operators | Kernel `kozyrev.padic.haar.v1` |
| **N. A. Kozyrev** | Zeitdichte, Torsionsfelder — keine etablierte Laborphysik | Kein Nachweis, keine UI-Behauptung |

Für **p=2** sind Kozyrev-Wavelets **Haar-Wavelets**. Das ist Definition, kein Makel.
v1 nutzt Haar-DWT (CPU AVX-512 Zen 5 für N≤2048, CUDA-Filterbank für Batches)
plus optionale Spektralmultiplikation `λ_j = p^{α(1-j)}`. UI-Text: „p-adisches
Wavelet-Rechenmodell“, nie „Nachweis einer Zeitwelle“.

## Was aus den Anhängen übernommen wird

- Filterbank O(N), Diagonalität von D^α als Rechenersparnis
- Heterogene Teilung: kleine N auf Ryzen, Batches auf Ada
- GPS-PPS **nur** als Uhr für `aurelia-timerd` (chrony)

## Was nicht in den Produktivpfad (siehe [22-kozyrev-labor.md](22-kozyrev-labor.md))

- 3-Tier-KI: c2-Autoencoder, TRI-LSTM, Morphic-Transformer auf der GPU (K6)
- XGBoost-Heilmittel, Petrov, Weltenformel, Time-to-Zero (K7)
- GPS-PPS-Jitter als c2-Messung, RT-Core-Spiralen (K8)
- 16-Kanal-EEG / EDA als Kern; 1-MHz-Pipeline
- Medizinische Lesart (Schlaf, Stress)
- Physische Dioden/Spiegel in Chips

HRV-Ohrclip ist **D21**, kein EEG. p-adisch auf RR-Reihen: Kern, CopyGuard auf Text.

REG nur `kozyrev.reg.v1`, Quelle `simulated`/`derived`. p=3/5: Labor, nicht v1.

Katalog und Schalter: [22-kozyrev-labor.md](22-kozyrev-labor.md).
K1–K5 gesetzt, administrativ schaltbar. K6–K8 gesperrt.

