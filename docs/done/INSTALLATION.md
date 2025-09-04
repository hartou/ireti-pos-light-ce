# Installation and Deployment Guide

This guide covers running Online Retail POS locally and with Docker (single container and docker-compose with Postgres).

## Prerequisites
- Python 3.8+
- pip
- Docker and Docker Compose (optional but recommended)

## 1) Local setup (no Docker)

1. Clone repository
   ```bash
   git clone https://github.com/hartou/ireti-pos-light.git
   cd ireti-pos-light
   ```
2. Create and activate a virtual environment (recommended)
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Configure environment
   - Copy `.env.sample` to `.env` and adjust values as needed (secret key, DB, store info, etc.)
   - By default, the project uses SQLite. To use Postgres or MySQL, set `NAME_OF_DATABASE` and the DB_* variables in `.env`.

5. Initialize database
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Create superuser
   ```bash
   python manage.py createsuperuser
   ```
7. Run server
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   Access: http://127.0.0.1:8000

## 2) Docker: single container

Build and run directly from Dockerfile using SQLite by default.

```bash
# Build image
docker build -t onlineretailpos .

# Run (auto-create admin user by providing env vars)
docker run -p 8000:8000 \
  -e DJANGO_SUPERUSER_USERNAME=admin \
  -e DJANGO_SUPERUSER_PASSWORD=Admin123! \
  -e DJANGO_SUPERUSER_EMAIL=admin@example.com \
  onlineretailpos
```

Notes:
- You can provide a `.env` file using `--env-file /path/to/.env`.
- To use Postgres/MySQL from outside Docker, set DB variables and NAME_OF_DATABASE accordingly.

## 3) Docker Compose: with Postgres

This repo includes a `docker-compose.yml` that starts Postgres, runs a one-shot `migrate` job to apply migrations and create a superuser, and then starts the web app.

### Quick start
```bash
# Optional: adjust credentials in docker-compose.yml or provide a .env file
# Bring up the stack
docker compose up -d --build

# Check status
docker compose ps

# Tail logs
docker compose logs -f migrate
docker compose logs -f webapp
```

- Postgres healthcheck ensures the DB is ready before migrations run.
- The `migrate` service runs:
  - `python manage.py makemigrations`
  - `python manage.py migrate`
  - A Django script at `scripts/create_superuser.py` that creates the admin user (if env vars provided)
- The `webapp` starts after `migrate` succeeds and serves on `0.0.0.0:8000`.

### Default credentials and overrides
- Defaults in compose:
  - DB: `DBUSER/DBPASS/OnlineRetailPOS`
  - Superuser: `admin / Admin123!`
- Override via `.env` or environment variables:
  - `DJANGO_SUPERUSER_USERNAME`
  - `DJANGO_SUPERUSER_PASSWORD`
  - `DJANGO_SUPERUSER_EMAIL`

### Common issues
- Permission denied when building: ensure `postgres_data/` is excluded via `.dockerignore` (already configured).
- DisallowedHost when accessing via localhost: we include `'localhost'` in `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in dev settings.
- Stuck waiting for DB: the compose file includes a Postgres healthcheck; ensure the DB creds match.

## 4) Production considerations (outline)
- Use Postgres in a managed DB or a durable volume. Avoid SQLite for multi-user prod usage.
- Generate a strong `SECRET_KEY_DEV` (or `SECRET_KEY`) and keep it secret.
- Serve static files via a proper web server (Nginx) and run Django with Gunicorn/Uvicorn.
- Configure HTTPS and trusted hosts. Restrict admin access.
- Back up the database and `.env` securely.

## 5) Useful URLs
- App: http://127.0.0.1:8000
- Login: http://127.0.0.1:8000/user/login/
- Admin: http://127.0.0.1:8000/staff_portal/

---
If you run into issues, share the output of:
```bash
docker compose ps
docker compose logs --tail=200 migrate
docker compose logs --tail=200 webapp
```
