"""Base renderer class and common functionality for django-easy-icons.

This module provides the abstract base class that all icon renderers must inherit from,
along with common functionality for attribute handling and icon name resolution.

The BaseRenderer class handles:
- Icon name mapping and resolution
- HTML attribute building and merging
- Default attribute management
- Common interface for all renderers

Example:
    class MyRenderer(BaseRenderer):
        def render(self, name: str, **kwargs) -> SafeString:
            resolved_name = self.get_icon(name)
            attrs = self.build_attrs(**kwargs)
            return self.safe_return(f'<my-icon {attrs}>{resolved_name}</my-icon>')
"""

from abc import ABC, abstractmethod
from typing import Any

from django.forms.utils import flatatt
from django.utils.safestring import SafeString, mark_safe

from .exceptions import IconNotFoundError


class BaseRenderer(ABC):
    """Base class for all icon renderers.

    Renderers now declare their configuration explicitly via ``__init__``
    keyword arguments. The settings loader star-expands user supplied
    ``config`` dictionaries directly into that initializer. Common shared
    data (like icon name mappings) is still passed via ``icons``.
    """

    def __init__(
        self, *, icons: dict[str, str] | None = None, default_attrs: dict[str, Any] | None = None, **_: Any
    ):  # pragma: no cover - slim wrapper
        """Initialize the base renderer.

        Parameters
        ----------
        icons: Optional[Dict[str, str]]
            Mapping of logical icon names to renderer-specific identifiers.
        default_attrs: Optional[Dict[str, Any]]
            Default HTML attributes applied (and mergeable) across all renders.
        **_ : Any
            Ignored extra keyword arguments (consumed by concrete subclasses).
        """
        self.icons = icons or {}
        # Provide a unified place for managing default attributes so concrete
        # renderers don't need to duplicate ``self.default_attrs = default_attrs or {}``.
        self.default_attrs = (default_attrs or {}).copy()

    def get_icon(self, name: str) -> str:
        """Resolve icon name through renderer-specific icon mappings."""
        try:
            return self.icons[name]
        except KeyError:
            raise IconNotFoundError(f"Icon '{name}' not listed in available icons for {self.__class__.__name__}")

    def build_attrs(self, use_defaults: bool = True, **kwargs: Any) -> str:
        """Build HTML attributes string from configuration and provided kwargs.

        Args:
            use_defaults: Whether to merge with default attributes
            **kwargs: Additional attributes to include

        Returns:
            HTML attributes string
        """
        if not use_defaults:
            return flatatt(kwargs)

        # creates a copy of default_attrs then override with kwargs
        attrs = self.default_attrs.copy()
        attrs.update(kwargs)

        return flatatt(attrs)

    @abstractmethod
    def render(self, name: str, **kwargs: Any) -> SafeString:
        """Render an icon with the given name and attributes.

        Args:
            name: The icon name to render
            **kwargs: Additional attributes for the icon

        Returns:
            Safe HTML string containing the rendered icon
        """
        pass

    def __call__(self, name: str, **kwargs: Any) -> SafeString:
        """Make renderer instances callable.

        Args:
            name: The icon name to render
            **kwargs: Additional attributes for the icon

        Returns:
            Safe HTML string containing the rendered icon
        """
        return self.render(name, **kwargs)

    def safe_return(self, content: str) -> SafeString:
        """Return HTML content marked as safe (internal helper)."""
        return mark_safe(content)  # noqa: S308
