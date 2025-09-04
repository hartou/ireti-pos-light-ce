# End-to-end tests (Playwright)

This folder contains Playwright tests that exercise PWA user stories and functional acceptance criteria.

## Prerequisites
- Node.js 18+
- Docker + Docker Compose (to run the app stack)
- GitHub CLI (optional, for coding agent / PR flow)

## Local run
1. Start the stack in another terminal:

```bash
docker compose up -d --build
```

2. Install test deps and browsers:

```bash
npm ci || npm install
npm run postinstall
```

3. Run tests:

```bash
npm run test:e2e
```

4. Open the HTML report (optional):

```bash
npm run test:e2e:report
```

Notes
- Tests assume BASE_URL=http://127.0.0.1:8000. You can override by exporting BASE_URL.
- Default admin credentials come from docker-compose: admin / Admin123!

## CI workflow
- See `.github/workflows/e2e.yml` which builds the app, brings up docker-compose, waits for port 8000, then runs Playwright tests and uploads the report artifact.

## Reusability
- Add new specs in `tests/e2e/` and name them with the story ID (e.g., `pwa-004-static-cache.spec.ts`).
- Use IDs as issue titles to tie them to docs; the sync workflow can auto-close when docs are updated to Completed.
