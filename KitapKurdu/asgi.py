"""
ASGI config for KitapKurdu project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# This tells Django where to find the configuration file (settings.py).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KitapKurdu.settings")
application = get_asgi_application()
