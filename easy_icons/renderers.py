"""Concrete renderer implementations for django-easy-icons.

All input validation responsibility is delegated to a single place:
``BaseRenderer.get_icon``. Renderers themselves assume any name
they receive has passed that minimal check and focus purely on output
generation.

The public API for consumers is ``easy_icons.utils.icon``; this module
only exposes the concrete classes.
"""

from typing import Any

from django.template.loader import render_to_string
from django.utils.safestring import SafeString

from .base import BaseRenderer
from .exceptions import InvalidSvgError


class SvgRenderer(BaseRenderer):
    """Renderer for SVG icons sourced from template files.

    Parameters
    ----------
    svg_dir: str = "icons"
        Directory (template prefix) where SVG template fragments live.
    default_attrs: dict | None
        Default attributes to inject/merge into rendered SVG root element.
    icons: dict[str,str] | None
        Name mapping provided via settings.
    """

    def __init__(self, *, svg_dir: str = "icons", **kwargs: Any):
        super().__init__(**kwargs)
        self.svg_dir = svg_dir

    def render(self, name: str, **kwargs: Any) -> SafeString:  # noqa: D401
        resolved_name = self.get_icon(name)
        template_name = f"{self.svg_dir}/{resolved_name}"
        svg_str = render_to_string(template_name)
        return self._inject_svg_attrs(svg_str, **kwargs)

    def _inject_svg_attrs(self, svg_str: str, **kwargs: Any) -> SafeString:
        """Inject attributes into the SVG element.

        Args:
            svg_str: The SVG content as a string
            **kwargs: Additional attributes to inject into the SVG tag

        Returns:
            Safe HTML string with attributes injected
        """
        attrs = self.build_attrs(**kwargs)

        if not attrs:
            return self.safe_return(svg_str)

        # Split on '<svg' to isolate the svg tag
        before, sep, after = svg_str.partition("<svg")

        if not sep:  # No '<svg' found
            raise InvalidSvgError("No <svg> tag found in SVG content")

        result = f"{before}<svg {attrs} {after.strip()}"
        return self.safe_return(result)


class ProviderRenderer(BaseRenderer):
    """Renderer for provider / font icon classes using full class strings."""

    template = '<{tag} class="{css_class}" {attrs}></{tag}>'

    def __init__(self, *, tag: str = "i", **kwargs: Any):
        super().__init__(**kwargs)
        self.tag = tag

    def render(self, name: str, **kwargs: Any) -> SafeString:  # noqa: D401
        tag = self.tag
        resolved_icon = f"{self.get_icon(name)} {kwargs.pop('class', '')} "
        attrs = self.build_attrs(**kwargs)
        element = self.template.format(tag=tag, css_class=resolved_icon.strip(), attrs=attrs).strip()
        return self.safe_return(element)


class SpritesRenderer(BaseRenderer):
    """Renderer for SVG sprite symbols via <use>.

    Parameters
    ----------
    sprite_url: str (required)
        Base URL/path to the sprite sheet. Required; raises ValueError if missing.
    default_attrs: dict | None
        Default attributes for the outer <svg> element.
    """

    template = """<svg {attrs}>
                    <use href="{sprite_url}#{resolved_name}"></use>
                  </svg>"""

    def __init__(self, *, sprite_url: str | None = None, **kwargs: Any):
        if not sprite_url:
            raise ValueError("SpritesRenderer requires 'sprite_url' keyword argument")
        super().__init__(**kwargs)
        self.sprite_url = sprite_url

    def render(self, name: str, **kwargs: Any) -> SafeString:  # noqa: D401
        resolved_name = self.get_icon(name)
        sprite_url = self.sprite_url
        attrs = self.build_attrs(**kwargs)

        element = self.template.format(sprite_url=sprite_url, resolved_name=resolved_name, attrs=attrs).strip()

        return self.safe_return(element)
