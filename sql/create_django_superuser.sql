-- Deprecated: Not used. Superuser is created by the docker-compose "migrate" job via Django ORM.
-- You can safely delete this file.

-- Template SQL to create a Django superuser directly via SQL (use only if you cannot run Django commands)
-- IMPORTANT: You must provide a valid Django password hash for the desired password.
-- Generate a hash inside the Django app context, for example:
--   docker compose run --rm webapp python - <<'PY'
--   import os
--   os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('SETTINGS','onlineretailpos.settings.devlopement'))
--   from django.contrib.auth.hashers import make_password
--   print(make_password('Admin123!'))  # replace with your password
--   PY
-- Then replace {{PASSWORD_HASH}} below.

-- Replace these placeholders:
--   {{USERNAME}}       e.g., admin
--   {{EMAIL}}          e.g., admin@example.com
--   {{PASSWORD_HASH}}  e.g., pbkdf2_sha256$390000$...

INSERT INTO auth_user (
  password,
  last_login,
  is_superuser,
  username,
  first_name,
  last_name,
  email,
  is_staff,
  is_active,
  date_joined
) VALUES (
  '{{PASSWORD_HASH}}',
  NULL,
  TRUE,
  '{{USERNAME}}',
  '',
  '',
  '{{EMAIL}}',
  TRUE,
  TRUE,
  NOW()
)
ON CONFLICT (username) DO NOTHING;

-- Ensure the auth_user ID sequence is up-to-date (safe no-op if already correct)
SELECT setval(
  pg_get_serial_sequence('auth_user','id'),
  GREATEST((SELECT COALESCE(MAX(id), 1) FROM auth_user), 1)
);
