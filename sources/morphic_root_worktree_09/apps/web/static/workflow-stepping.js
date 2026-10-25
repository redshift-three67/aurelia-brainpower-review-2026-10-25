"use strict";

const STEP_LABELS = ["Init","Eingabe","Signatur","Fokus","EMF","Amplifier","Palette","Matrix","Quantum","Post","Export","Harmonie"];
let currentStep = 0;

function showWorkflowStep(index, moveFocus = true) {
  const bounded = Math.max(0, Math.min(STEP_LABELS.length - 1, index));
  const panels = Array.from(document.querySelectorAll(".workflow-panel"));
  const steps = Array.from(document.querySelectorAll(".workflow-step"));
  const connectors = Array.from(document.querySelectorAll(".workflow-connector"));
  panels.forEach((panel, i) => {
    panel.classList.toggle("active", i === bounded);
    panel.setAttribute("aria-hidden", i === bounded ? "false" : "true");
  });
  steps.forEach((step, i) => {
    step.classList.toggle("active", i === bounded);
    step.classList.toggle("completed", i < bounded);
    step.setAttribute("tabindex", i === bounded ? "0" : "-1");
    if (i === bounded) step.setAttribute("aria-current", "step");
    else step.removeAttribute("aria-current");
  });
  connectors.forEach((connector, i) => connector.classList.toggle("completed", i < bounded));
  currentStep = bounded;
  const percent = Math.round(((bounded + 1) / STEP_LABELS.length) * 100);
  const progress = document.querySelector("#workflow-progress");
  progress.style.width = `${percent}%`;
  progress.setAttribute("aria-valuenow", String(percent));
  document.querySelector("#workflow-progress-label").textContent = `${bounded + 1} / ${STEP_LABELS.length}`;
  document.querySelector("#workflow-prev").disabled = bounded === 0;
  document.querySelector("#workflow-next").disabled = bounded === STEP_LABELS.length - 1;
  if (moveFocus && steps[bounded]) {
    steps[bounded].focus();
    steps[bounded].scrollIntoView({block: "nearest", inline: "center"});
  }
}

function buildWorkflowNavigation() {
  const nav = document.querySelector("#workflow-nav");
  STEP_LABELS.forEach((label, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "workflow-step";
    const buttonId = `workflow-step-${index + 1}`;
    const panelId = `workflow-panel-${index + 1}`;
    button.id = buttonId;
    button.setAttribute("aria-controls", panelId);
    const panel = document.querySelector(`#${panelId}`);
    if (panel) panel.setAttribute("aria-labelledby", buttonId);
    const number = document.createElement("span");
    number.className = "workflow-step-number";
    number.textContent = String(index + 1);
    button.appendChild(number);
    button.appendChild(document.createTextNode(label));
    button.addEventListener("click", () => showWorkflowStep(index));
    button.addEventListener("keydown", (event) => {
      let target = null;
      switch (event.key) {
        case "ArrowRight": target = Math.min(currentStep + 1, STEP_LABELS.length - 1); break;
        case "ArrowLeft": target = Math.max(currentStep - 1, 0); break;
        case "Home": target = 0; break;
        case "End": target = STEP_LABELS.length - 1; break;
        default: return;
      }
      event.preventDefault();
      showWorkflowStep(target);
    });
    nav.appendChild(button);
    if (index < STEP_LABELS.length - 1) {
      const connector = document.createElement("span");
      connector.className = "workflow-connector";
      connector.setAttribute("aria-hidden", "true");
      nav.appendChild(connector);
    }
  });
  document.querySelector("#workflow-prev").addEventListener("click", () => showWorkflowStep(currentStep - 1));
  document.querySelector("#workflow-next").addEventListener("click", () => showWorkflowStep(currentStep + 1));
  showWorkflowStep(0, false);
}

document.addEventListener("DOMContentLoaded", buildWorkflowNavigation);
