#!/usr/bin/env bash
set -euo pipefail

# Create GitHub issues for Broken Links user stories using IDs as exact titles.
# Usage: ./scripts/create_broken_link_issues.sh <owner/repo>

REPO="${1:-}"
if [[ -z "${REPO}" ]]; then
  echo "Usage: $0 <owner/repo>" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) not found. Install from https://cli.github.com/" >&2
  exit 1
fi

# Verify auth and repo access
if ! gh auth status -h github.com >/dev/null 2>&1; then
  echo "Please authenticate: gh auth login" >&2
  exit 1
fi
if ! gh repo view "${REPO}" >/dev/null 2>&1; then
  echo "Repo not accessible: ${REPO}" >&2
  exit 1
fi

echo "Using repo: ${REPO}" >&2

# Ensure labels exist (ignore errors if they already exist)
ensure_label() {
  local name="$1"; shift
  local color="$1"; shift
  local desc="$1"; shift
  if ! gh label list -R "${REPO}" --json name -q '.[].name' | grep -qx "${name}"; then
    gh label create "${name}" --color "${color}" --description "${desc}" -R "${REPO}" || true
  fi
}

ensure_label bug d73a4a "Bug or defect"
ensure_label QA e4e669 "Quality assurance tasks"
ensure_label routing 5319e7 "URL routing / navigation"

issue_exists() {
  local id="$1"
  gh issue list -R "${REPO}" --state all --search "in:title ${id}" --json title -q '.[].title' | grep -qx "${id}"
}

create_issue() {
  local id="$1"; shift
  local url="$1"; shift
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
URL: ${url}
Path/Component: ${path}
Persona: ${persona}

User story
- ${userstory}

Acceptance criteria
$(for line in "${acceptance[@]}"; do echo "- ${line}"; done)

Status
- Pending

References
- docs/BROKEN_LINKS_USER_STORIES.md
- bugs.md
EOF
)

  gh issue create -R "${REPO}" \
    -t "${id}" \
    -b "${body}" \
    -l bug -l QA -l routing
}

create_issue BL-001 "/dashboard_sales/" "onlineretailpos/urls.py ➜ views.dashboard_sales" "Manager" \
  "Access Sales Dashboard without 404s" \
  "URL resolves and renders for authenticated user (200)" \
  "Unauthenticated user gets 302 to login" \
  "Any nav/menu link points to this path" \
  "Add a smoke test for both cases"

create_issue BL-002 "/dashboard_department/" "onlineretailpos/urls.py ➜ views.dashboard_department" "Manager" \
  "Access Department Dashboard reliably" \
  "URL resolves for authenticated user (200)" \
  "Unauthenticated: 302 to login" \
  "Menu link points to this path" \
  "Smoke test added"

create_issue BL-003 "/dashboard_products/" "onlineretailpos/urls.py ➜ views.dashboard_products" "Manager" \
  "Access Products Dashboard reliably" \
  "URL resolves for authenticated user (200)" \
  "Unauthenticated: 302 to login" \
  "Menu link points to this path" \
  "Smoke test added"

create_issue BL-004 "/transaction/" "onlineretailpos/urls.py ➜ transaction.views.transactionView" "Cashier/Manager" \
  "Open Transactions list without errors" \
  "URL resolves for authenticated user (200)" \
  "Unauthenticated: 302 to login" \
  "If query params required, sensible defaults exist" \
  "Smoke test added"

create_issue BL-005 "/register/product_lookup/" "onlineretailpos/urls.py ➜ inventory.views.product_lookup" "Cashier" \
  "Look up products from Register" \
  "URL resolves for authenticated user (200)" \
  "Unauthenticated: 302 to login" \
  "Register menu/button links here" \
  "Smoke test added"

create_issue BL-006 "/inventory/" "onlineretailpos/urls.py ➜ inventory.views.inventoryAdd" "Inventory Clerk" \
  "Open Add Inventory page" \
  "URL resolves for authenticated user (200)" \
  "Unauthenticated: 302 to login" \
  "Sidebar/nav link points here" \
  "Smoke test added"

create_issue BL-007 "/staff_portal/" "Django Admin (root)" "Admin" \
  "Reach Admin portal login/index" \
  "URL resolves to Admin (200 when logged in, 302 to login when not)" \
  "Admin CSS/JS load without errors" \
  "Smoke test added"

create_issue BL-008 "/staff_portal/auth/group/" "Django Admin ➜ Auth Group changelist" "Admin" \
  "Manage Groups in Admin" \
  "URL resolves for superuser (200)" \
  "Non-admin users redirected/forbidden as expected" \
  "Link from Admin index works" \
  "Smoke test added (admin case)"

create_issue BL-009 "/retail_display/" "onlineretailpos/urls.py ➜ views.retail_display" "Cashier/Customer" \
  "Clarify and wire up Customer Display page" \
  "Confirm intended usage and params" \
  "URL resolves (200) with defaults" \
  "Register can open this screen (if applicable)" \
  "Basic smoke test added"
