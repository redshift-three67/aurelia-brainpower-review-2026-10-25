/* Gemeinsame GV-Balkengrafik (Original: GENERAL VITALITY GRAPH, Auto-Modus).
   Farblogik aus GuiElements: >=1000 Akzent, <500 warm, <250 stopptend. */

export function drawSeries(canvas, series) {
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  ctx.clearRect(0, 0, width, height);
  const styles = getComputedStyle(document.documentElement);
  const accent = styles.getPropertyValue("--mod-accent").trim() || "#2C4A3E";
  const warn = styles.getPropertyValue("--aur-warn").trim() || "#8a6d2f";
  const stop = styles.getPropertyValue("--aur-stop").trim() || "#7c3a35";
  const barWidth = Math.max(2, Math.floor(width / Math.max(series.length, 1)) - 1);
  series.forEach((gv, index) => {
    const barHeight = Math.min(1, gv / 1000) * (height - 6);
    ctx.fillStyle = gv >= 1000 ? accent : gv < 250 ? stop : gv < 500 ? warn : accent;
    ctx.globalAlpha = gv >= 1000 ? 0.95 : 0.75;
    ctx.fillRect(index * (barWidth + 1), height - barHeight, barWidth, barHeight);
  });
  ctx.globalAlpha = 1;
}
