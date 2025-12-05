import os
import django
from django.core.management import execute_from_command_line

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miapp.settings")
django.setup()

execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000"])
