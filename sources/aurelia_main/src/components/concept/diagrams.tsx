export function HybridDiagram() {
  const layers = [
    {
      name: "Öffentliche Schicht",
      detail: "Website, EEAT-Texte, Login-UI, PWA — dieses Frontend",
    },
    {
      name: "Control Plane · Debian EU",
      detail: "Auth, Mandanten, Rollen, Abos, Audit-Index — keine Zeugeninhalte",
    },
    {
      name: "Data + Compute · GPU Server M G1",
      detail:
        "Postgres, MinIO, Redis, aurelia-gpud (16 GB Job-Pool), Timerd, CopyGuard im RAM, Emitterd — Ryzen 5 9600X · RTX 4000 SFF Ada 20 GB · 128 GB DDR5",
    },
  ];

  return (
    <ol className="space-y-2" aria-label="Hybridarchitektur">
      {layers.map((layer, i) => (
        <li
          key={layer.name}
          className="rounded-xl border border-border bg-elevated px-5 py-4 sm:px-6"
        >
          <p className="font-mono text-xs tabular-nums text-subtle">Ebene {i + 1}</p>
          <p className="mt-1 font-display text-xl font-medium">{layer.name}</p>
          <p className="mt-1 text-sm leading-relaxed text-muted">{layer.detail}</p>
        </li>
      ))}
      <li className="rounded-xl border border-dashed border-border px-5 py-4 sm:px-6">
        <p className="font-mono text-xs tabular-nums text-subtle">Neben Spur</p>
        <p className="mt-1 font-display text-xl font-medium">Lovable Cloud</p>
        <p className="mt-1 text-sm leading-relaxed text-muted">
          Preview und Gestaltung, angebunden an radiquant-cloud-build. 0 Tabellen, nie
          publiziert. Kein Produktiv-Dataplane, kein Disconnect.
        </p>
      </li>
    </ol>
  );
}

export function PipelineDiagram() {
  const steps = [
    ["01", "Ingest", "Zeuge, Rate, Protokoll — Envelope-verschlüsselt"],
    ["02", "Normierung", "AVIF/Opus, Hash, Schema-Validierung"],
    ["03", "CPU-Orchestrierung", "Ryzen plant Jobs, 16-GB-VRAM-Pool, Fair-Queue"],
    ["04", "CUDA-Kerne", "FFT, Haar/p-adisch, Harmonisierungspfad — tenant-isoliert"],
    ["05", "Optional Quantum", "cuQuantum / PennyLane, gleicher Pool, eigener Modus"],
    ["06", "CopyGuard + Ausweis", "Lexikon + Phi-4-mini im RAM, Passport, Persistenz"],
  ];

  return (
    <ol className="grid gap-2 sm:grid-cols-2">
      {steps.map(([n, title, body]) => (
        <li key={n} className="rounded-xl border border-border bg-elevated p-4 sm:p-5">
          <p className="font-mono text-xs text-subtle">{n}</p>
          <p className="mt-1 font-display text-lg font-medium">{title}</p>
          <p className="mt-1 text-sm leading-relaxed text-muted">{body}</p>
        </li>
      ))}
    </ol>
  );
}

export function PassportPreview() {
  const rows: Array<[string, string]> = [
    ["run_id", "8f3c-19aa-7b21"],
    ["tenant_id", "tnt_04c1"],
    ["modus", "strikt"],
    ["kernel", "kozyrev.padic.haar.v1"],
    ["kernel_hash", "sha256:9c1e…a04"],
    ["input_hash", "sha256:41ab…e2"],
    ["vram_mb", "420 · pool 16384"],
    ["copyguard", "allow · digest 7e2a…c1 · ram"],
    ["dauer_ms", "1842"],
    ["signatur", "Ed25519 · worker-01"],
  ];

  return (
    <div className="rounded-xl border border-border bg-elevated p-5 sm:p-6">
      <p className="text-xs font-medium tracking-[0.16em] text-muted uppercase">
        Berechnungsausweis · Beispiel
      </p>
      <dl className="mt-4 grid gap-2">
        {rows.map(([k, v]) => (
          <div key={k} className="flex flex-wrap justify-between gap-2 border-b border-border/80 py-2 last:border-0">
            <dt className="font-mono text-xs text-subtle">{k}</dt>
            <dd className="font-mono text-xs text-fg">{v}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

export function ClipboardDiagram() {
  const steps = [
    ["1", "Analyse-Lauf", "Kernel + Passport. Rohartefakt, noch kein Timer."],
    ["2", "Zwischenablage", "Draft, tenant- und klientenbezogen. Anpassen, CopyGuard."],
    ["3", "Promote", "Nur Praktiker, step-up später. Einziger Weg in die Spur."],
    ["4", "Harmonisierungsspur", "queued → armed → running ⇄ paused → stopped."],
    ["5", "Parallelkanäle", "Mehrere Spuren je Mandant. Ein Emitter global."],
    ["6", "Ende", "archived oder deleted. Ausweis und Audit bleiben."],
  ];

  return (
    <ol className="grid gap-2 sm:grid-cols-2" aria-label="Zwischenablage zur Harmonisierung">
      {steps.map(([n, title, body]) => (
        <li key={n} className="rounded-xl border border-border bg-elevated p-4 sm:p-5">
          <p className="font-mono text-xs text-subtle">{n}</p>
          <p className="mt-1 font-display text-lg font-medium">{title}</p>
          <p className="mt-1 text-sm leading-relaxed text-muted">{body}</p>
        </li>
      ))}
    </ol>
  );
}
