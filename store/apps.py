from django.apps import AppConfig

"""
    This class is registered in 'INSTALLED_APPS' (in settings.py) 
    to load the application and its models into the project.
    Specifies the default type for primary keys (ID fields) in models.
    """


class StoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "store"  # The unique name of the application within the Django project.
