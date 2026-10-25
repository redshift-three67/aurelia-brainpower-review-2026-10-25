/* PEGGOTTY — RadionicScript-Editor (Original-Minisprache). */

export function initPeggottyView(api) {
  const nameSelect = document.getElementById("pg-name");
  const loadBtn = document.getElementById("pg-load-btn");
  const text = document.getElementById("pg-text");
  const runBtn = document.getElementById("pg-run-btn");
  const output = document.getElementById("pg-output");

  api.scripts().then((data) => {
    for (const name of data.scripts || []) {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      nameSelect.appendChild(option);
    }
  });

  loadBtn.addEventListener("click", async () => {
    const name = nameSelect.value;
    if (!name) return;
    try {
      const data = await api.script(name);
      text.value = data.content || "";
    } catch (error) {
      alert(`Laden fehlgeschlagen: ${error.message}`);
    }
  });

  runBtn.addEventListener("click", async () => {
    runBtn.disabled = true;
    output.hidden = false;
    output.textContent = "Führe aus …";
    try {
      const result = await api.scriptExecute({ script: text.value });
      const lines = ["== AUSGABE ==", ...(result.output || [])];
      if (result.errors?.length) {
        lines.push("== FEHLER ==", ...result.errors);
      }
      lines.push("== VARIABLEN ==");
      for (const [key, value] of Object.entries(result.variables || {})) {
        lines.push(`${key} = ${value}`);
      }
      output.textContent = lines.join("\n");
    } catch (error) {
      output.textContent = `Fehler: ${error.message}`;
    } finally {
      runBtn.disabled = false;
    }
  });
}
