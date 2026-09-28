"""The ``{% icon %}`` template tag."""

from django import template
from django.utils.safestring import SafeString

from .. import utils

register = template.Library()


@register.simple_tag
def icon(
    name: str, renderer: str | None = None, defaults: dict | None = None, **kwargs
) -> SafeString | str:
    """Render an icon in a template.

    Args:
        name: The logical icon name.
        renderer: The configured renderer to use. When omitted, the renderer
            that registered ``name`` is used.
        defaults: Attributes to apply, which keyword attributes override.
        **kwargs: HTML attributes for the icon.

    Returns:
        The icon's markup, or an empty string when the icon is not found and
        ``EASY_ICONS_FAIL_SILENTLY`` is true.

    Example:
        Load the library, then render icons by name::

            {% load easy_icons %}
            {% icon "home" %}
            {% icon "heart" renderer="fontawesome" class="gold" %}
            {% icon "home" class="bg-primary" defaults=attr_dict %}
    """
    if defaults:
        merged_kwargs = defaults
        merged_kwargs.update(kwargs)
        kwargs = merged_kwargs
        if "name" in kwargs:
            del kwargs["name"]

    return utils.icon(name, renderer=renderer, **kwargs)
