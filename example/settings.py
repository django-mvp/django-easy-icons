"""Settings for the example project."""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


sys.path.append(str(BASE_DIR / "tests"))

SECRET_KEY = "=bodvqgkt@)emfe2!($i#1zd(x27@u!9*9+)^$8bu#sqsmm^*n"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "easy_icons",
    "example",
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "example" / "static",
]

ROOT_URLCONF = "example.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Override the EASY_ICONS configuration to demonstrate the new API
EASY_ICONS = {
    # Default SVG renderer configuration
    "default": {
        "renderer": "easy_icons.renderers.SvgRenderer",
        "config": {
            "svg_dir": "icons",
            "default_attrs": {
                "height": "1em",
                "fill": "currentColor",
            },
        },
        "icons": {
            "home": "home.svg",
            "star": "star.svg",
            "user": "user.svg",
        },
    },
    # Font Awesome provider renderer
    "fontawesome": {
        "renderer": "easy_icons.renderers.ProviderRenderer",
        "config": {
            "tag": "i",
        },
        "icons": {
            "heart": "fas fa-heart",
            "star": "fas fa-star",
            "admin": "fas fa-toolbox",
            "user": "fas fa-user",
            "cog": "fas fa-cog",
        },
    },
    # Bootstrap Icons sprite renderer (using local static file)
    "sprites": {
        "renderer": "easy_icons.renderers.SpritesRenderer",
        "config": {
            "sprite_url": "/static/example/bootstrap-icons.svg",
            "default_attrs": {
                "height": "2em",
                "width": "2em",
                "fill": "currentColor",
            },
        },
        "icons": {
            "zero": "0-circle",
            "one": "1-circle",
            "zero-filled": "0-circle-fill",
            "one-filled": "1-circle-fill",
            "zero-square": "0-square",
        },
    },
}

# Add some logging to help with debugging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "easy_icons": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
