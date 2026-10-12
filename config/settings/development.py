"""
FleetOps Cloud — Local Development Settings.
"""

from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# In local development, use console email backend for testing verification
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Turn off WhiteNoise strict manifest requirements in local development
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
