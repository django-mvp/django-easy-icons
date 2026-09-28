"""The SVG template, icon font and sprite sheet renderers."""

from typing import Any

from django.template.loader import render_to_string
from django.utils.safestring import SafeString

from .base import BaseRenderer
from .exceptions import InvalidSvgError


class SvgRenderer(BaseRenderer):
    """Render icons from SVG files loaded as Django templates.

    Args:
        svg_dir: Template directory the SVG files live in.
        **kwargs: ``icons`` and ``default_attrs``, passed to `BaseRenderer`.
            The default attributes land on the root ``<svg>`` element.
    """

    def __init__(self, *, svg_dir: str = "icons", **kwargs: Any):
        super().__init__(**kwargs)
        self.svg_dir = svg_dir

    def render(self, name: str, **kwargs: Any) -> SafeString:
        """Render the icon's SVG template with the attributes on its root element."""
        resolved_name = self.get_icon(name)
        template_name = f"{self.svg_dir}/{resolved_name}"
        svg_str = render_to_string(template_name)
        return self._inject_svg_attrs(svg_str, **kwargs)

    def _inject_svg_attrs(self, svg_str: str, **kwargs: Any) -> SafeString:
        """Add attributes to the first ``<svg>`` element of the markup.

        Args:
            svg_str: The rendered SVG markup.
            **kwargs: HTML attributes for the ``<svg>`` element.

        Returns:
            The markup with the attributes added, marked safe.

        Raises:
            InvalidSvgError: The markup contains no ``<svg`` tag.
        """
        attrs = self.build_attrs(**kwargs)

        if not attrs:
            return self.safe_return(svg_str)

        before, sep, after = svg_str.partition("<svg")

        if not sep:
            raise InvalidSvgError("No <svg> tag found in SVG content")

        result = f"{before}<svg {attrs} {after.strip()}"
        return self.safe_return(result)


class ProviderRenderer(BaseRenderer):
    """Render icon-font icons as an empty element carrying the icon's classes.

    Args:
        tag: The HTML element to render, such as ``i`` or ``span``.
        **kwargs: ``icons`` and ``default_attrs``, passed to `BaseRenderer`.

    Attributes:
        template: Format string for the rendered element.
    """

    template = '<{tag} class="{css_class}" {attrs}></{tag}>'

    def __init__(self, *, tag: str = "i", **kwargs: Any):
        super().__init__(**kwargs)
        self.tag = tag

    def render(self, name: str, **kwargs: Any) -> SafeString:
        """Render the element with the icon's classes before any ``class`` passed in."""
        tag = self.tag
        resolved_icon = f"{self.get_icon(name)} {kwargs.pop('class', '')} "
        attrs = self.build_attrs(**kwargs)
        element = self.template.format(
            tag=tag, css_class=resolved_icon.strip(), attrs=attrs
        ).strip()
        return self.safe_return(element)


class SpritesRenderer(BaseRenderer):
    """Render symbols from an SVG sprite sheet through ``<use>``.

    Args:
        sprite_url: URL of the sprite sheet.
        **kwargs: ``icons`` and ``default_attrs``, passed to `BaseRenderer`.
            The default attributes land on the outer ``<svg>`` element.

    Attributes:
        template: Format string for the rendered ``<svg>`` element.

    Raises:
        ValueError: ``sprite_url`` is missing or empty.
    """

    template = """<svg {attrs}>
                    <use href="{sprite_url}#{resolved_name}"></use>
                  </svg>"""

    def __init__(self, *, sprite_url: str | None = None, **kwargs: Any):
        if not sprite_url:
            raise ValueError("SpritesRenderer requires 'sprite_url' keyword argument")
        super().__init__(**kwargs)
        self.sprite_url = sprite_url

    def render(self, name: str, **kwargs: Any) -> SafeString:
        """Render an ``<svg>`` that references the icon's symbol in the sprite sheet."""
        resolved_name = self.get_icon(name)
        sprite_url = self.sprite_url
        attrs = self.build_attrs(**kwargs)

        element = self.template.format(
            sprite_url=sprite_url, resolved_name=resolved_name, attrs=attrs
        ).strip()

        return self.safe_return(element)
