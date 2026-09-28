"""Django app configuration for the example project."""

from django.apps import AppConfig


class ExampleConfig(AppConfig):
    """Register the example project's templates and static files."""

    name = "example"
    default_auto_field = "django.db.models.BigAutoField"
