/* Info-View: Kernel-Ausweis (ABI), Entropie-Status — E-E-A-T: Herkunft &
   Nachvollziehbarkeit sichtbar (UI_DESIGN_STANDARD §3). */

export function initInfoView(api) {
  const manifestList = document.getElementById("manifest-list");
  const entropyList = document.getElementById("entropy-list");

  api.manifest().then((m) => {
    manifestList.innerHTML = "";
    const rows = [
      ["id", m.id],
      ["version", m.version],
      ["hash", m.hash],
      ["class", m.class],
      ["repro", m.repro],
      ["budget", `${m.budget.vram_mb} MB VRAM · ~${m.budget.cpu_ms_est} ms · batch ${m.budget.max_batch}`],
      ["entry", m.entry],
      ["hardware", m.isHardwareActivatable ? "aktivierbar" : "isHardwareActivatable: false (Emission nur via aurelia-emitterd)"],
      ["copy", m.copy.join(" — ")],
    ];
    for (const [key, value] of rows) {
      const dt = document.createElement("dt");
      dt.textContent = key;
      const dd = document.createElement("dd");
      dd.textContent = String(value);
      manifestList.append(dt, dd);
    }
  });

  api.entropyStatus().then((status) => {
    entropyList.innerHTML = "";
    const rows = [
      ["Arbeitsmodus (Settings)", status.defaultMode],
      ["Factory-Default", status.factoryDefault],
      ["Modi", status.modes.join(" · ")],
      ["Kette", status.chain.join(" → ")],
      ["Hinweis", status.note],
    ];
    for (const [key, value] of rows) {
      const dt = document.createElement("dt");
      dt.textContent = key;
      const dd = document.createElement("dd");
      dd.textContent = String(value);
      entropyList.append(dt, dd);
    }
  });
}
