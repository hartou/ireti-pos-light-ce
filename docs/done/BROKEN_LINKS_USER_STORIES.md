# Broken links user stories and acceptance criteria (August 10, 2025)

This document tracks fixes for broken or unclear routes collected in `bugs.md`. Each row is a user story with acceptance criteria to mark it “link-fixed”.

Notes
- Status values: use `Pending` (default) or `Completed` when the route is fixed and verified. The CI will auto-close the matching GitHub issue when set to Completed.
- Treat admin-only pages as protected: unauthenticated users should be redirected to login (302) rather than getting 404.
- Prefer adding small request tests to prevent regressions.

---

| ID | URL | Path/Component | Persona | User story | Acceptance criteria (condensed) | Status |
|---|---|---|---|---|---|---|
| BL-001 | `/dashboard_sales/` | `onlineretailpos/urls.py` ➜ `views.dashboard_sales` | Manager | Access Sales Dashboard without 404s | - URL resolves and renders for authenticated user (200)<br>- Unauthenticated user gets 302 to login<br>- Any nav/menu link points to this path<br>- Add a smoke test for both cases | Completed |
| BL-002 | `/dashboard_department/` | `onlineretailpos/urls.py` ➜ `views.dashboard_department` | Manager | Access Department Dashboard reliably | - URL resolves for authenticated user (200)<br>- Unauthenticated: 302 to login<br>- Menu link points to this path<br>- Smoke test added | Completed |
| BL-003 | `/dashboard_products/` | `onlineretailpos/urls.py` ➜ `views.dashboard_products` | Manager | Access Products Dashboard reliably | - URL resolves for authenticated user (200)<br>- Unauthenticated: 302 to login<br>- Menu link points to this path<br>- Smoke test added | Completed |
| BL-004 | `/transaction/` | `onlineretailpos/urls.py` ➜ `transaction.views.transactionView` | Cashier/Manager | Open Transactions list without errors | - URL resolves for authenticated user (200)<br>- Unauthenticated: 302 to login<br>- If query params required, sensible defaults exist<br>- Smoke test added | Completed |
| BL-005 | `/register/product_lookup/` | `onlineretailpos/urls.py` ➜ `inventory.views.product_lookup` | Cashier | Look up products from Register | - URL resolves for authenticated user (200)<br>- Unauthenticated: 302 to login<br>- Register menu/button links here<br>- Smoke test added | Completed |
| BL-006 | `/inventory/` | `onlineretailpos/urls.py` ➜ `inventory.views.inventoryAdd` | Inventory Clerk | Open Add Inventory page | - URL resolves for authenticated user (200)<br>- Unauthenticated: 302 to login<br>- Sidebar/nav link points here<br>- Smoke test added | Completed |
| BL-007 | `/staff_portal/` | Django Admin (root) | Admin | Reach Admin portal login/index | - URL resolves to Admin (200 when logged in, 302 to login when not)<br>- Admin CSS/JS load without errors<br>- Smoke test added | Completed |
| BL-008 | `/staff_portal/auth/group/` | Django Admin ➜ Auth Group changelist | Admin | Manage Groups in Admin | - URL resolves for superuser (200)<br>- Non-admin users redirected/forbidden as expected<br>- Link from Admin index works<br>- Smoke test added (admin case) | Completed |
| BL-009 | `/retail_display/` | `onlineretailpos/urls.py` ➜ `views.retail_display` | Cashier/Customer | Clarify and wire up Customer Display page | - Confirm intended usage and params<br>- URL resolves (200) with defaults<br>- Register can open this screen (if applicable)<br>- Basic smoke test added | Completed |

---

### cross-cutting acceptance criteria (apply to all)
- For protected pages, unauthenticated users receive a 302 redirect to login, not 404.
- For public pages (if any), use 200 with helpful messaging when data is empty.
- All linked navigation items point to the correct paths; remove dead links.
- Add a minimal Django request test for 200/302 behavior per route.

### appendix: workflow checklist per story
1) Confirm the route exists in `onlineretailpos/urls.py` (or Admin)
2) Implement/fix the view and required template(s)
3) Verify auth behavior (200 when logged in; 302 to login when not)
4) Fix or remove any dead navigation links
5) Add a small test (optional but preferred)
6) Set Status to `Completed` when done

### quick-create GitHub issues
Use the helper script to open one issue per story with the ID as the exact title.

Requirements: GitHub CLI (gh) authenticated with access to the repo.

```bash
bash scripts/create_broken_link_issues.sh hartou/ireti-pos-light
```

### automation
- The workflow `.github/workflows/sync_broken_link_issues.yml` monitors this file.
- When a row’s Status is changed to `Completed`, the workflow finds the matching open issue (title equals the ID) and closes it automatically.
