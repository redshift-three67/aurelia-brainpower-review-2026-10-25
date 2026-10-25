import { createFileRoute, Link } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, Cards, H2, List, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";
import { PassportPreview, PipelineDiagram } from "@/components/concept/diagrams";

export const Route = createFileRoute("/compute")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="03"
          kicker="Echtzeit-Compute"
          title="Die Ada bleibt gesperrt; der gesetzte Schedulervertrag wartet auf das Gate."
          lead="CUDA und Quantum sind aktuell gesperrt. Nach Freigabe plant aurelia-gpud einen 16-GB-Job-Pool, isoliert bis job_id; CopyGuard bleibt im RAM und virtuelle Timer außerhalb des VRAM."
        />

        <Reco>
          Zielarchitektur nach bestandenem Gate: ein Scheduler, ein Timer-Daemon mit
          Postgres-Ledger, ein Emitter-Daemon und CopyGuard im RAM. 20 Klienten sind
          Belegung; GPU-Occupancy bleibt geplant bei 1–4. Bis dahin keine CUDA-
          Aktivierung und ausschließlich synthetische Daten.
        </Reco>

        <PipelineDiagram />

        <div>
          <H2>aurelia-gpud — Isolation ohne MIG</H2>
          <P>
            Die RTX 4000 SFF Ada kann nicht in Hardware-Scheiben (MIG). Isolation ist
            deshalb Vertrag plus Test: eigener Stream, VRAM-Arena, tenant_id auf jedem
            Buffer, Drain nach Job, Fair-Queue nach Quota.
          </P>
          <div className="mt-4">
            <List
              items={[
                "Pre-flight: kernel.budget.vram_mb. Admit nur wenn laufend + neu ≤ 16 GB.",
                "Kein Default-Stream-Mix, kein Peer-Zugriff zwischen Mandanten.",
                "Nach Job: Stream destroy, Mempool-Trim. OOM oder ECC: Pause, nicht Weitermogeln.",
                "MPS höchstens intern für den Worker, nie als Sicherheitsgrenze.",
                "Cross-Tenant-Tensor in CI ist Stop-the-line, analog zu RLS.",
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Rollen nach dem Umbau</H2>
          <div className="mt-5">
            <Spec
              rows={[
                [
                  "RTX 4000 SFF Ada",
                  "16 GB Job-Pool: FFT, Haar/p-adisch, Harmonisierungspfad, optionales cuQuantum. 2+2 GB Runtime/Kopf.",
                ],
                [
                  "Ryzen 5 9600X",
                  "API, Postgres, Redis, timerd, emitterd, gpud-Orchestrierung, CopyGuard-Runtime, WebSocket-Fanout, AVX-512 für kleine pWT.",
                ],
                [
                  "128 GB DDR5",
                  "CopyGuard-Gewichte + KV, Shared Buffers, Puffer. Replica der Gewichte auf beiden NVMe.",
                ],
                [
                  "WebSocket",
                  "Analyse-Progress, Clipboard-Events, Harmonisierungsticks und ACK. Kein Zeugenklartext.",
                ],
              ]}
            />
          </div>
        </div>

        <div>
          <H2>Quantum im selben Pool (U06)</H2>
          <P>
            cuQuantum / PennyLane Lightning-GPU / Qiskit Aer GPU hinter der ABI, opt-in,
            gleicher Allocator. Volle Statevector nur bei niedriger Qubit-Zahl. Nie still
            mit strikten CUDA-Läufen in einem Ergebnis vermischt. Nie den RAM-Wächter
            verdrängen.
          </P>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <PassportPreview />
          <Cards
            items={[
              {
                title: "Strikt",
                body: "Default. Gleiche Kernel-Version, gleiche Parameter, gleiche GPU-Architektur → gleiches Ergebnis.",
              },
              {
                title: "Queue statt Hoffnung",
                body: "Pool voll = warten oder ablehnen. Eine simulierte Occupancy, die wie Hardware wirkt, ist verboten.",
              },
            ]}
          />
        </div>

        <Callout title="Kozyrev hier nur als DSP">
          Die Namens- und Physikprüfung steht in{" "}
          <Link to="/kozyrev" className="underline decoration-from-font">
            Kapitel 05b
          </Link>
          . Compute sieht nur Kernel-IDs und Budgets.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}
