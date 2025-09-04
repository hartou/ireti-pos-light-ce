PWA manual testing guide

This document describes how to manually verify the core PWA behavior of Ireti POS Light. Use it when automated E2E is unavailable. It maps to the initial PWA user stories (PWA-001, PWA-002, PWA-003, PWA-017).

Prerequisites
- Node is not required.
- Docker optional. You can run the Django server directly or via docker-compose.
- Browser: recent Chrome/Edge or Firefox. For installability checks, use Chrome/Edge.

Start the app
Option A — docker compose
1) docker compose up -d --build
2) Wait until http://127.0.0.1:8000 is reachable. If you see a login page, the app is up.

Option B — local Python
1) python3 -m venv .venv && source .venv/bin/activate
2) pip install -r requirements.txt
3) python manage.py migrate
4) python manage.py runserver 0.0.0.0:8000

Login
- Visit http://127.0.0.1:8000/user/login/
- Log in with an existing staff account. If none exists, create one: python manage.py createsuperuser

Checks

<a id="pwa-001-manifest"></a>
## PWA-001 — Manifest is served
- Open DevTools → Application → Manifest.
- Verify: name, short_name, theme_color present; icons 192x192 and 512x512 present; start_url is / and display is standalone.
- Alternatively open http://127.0.0.1:8000/static/manifest.webmanifest and verify JSON loads without errors.

<a id="pwa-002-service-worker-registers"></a>
## PWA-002 — Service worker registers
- DevTools → Application → Service Workers.
- Reload the page. You should see a registered service worker (scope /static/js/ or / depending on registration) and an “activated” status.
- In the Console, check there are no registration errors.

<a id="pwa-003-install-prompt-ux"></a>
## PWA-003 — Install prompt UX
- On a Chromium browser, navigate to the site root while logged in or on the login page.
- If the install button is visible in the header/footer (depending on base.html), click it.
- Expected: Browser “Install App” prompt appears. You can install and launch the app standalone.
- Post-install: Verify window opens without URL bar (standalone display mode) and uses the manifest name and icon.

<a id="pwa-017-offline-fallback"></a>
## PWA-017 — Offline fallback page works
- With the page open, DevTools → Network tab → set Throttle to Offline.
- In a new tab, navigate to http://127.0.0.1:8000/offline.
- Expected: The offline page renders from cache without a network.
- Optional: Try loading a cached shell page (like /user/login/) to confirm graceful behavior.

Troubleshooting
- If service worker doesn’t register: ensure the static files are served and that base.html includes the registration script. Clear site data and hard reload.
- If manifest shows errors: open the manifest URL directly and check for trailing commas or wrong MIME. The link tag in base.html should have rel="manifest" and correct href.
- If offline doesn’t show: ensure /offline route exists and is included in the SW precache list. Update the service worker version string and hard refresh.
- If install prompt doesn’t appear: Chromium requires user engagement and valid manifest + service worker. Use the Application tab’s “Manifest” check to confirm installability.

Appendix
- Files involved: onlineretailpos/templates/base.html, onlineretailpos/static/manifest.webmanifest, onlineretailpos/static/js/sw.js, onlineretailpos/templates/offline.html, onlineretailpos/views.py (offline_page)
- Dev server URL: http://127.0.0.1:8000
