# PWA user stories and acceptance criteria (August 10, 2025)

This document tracks Progressive Web App (PWA) transformation work in a compact table. Each row includes a user story and acceptance criteria to mark the task “PWA-complete”.

Notes
- Target platforms: Chrome/Edge (Windows), Chrome (Android tablets), ChromeOS; basic support for Safari (iOS/iPadOS) with known limitations.
- Status values: use `Pending` (default), `Completed`, or `Deferred` (optional items like push).
- Use HTTPS, proper caching strategies, and don’t cache sensitive/auth content.
- Create one GitHub issue per row using the ID as the exact issue title.

---

| ID | Area | Path/Component | Persona | User story | Acceptance criteria (condensed) | Status |
|---|---|---|---|---|---|---|
| [PWA-001](./PWA_MANUAL_TESTING.md#pwa-001-manifest) | Manifest | `onlineretailpos/static/manifest.webmanifest` | Operator | Install the POS as an app from the browser | - Manifest with name/short_name/start_url/display=standalone/theme/background<br>- App icons (192/512) referenced and present<br>- Linked from base template `<link rel="manifest">` | Completed |
| [PWA-002](./PWA_MANUAL_TESTING.md#pwa-002-service-worker-registers) | Service Worker (shell) | `onlineretailpos/static/js/sw.js` | Operator | Use POS offline for shell navigation | - Service worker registers from base template<br>- Precache app shell (core HTML/CSS/JS, logo)<br>- Offline fallback page works<br>- Versioned cache and clean-up | Completed |
| [PWA-003](./PWA_MANUAL_TESTING.md#pwa-003-install-prompt-ux) | Install UX | Templates / small JS | Operator | See “Install app” prompt/button | - Handle `beforeinstallprompt` and show install button<br>- Install success/cancel tracked (optional)<br>- Works on Chrome desktop and Android | Completed |
| PWA-004 | Static assets caching | Service worker | Operator | Fast loads with cached CSS/JS/img | - Cache-first for hashed static assets<br>- Respect cache-busting via file hashes<br>- Fallback to network on miss | Completed |
| PWA-005 | Runtime API caching (read-only) | Service worker | Operator | Read lists/dashboards even with flaky network | - Stale-while-revalidate for GET endpoints (safe data)<br>- No caching for auth or POST/PUT/DELETE<br>- Proper cache partitioning and TTLs | Completed |
| PWA-006 | Offline cart & queue | IndexedDB + SW | Cashier | Continue ringing items offline and sync later | - Cart stored in IndexedDB<br>- Background Sync used when available; manual retry fallback<br>- Conflict-safe server sync logic | Completed |
| PWA-007 | Network status UI | Base UI | Cashier | Know when I’m offline and what’s disabled | - Online/offline indicator visible<br>- Disable payment/receipt actions while offline<br>- Tooltip/explanation provided | Completed |
| PWA-008 | Receipt printing (LAN) | Django endpoint + settings | Cashier | Print to LAN thermal printer reliably | - Django endpoint sends ESC/POS to configured printer IP (python-escpos or socket)<br>- Settings UI to store printer IP and test print<br>- PWA calls endpoint and shows success/error | Completed |
| PWA-009 | Camera barcode scanner | Register/Add Inventory | Cashier | Scan with device camera if no scanner | - Integrate zxing-js/browser<br>- Toggle in UI + permission flow<br>- Scanned code fills input; fallback to manual entry | Completed |
| PWA-010 | Payment terminal (phase 1) | Config + tender flow | Cashier | Take card payments via supported terminal | - Mode A: Standalone terminal (amount keyed) and POS records tender ref; OR<br>- Mode B: Stripe Terminal Web SDK w/ WisePOS E (HTTPS, region supported)<br>- Errors surfaced; clear reconciliation path | Completed |
| PWA-011 | App settings UI | Settings page | Manager | Configure printer/payment/language | - UI to set printer IP, payment mode, and defaults<br>- Persist per store/user; validation and test actions | Completed |
| PWA-012 | iOS PWA basics | Meta tags / icons | Operator | Install/use on iOS within limits | - Apple touch icons, status-bar style, splash meta<br>- Test install, launch, basic offline<br>- Document limitations (no Background Sync/WebUSB) | Completed |
| PWA-013 | Kiosk readiness (Android) | Docs + Config | Operator | Run in kiosk-like mode on Android | - Document TWA wrap and kiosk setup<br>- Verify deep link/start_url and display correctness | Completed |
| PWA-014 | Security headers | Django settings | Admin | Safe-by-default PWA headers | - CSP allows SW and required origins (self, Stripe if used)<br>- Service-Worker-Allowed scope as needed<br>- Strict-Transport-Security in prod | Completed |
| PWA-015 | Lighthouse PWA audit | CI/manual | Admin | Meet PWA best practices | - Lighthouse PWA audits ≥ 90 (installable, offline, HTTPS)<br>- Document any accepted exceptions | Completed |
| PWA-016 | SW update flow | SW + UI | Operator | Get notified when a new version is ready | - Detect new SW; show ‘Update available’ prompt<br>- Click to skipWaiting/clients.claim and reload | Completed |
| [PWA-017](./PWA_MANUAL_TESTING.md#pwa-017-offline-fallback) | Offline/error pages | Templates | Operator | Friendly fallbacks when offline/errors | - Precache `/offline` page<br>- Graceful 500/timeout UI with retry | Completed |
| PWA-018 | Push notifications (optional) | SW + backend | Manager | Receive optional alerts | - Topic design and consent UI<br>- VAPID keys setup (if using Web Push)<br>- Can be marked Deferred initially | Deferred |

---

### cross-cutting acceptance criteria (apply to all PWA tasks)
- App is installable (manifest + SW + served over HTTPS); no mixed content.
- No sensitive/authenticated responses cached; only safe GET data is cached and governed by TTL.
- Works on Chrome desktop and Android tablets; basic verification on Safari.
- Clear rollback path: unregister SW and clear caches without breaking the app.

### appendix: workflow checklist per task
1) Implement feature (manifest/SW/UX)
2) Add tests/manual steps and update docs
3) Verify on Chrome desktop + Android tablet
4) Run Lighthouse PWA audits and address gaps
5) Set Status to `Completed` when acceptance criteria are met

### quick-create GitHub issues
Use the helper script to open one issue per PWA story with the ID as the exact title.

Requirements: GitHub CLI (gh) authenticated with access to the repo.

```bash
bash scripts/create_pwa_issues.sh hartou/ireti-pos-light
```
