import { createFileRoute } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/live")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="03b"
          kicker="Live & Emitter"
          title="Ein Socket für Analyse und Harmonisierung. Der Server bleibt die Uhr."
          lead="Backbone-Nähe senkt die RTT. Die 1-Gbit-NIC bleibt die Kante. WebSocket trägt Progress, Clipboard-Events, Ticks und ACK. Spooky2 hängt am Daemon. Gesetzt: C08, D05 und D15."
        />

        <Reco>
          Commands (start, pause, stop, archive, delete) gehen zum Server und kommen
          als ACK zurück. Der Browser rendert. Er rechnet nicht, er taktet nicht, er
          spricht nicht mit USB.
        </Reco>

        <div>
          <H2>WebSocket-Fachkanal</H2>
          <div className="mt-5">
            <Cards
              items={[
                {
                  title: "Analyse",
                  body: "Progress, Queue-Position, Fertig mit Passport-ID — nicht mit Zeugenklartext. Reconnect an letzter Event-ID.",
                },
                {
                  title: "Zwischenablage",
                  body: "Draft-Updates, CopyGuard-reason, Promote-ACK. Tenant-Scope im Frame.",
                },
                {
                  title: "Harmonisierung",
                  body: "Ticks, Zustand, Intensität. Binary, zstd. 50 ms Ziel (U08). Droppen erlaubt, erfinden verboten.",
                },
                {
                  title: "Symbole & Cues",
                  body: "SVG/Canvas, rAF. Opus 24–48 kbit/s. prefers-reduced-motion: ein Frame plus Text.",
                },
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Spooky2 / Generator X Pro</H2>
          <P>
            Offizielle GUI: Windows. Chip: Silicon Labs CP210x → /dev/ttyUSB*. Die App
            mietet aurelia-emitterd (Lease → Arming → ACK). Occupied = Warteschlange,
            niemals Fake-Emission. GPU-Job und Emitter sind getrennte Leases — 20
            CUDA-Klienten teilen sich nicht den Generator.
          </P>
          <div className="mt-4">
            <List
              items={[
                "Kein WebUSB, kein Browser-HID, kein Windows-Companion als Default.",
                "Aktivierung erst nach Hardware-Gate; bis dahin isHardwareActivatable false.",
                "GX Pro kann Presets halten — Arming trotzdem vom Daemon, sonst driftet der Ausweis.",
              ]}
            />
          </div>
        </div>

        <div>
          <H2>HRV-Ohrclip (D21, gesetzt)</H2>
          <P>
            USB- oder BLE-Ohrclip, kein EEG. Der Clip sitzt am Menschen. Der
            GPU-Server im Rack hat nicht zwanzig Clips an der Rückseite — USB-Länge
            und Rechenzentrum passen nicht zusammen.
          </P>
          <div className="mt-4">
            <List
              items={[
                "Remote: Web Bluetooth oder Hersteller-Companion, RR-Intervalle über den Fachkanal, Envelope. Nicht WebUSB-Spooky2.",
                "Praxis vor Ort: USB am Praxis-Rechner plus Relay, nicht am Debian-Root im Rack.",
                "Speicherung derived. Quelle measured nur bei ACK des Clips, sonst not-available.",
                "DSP darf kozyrev.padic.haar auf der RR-Reihe nutzen. CopyGuard blockt Stress- und Schlafdiagnose.",
                "Ein Clip = ein Klient, exclusive analog zum Emitter. isHardwareActivatable false bis Gate.",
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Cache, Performance, Wischen</H2>
          <div className="mt-5">
            <Spec
              rows={[
                ["Marke / JS / Fonts", "immutable Hash, public, max-age lang, selbst gehostet."],
                ["Zeugen / Session", "Cache-Control: private, no-store. Kein CDN, kein Service Worker in Phase 0/1."],
                ["Live", "Kein Bild-URL-Stroboskop. Canvas stirbt mit der Sitzung."],
                ["Wischen", "revokeObjectURL, caches.delete, IndexedDB drop, WS close, AudioContext close."],
                ["Prefetch", "Nur öffentliche EEAT-Texte. Kein Prefetch von /session/*."],
                ["Mobile", "Eine Spalte, 44 px, Cues statt Video. Backbone hilft dem Desktop, nicht dem Funkloch."],
              ]}
            />
          </div>
        </div>

        <Callout title="Kein Video">
          O08 / D10: keine Videos, kein WebRTC. Live ist der WebSocket-Fachkanal
          für Analyse und Harmonisierung.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}
