from django.apps import AppConfig


class EasyIconsConfig(AppConfig):
    """Configuration for the Easy Icons Django app."""

    name = "easy_icons"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "Easy Icons"

    def ready(self):
        """Build the global icon registry when Django starts."""
        from . import utils

        utils.build_icon_registry()
