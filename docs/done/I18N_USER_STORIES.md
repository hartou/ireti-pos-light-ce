# i18n user stories and acceptance criteria (August 10, 2025)

This document tracks internationalization work for each end-user template in a compact table. Each row includes a user story and acceptance criteria to mark the page “i18n-complete”.

Notes
- Target languages: English (base), French (fr), Spanish (es)
- Use `{% load i18n %}`, `{% trans %}`, `{% blocktrans %}` in templates; use `gettext_lazy` (`_()`) in Python
- After edits: update PO catalogs (fr/es) and compile (see docs/TRANSLATION.md)
- Create one GitHub issue per row using the ID as the exact issue title
- Status values: use `Pending` (default) or `Completed` when done. The CI will auto-close the matching issue when set to Completed.

---

| ID | Template | Path | Persona | User story | Acceptance criteria (condensed) | Status |
|---|---|---|---|---|---|---|
| I18N-001 | addInventory.html | `onlineretailpos/templates/addInventory.html` | Inventory Clerk | See Add Inventory in my language to add/update items confidently | - i18n loaded; headings/buttons/labels/placeholders translated<br>- Client-side prompts/alerts localized<br>- Field labels via template or form `_()`<br>- fr/es catalogs updated; no English leakage | Completed |
| I18N-002 | productLookup.html | `onlineretailpos/templates/productLookup.html` | Cashier | Look up product prices in my language to assist customers | - Title/filters/buttons/table headers translated<br>- Empty-state messages localized<br>- JS prompts/messages localized | Completed |
| I18N-003 | productsDashboard.html | `onlineretailpos/templates/productsDashboard.html` | Manager | View product KPIs in my language | - Headings/tables/buttons localized<br>- Chart axis/legends/tooltips localized (labels passed from views via `_()` when defined in Python) | Completed |
| I18N-004 | salesDashboard.html | `onlineretailpos/templates/salesDashboard.html` | Manager | Track sales and KPIs in my language | - Cards/headings/filters localized<br>- Chart titles/labels/tooltips localized (server-provided labels via `_()`) | Completed |
| I18N-005 | departmentDashboard.html | `onlineretailpos/templates/departmentDashboard.html` | Manager | Analyze department performance in my language | - Static labels/controls localized<br>- Chart/legend strings localized (via `_()` from views) | Completed |
| I18N-006 | transactions.html | `onlineretailpos/templates/transactions.html` | Cashier/Manager | View/filter transactions in my language for review | - Page title/filters/table headers/actions localized<br>- Empty-state and error messages localized | Completed |
| I18N-007 | reportsRegular.html | `onlineretailpos/templates/reportsRegular.html` | Manager | Read standard reports in my language | - Sections/filters/tables/export buttons localized<br>- Totals/footers labels localized | Completed |
| I18N-008 | recallTransaction.html | `onlineretailpos/templates/recallTransaction.html` | Cashier | Recall/suspend transactions in my language | - Headings/instructions/buttons localized<br>- Table headers/status messages localized | Completed |
| I18N-009 | endTransaction.html | `onlineretailpos/templates/endTransaction.html` | Cashier | Complete checkout in my language to avoid mistakes | - Payment buttons/instructions/dialogs localized<br>- Validation and error prompts localized (template-side JS via `{% trans %}`) | Completed |
| I18N-010 | receiptView.html | `onlineretailpos/templates/receiptView.html` | Cashier/Customer | Display/print receipts with localized labels | - Receipt headers/labels/footers localized<br>- “Thank you”, tax/subtotal/total/change labels localized | Completed |
| I18N-011 | retailDisplay.html | `onlineretailpos/templates/retailDisplay.html` | Customer | Understand my purchase on the customer screen in my language | - Visible labels/headings localized<br>- Rotating/status messages localized | Completed |
| I18N-012 | registration/login.html | `onlineretailpos/templates/registration/login.html` | Staff/Cashier | Log in using a localized form to reduce errors | - Form title/placeholders/labels/submit button localized<br>- Template-surfaced auth error messages localized | Completed |
| I18N-013 | registration/change_password.html | `onlineretailpos/templates/registration/change_password.html` | Staff/Cashier | Change password using a localized form | - Headings/instructions/buttons localized<br>- Template success/error messages localized | Completed |
| I18N-014 | admin/base.html | `onlineretailpos/templates/admin/base.html` | Staff/Admin | See customized admin base strings localized | - Any custom template strings localized (Django admin core already localized upstream) | Completed |
| I18N-015 | Data: product/department labels | `inventory/models.py`, `onlineretailpos/admin.py` | Manager/Cashier | See product and department names in my language across UI, receipts, and reports | - Approach selected and implemented (per-language fields like `name_fr`/`name_es` or `django-modeltranslation`)<br>- Admin/editor UI to manage localized names<br>- UI uses localized label with fallback to base; search works on localized/base fields<br>- Receipts/reports display localized names<br>- Docs updated in TRANSLATION.md | Completed |

---

### already localized

| Template | Path | Notes | Status |
|---|---|---|---|
| base.html | `onlineretailpos/templates/base.html` | Navigation, menu items, user menu, language switcher | Done |
| retailScreen.html | `onlineretailpos/templates/retailScreen.html` | Register page: headings, buttons, table headers, dialogs | Done |

### cross-cutting acceptance criteria (apply to all pages)
- `{% load i18n %}` present at the top of the template
- All visible static strings wrapped with `{% trans %}` or `{% blocktrans %}`
- Client-side texts generated in templates (alerts/prompts/dialogs) translated via `{% trans %}`
- Python-provided labels/messages use `gettext_lazy` (`_()`) in views/forms where applicable
- `locale/fr/` and `locale/es/` PO files updated; `compilemessages` run; no missing translations on fr/es
- Quick smoke test: switching languages updates the page with no English leftovers

### appendix: workflow checklist per page
1) Add `{% load i18n %}`
2) Wrap strings with `{% trans %}`/`{% blocktrans %}`
3) Adjust Python labels with `_()` if needed
4) Extract messages (`makemessages`), translate fr/es, compile
5) Verify in UI by switching languages

### quick-create GitHub issues
Use the helper script to open one issue per user story with the ID as the exact title.

Requirements: GitHub CLI (gh) authenticated with access to the repo.

```bash
bash scripts/create_i18n_issues.sh hartou/ireti-pos-light
```

If you prefer the UI, use the i18n Task issue template and set the title to the ID (e.g., I18N-001).

### automation
- The workflow `.github/workflows/sync_i18n_issues.yml` monitors this file.
- When you change a row’s Status to `Completed`, the workflow finds the open issue with the same ID as title and closes it automatically (adds a comment, then closes).
- You can trigger it by pushing a commit to this file, via the scheduled run (daily), or manually with “Run workflow” in GitHub Actions.
