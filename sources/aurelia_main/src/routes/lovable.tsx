import { createFileRoute, Link } from "@tanstack/react-router";
import { ConceptShell } from "@/components/concept/shell";
import { Callout, DataTable, H2, P, PageHeader, Reco, Spec, Stack } from "@/components/concept/ui";
import { LOVABLE_NUTZEN, LOVABLE_URTEIL } from "@/lib/concept/lovable-nutzen";
import {
  ERSTE_HYBRID_FLAECHEN,
  HYBRID_ALTERNATIVEN,
  STANDALONE_URTEIL,
} from "@/lib/concept/standalone";

export const Route = createFileRoute("/lovable")({ component: Page });

function Page() {
  return (
    <ConceptShell>
      <Stack>
        <PageHeader
          chapter="02c"
          kicker="Lovable und Hybrid"
          title="H1–H3 gesetzt. Lovable ist nicht die Laufzeit."
          lead="Origin ist M G1. Backup ist Pflicht. Pflichtseiten kommen aus diesem Baum. Die Lovable-Cloud bleibt Heritage — tot, bis Sie disconnecten. D24 gesetzt."
        />

        <Reco>{STANDALONE_URTEIL.lang}</Reco>

        <div>
          <H2>Was die erste Ausarbeitung wirklich meinte</H2>
          <P>
            Nachzulesen in D03, docs/02-architecture.md („souveräner Kern, schlanke
            öffentliche Kante, Lovable neben Spur“) und Kapitel 11. Die L-IDs sind
            die spätere Feingliederung derselben Flächen.
          </P>
          <div className="mt-5">
            <DataTable
              caption="Erstfassung Hybrid → L-IDs"
              headers={["Damals", "Quelle im Repo", "L-ID", "Für AURELIA heute"]}
              rows={ERSTE_HYBRID_FLAECHEN.map((r) => ({
                key: r.l,
                cells: [r.damals, r.quelle, r.l, r.fuerAurelia],
              }))}
            />
          </div>
        </div>

        <div>
          <H2>Lovable-Flächen, unverändert bewertet</H2>
          <div className="mt-5">
            <DataTable
              caption="Lovable-Nutzen gegen Risiko"
              headers={["ID", "Fläche", "Urteil", "Positiver Nutzen"]}
              rows={LOVABLE_NUTZEN.map((r) => ({
                key: r.id,
                cells: [r.id, r.flaeche, r.urteil, r.nutzen],
              }))}
            />
          </div>
        </div>

        <div>
          <H2>Andere Kombinationen — was der Ada wirklich hilft</H2>
          <P>
            „Hybrid“ nützt nur, wenn es den Origin entlastet oder rettet — nicht,
            wenn es eine zweite Uhr erfindet.
          </P>
          <div className="mt-5">
            <DataTable
              caption="Standalone und Alternativen"
              headers={["ID", "Kombination", "Lock", "Urteil", "Grund"]}
              rows={HYBRID_ALTERNATIVEN.map((r) => ({
                key: r.id,
                cells: [r.id, r.kombination, r.lock, r.urteil, r.grund],
              }))}
            />
          </div>
        </div>

        <div>
          <H2>Ist Lovable (Kapitel 11)</H2>
          <div className="mt-5">
            <Spec
              rows={[
                ["Projekt", "ccecde78-… · leer, nie publiziert, Region unbelegt"],
                ["GitHub-Sync", "radiquant-cloud-build / radiquant4 — Heritage, nicht AURELIA-Laufzeit"],
                ["Investition", LOVABLE_URTEIL.investition],
                ["D24", "gesetzt: H1 Origin, H2 Backup, H3 Caddy-Kante. H5–H8 gesperrt."],
              ]}
            />
          </div>
        </div>

        <Callout title="Was noch offen ist">
          Backup-SKU, optionales H4, X-Katalog, das Wort Phase 1, Heritage-Disconnect.
          Liste:{" "}
          <Link to="/offen" className="underline decoration-from-font">
            Offen
          </Link>
          .
        </Callout>
      </Stack>
    </ConceptShell>
  );
}
