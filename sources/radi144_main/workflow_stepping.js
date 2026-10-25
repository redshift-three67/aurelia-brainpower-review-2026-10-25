// ========== STEP DEFINITIONS ==========
const STEPS = [
  { num: 1, label: "Init", title: "System-Init" },
  { num: 2, label: "Input", title: "Eingabe" },
  { num: 3, label: "Signatur", title: "Klienten-Signatur" },
  { num: 4, label: "Fokus", title: "Fokus-Vektor" },
  { num: 5, label: "EMF", title: "EMF-Kompensation" },
  { num: 6, label: "Amplifier", title: "Amplifier" },
  { num: 7, label: "Palette", title: "Farbpalette" },
  { num: 8, label: "Matrix", title: "Matrix-Suche" },
  { num: 9, label: "Quantum", title: "D-Wave" },
  { num: 10, label: "Post", title: "Post-Processing" },
  { num: 11, label: "Export", title: "Ausgabe" },
  { num: 12, label: "API", title: "API & Monitor" },
];

let currentStep = 0;

// ========== BUILD NAV ==========
function buildNav() {
  const nav = document.getElementById("navInner");
  nav.innerHTML = "";
  STEPS.forEach((s, i) => {
    if (i > 0) {
      const conn = document.createElement("div");
      conn.className = "nav-conn" + (i <= currentStep ? " done" : "");
      nav.appendChild(conn);
    }
    const step = document.createElement("div");
    step.className = "nav-step" + (i === currentStep ? " active" : "") + (i < currentStep ? " completed" : "");
    step.innerHTML = `<div class="nav-num">${i < currentStep ? "✓" : s.num}</div><span>${s.label}</span>`;
    step.onclick = () => goToStep(i);
    nav.appendChild(step);
  });
}

// ========== NAVIGATE ==========
function goToStep(idx) {
  if (idx < 0 || idx >= STEPS.length) return;
  // Hide current
  document.querySelectorAll(".step-panel").forEach(p => p.classList.remove("active"));
  currentStep = idx;
  // Show target
  const target = document.querySelector(`.step-panel[data-step="${idx}"]`);
  if (target) target.classList.add("active");
  // Update nav
  buildNav();
  // Update progress
  const pct = ((idx + 1) / STEPS.length * 100).toFixed(1);
  document.getElementById("overallFill").style.width = pct + "%";
  document.getElementById("overallPct").textContent = `${idx + 1} / ${STEPS.length}`;
  // Update buttons
  document.getElementById("btnPrev").disabled = idx === 0;
  const btnNext = document.getElementById("btnNext");
  if (idx === STEPS.length - 1) {
    btnNext.innerHTML = "✓ Abgeschlossen";
    btnNext.disabled = true;
  } else {
    btnNext.innerHTML = "Weiter →";
    btnNext.disabled = false;
  }
  // Scroll nav into view
  const navStep = document.querySelectorAll(".nav-step")[idx];
  if (navStep) navStep.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
  // Scroll to top
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function navigate(dir) {
  goToStep(currentStep + dir);
}

// ========== DEMO MATRIX ==========
function buildDemoMatrix() {
  const container = document.getElementById("demoMatrix");
  if (!container) return;
  
  const palette = [
    "#F8F8FF", "#E74C3C", "#E67E22", "#F1C40F", "#2ECC71",
    "#1ABC9C", "#3498DB", "#9B59B6", "#E91E63", "#FFD700"
  ];
  
  // Generate a seeded pseudo-random 12x12 matrix
  let seed = 42;
  function rand() {
    seed = (seed * 16807 + 0) % 2147483647;
    return seed;
  }
  
  container.innerHTML = "";
  for (let i = 0; i < 144; i++) {
    const val = rand() % 10;
    const cell = document.createElement("div");
    cell.className = "mc";
    cell.style.background = palette[val];
    // Contrast text
    const hex = palette[val].replace("#", "");
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    cell.style.color = lum > 128 ? "#000" : "#fff";
    cell.textContent = val;
    cell.title = `Zelle [${Math.floor(i/12)},${i%12}] = ${val} → ${palette[val]}`;
    container.appendChild(cell);
  }
}

// ========== KEYBOARD NAVIGATION ==========
document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight" || e.key === "ArrowDown") {
    e.preventDefault();
    navigate(1);
  } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
    e.preventDefault();
    navigate(-1);
  }
});

// ========== INIT ==========
buildNav();
buildDemoMatrix();
