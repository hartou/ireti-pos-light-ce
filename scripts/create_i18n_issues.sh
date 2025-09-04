#!/usr/bin/env bash
set -euo pipefail

# Create GitHub issues for i18n user stories using IDs as exact titles.
# Usage: ./scripts/create_i18n_issues.sh <owner/repo>

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

ensure_label i18n 5319e7 "Internationalization tasks"
ensure_label translation 0e8a16 "Translation work"
ensure_label template 1d76db "Template-related"

issue_exists() {
  local id="$1"
  gh issue list -R "${REPO}" --state all --search "in:title ${id}" --json title -q '.[].title' | grep -qx "${id}"
}

create_issue() {
  local id="$1"; shift
  local template="$1"; shift
  local path="$1"; shift
  local persona="$1"; shift
  local userstory="$1"; shift
  local -a acceptance=("$@")

  if issue_exists "${id}"; then
    echo "Skipping existing issue: ${id}" >&2
    return 0
  fi

  # Build body
  local body
  body=$(cat <<EOF
Template: ${template}
Path: ${path}
Persona: ${persona}

User story
- ${userstory}

Acceptance criteria
$(for line in "${acceptance[@]}"; do echo "- ${line}"; done)

Status
- Pending

References
- docs/I18N_USER_STORIES.md
EOF
)

  gh issue create -R "${REPO}" \
    -t "${id}" \
    -b "${body}" \
    -l i18n -l translation -l template
}

# Create issues from the canonical list (IDs must match docs/I18N_USER_STORIES.md)
create_issue I18N-001 addInventory.html \
  onlineretailpos/templates/addInventory.html \
  "Inventory Clerk" \
  "See Add Inventory in my language to add/update items confidently" \
  "i18n loaded; headings/buttons/labels/placeholders translated" \
  "Client-side prompts/alerts localized" \
  "Field labels via template or form _()" \
  "fr/es catalogs updated; no English leakage"

create_issue I18N-002 productLookup.html \
  onlineretailpos/templates/productLookup.html \
  "Cashier" \
  "Look up product prices in my language to assist customers" \
  "Title/filters/buttons/table headers translated" \
  "Empty-state messages localized" \
  "JS prompts/messages localized"

create_issue I18N-003 productsDashboard.html \
  onlineretailpos/templates/productsDashboard.html \
  "Manager" \
  "View product KPIs in my language" \
  "Headings/tables/buttons localized" \
  "Chart axis/legends/tooltips localized (labels via _() from views)"

create_issue I18N-004 salesDashboard.html \
  onlineretailpos/templates/salesDashboard.html \
  "Manager" \
  "Track sales and KPIs in my language" \
  "Cards/headings/filters localized" \
  "Chart titles/labels/tooltips localized (labels via _() from views)"

create_issue I18N-005 departmentDashboard.html \
  onlineretailpos/templates/departmentDashboard.html \
  "Manager" \
  "Analyze department performance in my language" \
  "Static labels/controls localized" \
  "Chart/legend strings localized (labels via _() from views)"

create_issue I18N-006 transactions.html \
  onlineretailpos/templates/transactions.html \
  "Cashier/Manager" \
  "View/filter transactions in my language for review" \
  "Page title/filters/table headers/actions localized" \
  "Empty-state and error messages localized"

create_issue I18N-007 reportsRegular.html \
  onlineretailpos/templates/reportsRegular.html \
  "Manager" \
  "Read standard reports in my language" \
  "Sections/filters/tables/export buttons localized" \
  "Totals/footers labels localized"

create_issue I18N-008 recallTransaction.html \
  onlineretailpos/templates/recallTransaction.html \
  "Cashier" \
  "Recall/suspend transactions in my language" \
  "Headings/instructions/buttons localized" \
  "Table headers/status messages localized"

create_issue I18N-009 endTransaction.html \
  onlineretailpos/templates/endTransaction.html \
  "Cashier" \
  "Complete checkout in my language to avoid mistakes" \
  "Payment buttons/instructions/dialogs localized" \
  "Validation and error prompts localized (template-side JS via {% trans %})"

create_issue I18N-010 receiptView.html \
  onlineretailpos/templates/receiptView.html \
  "Cashier/Customer" \
  "Display/print receipts with localized labels" \
  "Receipt headers/labels/footers localized" \
  "\"Thank you\", tax/subtotal/total/change labels localized"

create_issue I18N-011 retailDisplay.html \
  onlineretailpos/templates/retailDisplay.html \
  "Customer" \
  "Understand my purchase on the customer screen in my language" \
  "Visible labels/headings localized" \
  "Rotating/status messages localized"

create_issue I18N-012 registration/login.html \
  onlineretailpos/templates/registration/login.html \
  "Staff/Cashier" \
  "Log in using a localized form to reduce errors" \
  "Form title/placeholders/labels/submit button localized" \
  "Template-surfaced auth error messages localized"

create_issue I18N-013 registration/change_password.html \
  onlineretailpos/templates/registration/change_password.html \
  "Staff/Cashier" \
  "Change password using a localized form" \
  "Headings/instructions/buttons localized" \
  "Template success/error messages localized"

create_issue I18N-014 admin/base.html \
  onlineretailpos/templates/admin/base.html \
  "Staff/Admin" \
  "See customized admin base strings localized" \
  "Any custom template strings localized (Django admin core already localized upstream)"

create_issue I18N-015 "Data: product/department labels" \
  "inventory/models.py, onlineretailpos/admin.py" \
  "Manager/Cashier" \
  "See product and department names in my language across UI, receipts, and reports" \
  "Approach selected and implemented (per-language fields like name_fr/name_es or django-modeltranslation)" \
  "Admin/editor UI to manage localized names" \
  "UI uses localized label with fallback to base; search works on localized/base fields" \
  "Receipts/reports display localized names" \
  "Docs updated in TRANSLATION.md"

