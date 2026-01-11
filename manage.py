#!/usr/bin/env python
import os
import sys


def main():
    """Run administrative tasks."""
    # This tells Django which settings file to use (settings.py).
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KitapKurdu.settings")
    try:
        # This function takes arguments from the command line (e.g., 'runserver', 'migrate')
        # and executes the corresponding Django command.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # If Django is not installed or the virtual environment is not activated,
        # raise a clear error message to help the developer debug the issue.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)  # Terminale girilen komutu yürütün.


if __name__ == "__main__":
    main()
