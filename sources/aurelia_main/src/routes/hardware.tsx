import { createFileRoute, Link } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, H2, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";

export const Route = createFileRoute("/hardware")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="03a"
          kicker="Hardware"
          title="GPU Server M G1 — gemessen. Budget folgt dem CUDA-Zweck."
          lead="Die Karte rechnet Analyse- und Harmonisierung-DSP. Der Wächter sitzt im RAM. Die Uhr sitzt in Postgres. 20 Klienten sind ein Beispiel für Belegung — virtuelle Timer liegen nicht im VRAM."
        />

        <Reco>
          Ryzen 5 9600X orchestriert. RTX 4000 SFF Ada (20 GB) ist der Job-Pool.
          128 GB DDR5 tragen CopyGuard redundant zu den NVMe. Kein MIG, kein 14B,
          kein LLM auf der Ada.
        </Reco>

        <Spec
          rows={[
            ["CPU", "AMD Ryzen 5 9600X · 6 Kerne / 12 Threads · 3900 / 5400 MHz · AVX-512 (Zen 5)"],
            ["GPU", "NVIDIA RTX 4000 SFF Ada · 20 GB · CUDA 12.x · kein MIG"],
            ["RAM", "128 GB DDR5 — CopyGuard, Postgres, Puffer"],
            ["Platte", "2× 1 TB NVMe — Akten-Spiegel, Modell-Replica"],
            ["Netz", "2× 1 Gbit/s, Backbone-nah — Failover, keine naive HD-Live"],
            ["Betrieb", "IPMI · redundantes Netzteil · Debian Bookworm Root"],
          ]}
        />

        <div>
          <H2>VRAM-Budget (gesetzt, C03)</H2>
          <div className="mt-5">
            <Spec
              rows={[
                ["Runtime", "2 GB — Treiber, CUDA-Kontext, kein Overcommit"],
                ["Job-Pool", "16 GB — Analyse, Harmonisierung, optionales Quantum, tenant-isoliert"],
                ["Kopf", "2 GB — Reserve, ECC, Peek"],
                ["CopyGuard", "0 GB VRAM — RAM/NVMe (C02)"],
              ]}
            />
          </div>
        </div>

        <Callout title="20 parallel, ehrlich">
          20 Klienten sind Belegung. Harmonisierungskanäle sind virtuell (D20).
          GPU-Jobs werden fair gequeued, typisch 1–4 im Pool. Details:{" "}
          <Link to="/compute" className="underline decoration-from-font">
            Scheduler
          </Link>{" "}
          und in der{" "}
          <Link to="/freigabe" className="underline decoration-from-font">
            Freigabe
          </Link>
          . Llama-3.1-8B Score 507 und Qwen2.5-14B Score 268 bleiben Demo, nicht Betrieb.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}
