import os
import sys
import django

# 👉 project root add to python path
PROJECT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'firstproject')
sys.path.append(PROJECT_DIR)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "firstproject.settings"
)

django.setup()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
