# Scan-first, cart-first register design (cashier optimized)

Goals
- Minimize interactions for the common path (scan → confirm → tender).
- Keep input focus stable for wedge scanners; enable full keyboard use.
- Always-visible totals and quick tender buttons.
- Clear offline state and guardrails around payment while offline.

Layout
- Left (scan pane):
  - Big barcode input (auto-focus) + Qty field + Add button.
  - Shortcuts help (F-keys) and last-scan confirmation.
- Right (cart pane):
  - Scrollable compact cart table: Item, Qty, Price, Line total.
  - Footer with Subtotal, Tax, Total, and quick tenders (Cash/Card/EBT) + Clear.
  - Suspend/Recall at header.

Behavior
- Focus management: barcode field keeps focus unless a text input is active.
- Keyboard shortcuts (suggested): F2 void line, F4 qty multiplier, F9 suspend, F10 recall.
- Offline handling: show badge; disable tender buttons when offline (future enhancement).
- Accessibility: high-contrast totals, large tap targets for tenders.

Route
- Path: `/register/scan/`
- Template: `register_scan.html`
- View: `register_scan` in `onlineretailpos.views` (reuses `EnterBarcode`).

Next enhancements
- Line-level actions (void/qty) with hotkeys.
- Last-scan toast and error banners (e.g., Product not found).
- IndexedDB offline cart sync (align with PWA stories).
- Printer readiness indicator and test print entry point.
