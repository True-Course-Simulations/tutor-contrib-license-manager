from license_manager.settings.production import * # pylint: disable=wildcard-import, unused-wildcard-import

{% include "license_manager/apps/license_manager/settings/partials/common.py" %}

# -------------------------------------------------------------------
# Static files / WhiteNoise configuration
# Updated by: Cannon Smith
# MIDDLEWARE comes from base settings as a tuple, so we rebuild it
# to insert WhiteNoise right after SecurityMiddleware.
# -------------------------------------------------------------------
# Insert WhiteNoise right after SecurityMiddleware (recommended order)
MIDDLEWARE = list(MIDDLEWARE)
try:
    security_index = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
except ValueError:
    # Fallback: if for some reason SecurityMiddleware isn't present,
    # put WhiteNoise at the front but after we converted to list.
    security_index = -1

MIDDLEWARE.insert(security_index + 1, "whitenoise.middleware.WhiteNoiseMiddleware")
MIDDLEWARE = tuple(MIDDLEWARE)

# For now, avoid manifest-based storage to get rid of
# "Missing staticfiles manifest entry" errors.
# Django 4.2+: use STORAGES instead of STATICFILES_STORAGE (they are mutually exclusive).
# Keep existing STORAGES (including "default") and override only "staticfiles".
STORAGES = dict(STORAGES)  # shallow copy in case it's defined upstream
STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
}

# Let WhiteNoise fall back to Django finders (fine for dev)
WHITENOISE_USE_FINDERS = True

# -------------------------------------------------------------------
# CORS / CSRF / OAuth config for Tutor
# -------------------------------------------------------------------
# FIX NOTE: confirm whether License Manager uses MFE.
CORS_ORIGIN_WHITELIST = list(CORS_ORIGIN_WHITELIST) + [
    "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ MFE_HOST }}",
]

CSRF_TRUSTED_ORIGINS = [
    "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ MFE_HOST }}",
]

SOCIAL_AUTH_EDX_OAUTH2_PUBLIC_URL_ROOT = "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ LMS_HOST }}"
BACKEND_SERVICE_EDX_OAUTH2_KEY = "{{ LICENSE_MANAGER_OAUTH2_KEY }}"

{{ patch("license-manager-settings-production") }}
