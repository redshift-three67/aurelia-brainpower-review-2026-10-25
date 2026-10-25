import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "node:test";

let subject = {};
try {
  const source = await readFile(new URL("./views/gv_observations.js", import.meta.url), "utf8");
  const encoded = Buffer.from(source).toString("base64");
  subject = await import(`data:text/javascript;base64,${encoded}`);
} catch (_) {
  // The red phase expects missing production helpers to fail the assertions below.
}

test("pairs GV controls by broadcast ID even when signatures repeat", () => {
  const rows = subject.pairGvControls({
    eligible: [
      { broadcastId: "broadcast-a", signature: "same rate", observationBinding: { sessionId: "session-a" } },
      { broadcastId: "broadcast-b", signature: "same rate", observationBinding: { sessionId: "session-b" } },
    ],
    controls: [
      { broadcastId: "broadcast-a", enabled: true, binding: { scope: "case" } },
      { broadcastId: "broadcast-b", enabled: false, binding: { scope: "session" } },
      { broadcastId: "direct-only", enabled: true, binding: { scope: "direct" } },
    ],
  });

  assert.deepEqual(rows.map((row) => row.broadcastId), ["broadcast-a", "broadcast-b", "direct-only"]);
  assert.equal(rows[0].binding.sessionId, "session-a");
  assert.equal(rows[1].binding.sessionId, "session-b");
  assert.equal(rows[2].eligible, false);
});

test("derives direction labels and the strong trend threshold from delta", () => {
  assert.deepEqual(subject.trendPresentation({ direction: "up", delta: 199 }), {
    label: "Steigend", tone: "up", delta: 199,
  });
  assert.deepEqual(subject.trendPresentation({ direction: "up", delta: 200 }), {
    label: "Stark steigend", tone: "up", delta: 200,
  });
  assert.deepEqual(subject.trendPresentation({ direction: "down", delta: -200 }), {
    label: "Stark sinkend", tone: "down", delta: -200,
  });
  assert.deepEqual(subject.trendPresentation({ direction: "baseline", delta: null }), {
    label: "Basis", tone: "neutral", delta: null,
  });
});