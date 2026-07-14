"""Template tags for django-easy-icons.

This module provides Django template tags for rendering icons in templates.
The main template tag is {% icon %} which integrates with the django-easy-icons
rendering system.

Usage in templates:
    {% load easy_icons %}

    <!-- Basic usage -->
    {% icon "home" %}

    <!-- With attributes -->
    {% icon "user" class="nav-icon" height="2em" %}

    <!-- Using specific renderer -->
    {% icon "heart" renderer="fontawesome" %}

    <!-- With template variables -->
    {% icon icon_name class=css_class %}

The template tag supports all the same functionality as the Python icon() function,
including multiple renderers, attribute merging, and Django's automatic HTML escaping.
"""

from django import template
from django.utils.safestring import SafeString

from .. import utils

register = template.Library()


@register.simple_tag
def icon(name: str, renderer: str | None = None, defaults: dict | None = None, **kwargs) -> SafeString | str:
    """Template tag to render an icon.

    Usage:
        {% icon "home" %}  {# Auto-detects renderer #}
        {% icon "home" renderer="fontawesome" %}  {# Explicit renderer #}
        {% icon "home" renderer="sprites" %}
        {% icon "home" class="large" height="2em" %}
        {% icon "heart" renderer="fontawesome" class="gold" %}
        {% icon "home" defaults=attr_dict %}
        {% icon "home" class="bg-primary" defaults=attr_dict %}

    Args:
        name: The icon name to render
        renderer: Name of the renderer to use (auto-detects if None)
        defaults: Dictionary of default attributes to merge with kwargs
        **kwargs: Additional attributes for the icon

    Returns:
        Safe HTML string containing the rendered icon, or empty string if not found
        and EASY_ICONS_FAIL_SILENTLY is True
    """
    # Merge defaults with kwargs if provided
    if defaults:
        # Start with defaults and update with kwargs
        # This allows kwargs to override defaults values
        merged_kwargs = defaults
        merged_kwargs.update(kwargs)
        kwargs = merged_kwargs
        if "name" in kwargs:
            del kwargs["name"]

    return utils.icon(name, renderer=renderer, **kwargs)
