"""
WSGI config for KitapKurdu project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Bu, WSGI sunucusunun hangi ayar dosyasını kullanacağını bilmesini sağlar.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KitapKurdu.settings")
# to communicate with your Django application.
application = get_wsgi_application()
