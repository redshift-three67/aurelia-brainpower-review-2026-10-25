# Dependencies Audit Report: package.json & Workspaces

- **Date:** 2026-09-09
- **Scope:** Root `package.json` and monorepo workspaces (`apps/*`, `ui-tui`, `ui-tui/packages/*`, `web`, `tests-js`)
- **Execution Mechanism:** Claude Code CLI (`claude -p`), `npm audit`, workspace manifest analysis

---

## 1. Executive Summary

- **Overall Risk:** **High**
- **Vulnerabilities Found:** **11 total** (9 High, 2 Moderate, 0 Critical)
- **Primary Vulnerability Classes:**
  - Unvalidated symlink path traversal / arbitrary file overwrite (`extract-zip`)
  - Renderer isolation & ProtocolResponse cache reuse popup bypass (`electron`)
  - Merge-key CPU denial of service (`js-yaml`)
  - Arbitrary file read in test mock redirection (`vitest`)

---

## 2. Security Vulnerabilities Detail

| Severity | Package | Advisory / CVE | Impact / Path | Fix / Action |
|---|---|---|---|---|
| **High** | `electron@40.10.2` | `GHSA-9f4c-93c8-jc8g`<br>`GHSA-r4w5-6pfg-jxp5` | Renderer sandbox breakout & session leak in `apps/desktop`. | Upgrade to `40.10.6+`. |
| **High** | `extract-zip<=2.0.1` | `GHSA-jmr9-qjv8-65gv`<br>`GHSA-7pqw-9j4j-h8q3` | Symlink path traversal via electron unpacker. | Resolved via upgrading `electron` to `40.10.6+`. |
| **High** | `js-yaml@4.0.0 - 4.3.1` | `GHSA-2883-xcg3-v3hh` | Merge key CPU denial of service. | Update root override `js-yaml@^4` to `^4.3.2`. |
| **High** | `electron-builder@26.15.3 - 26.15.7` | Via `app-builder-lib`, `builder-util` (transitive `js-yaml`) | Packaging & build-time exposure. | Upgrade to `electron-builder@26.16.1+`. |
| **Moderate** | `vitest@4.1.10`<br>`@vitest/mocker` | `GHSA-82fw-gwwq-j7x9` | Arbitrary file read during test execution. | Upgrade `vitest` to `4.1.11+`. |

---

## 3. Override Inconsistencies & Root Flaws

1. **Vulnerable `js-yaml` Override Pin:**
   - Root `package.json` overrides currently force `"js-yaml@^4": "4.3.1"`, which actively enforces the vulnerable version (`GHSA-2883-xcg3-v3hh` affects `<=4.3.1`).
   - **Remedy:** Bump to `"js-yaml@^4": "^4.3.2"`.
2. **`allowScripts` Desynchronization:**
   - Root `allowScripts` allows `"electron@40.10.2": true`. Upgrading `electron` without matching `allowScripts` will block native installation scripts.
3. **Workspace Version Drift:**
   - `protobufjs`: Root pins `^8.7.1`, photon sidecar uses `8.7.1`, while `scripts/whatsapp-bridge` uses `^7.5.5`.
   - `nanoid`: Root uses `3.3.18`, while `website` declares `3.3.17`.

---

## 4. Remediation Plan

1. **Root `package.json`:**
   - Update `overrides["js-yaml@^4"]` to `"^4.3.2"`.
   - Update `allowScripts["electron@40.10.2"]` to `"electron@40.10.6": true`.
   - Set explicit lower bound in `engines.npm`: `">=10.8.0 <11.10.0 || >=11.17.0"`.
2. **Workspaces:**
   - `apps/desktop/package.json`: bump `electron` to `^40.10.6`, `electron-builder` to `^26.16.1`.
   - `tests-js`, `desktop`, `ui-tui`, `web`: bump `vitest` to `^4.1.11`.
   - Deduplicate `nanoid` in `website` to `3.3.18`.
3. **Verification:**
   - Re-run `npm install` and `npm audit` to confirm clean report.
