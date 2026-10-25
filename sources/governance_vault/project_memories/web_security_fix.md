# Web Security Fix

Date: 2026-09-10

## Finding

`web/package.json` already required `vitest` `^4.1.11`, but the shared root lockfile still resolved `vitest` and `@vitest/mocker` to `4.1.10`. The stale resolution left the workspace exposed to GHSA-82fw-gwwq-j7x9 (arbitrary file read in test mock redirection).

The remediation also exposed two current high-severity findings in the shared lockfile:

- `electron@40.10.6` was affected by GHSA-9f4c-93c8-jc8g; its fixed release is `41.10.3`.
- `js-yaml@4.3.1` was affected by GHSA-2883-xcg3-v3hh; its fixed release is `4.3.2`.

## Changes

- Updated `apps/desktop/package.json`: `vitest` `4.1.10` -> `4.1.11`, allowing the web workspace's declared safe Vitest version to resolve from the shared lockfile.
- Updated `apps/desktop/package.json`: `electron` `40.10.6` -> `41.10.3`.
- Corrected the root `js-yaml` override to apply globally and resolved it to `4.3.2`.
- Updated the Electron install-script allowlist for `electron@41.10.3`.
- Regenerated `package-lock.json` with the targeted resolutions.

## Verification

- `npm audit --workspace web`: 0 vulnerabilities.
- `npm run --workspace web check`: passed — TypeScript, 41 Vitest files / 298 tests, and ESLint (27 pre-existing warnings; no errors).
- `npm run --workspace web build`: passed.
- Confirmed installed versions: `vitest` and `@vitest/mocker` `4.1.11`; `electron` `41.10.3`; `js-yaml` `4.3.2`.
