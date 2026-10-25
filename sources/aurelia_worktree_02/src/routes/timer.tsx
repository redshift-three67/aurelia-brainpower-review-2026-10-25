import { createFileRoute, Link } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/timer")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="03c"
          kicker="Timer & Persistenz"
          title="Viele Uhren pro Klient. Eine Wahrheit auf der Platte."
          lead="20 Klienten sind ein Beispiel für Belegung, nicht die Kapazität. Virtuelle Harmonisierungskanäle sind klein und zahlreich. Nach einem Server-Reset muss die Zeit stimmen — deshalb ist die Ada nicht das Ledger."
        />

        <Reco>
          Source of Truth: Postgres-WAL. Heißer Pfad: aurelia-timerd im DDR5.
          GPU nur, wenn ein Kanal wirklich DSP oder Waveform braucht, als Job im
          16-GB-Pool, isoliert auf (tenant, client, channel). Das ist D20, gesetzt.
        </Reco>

        <div>
          <H2>Warum nicht VRAM als Timer-Speicher</H2>
          <P>
            Sie bevorzugten die GPU, weil Harmonisierung Echtzeit ist. Echtzeit der
            Rechnung ja — Echtzeit der Uhr nein. VRAM ist flüchtig: Reboot, NVIDIA-
            Driver-Reset, Prozessabsturz, cudaDeviceReset löschen denselben Speicher,
            in dem die Kanäle lägen. Genau die Persistenz, die Sie verlangen, kann
            die Ada nicht liefern. Sie wäre ein schneller Notizblock ohne Bleistift
            nach dem Stromausfall.
          </P>
          <div className="mt-5">
            <Spec
              rows={[
                [
                  "GPU VRAM",
                  "Gut für DSP/Waveform eines Ticks. Tot nach Reset. 16 GB sind für Jobs reserviert (C03). Ungeeignet als Ledger.",
                ],
                [
                  "RAM / timerd",
                  "Gut für 50-ms-UI-Ticks und Tausende Zustandsmaschinen (wenige KB je Kanal). Nach Reset leer, wenn nicht gespiegelt.",
                ],
                [
                  "Postgres WAL",
                  "Überlebt Reset, RLS, SKIP LOCKED, bewiesene fsync-Semantik. Das ist die Uhr, die man nach dem Reboot noch lesen kann.",
                ],
                [
                  "Redis AOF",
                  "Zulässiger Hot-Cache vor Postgres, nicht statt WAL. Extra bewegliches Teil.",
                ],
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Ideale Teilung</H2>
          <div className="mt-5">
            <Cards
              items={[
                {
                  title: "Kanalzustand",
                  body: "Postgres: status, t0, last_tick, params, tenant/client/channel. Jeder Start/Pause/Stop fsync. Running: Checkpoint alle 500–1000 ms, nicht jeder 50-ms-UI-Tick.",
                },
                {
                  title: "Hot path",
                  body: "timerd im RAM, monotonic clock + chrony. 50 ms Ticks an den WebSocket. Droppen erlaubt, erfinden verboten.",
                },
                {
                  title: "DSP-Slice",
                  body: "Nur wenn der Kanal Kernel/Waveform braucht: Job an gpud, eigene Arena. Sonst bleibt die Ada frei für Analysen anderer Klienten.",
                },
                {
                  title: "Nach Reset",
                  body: "Kanäle in running/paused/armed laden. Lücke now − last_checkpoint in den Ausweis schreiben. Nicht heimlich aufholen.",
                },
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Kapazität, ehrlich</H2>
          <div className="mt-4">
            <List
              items={[
                "Default-Quota 16 Kanäle pro Klient, hebbar (D09). 20 gleichzeitige Klienten × 16 = 320 Kanäle — trivial für den 9600X und 128 GB.",
                "Ein Kanalzustand: wenige KB. Tausende wären RAM-seitig möglich; die Grenze ist Tick-Schreiblast, WebSocket-Fanout und Fairness, nicht die GPU.",
                "50 ms fsync × 320 Kanäle ≈ 6400 Commits/s — unnötig. Deshalb Checkpoint 500–1000 ms plus sofort bei Zustandswechsel.",
                "GPU-DSP bleibt 1–4 Occupancies im Pool. Idle-Timer kosten kein VRAM.",
                "Emitter bleibt 1 global (D14). Viele Timer ≠ viele Generatoren.",
                "Isolation auch innerklientlich: Analyse-Job A, Analyse-Job B, Harmonisierungskanal 1 und 2 teilen keinen Buffer und kein RNG.",
              ]}
            />
          </div>
        </div>

        <Callout title="HRV-Ohrclip (D21)">
          Der Clip sitzt am Ohr, nicht an der GPU-Rückseite. RR-Intervalle kommen
          über den Fachkanal, werden derived gespeichert und dürfen als 1D-Reihe
          durch denselben p-adischen Kernel. Details in{" "}
          <Link to="/live" className="underline decoration-from-font">
            Live
          </Link>{" "}
          und{" "}
          <Link to="/freigabe" className="underline decoration-from-font">
            U12
          </Link>
          .
        </Callout>
      </Stack>
    </ConceptShell>
  );
}
