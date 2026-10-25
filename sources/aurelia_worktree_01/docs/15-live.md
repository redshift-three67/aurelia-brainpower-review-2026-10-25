# Live, Cache, Emitter, WebSocket-Fachkanal

## Spooky2 / Generator X Pro

Offizielle GUI: Windows. Treiber: Silicon Labs CP210x.
Bookworm: `cp210x` → `/dev/ttyUSB*`.
WebUSB: verboten.

`aurelia-emitterd`: Lease → Arming → ACK → Emission → Reset.
Occupied = Warteschlange. GPU-Job und Emitter sind **getrennte** Leases.
Bis Hardware-Gate: `isHardwareActivatable: false`.

## WebSocket

Gesetzt: C08, D05 und D15.

Ein Fachkanal, Server autoritativ:

| Ereignis | Inhalt |
|---|---|
| Analyse | Progress, Queue, Passport-ID (kein Zeugenklartext) |
| Zwischenablage | Draft-Update, CopyGuard-reason, Promote-ACK |
| Harmonisierung | Ticks, Zustand, Command → ACK |
| Symbole / Cues | SVG/Canvas; Opus 24–48 kbit/s |

Tick-Vorschlag (U08, gesetzt): UI 50 ms aus timerd-RAM. Durable Checkpoint
500–1000 ms (D20). Analyse-Progress 200 ms.

## HRV-Ohrclip (D21)

Clip am Menschen, nicht am Rack. Remote: Web Bluetooth / Companion → RR über
den Fachkanal. Praxis: USB am Praxis-Rechner, Relay. Kein EEG. CopyGuard auf
Texte. Exclusive analog Emitter. Details: [21-timer.md](21-timer.md) berührt
nur die Uhr; Sensorvertrag hier und in D21.


`prefers-reduced-motion`: ein statischer Frame plus Textstatus.

D10 / O08: kein Video und kein WebRTC. Externe Videokonferenzen sind kein Teil
von AURELIA. Der produktinterne Live-Kanal bleibt WebSocket.

## Cache und Wischen

- Marke/JS/Fonts: immutable, long cache
- Zeugen/Session: `Cache-Control: private, no-store`, kein CDN, kein SW in Phase 0/1
- Wischen: `revokeObjectURL`, `caches.delete`, IndexedDB drop, WS close, AudioContext close
- Prefetch nur öffentlicher Texte
