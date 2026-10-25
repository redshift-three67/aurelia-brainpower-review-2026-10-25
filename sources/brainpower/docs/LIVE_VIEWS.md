# Local Chrome live views

Live views are optional. They launch a **visible, separately owned Chrome window**, then capture its viewport and a bounded sample of JavaScript exceptions/browser log messages. They do not attach to an existing browser, copy the user's normal Chrome profile, start project servers, submit forms or run model-generated browser commands.

## Configuration and interface

The production module uses Python's standard library and an installed Chrome/Chromium executable. There are no Playwright, Node or pip dependencies. `chrome_path` can name an explicit executable; otherwise standard Windows Chrome installation locations and Chrome/Chromium on PATH are checked.

Configure exact allowed targets:

```json
{
  "data_dir": "runtime",
  "live_views": {
    "governor": {"url": "http://127.0.0.1:8787/"}
  }
}
```

An empty mapping enables no targets. The caller must pass the exact configured URL, including its path and trailing slash. URLs require HTTP, `localhost`, `127.0.0.1` or `::1`, and an explicit numeric port. Embedded credentials, fragments, control characters and port 3000 are rejected. Each configured Live View needs its own port, regardless of loopback hostname spelling; project views cannot use the Governor or runtime-probe port. The service configuration layer decides which project IDs may be registered. An optional `expected_openapi_title` compares the local `/openapi.json` title before Chrome is launched; a missing or different title blocks the view. This guards against accidental service mixups, not malicious impersonation.

## Current module targets

The local operator configuration lists Governor (`127.0.0.1:8787/`), RadiWorks (`127.0.0.1:8091/`), Radi144 (`127.0.0.1:8090/user_workflow.html`) and Morphic (`127.0.0.1:8000/static/index.html`). RadiWorks exposes an API preview on its configured port; loading that address verifies reachability and the browser response, **not** a complete module user interface. Aurelia and Modul_Templates have no browser target configured.

The current Radi144 `main.py` defaults to loopback port 8090; its README still mentions 8000 and is stale for this checkout. RadiWorks `run.py` also defaults to 8090, so **start RadiWorks explicitly on 8091** from its engine directory with its usual Python environment and `run.py --port 8091`. Morphic `web_server.py` defaults to loopback port 8000. The Governor neither starts nor stops these project services. The three configured OpenAPI titles are checked before a Live View opens; a title mismatch or unavailable target blocks the view. Changes to `config.local.json` take effect on the next controlled Governor start; an already running instance keeps its loaded target list.

A Live View is a local pre-release test aid. A successful capture does not synchronize a model review, accept a matrix step, or authorize Aurelia integration.

`LiveViews(config)` provides:

- `start(project_id, url)` → `{id, project_id, url, pid, debug_port, status}`; status is `running` after debugger discovery. IDs are 32 hexadecimal characters.
- `snapshot(id)` → those fields plus absolute `screenshot`, `captured_at`, `exceptions`, `logs`, and `log_scope`.
- `stop(id)` → final view state; stops only that owned browser.
- `state()` → known session states.
- `close()` → attempts to stop every owned session, even if one fails.

The root service exposes these through its authenticated action/job and screenshot routes. It must keep session IDs as opaque lookup keys and serve images only from its validated live directory. The module accepts no arbitrary CDP commands or JavaScript expressions from callers.

## Ownership and network restrictions

Each start creates a fresh `<data_dir>/live/<id>` profile and launches Chrome with `--remote-debugging-port=0`, using Chrome's own `DevToolsActivePort` record to discover the random loopback debugger port. No fixed existing debugger port is reused. `Browser.close` is attempted through that owned debugger; fallback termination acts only on the saved `Popen` object. There is no process-name kill or global Chrome shutdown.

A local HTTP preflight rejects redirects and ignores system proxy settings. Chrome's outgoing HTTP/WebSocket traffic uses a reserved, non-listening loopback proxy, with direct bypass limited to loopback hosts on the selected target's port. Wildcard DNS resolution is disabled with explicit numeric and named loopback exclusions; background networking, QUIC, extensions, sync and several background services are disabled. This blocks external page resources rather than silently allowing their network requests. Apps depending on external fonts, APIs or assets may display missing resources. These are Chrome network settings, not an operating-system sandbox against a modified browser or administrator-enforced browser policy. The bypass syntax follows Chromium's [proxy documentation](https://chromium.googlesource.com/chromium/src/+/HEAD/net/docs/proxy.md).

Before capture, the helper checks the real document URL, document readiness and nonzero viewport dimensions using one fixed read-only expression. A browser error page or navigation outside the selected origin is rejected, even if the target listing still contains the original requested URL. A page still rendering can be retried. The viewport capture uses the documented [Page.captureScreenshot](https://chromedevtools.github.io/devtools-protocol/tot/Page/#method-captureScreenshot) CDP method.

## Bounds and retention

At most three owned Chrome sessions run simultaneously. Startup waits up to ten seconds for debugger discovery after bounded endpoint preflight. Capture has a twelve-second CDP deadline plus a bounded target-list request; readiness receives up to four seconds within that deadline. There is no indefinite retry. Closing uses short bounded waits before terminating its owned process.

The stdlib WebSocket client validates the handshake, masks client frames, handles fragmented text and ping/pong, rejects unsupported frames and enforces an 8 MiB message bound. HTTP reads, target lists and discovery files also have size limits. At most 100 exception/log entries are retained per capture, with each message truncated to 2,000 characters. The latest valid PNG atomically replaces `<data_dir>/live/<id>/screenshot.png`.

Logs cover events observed after enabling the capture domains, including any entries Chrome emits on enabling them. They are **not a complete console history** or continuous error monitoring. Snapshots contain whatever the selected local page displays. Profiles and screenshots remain locally after stopping for inspection; closing does not recursively delete them. Session process ownership is in memory: an interrupted service does not later attach to or kill an old browser by PID. Such a window can be closed manually.

## Verification

Unit tests cover URL rejection, exact target matching, isolated profiles, owned-process shutdown, startup timeout, capture-origin checks, PNG writes, protocol deadlines, masking, fragmentation, ping/pong, handshake validation, message bounds and bounded log history.

A real local Governor capture on 2026-09-12 reproduced and fixed two startup issues: debugger discovery can precede a renderable viewport, and a wildcard DNS rule needs explicit numeric loopback exclusions. The corrected immediate start→capture flow produced a visually verified Governor screenshot, not a browser error page. Evidence is in `artifacts/live_view_verification.json` and the screenshot path recorded there. That test-owned Chrome window was closed afterward; the existing Governor server was not restarted. One local HTTP 404 was recorded, with no captured JavaScript exception.
