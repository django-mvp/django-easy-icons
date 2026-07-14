"""Django Easy Icons - Flexible icon rendering for Django templates.

This package provides a simple, consistent way to include icons in Django templates
with support for multiple rendering backends including SVG files, font icon libraries,
and SVG sprite sheets.

Basic usage:
    from easy_icons import icon

    # Render an icon with default renderer
    home_icon = icon("home")

    # Render with attributes
    user_icon = icon("user", height="2em", **{"class": "nav-icon"})

    # Use specific renderer
    fa_icon = icon("heart", renderer="fontawesome")

Template usage:
    {% load easy_icons %}
    {% icon "home" %}
    {% icon "user" class="nav-icon" %}
    {% icon "heart" renderer="fontawesome" %}
"""

from .utils import icon

__version__ = "0.1.0"
__all__ = ["icon"]
