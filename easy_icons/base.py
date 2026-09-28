"""The base class every icon renderer subclasses."""

from abc import ABC, abstractmethod
from typing import Any

from django.forms.utils import flatatt
from django.utils.safestring import SafeString, mark_safe

from .exceptions import IconNotFoundError


class BaseRenderer(ABC):
    """Base class for all icon renderers.

    Subclasses declare their configuration as keyword arguments to ``__init__``.
    The settings loader star-expands each renderer's ``config`` dictionary into
    that initializer and passes the icon mapping as ``icons``
    (docs/adr/0003-settings-star-expansion.md). Keyword arguments meant for a
    subclass are ignored here.

    Args:
        icons: Logical icon names mapped to renderer-specific identifiers.
        default_attrs: HTML attributes applied to every icon, which per-call
            attributes override.
    """

    def __init__(
        self,
        *,
        icons: dict[str, str] | None = None,
        default_attrs: dict[str, Any] | None = None,
        **_: Any,
    ):  # pragma: no cover - slim wrapper
        self.icons = icons or {}
        self.default_attrs = (default_attrs or {}).copy()

    def get_icon(self, name: str) -> str:
        """Return the renderer-specific identifier for a logical icon name.

        Args:
            name: The logical icon name.

        Returns:
            The identifier this renderer's icon mapping holds for ``name``.

        Raises:
            IconNotFoundError: The mapping has no entry for ``name``.
        """
        try:
            return self.icons[name]
        except KeyError:
            raise IconNotFoundError(
                f"Icon '{name}' not listed in available icons for {self.__class__.__name__}"
            ) from None

    def build_attrs(self, use_defaults: bool = True, **kwargs: Any) -> str:
        """Build HTML attributes string from configuration and provided kwargs.

        Args:
            use_defaults: Merge the renderer's default attributes under ``kwargs``.
            **kwargs: Attributes for this icon.

        Returns:
            The attributes as an HTML attribute string.
        """
        if not use_defaults:
            return flatatt(kwargs)

        attrs = self.default_attrs.copy()
        attrs.update(kwargs)

        return flatatt(attrs)

    @abstractmethod
    def render(self, name: str, **kwargs: Any) -> SafeString:
        """Render an icon with the given name and attributes.

        Args:
            name: The logical icon name.
            **kwargs: HTML attributes for the icon.

        Returns:
            The icon's markup, marked safe.
        """

    def __call__(self, name: str, **kwargs: Any) -> SafeString:
        """Render an icon, so a renderer instance can be called directly.

        Args:
            name: The logical icon name.
            **kwargs: HTML attributes for the icon.

        Returns:
            The icon's markup, marked safe.
        """
        return self.render(name, **kwargs)

    def safe_return(self, content: str) -> SafeString:
        """Mark rendered markup as safe for templates.

        Args:
            content: Markup built from escaped attributes.

        Returns:
            ``content`` marked safe.
        """
        return mark_safe(content)  # noqa: S308
