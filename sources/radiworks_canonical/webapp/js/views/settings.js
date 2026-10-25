/* Einstellungen-View (Aether_3): Booleans als Schalter, Integers/Strings als
   Felder — Speichern via PUT /settings (Contract §6). */

export function initSettingsView(api) {
  const boolBox = document.getElementById("settings-booleans");
  const intBox = document.getElementById("settings-integers");
  const strBox = document.getElementById("settings-strings");
  const saveBtn = document.getElementById("settings-save-btn");
  const out = document.getElementById("settings-out");

  const state = { booleans: {}, integers: {}, strings: {} };

  api.settings().then((data) => {
    state.booleans = data.booleans || {};
    state.integers = data.integers || {};
    state.strings = data.strings || {};
    render();
  });

  function render() {
    boolBox.innerHTML = "";
    for (const [key, value] of Object.entries(state.booleans)) {
      const row = document.createElement("label");
      row.className = "settings-row";
      const box = document.createElement("input");
      box.type = "checkbox";
      box.checked = value === true;
      box.dataset.key = key;
      box.dataset.type = "boolean";
      const name = document.createElement("span");
      name.textContent = key === "dynamic.adjustments"
        ? "dynamic.adjustments (derzeit nur gespeichert, kein aktiver RadiWorks-Ablauf)"
        : key;
      const stateText = document.createElement("span");
      stateText.className = "hint";
      const statusText = (checked) => key === "dynamic.adjustments"
        ? (checked ? "true · ohne Wirkung im Prototyp" : "false · ohne Wirkung im Prototyp")
        : (checked ? "true" : "false");
      stateText.textContent = statusText(box.checked);
      box.addEventListener("change", () => { stateText.textContent = statusText(box.checked); });
      row.append(box, name, stateText);
      boolBox.appendChild(row);
    }

    intBox.innerHTML = "";
    for (const [key, value] of Object.entries(state.integers)) {
      intBox.appendChild(numberRow(key, value));
    }

    strBox.innerHTML = "";
    for (const [key, value] of Object.entries(state.strings)) {
      strBox.appendChild(textRow(key, value));
    }
  }

  function numberRow(key, value) {
    const row = document.createElement("label");
    row.className = "settings-row";
    const input = document.createElement("input");
    input.type = "number"; input.value = value; input.dataset.key = key; input.dataset.type = "integer";
    const name = document.createElement("span"); name.textContent = key;
    row.append(input, name);
    return row;
  }

  function textRow(key, value) {
    const row = document.createElement("label");
    row.className = "settings-row settings-row-wide";
    const input = document.createElement("input");
    input.type = "text"; input.value = value; input.dataset.key = key; input.dataset.type = "string";
    const name = document.createElement("span"); name.textContent = key;
    row.append(input, name);
    return row;
  }

  saveBtn.addEventListener("click", async () => {
    const payload = { booleans: {}, integers: {}, strings: {} };
    for (const input of document.querySelectorAll("#view-settings [data-key]")) {
      const { key, type } = input.dataset;
      if (type === "boolean") payload.booleans[key] = input.checked;
      else if (type === "integer") payload.integers[key] = Number(input.value);
      else payload.strings[key] = input.value;
    }
    try {
      await api.updateSettings(payload);
      out.textContent = "Gespeichert.";
      setTimeout(() => { out.textContent = ""; }, 2500);
    } catch (error) {
      out.textContent = `Fehler: ${error.message}`;
    }
  });
}
