import { createFileRoute } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, H2, List, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";
import { HybridDiagram } from "@/components/concept/diagrams";

export const Route = createFileRoute("/architektur")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="02"
          kicker="Architektur"
          title="Souveräner Kern, schlanke Kante, keine vermischte Wolke."
          lead="Der GPU Server M G1 ist die eigentliche Plattform. Die Web-App ist das Gesicht. Lovable Cloud ist ein Werkzeug für unpersönliche Oberfläche — nachgewiesen leer, und so bleibt es."
        />

        <Reco>
          Drei Ebenen mit harter Grenze. Art.-9-Daten, CUDA, Timer und Emitter nur auf
          Debian. Dieses Frontend für Website und Anwendung. Lovable verbunden, aber
          datenschutzleer — kein Disconnect, kein Force-Push, keine zweite Control-Plane.
        </Reco>

        <HybridDiagram />

        <div>
          <H2>Warum diese Trennung tragfähig ist</H2>
          <div className="mt-4">
            <P>
              Der Server bringt Ryzen 5 9600X, RTX 4000 SFF Ada mit 20 GB, 128 GB DDR5
              und zwei 1-Gbit-Uplinks bereits mit. Genau dort gehören CUDA,
              Kozyrev-inspirierte DSP, cuQuantum, parallele Timer, CopyGuard und die
              Datenbank hin. Eine Cloud ohne GPU kann diese Arbeit nicht ehrlich
              übernehmen; sie kann sie nur vortäuschen.
            </P>
            <div className="mt-4">
              <P>
                Lovable (Projekt ccecde78-…, Sync auf radiquant-cloud-build / Branch
                radiquant4) ist als Anbindung da. Als Control-Plane ist es nicht
                umgesetzt: 0 Tabellen, 0 Migrationen, 0 RLS, 0 Functions, Publish nie,
                Region unbelegt. Das ist Architekturgrenze, nicht ein Mangel, den man
                „schnell in der Cloud füllt“.
              </P>
            </div>
          </div>
        </div>

        <Spec
          rows={[
            ["Frontend", "TanStack Start, React 19, Tailwind — diese Codebasis. PWA-fähig, barrierefrei, EEAT-Website und App-UI in einem System."],
            ["API / BFF", "FastAPI auf Debian (CUDA-Ökosystem). mTLS intern, TLS 1.3 nach außen."],
            ["Control Plane", "Auth, Mandanten, RBAC, Abo-Quotas, Audit-Index. Metadaten ohne Zeugenpayload. Ort: M G1, nicht Lovable."],
            ["Data Plane", "PostgreSQL 16 + TimescaleDB + pgvector, MinIO, Redis. LUKS plus Envelope Encryption."],
            ["Compute Plane", "GPU-Worker, aurelia-timerd, CopyGuard-Slot, VRAM-Allocator, Kernel-Registry."],
            ["Emitter Plane", "aurelia-emitterd über CP210x. Lease → Arming → ACK. Nie WebUSB."],
            ["Realtime", "WebSocket-Fachkanal. Kein Video (D10). Server sendet Tick, Client rendert."],
            ["Lovable", "Preview und Gestaltung. Kein Produktivpfad für Sitzungen. Anbindung bleibt."],
          ]}
        />

        <div>
          <H2>Netz und Vertrauensgrenzen</H2>
          <div className="mt-4">
            <List
              items={[
                "Öffentliches HTTPS endet am Reverse Proxy (Caddy oder Nginx) auf Debian.",
                "Worker sprechen nur intern (gRPC/NATS) und nie direkt das Internet.",
                "Schlüssel für Zeugen liegen in einem Keystore auf dem Server (TPM/LUKS, später HSM-fähig).",
                "Backups sind mandantenfähig, verschlüsselt, mit getrennten Restore-Tests.",
                "Observability (OpenTelemetry) enthält keine Zeugeninhalte und keine Klarnamen in Logs.",
                "1-Gbit-Kante: adaptive Live-Formate, Failover über den zweiten Uplink, kein naiver HD-Stream.",
              ]}
            />
          </div>
        </div>

        <Callout title="Zukunftsfähigkeit">
          Die Verträge (Kernel-ABI, Passport, Tenant-Scope, WebSocket-Schema, Emitter-Lease)
          sind langlebiger als einzelne Bibliotheken. CUDA 12, PennyLane oder ein späterer
          QPU-Adapter können hinter derselben ABI tauschen, ohne Archive zu brechen.
        </Callout>
      </Stack>
    </ConceptShell>
  );
}
