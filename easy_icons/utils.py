"""Main interface functions for django-easy-icons.

This module provides the primary public API for the django-easy-icons package,
including renderer management, caching, and the main icon() function used by
both Python code and template tags.

Functions:
    get_renderer(name): Get a configured renderer instance by name
    clear_cache(): Clear the renderer instance cache
    build_icon_registry(): Build global icon->renderer lookup dict
    icon(name, renderer, **kwargs): Render an icon using the specified or auto-detected renderer

The icon() function is the main entry point for rendering icons and supports:
- Automatic renderer detection based on icon name
- Multiple configured renderers
- Attribute merging and customization
- Caching for performance
- Integration with Django's SafeString for secure HTML output

Example:
    # Auto-detect renderer (searches default, then other renderers)
    home_icon = icon("home")

    # With custom attributes
    user_icon = icon("user", **{"class": "large", "data-role": "button"})

    # Using explicit renderer
    fa_icon = icon("heart", renderer="fontawesome")
"""

import logging
from typing import Any, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.safestring import SafeString

from .exceptions import IconNotFoundError

# Simple module-level cache for renderer instances
_renderer_cache: dict[str, Any] = {}

# Global icon->renderer lookup dict (built at app startup)
_icon_registry: dict[str, str] = {}  # {icon_name: renderer_name}

logger = logging.getLogger("easy_icons")


def _expand_aliases(mapping: dict[str, str]) -> dict[str, str]:
    """Expand comma-separated alias keys into individual icon entries.

    A single mapping entry may declare several aliases for one icon by
    separating them with commas, e.g. ``{"plus,create,add": "bi bi-plus"}``.
    Each alias is stripped of surrounding whitespace and mapped to the same
    value. Keys without a comma are copied unchanged, so existing
    configurations are completely unaffected.

    Within a single comma group, a later alias overrides an earlier duplicate,
    matching Python's normal dict-construction semantics.

    Args:
        mapping: Raw icon mapping whose keys may contain comma-separated aliases.

    Returns:
        A new mapping with every alias expanded to its own key.

    Note:
        Because the comma is the alias delimiter, a logical icon name cannot
        itself contain a comma.
    """
    expanded: dict[str, str] = {}
    for key, value in mapping.items():
        if "," not in key:
            expanded[key] = value
            continue
        for alias in key.split(","):
            alias = alias.strip()
            if alias:
                expanded[alias] = value
    return expanded


def resolve_icons(renderer_config: dict[str, Any], renderer_name: str) -> dict[str, str]:
    """Build the final icon mapping for a single renderer configuration.

    Merges icon packs (last-wins) and then explicit ``icons`` on top, expanding
    any comma-separated alias keys *per layer* so that precedence is applied at
    the level of individual icon names rather than raw (possibly multi-alias)
    keys. This is the single source of truth used by both :func:`get_renderer`
    and :func:`build_icon_registry`.

    Args:
        renderer_config: The per-renderer configuration dict from ``EASY_ICONS``.
        renderer_name: Name of the renderer (used for logging context).

    Returns:
        Mapping of fully-expanded logical icon names to renderer identifiers.
    """
    packs_list = renderer_config.get("packs", [])
    merged_icons: dict[str, str] = {}

    if packs_list:
        merged_icons = load_and_merge_packs(packs_list, renderer_name)

    # Explicit icons always override pack icons.
    explicit_icons = renderer_config.get("icons", {}) or {}
    merged_icons.update(_expand_aliases(explicit_icons))

    return merged_icons


def load_and_merge_packs(packs_list: list[str], renderer_name: str) -> dict[str, str]:
    """Load and merge icon packs from dotted paths.

    Icon packs allow third-party packages to provide icon definitions that users can
    easily include in their configuration without manual copy/paste. Packs are merged
    sequentially with last-wins precedence, meaning later packs in the list will
    override icon definitions from earlier packs.

    Invalid imports or non-dict values are logged as warnings and skipped gracefully,
    allowing the application to continue functioning even if some packs fail to load.

    Args:
        packs_list: List of dotted Python paths to icon pack dictionaries
                   (e.g., ["mypackage.icons.FONTAWESOME", "other.icons.SVG"])
        renderer_name: Name of the renderer (used for logging context)

    Returns:
        Merged dictionary of all valid packs, where keys are icon names and
        values are icon identifiers specific to the renderer type

    Example:
        >>> packs = ["example.icons.PACK_ONE", "example.icons.PACK_TWO"]
        >>> icons = load_and_merge_packs(packs, "svg")
        >>> # Returns merged dict with PACK_TWO overriding PACK_ONE for any collisions

    Note:
        This function is called automatically by get_renderer() and build_icon_registry()
        when processing the "packs" key in EASY_ICONS configuration.
    """
    merged_icons = {}

    for pack_path in packs_list:
        try:
            pack_data = import_string(pack_path)

            if not isinstance(pack_data, dict):
                logger.warning(
                    f"Renderer '{renderer_name}': Pack '{pack_path}' is not a dictionary "
                    f"(got {type(pack_data).__name__}). Skipping."
                )
                continue

            # Merge with last-wins precedence, expanding any comma-separated
            # alias keys before merging so precedence applies per icon name.
            merged_icons.update(_expand_aliases(pack_data))
            logger.debug(f"Renderer '{renderer_name}': Loaded {len(pack_data)} icons from pack '{pack_path}'")

        except ImportError as e:
            logger.warning(f"Renderer '{renderer_name}': Cannot import pack '{pack_path}': {e}. Skipping.")
        except Exception as e:
            logger.warning(f"Renderer '{renderer_name}': Error loading pack '{pack_path}': {e}. Skipping.")

    return merged_icons


def get_renderer(name: str = "default") -> Any:
    """Get a configured renderer instance.

    Args:
        name: Name of the renderer to get (defaults to 'default')

    Returns:
        Configured renderer instance

    Raises:
        ImproperlyConfigured: If renderer is not configured or cannot be imported
    """
    # Check cache first
    if name in _renderer_cache:
        return _renderer_cache[name]

    # Get configuration from settings or use empty dict
    config = getattr(settings, "EASY_ICONS", {})

    # Validate basic configuration structure
    if not isinstance(config, dict):
        raise ImproperlyConfigured("EASY_ICONS setting must be a dictionary")

    # Ensure requested renderer exists
    if name not in config:
        raise ImproperlyConfigured(f"Renderer '{name}' is not configured in EASY_ICONS")

    renderer_config = config[name]

    # Validate renderer configuration structure
    if not isinstance(renderer_config, dict):
        raise ImproperlyConfigured(f"EASY_ICONS['{name}'] must be a dictionary")

    if "renderer" not in renderer_config:
        raise ImproperlyConfigured(f"EASY_ICONS['{name}'] must specify a 'renderer' class path")

    # Import and instantiate the renderer class
    renderer_class_path = renderer_config["renderer"]

    try:
        renderer_class = import_string(renderer_class_path)
    except ImportError as e:
        raise ImproperlyConfigured(f"Cannot import renderer class '{renderer_class_path}': {e}")

    # Extract configuration options
    renderer_kwargs = renderer_config.get("config", {}) or {}

    # Resolve packs + explicit icons (with alias expansion) into one mapping.
    merged_icons = resolve_icons(renderer_config, name)

    # Create instance
    try:
        renderer_instance = renderer_class(
            icons=merged_icons,
            **renderer_kwargs,
        )
    except Exception as e:
        raise ImproperlyConfigured(f"Cannot instantiate renderer '{name}' with class '{renderer_class_path}': {e}")

    # Cache the instance
    _renderer_cache[name] = renderer_instance
    return renderer_instance


def clear_cache() -> None:
    """Clear renderer cache.

    Useful for testing and development when settings might change.
    """
    _renderer_cache.clear()


def build_icon_registry() -> None:
    """Build global icon->renderer lookup dictionary at app startup.

    Lookup order:
    1. 'default' renderer icons (if it exists)
    2. All other renderers in settings order

    When multiple renderers define the same icon, the first one encountered wins.
    Collisions are logged as warnings to help users debug configuration.
    """
    global _icon_registry
    _icon_registry.clear()

    config = getattr(settings, "EASY_ICONS", {})
    if not isinstance(config, dict):
        return

    # Track collisions for logging
    collisions: dict[str, list[str]] = {}  # {icon_name: [renderer_names]}

    # Process 'default' renderer first if it exists
    renderers_to_process = []
    if "default" in config:
        renderers_to_process.append("default")

    # Then add all other renderers in order
    for renderer_name in config:
        if renderer_name != "default" and not renderer_name.isupper():
            renderers_to_process.append(renderer_name)

    # Build the registry
    for renderer_name in renderers_to_process:
        renderer_config = config[renderer_name]
        if not isinstance(renderer_config, dict):
            continue

        # Resolve packs + explicit icons (with alias expansion) into one mapping.
        merged_icons = resolve_icons(renderer_config, renderer_name)

        for icon_name in merged_icons:
            if icon_name in _icon_registry:
                # Collision - track it
                if icon_name not in collisions:
                    collisions[icon_name] = [_icon_registry[icon_name]]
                collisions[icon_name].append(renderer_name)
            else:
                # First occurrence - register it
                _icon_registry[icon_name] = renderer_name

    # Log collisions as warnings
    for icon_name, renderer_list in collisions.items():
        logger.warning(
            f"Icon name collision: '{icon_name}' defined in multiple renderers: "
            f"{', '.join(renderer_list)}. Using '{renderer_list[0]}'."
        )


def icon(name: str, renderer: str | None = None, **kwargs: Any) -> SafeString | str:
    """Render an icon using the specified or auto-detected renderer.

    Lookup strategy when renderer is not specified:
    1. If icon registry is built, check for the icon in registry
    2. If registry is empty (not built), fall back to 'default' renderer (backwards compat)
    3. If not found and EASY_ICONS_FAIL_SILENTLY is True, return empty string
    4. If not found and EASY_ICONS_FAIL_SILENTLY is False, raise IconNotFoundError

    Args:
        name: The icon name to render
        renderer: Name of the renderer to use (auto-detects if None)
        **kwargs: Additional attributes for the icon

    Returns:
        Safe HTML string containing the rendered icon, or empty string if not found
        and fail_silently is True

    Raises:
        IconNotFoundError: If icon not found and EASY_ICONS_FAIL_SILENTLY is False
    """
    # Get fail_silently setting (defaults to DEBUG)
    fail_silently = getattr(settings, "EASY_ICONS_FAIL_SILENTLY", settings.DEBUG)

    # Auto-detect renderer if not explicitly provided
    if renderer is None:
        # If registry is built (not empty), use it
        if _icon_registry:
            renderer = _icon_registry.get(name)

            if renderer is None:
                # Icon not found in any renderer
                if fail_silently:
                    return ""

                # Provide helpful error message
                available = sorted(_icon_registry.keys())
                raise IconNotFoundError(
                    f"Icon '{name}' not found in any configured renderer. "
                    f"Available icons: {', '.join(available[:10])}"
                    f"{' ...' if len(available) > 10 else ''}"
                )
        else:
            # Registry not built - fall back to 'default' for backwards compatibility
            renderer = "default"

    # Render with the determined renderer
    try:
        renderer_instance = get_renderer(renderer)
        return cast(SafeString, renderer_instance(name, **kwargs))
    except IconNotFoundError:
        # Icon not found in the specific renderer
        if fail_silently:
            return ""
        raise
