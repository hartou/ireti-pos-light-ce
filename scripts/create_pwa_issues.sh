#!/usr/bin/env bash
set -euo pipefail

# Create GitHub issues for PWA user stories using IDs as exact titles.
# Usage: ./scripts/create_pwa_issues.sh <owner/repo>

REPO="${1:-}"
if [[ -z "${REPO}" ]]; then
  echo "Usage: $0 <owner/repo>" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) not found. Install from https://cli.github.com/" >&2
  exit 1
fi

if ! gh auth status -h github.com >/dev/null 2>&1; then
  echo "Please authenticate: gh auth login" >&2
  exit 1
fi
if ! gh repo view "${REPO}" >/dev/null 2>&1; then
  echo "Repo not accessible: ${REPO}" >&2
  exit 1
fi

echo "Using repo: ${REPO}" >&2

ensure_label() {
  local name="$1"; shift
  local color="$1"; shift
  local desc="$1"; shift
  if ! gh label list -R "${REPO}" --json name -q '.[].name' | grep -qx "${name}"; then
    gh label create "${name}" --color "${color}" --description "${desc}" -R "${REPO}" || true
  fi
}

ensure_label PWA 0fbf00 "PWA transformation tasks"
ensure_label frontend 1d76db "Frontend/UI"

issue_exists() {
  local id="$1"
  gh issue list -R "${REPO}" --state all --search "in:title ${id}" --json title -q '.[].title' | grep -qx "${id}"
}

create_issue() {
  local id="$1"; shift
  local area="$1"; shift
  local path="$1"; shift
  local persona="$1"; shift
  local userstory="$1"; shift
  local -a acceptance=("$@")

  if issue_exists "${id}"; then
    echo "Skipping existing issue: ${id}" >&2
    return 0
  fi

  local body
  body=$(cat <<EOF
Area: ${area}
Path/Component: ${path}
Persona: ${persona}

User story
- ${userstory}

Acceptance criteria
$(for line in "${acceptance[@]}"; do echo "- ${line}"; done)

Status
- Pending

References
- docs/PWA_USER_STORIES.md
EOF
)

  gh issue create -R "${REPO}" \
    -t "${id}" \
    -b "${body}" \
    -l PWA -l frontend
}

create_issue PWA-001 Manifest onlineretailpos/static/manifest.webmanifest "Operator" \
  "Install the POS as an app from the browser" \
  "Manifest with name/short_name/start_url/display=standalone/theme/background" \
  "App icons (192/512) referenced and present" \
  "Linked from base template <link rel=\"manifest\">"

create_issue PWA-002 "Service Worker (shell)" onlineretailpos/static/js/sw.js "Operator" \
  "Use POS offline for shell navigation" \
  "Service worker registers from base template" \
  "Precache app shell (core HTML/CSS/JS, logo)" \
  "Offline fallback page works" \
  "Versioned cache and clean-up"

create_issue PWA-003 "Install UX" "Templates / small JS" "Operator" \
  "See Install app prompt/button" \
  "Handle beforeinstallprompt and show install button" \
  "Install success/cancel tracked (optional)" \
  "Works on Chrome desktop and Android"

create_issue PWA-004 "Static assets caching" ServiceWorker "Operator" \
  "Fast loads with cached CSS/JS/img" \
  "Cache-first for hashed static assets" \
  "Respect cache-busting via file hashes" \
  "Fallback to network on miss"

create_issue PWA-005 "Runtime API caching (read-only)" ServiceWorker "Operator" \
  "Read lists/dashboards even with flaky network" \
  "Stale-while-revalidate for GET endpoints (safe data)" \
  "No caching for auth or POST/PUT/DELETE" \
  "Proper cache partitioning and TTLs"

create_issue PWA-006 "Offline cart & queue" IndexedDB+SW "Cashier" \
  "Continue ringing items offline and sync later" \
  "Cart stored in IndexedDB" \
  "Background Sync used when available; manual retry fallback" \
  "Conflict-safe server sync logic"

create_issue PWA-007 "Network status UI" BaseUI "Cashier" \
  "Know when I’m offline and what’s disabled" \
  "Online/offline indicator visible" \
  "Disable payment/receipt actions while offline" \
  "Tooltip/explanation provided"

create_issue PWA-008 "Receipt printing (LAN)" DjangoEndpoint "Cashier" \
  "Print to LAN thermal printer reliably" \
  "Django endpoint sends ESC/POS to configured printer IP" \
  "Settings UI to store printer IP and test print" \
  "PWA calls endpoint and shows success/error"

create_issue PWA-009 "Camera barcode scanner" Register+AddInventory "Cashier" \
  "Scan with device camera if no scanner" \
  "Integrate zxing-js/browser" \
  "Toggle in UI + permission flow" \
  "Scanned code fills input; fallback to manual entry"

create_issue PWA-010 "Payment terminal (phase 1)" Config+TenderFlow "Cashier" \
  "Take card payments via supported terminal" \
  "Mode A: Standalone terminal (amount keyed) and POS records tender ref; OR" \
  "Mode B: Stripe Terminal Web SDK w/ WisePOS E (HTTPS, region supported)" \
  "Errors surfaced; clear reconciliation path"

create_issue PWA-011 "App settings UI" SettingsPage "Manager" \
  "Configure printer/payment/language" \
  "UI to set printer IP, payment mode, and defaults" \
  "Persist per store/user; validation and test actions"

create_issue PWA-012 "iOS PWA basics" Meta+Icons "Operator" \
  "Install/use on iOS within limits" \
  "Apple touch icons, status-bar style, splash meta" \
  "Test install, launch, basic offline" \
  "Document limitations (no Background Sync/WebUSB)"

create_issue PWA-013 "Kiosk readiness (Android)" Docs+Config "Operator" \
  "Run in kiosk-like mode on Android" \
  "Document TWA wrap and kiosk setup" \
  "Verify deep link/start_url and display correctness"

create_issue PWA-014 "Security headers" DjangoSettings "Admin" \
  "Safe-by-default PWA headers" \
  "CSP allows SW and required origins (self, Stripe if used)" \
  "Service-Worker-Allowed scope as needed" \
  "Strict-Transport-Security in prod"

create_issue PWA-015 "Lighthouse PWA audit" CI+Manual "Admin" \
  "Meet PWA best practices" \
  "Lighthouse PWA audits ≥ 90 (installable, offline, HTTPS)" \
  "Document any accepted exceptions"

create_issue PWA-016 "SW update flow" SW+UI "Operator" \
  "Get notified when a new version is ready" \
  "Detect new SW; show Update available prompt" \
  "Click to skipWaiting/clients.claim and reload"

create_issue PWA-017 "Offline/error pages" Templates "Operator" \
  "Friendly fallbacks when offline/errors" \
  "Precache /offline page" \
  "Graceful 500/timeout UI with retry"

create_issue PWA-018 "Push notifications (optional)" SW+Backend "Manager" \
  "Receive optional alerts" \
  "Topic design and consent UI" \
  "VAPID keys setup (if using Web Push)" \
  "Can be marked Deferred initially"
