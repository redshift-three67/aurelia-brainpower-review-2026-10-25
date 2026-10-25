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
          title="GPU Server M G1 — inventarisiert; Aktivierung bleibt gesperrt."
          lead="Die RTX 4000 SFF Ada ist nach dem Gate für Analyse- und Harmonisierung-DSP vorgesehen. CopyGuard bleibt im RAM, die Uhr in Postgres. CUDA, USB und Art.-9-Klartext sind aktuell gesperrt."
        />

        <Reco>
          Ryzen 5 9600X orchestriert. Die RTX 4000 SFF Ada (20 GB) erhält nach
          Freigabe den 2/16/2-Plan; 128 GB DDR5 tragen CopyGuard. Geplant sind
          2×2 TB WD_BLACK SN850X mit RAID1/LUKS2/LVM. Kein MIG, kein LLM auf der Ada.
        </Reco>

        <Spec
          rows={[
            ["CPU", "AMD Ryzen 5 9600X · 6 Kerne / 12 Threads · 3900 / 5400 MHz · AVX-512 (Zen 5)"],
            ["GPU", "NVIDIA RTX 4000 SFF Ada · 20 GB · CUDA gesperrt bis Gate · kein MIG"],
            ["RAM", "128 GB DDR5 — CopyGuard, Postgres, Puffer"],
            ["Storage-Plan", "2×2 TB WD_BLACK SN850X — geplant mit RAID1/LUKS2/LVM"],
            ["Netz", "2× 1 Gbit/s, Backbone-nah — Failover, keine naive HD-Live"],
            ["Betrieb", "Ubuntu Server 24.04.4 LTS amd64 · minimales GNOME · IPMI · redundantes Netzteil"],
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
