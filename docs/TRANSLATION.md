# Translation (i18n) Setup

This project is configured for Django i18n with a language switcher in the top navbar.

## Languages
- English (`en`)
- French (`fr`)
- Spanish (`es`)

You can add more in `iretilightpos/settings/base.py` under `LANGUAGES`.

## Mark strings for translation
Wrap user-facing strings in templates and Python with translation tags/functions, for example:

- Templates: `{% load i18n %}` at top, then `{% trans "Text" %}` or `{% blocktrans %}...{% endblocktrans %}`
- Python: `from django.utils.translation import gettext as _` then `_("Text")`

## Create and compile messages
Run these from the repo root. (Use the container shell or your local environment with Django installed.)

```bash
# Extract strings to locale/<lang>/LC_MESSAGES/django.po
django-admin makemessages -l fr
django-admin makemessages -l es

# Edit the generated PO files to provide translations, then compile
django-admin compilemessages
```

Inside Docker (compose):
```bash
docker compose run --rm webapp bash -lc "django-admin makemessages -l fr && django-admin makemessages -l es && django-admin compilemessages"
```

## Switching languages
Use the dropdown in the top-right navbar. It posts to `/i18n/setlang/` and refreshes the current page in the selected language.

## Data Translations (I18N-015)

Starting with I18N-015, the system supports localized names for products and departments stored directly in the database.

### Product and Department Localized Names

**Product Model Fields:**
- `name` (required): Base English name
- `name_fr` (optional): French translation
- `name_es` (optional): Spanish translation

**Department Model Fields:**
- `department_name` (required): Base English name  
- `department_name_fr` (optional): French translation
- `department_name_es` (optional): Spanish translation

### Admin Interface

In the Django admin:
1. **Products**: Edit products to add French/Spanish names in the "Names" section
2. **Departments**: Edit departments to add French/Spanish names in the "Department Names" section
3. **Search**: Admin search works across base and localized names

### Behavior

- **Cart/Receipts**: When adding items to cart, localized names are used based on current language
- **Fallback**: If no localized name exists, base name is used automatically
- **Reports**: Historical transactions preserve the name at time of sale

### Developer Usage

Use the helper methods in code:

```python
# Get localized name for current language
product.get_localized_name()
department.get_localized_name()

# Get localized name for specific language
product.get_localized_name('fr')  # French
product.get_localized_name('es')  # Spanish
```

## Notes
- Ensure `LocaleMiddleware` is enabled and comes after `SessionMiddleware` in `MIDDLEWARE` (already configured).
- Translations live in `locale/` at the project root.
