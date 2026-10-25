(() => {
  "use strict";

  const byId = (id) => document.getElementById(id);
  const sourceStatuses = new Set(["ok", "partial", "fallback"]);
  const sourceMetrics = [
    ["ent", "entropy_score", "rng", "entStatus", 3],
    ["jit", "timing_jitter_ms", "cpu_timing", "jitStatus", 2],
    ["load", "system_load", "system_load", "loadStatus", 3],
    ["sensor", "sensor_entropy", "sensor_entropy", "sensorStatus", 3],
  ];
  const finiteNumber = (value) => {
    if (value === null || value === undefined) return null;
    if (typeof value === "string" && value.trim() === "") return null;
    if (typeof value !== "number" && typeof value !== "string") return null;
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric : null;
  };
  const formatted = (value, digits) => {
    const numeric = finiteNumber(value);
    return numeric === null ? "--" : numeric.toFixed(digits);
  };
  const setText = (id, value) => {
    const node = byId(id);
    if (node) node.textContent = value;
  };
  const setSourceStatus = (id, value) => {
    const status = sourceStatuses.has(value) ? value : "unknown";
    const node = byId(id);
    if (!node) return;
    node.textContent = status;
    node.className = `monitor-source-status status-${status}`;
  };

  function update(payload) {
    const emfIndex = finiteNumber(payload?.emf_index);
    setText("emf", formatted(payload?.emf_index, 3));
    const sourceHealth = payload?.source_health && typeof payload.source_health === "object"
      ? payload.source_health
      : {};
    sourceMetrics.forEach(([valueId, valueKey, sourceKey, statusId, digits]) => {
      setText(valueId, formatted(payload?.[valueKey], digits));
      setSourceStatus(statusId, sourceHealth[sourceKey]);
    });
    setText("rec", String(payload?.recommendation || "--"));

    const progress = byId("emfBar");
    if (progress) {
      if (emfIndex === null) {
        progress.hidden = true;
        progress.removeAttribute("value");
      } else {
        progress.hidden = false;
        progress.value = Math.max(0, Math.min(1, emfIndex));
      }
    }

    const frequencies = Array.isArray(payload?.counter_frequencies)
      ? payload.counter_frequencies
          .map(finiteNumber)
          .filter((value) => value !== null)
          .map((value) => `${value.toFixed(1)} Hz`)
      : [];
    setText("freq", frequencies.join(", ") || "--");
  }

  const wsUrl = `${location.protocol === "https:" ? "wss://" : "ws://"}${location.host}/api/emf/ws`;
  let socket;

  function connect() {
    setText("connectionState", "Verbindung wird aufgebaut …");
    socket = new WebSocket(wsUrl);
    socket.onopen = () => setText("connectionState", "Verbunden");
    socket.onmessage = (event) => {
      try {
        update(JSON.parse(event.data));
        setText("connectionState", "Verbunden");
      } catch (_) {
        setText("connectionState", "Ungültige Messantwort verworfen");
      }
    };
    socket.onclose = () => {
      setText("connectionState", "Verbindung getrennt – neuer Versuch folgt");
      setTimeout(connect, 3000);
    };
    socket.onerror = () => socket.close();
  }

  connect();
})();
