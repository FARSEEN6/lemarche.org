import os
import sys
import django

# 👉 project root add to python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "firstproject.firstproject.settings"
)

django.setup()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
