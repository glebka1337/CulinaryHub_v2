"""
WSGI config for culinaryhub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see

"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'culinaryhub.settings')

application = get_wsgi_application()
