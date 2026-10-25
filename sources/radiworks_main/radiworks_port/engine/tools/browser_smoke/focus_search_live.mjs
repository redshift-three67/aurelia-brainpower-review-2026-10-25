import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const TARGET_URL = process.env.RADIOWORKS_TEST_URL || "http://127.0.0.1:8104/";
const browser = await chromium.launch({
  headless: false,
  channel: "chrome",
});
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const pageErrors = [];
let analysisPosts = 0;
page.on("pageerror", (error) => pageErrors.push(error.message));
page.on("request", (request) => {
  if (request.method() === "POST" && new URL(request.url()).pathname === "/analysis") analysisPosts++;
});

try {
  await page.goto(TARGET_URL, { waitUntil: "domcontentloaded" });
  await page.getByRole("tab", { name: "Analyse" }).click();
  await page.waitForFunction(() => document.querySelector("#db-select")?.options.length > 0);
  const original = await page.locator("#db-select").inputValue();
  await page.locator("#db-search").fill("Synthetic");
  await page.waitForFunction(() => document.querySelector("#db-search-status")?.textContent.includes("1 von 1"));
  assert.equal(await page.locator("#db-select").inputValue(), original);
  await page.locator("#db-search").fill("Essenzen");
  assert.match(await page.locator("#db-search-status").innerText(), /Keine Namenstreffer/);
  assert.equal(await page.locator("#db-select").inputValue(), original);
  await page.locator("#db-search-clear").focus();
  await page.keyboard.press("Enter");
  assert.equal(await page.locator("#db-search").inputValue(), "");
  assert.equal(analysisPosts, 0);

  await page.getByRole("tab", { name: "Fälle" }).click();
  const priorCase = await page.request.get(new URL("/cases/current", TARGET_URL).toString());
  const priorName = (await priorCase.json()).name;
  if (priorName) {
    await page.locator("#case-list .case-row").filter({ hasText: priorName }).locator("button").first().click();
    await page.waitForFunction(() => document.querySelector("#case-load-status")?.textContent.includes("geladen"));
  }
  await page.locator("#case-name").fill(priorName || "Synthetischer Testfall");
  await page.locator("#case-desc").fill("Künstliche Beschreibung");
  await page.locator("#case-focus").fill("Synthetic");
  await page.locator("#case-save-btn").click();
  await page.waitForFunction(() => document.querySelector("#case-save-status")?.textContent.includes("Fall gespeichert"));
  const caseData = await page.request.get(new URL("/cases/current", TARGET_URL).toString());
  assert.equal((await caseData.json()).focus, "Synthetic");

  await page.getByRole("tab", { name: "Analyse" }).click();
  await page.locator("#db-focus-search").waitFor({ state: "visible" });
  await page.waitForFunction(() => !document.querySelector("#db-focus-search")?.disabled);
  await page.locator("#db-focus-search").click();
  assert.equal(await page.locator("#db-search").inputValue(), "Synthetic");
  assert.equal(await page.locator("#db-select").inputValue(), original);
  assert.equal(analysisPosts, 0);

  await page.locator("#mode-select").selectOption("seeded");
  await page.locator("#seed-input").fill("17");
  await page.locator("#analyze-form button[type=submit]").click();
  await page.waitForFunction(() => document.querySelector("#result-count")?.textContent.includes("Raten"));
  const draft = await page.request.get(new URL("/analysis/current", TARGET_URL).toString());
  assert.equal(draft.status(), 200);

  const editAlerts = [];
  page.on("dialog", async (dialog) => {
    editAlerts.push(dialog.message());
    await dialog.dismiss();
  });
  await page.locator("#edit-case-btn").click();
  await page.locator("#edit-desc").fill("Sichere Testnotiz");
  await page.locator("#edit-save-btn").click();
  await page.locator("#edit-dialog").waitFor({ state: "hidden", timeout: 5000 }).catch(() => {
    throw new Error(`Synthetic edit did not close: ${editAlerts.join(" | ")}`);
  });

  await page.setViewportSize({ width: 390, height: 800 });
  assert.equal(await page.locator("#db-search").isVisible(), true);
  await page.setViewportSize({ width: 320, height: 800 });
  assert.equal(await page.locator("#db-search-clear").isVisible(), true);
  assert.deepEqual(pageErrors, []);
  console.log(JSON.stringify({ search: "ok", focus: "ok", analysisPosts, pageErrors: 0 }));
} finally {
  await browser.close();
}
