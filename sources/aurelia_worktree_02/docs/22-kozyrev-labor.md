# Kozyrev: K1–K5 gesetzt, K6–K8 gesperrt

Kanon: `src/lib/concept/kozyrev-labor.ts`. Portal: `/kozyrev`.
Operator 2026-08-23: nur K1–K5, exakt nach Empfehlung, administrativ schaltbar.
Zweite Prüfung: Destabilisation = Bruch von C01 / C03 / D01 / D20 oder der 20-Klienten-Isolation.

## Urteil

K1–K5 **gesetzt**. K6–K8 **gesperrt** (kein Kernel-ID, kein Schalter, kein Scaffold).
Lovable unberührt — D03/D24 gesetzt; Disconnect bleibt WV04 optional.

## Gesetzt

| ID | Stück | Default | Schalter | Destabilisiert? |
|---|---|---|---|---|
| K1 | `kozyrev.padic.haar.v1` | **an** | ja, ausbar | Nein. O(N)-DSP. |
| K2 | `kozyrev.reg.v1` | aus | ja | Nein, wenn simulated und nicht still gemischt. |
| K3 | `kozyrev.lab.*` leer | aus | ja; `executable: false` hart | Nein. |
| K4 | p=3/5 eigene IDs | aus | ja | Nein. Filterbank, eigenes Admit. |
| K5 | Haar auf HRV-RR | aus | ja; braucht K1 + Clip | Nein. 1D, kleine N, CopyGuard. |

## Gesperrt

| ID | Stück | Warum kein Schalter |
|---|---|---|
| K6 | Autoencoder + LSTM + Transformer auf der Ada | Kippt C01/C03 und den Job-Pool. |
| K7 | Heilmittel / Time-to-Zero | HWG, D01. |
| K8 | PPS-als-c2, Weltenformel, RT-Spiralen | Falsche Quelle / Claim durch ID-Reservierung. |

## Schalter (D23)

Kette: **platform AND tenant AND session**. Fehlendes Flag = aus.
Umschalten = auditiertes Ereignis (wer, wann, scope).
Admit prüft das Flag **vor** VRAM. UI blendet aus, fallbackt nicht.
K5 folgt K1. `lab.*` bleibt `executable: false` ohne neues gesetztes Gate.

Details: `KOZYREV_SCHALTER` und D22/D23 in `src/lib/concept/decisions.ts`.
