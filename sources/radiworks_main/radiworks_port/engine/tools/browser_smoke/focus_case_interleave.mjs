import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const base = process.env.RADIOWORKS_TEST_URL || "http://127.0.0.1:8104/";
const suffix = randomUUID().slice(0, 8);
const nameA = `Synthetic Interleave A ${suffix}`;
const nameB = `Synthetic Interleave B ${suffix}`;
const browser = await chromium.launch({ channel: "chrome", headless: false });
const page = await browser.newPage();
let switched = false;

try {
  assert.equal((await page.request.post(new URL("/cases", base).toString(), {
    data: { name: nameA, description: "A baseline", focus: "A" },
  })).status(), 200);
  await page.goto(base, { waitUntil: "domcontentloaded" });
  await page.getByRole("tab", { name: "Fälle" }).click();
  const rowA = page.locator("#case-list .case-row").filter({ hasText: nameA });
  await rowA.locator("button").first().click();
  await page.waitForFunction(() => document.querySelector("#case-load-status")?.textContent.includes("geladen"));
  await page.locator("#case-name").fill(nameA);

  await page.route("**/cases/current/metadata", async (route) => {
    if (switched) return route.continue();
    const savedA = await route.fetch();
    assert.equal(savedA.status(), 200);
    const createdB = await page.request.post(new URL("/cases", base).toString(), {
      data: { name: nameB, description: "B baseline", focus: "B" },
    });
    assert.equal(createdB.status(), 200);
    switched = true;
    await route.fulfill({ response: savedA });
  });

  await page.locator("#case-desc").fill("A erster Speicherwert");
  await page.locator("#case-save-btn").click();
  await page.waitForFunction(() => document.querySelector("#case-save-status")?.textContent.includes("Fall gespeichert"),
    null, { timeout: 7000 }).catch(async () => {
    throw new Error(`First save status: ${await page.locator("#case-save-status").innerText()}; switched=${switched}`);
  });
  assert.equal(switched, true);

  await page.locator("#case-desc").fill("A zweiter Speicherwert");
  await page.locator("#case-save-btn").click();
  await page.waitForFunction(() => /Fall (gespeichert|konnte nicht gespeichert)/.test(
    document.querySelector("#case-save-status")?.textContent || ""));
  const status = await page.locator("#case-save-status").innerText();
  assert.match(status, /Fall konnte nicht gespeichert werden: Aktiver Fall hat sich geändert/);
  const current = await (await page.request.get(new URL("/cases/current", base).toString())).json();
  assert.equal(current.name, nameB);
  assert.equal(current.description, "B baseline");
  console.log("PASS interleaved case switch cannot retarget subsequent save");
} finally {
  await browser.close();
}
