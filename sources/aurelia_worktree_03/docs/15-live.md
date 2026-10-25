# Live, Cache, Emitter, WebSocket-Fachkanal

## Spooky2 / Generator X Pro

Offizielle GUI: Windows. Treiber: Silicon Labs CP210x.
Ubuntu 24.04: `cp210x` → `/dev/ttyUSB*`.
WebUSB: verboten.

`aurelia-emitterd`: Lease → Arming → ACK → Emission → Reset.
Occupied = Warteschlange. GPU-Job und Emitter sind **getrennte** Leases.
Bis Hardware-Gate: `isHardwareActivatable: false`.

## WebSocket (C08 / D05 / D15 gesetzt)

Ein Fachkanal, Server autoritativ:

| Ereignis | Inhalt |
|---|---|
| Analyse | Progress, Queue, Passport-ID (kein Zeugenklartext) |
| Zwischenablage | Draft-Update, CopyGuard-reason, Promote-ACK |
| Harmonisierung | Ticks, Zustand, Command → ACK |
| Symbole / Cues | SVG/Canvas; Toncodec bleibt D11/WV06-Wiedervorlage |

Tick-Vorschlag (U08, gesetzt): UI 50 ms aus timerd-RAM. Durable Checkpoint
500–1000 ms (D20). Analyse-Progress 200 ms.

## HRV-Ohrclip (D21)

Der Ohrclip-Pfad ist ein zukünftiger, derzeit gesperrter Hardwarepfad. Clip am
Menschen, nicht am Rack. Nach einem neuen Hardware-Gate wäre remote Web
Bluetooth/Companion und vor Ort USB am Praxis-Rechner mit Relay vorgesehen.
Kein EEG; CopyGuard auf Texte. Exclusive analog Emitter. Details:
[21-timer.md](21-timer.md) berührt nur die Uhr; Sensorvertrag hier und in D21.


`prefers-reduced-motion`: ein statischer Frame plus Textstatus.

D10 / O08: Video, WebRTC, TURN und Aufzeichnung sind vollständig ausgeschlossen;
Phase 9 ist gestrichen. Live bleibt der WebSocket-Fachkanal.

## Cache und Wischen

- Marke/JS/Fonts: immutable, long cache
- Zeugen/Session: `Cache-Control: private, no-store`, kein CDN, kein SW in Phase 0/1
- Wischen: `revokeObjectURL`, `caches.delete`, IndexedDB drop, WS close, AudioContext close
- Prefetch nur öffentlicher Texte
