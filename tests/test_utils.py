"""Tests for easy_icons.utils."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template
from django.test import override_settings
from django.utils.safestring import SafeString

from easy_icons import icon as easy_icon
from easy_icons import utils
from easy_icons.exceptions import IconNotFoundError
from easy_icons.renderers import ProviderRenderer, SpritesRenderer, SvgRenderer
from easy_icons.utils import clear_cache

# Packs used to verify per-layer precedence during alias expansion.
PACK_WITH_ALIASES = {
    "plus,create,add": "pack-plus",
    "home": "pack-home",
}

# Test pack data structures
PACK_ONE = {
    "home": "home-v1.svg",
    "user": "user-v1.svg",
    "star": "star-v1.svg",
}

PACK_TWO = {
    "user": "user-v2.svg",  # Override from PACK_ONE
    "heart": "heart-v2.svg",  # New icon
}

PACK_THREE = {
    "star": "star-v3.svg",  # Override from PACK_ONE
    "admin": "admin-v3.svg",  # New icon
}

FONTAWESOME_PACK = {
    "heart": "fa-heart",
    "star": "fa-star",
}

INVALID_PACK = ["not", "a", "dictionary"]


class TestGetRenderer:
    """Test cases for the get_renderer function."""

    def setup_method(self):
        """Clear cache before each test."""
        utils.clear_cache()

    def test_get_renderer_default(self):
        """Test getting default renderer."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer()

            assert isinstance(renderer, SvgRenderer)
            assert renderer.svg_dir == "icons"
            assert renderer.icons == {"home": "home.svg"}

    def test_get_renderer_named(self):
        """Test getting named renderer."""
        config = {
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"heart": "fa-heart"},
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer("fontawesome")

            assert isinstance(renderer, ProviderRenderer)
            assert renderer.tag == "i"
            assert renderer.icons == {"heart": "fa-heart"}

    def test_get_renderer_caching(self):
        """Test that renderers are cached."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer1 = utils.get_renderer()
            renderer2 = utils.get_renderer()

            assert renderer1 is renderer2  # Same instance

    def test_get_renderer_no_easy_icons_setting(self):
        """Test get_renderer with no EASY_ICONS setting."""
        # Test with completely missing EASY_ICONS setting (empty dict behavior)
        with override_settings(EASY_ICONS={}):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "Renderer 'default' is not configured" in str(exc_info.value)

    def test_get_renderer_invalid_setting_type(self):
        """Test get_renderer with invalid EASY_ICONS setting type."""
        with override_settings(EASY_ICONS="not a dict"):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "EASY_ICONS setting must be a dictionary" in str(exc_info.value)

    def test_get_renderer_missing_renderer_config(self):
        """Test get_renderer with missing renderer in config."""
        config = {
            "other": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {},
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer("missing")

            assert "Renderer 'missing' is not configured" in str(exc_info.value)

    def test_get_renderer_invalid_renderer_config_type(self):
        """Test get_renderer with invalid renderer config type."""
        config = {"default": "not a dict"}

        with override_settings(EASY_ICONS=config):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "EASY_ICONS['default'] must be a dictionary" in str(exc_info.value)

    def test_get_renderer_missing_renderer_class(self):
        """Test get_renderer with missing renderer class path."""
        config = {"default": {"config": {}, "icons": {}}}

        with override_settings(EASY_ICONS=config):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "must specify a 'renderer' class path" in str(exc_info.value)

    def test_get_renderer_invalid_renderer_class(self):
        """Test get_renderer with invalid renderer class path."""
        config = {
            "default": {
                "renderer": "nonexistent.module.RendererClass",
                "config": {},
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "Cannot import renderer class" in str(exc_info.value)

    def test_get_renderer_renderer_instantiation_error(self):
        """Test get_renderer with renderer instantiation error."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {},  # Missing required sprite_url
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "Cannot instantiate renderer" in str(exc_info.value)

    def test_get_renderer_config_none(self):
        """Test get_renderer with None config values."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": None,
                "icons": None,
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer()

            assert isinstance(renderer, SvgRenderer)
            assert renderer.icons == {}

    def test_get_renderer_missing_config_and_icons(self):
        """Test get_renderer with missing config and icons sections."""
        config = {"default": {"renderer": "easy_icons.renderers.SvgRenderer"}}

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer()

            assert isinstance(renderer, SvgRenderer)
            assert renderer.icons == {}
            assert renderer.default_attrs == {}

    def test_get_renderer_complex_config(self):
        """Test get_renderer with complex configuration."""
        config = {
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {
                    "sprite_url": "/static/icons.svg",
                    "default_attrs": {"class": "sprite", "width": "24"},
                },
                "icons": {"logo": "brand-logo", "menu": "hamburger"},
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer("sprites")

            assert isinstance(renderer, SpritesRenderer)
            assert renderer.sprite_url == "/static/icons.svg"
            assert renderer.default_attrs == {"class": "sprite", "width": "24"}
            assert renderer.icons == {"logo": "brand-logo", "menu": "hamburger"}


class TestClearCache:
    """Test cases for the clear_cache function."""

    def test_clear_cache(self):
        """Test that clear_cache clears the renderer cache."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {},
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config):
            # Get renderer to populate cache
            renderer1 = utils.get_renderer()

            # Clear cache
            utils.clear_cache()

            # Get renderer again - should be new instance
            renderer2 = utils.get_renderer()

            assert renderer1 is not renderer2

    def test_clear_cache_empty(self):
        """Test clearing cache when it's already empty."""
        utils.clear_cache()
        utils.clear_cache()


class TestIcon:
    """Test cases for the icon function."""

    def test_icon_default_renderer(self):
        """Test icon function with default renderer."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            }
        }

        with override_settings(EASY_ICONS=config):
            with patch("easy_icons.renderers.render_to_string") as mock_render:
                mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'

                result = utils.icon("home")

                assert isinstance(result, SafeString)
                mock_render.assert_called_once_with("icons/home.svg")

    def test_icon_named_renderer(self):
        """Test icon function with named renderer."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {},
                "icons": {"home": "home.svg"},
            },
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"heart": "fa-heart"},
            },
        }

        with override_settings(EASY_ICONS=config):
            result = utils.icon("heart", renderer="fontawesome")

            assert isinstance(result, SafeString)
            assert '<i class="fa-heart"' in result

    def test_icon_with_attributes(self):
        """Test icon function with additional attributes."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"star": "fa-star"},
            }
        }

        with override_settings(EASY_ICONS=config):
            result = utils.icon("star", **{"class": "large", "data-role": "button"})

            # May have separate class attributes
            assert "fa-star" in result and "large" in result
            assert 'data-role="button"' in result

    def test_icon_use_defaults_false(self):
        """Test icon function with use_defaults=False."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i", "default_attrs": {"class": "icon"}},
                "icons": {"check": "fa-check"},
            }
        }

        with override_settings(EASY_ICONS=config):
            test_attrs = {"class": "custom"}
            result = utils.icon("check", use_defaults=False, **test_attrs)

            # ProviderRenderer always includes the icon class along with custom class
            assert "fa-check" in result and "custom" in result
            assert 'class="icon' not in result

    def test_icon_renderer_not_found(self):
        """Test icon function with non-existent renderer."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {},
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config), pytest.raises(ImproperlyConfigured):
            utils.icon("test", renderer="nonexistent")

    def test_icon_caching_across_calls(self):
        """Test that icon function uses cached renderers."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fa-home", "user": "fa-user"},
            }
        }

        with override_settings(EASY_ICONS=config):
            # Multiple calls should use same renderer instance
            result1 = utils.icon("home")
            result2 = utils.icon("user")

            assert "fa-home" in result1
            assert "fa-user" in result2

    def test_icon_multiple_renderers(self):
        """Test icon function with multiple configured renderers."""
        config = {
            "svg": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            },
            "fa": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"heart": "fa-heart"},
            },
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {"sprite_url": "/icons.svg"},
                "icons": {"logo": "brand"},
            },
        }

        with override_settings(EASY_ICONS=config):
            with patch("easy_icons.renderers.render_to_string") as mock_render:
                mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'

                svg_result = utils.icon("home", renderer="svg")
                fa_result = utils.icon("heart", renderer="fa")
                sprite_result = utils.icon("logo", renderer="sprites")

                assert "<svg" in svg_result
                assert '<i class="fa-heart"' in fa_result
                assert '<use href="/icons.svg#brand"' in sprite_result


class TestExpandAliases:
    """Unit tests for the low-level ``_expand_aliases`` helper."""

    def test_key_without_comma_unchanged(self):
        """A plain key is copied through untouched."""
        assert utils._expand_aliases({"home": "home.svg"}) == {"home": "home.svg"}

    def test_empty_mapping(self):
        """An empty mapping expands to an empty mapping."""
        assert utils._expand_aliases({}) == {}

    def test_comma_key_expands_to_each_alias(self):
        """Every comma-separated alias maps to the shared value."""
        result = utils._expand_aliases({"plus,create,add,new": "bi bi-plus"})
        assert result == {
            "plus": "bi bi-plus",
            "create": "bi bi-plus",
            "add": "bi bi-plus",
            "new": "bi bi-plus",
        }

    def test_whitespace_around_aliases_is_stripped(self):
        """Surrounding whitespace on each alias is ignored."""
        result = utils._expand_aliases({" plus , create ,add ": "bi bi-plus"})
        assert result == {
            "plus": "bi bi-plus",
            "create": "bi bi-plus",
            "add": "bi bi-plus",
        }

    def test_empty_aliases_are_dropped(self):
        """Blank tokens from stray/trailing commas are discarded."""
        result = utils._expand_aliases({"plus,,create,": "bi bi-plus"})
        assert result == {"plus": "bi bi-plus", "create": "bi bi-plus"}

    def test_mixed_plain_and_alias_keys(self):
        """Plain and aliased keys coexist in one mapping."""
        result = utils._expand_aliases({"home": "home.svg", "plus,add": "plus.svg"})
        assert result == {
            "home": "home.svg",
            "plus": "plus.svg",
            "add": "plus.svg",
        }


class TestResolveIconsWithAliases:
    """Alias behaviour through the ``resolve_icons`` merge path."""

    def test_explicit_icons_aliases_expanded(self):
        """Aliases declared in explicit ``icons`` are expanded."""
        config = {"icons": {"plus,create,add": "bi bi-plus"}}
        resolved = utils.resolve_icons(config, "default")
        assert resolved["plus"] == "bi bi-plus"
        assert resolved["create"] == "bi bi-plus"
        assert resolved["add"] == "bi bi-plus"

    def test_pack_aliases_expanded(self):
        """Aliases declared inside a pack are expanded."""
        config = {"packs": ["tests.test_utils.PACK_WITH_ALIASES"]}
        resolved = utils.resolve_icons(config, "default")
        assert resolved["plus"] == "pack-plus"
        assert resolved["create"] == "pack-plus"
        assert resolved["add"] == "pack-plus"
        assert resolved["home"] == "pack-home"

    def test_explicit_alias_overrides_pack_per_name(self):
        """Explicit icons override pack values at the individual-name level.

        The pack aliases ``plus``/``create``/``add`` to ``pack-plus``; the
        explicit config re-aliases only ``add``/``remove``. ``add`` must take
        the explicit value while the untouched pack aliases survive.
        """
        config = {
            "packs": ["tests.test_utils.PACK_WITH_ALIASES"],
            "icons": {"add,remove": "explicit-value"},
        }
        resolved = utils.resolve_icons(config, "default")
        assert resolved["add"] == "explicit-value"  # explicit wins
        assert resolved["remove"] == "explicit-value"
        assert resolved["plus"] == "pack-plus"  # untouched pack aliases remain
        assert resolved["create"] == "pack-plus"


class TestAliasesEndToEnd:
    """Aliases resolve through the public renderer and registry paths."""

    def _config(self):
        return {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"plus,create,add,new": "bi bi-plus"},
            }
        }

    def test_get_renderer_resolves_every_alias(self):
        """A renderer instance resolves each alias to the same identifier."""
        with override_settings(EASY_ICONS=self._config()):
            renderer = utils.get_renderer("default")
            for alias in ("plus", "create", "add", "new"):
                assert renderer.get_icon(alias) == "bi bi-plus"

    def test_registry_registers_every_alias(self):
        """The auto-detection registry indexes each alias name."""
        with override_settings(EASY_ICONS=self._config()):
            utils.build_icon_registry()
            for alias in ("plus", "create", "add", "new"):
                assert utils._icon_registry.get(alias) == "default"

    def test_icon_renders_via_any_alias(self):
        """The public ``icon()`` helper renders through any alias."""
        with override_settings(EASY_ICONS=self._config()):
            utils.build_icon_registry()
            html_plus = utils.icon("plus")
            html_add = utils.icon("add")
            assert "bi bi-plus" in html_plus
            assert "bi bi-plus" in html_add


class TestPackLoading:
    """Test basic pack loading functionality."""

    def test_load_single_pack(self):
        """Test loading a single pack."""
        result = utils.load_and_merge_packs(
            ["tests.test_utils.PACK_ONE"], "test_renderer"
        )
        assert result == PACK_ONE

    def test_load_multiple_packs_last_wins(self):
        """Test that later packs override earlier packs."""
        result = utils.load_and_merge_packs(
            [
                "tests.test_utils.PACK_ONE",
                "tests.test_utils.PACK_TWO",
            ],
            "test_renderer",
        )

        # PACK_TWO should override 'user' from PACK_ONE
        assert result["user"] == "user-v2.svg"
        # Original values should remain
        assert result["home"] == "home-v1.svg"
        assert result["star"] == "star-v1.svg"
        # New values from PACK_TWO
        assert result["heart"] == "heart-v2.svg"

    def test_load_three_packs_sequential_override(self):
        """Test that three packs merge with proper precedence."""
        result = utils.load_and_merge_packs(
            [
                "tests.test_utils.PACK_ONE",
                "tests.test_utils.PACK_TWO",
                "tests.test_utils.PACK_THREE",
            ],
            "test_renderer",
        )

        # PACK_THREE overrides 'star'
        assert result["star"] == "star-v3.svg"
        # PACK_TWO overrides 'user'
        assert result["user"] == "user-v2.svg"
        # PACK_ONE's 'home' remains
        assert result["home"] == "home-v1.svg"
        # New icons from each pack
        assert result["heart"] == "heart-v2.svg"
        assert result["admin"] == "admin-v3.svg"

    def test_load_invalid_import_path(self, caplog):
        """Test that invalid import paths log warnings and are skipped."""
        result = utils.load_and_merge_packs(
            [
                "tests.test_utils.PACK_ONE",
                "tests.test_utils.NONEXISTENT_PACK",
            ],
            "test_renderer",
        )

        # Should still load PACK_ONE
        assert result == PACK_ONE
        # Should log warning
        assert "Cannot import pack" in caplog.text
        assert "NONEXISTENT_PACK" in caplog.text

    def test_load_non_dict_pack(self, caplog):
        """Test that non-dict packs log warnings and are skipped."""
        result = utils.load_and_merge_packs(
            [
                "tests.test_utils.PACK_ONE",
                "tests.test_utils.INVALID_PACK",
            ],
            "test_renderer",
        )

        # Should still load PACK_ONE
        assert result == PACK_ONE
        # Should log warning
        assert "is not a dictionary" in caplog.text
        assert "INVALID_PACK" in caplog.text

    def test_load_empty_packs_list(self):
        """Test that empty packs list returns empty dict."""
        result = utils.load_and_merge_packs([], "test_renderer")
        assert result == {}


class TestPacksInRendererConfig:
    """Test packs configuration in EASY_ICONS renderer settings."""

    def setup_method(self):
        """Clear cache before each test."""
        utils.clear_cache()

    def test_renderer_with_single_pack(self):
        """Test renderer loads icons from single pack."""
        config = {
            "test": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "packs": ["tests.test_utils.PACK_ONE"],
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer("test")
            assert renderer.icons == PACK_ONE

    def test_renderer_with_multiple_packs(self):
        """Test renderer merges multiple packs with last-wins."""
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.PACK_ONE",
                        "tests.test_utils.PACK_TWO",
                    ],
                    "icons": {},
                }
            }
        ):
            renderer = utils.get_renderer("test")

            # PACK_TWO should override 'user'
            assert renderer.icons["user"] == "user-v2.svg"
            assert renderer.icons["home"] == "home-v1.svg"
            assert renderer.icons["heart"] == "heart-v2.svg"

    def test_explicit_icons_override_packs(self):
        """Test that explicit icons in 'icons' key override pack values."""
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.PACK_ONE",
                        "tests.test_utils.PACK_TWO",
                    ],
                    "icons": {
                        "user": "user-explicit.svg",
                        "custom": "custom.svg",
                    },
                }
            }
        ):
            renderer = utils.get_renderer("test")

            # Explicit 'user' should override both packs
            assert renderer.icons["user"] == "user-explicit.svg"
            # Pack icons should still be present
            assert renderer.icons["home"] == "home-v1.svg"
            assert renderer.icons["heart"] == "heart-v2.svg"
            # Explicit custom icon
            assert renderer.icons["custom"] == "custom.svg"

    def test_renderer_without_packs_key(self):
        """Test renderer works without 'packs' key (backwards compatible)."""
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "icons": {
                        "only": "explicit.svg",
                    },
                }
            }
        ):
            renderer = utils.get_renderer("test")

            assert renderer.icons == {"only": "explicit.svg"}

    def test_renderer_with_empty_packs_list(self):
        """Test renderer with empty packs list."""
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [],
                    "icons": {"only": "explicit.svg"},
                }
            }
        ):
            renderer = utils.get_renderer("test")

            assert renderer.icons == {"only": "explicit.svg"}


class TestIconRegistryWithPacks:
    """Test icon registry building with packs."""

    def setup_method(self):
        """Clear cache before each test."""
        utils.clear_cache()

    def test_registry_builds_with_packs(self):
        """Test that icon registry includes pack icons."""
        with override_settings(
            EASY_ICONS={
                "svg": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": ["tests.test_utils.PACK_ONE"],
                    "icons": {},
                }
            }
        ):
            utils.build_icon_registry()

            # All icons from PACK_ONE should be registered
            assert utils._icon_registry["home"] == "svg"
            assert utils._icon_registry["user"] == "svg"
            assert utils._icon_registry["star"] == "svg"

    def test_registry_with_multiple_renderers_and_packs(self):
        """Test registry with multiple renderers each having packs."""
        with override_settings(
            EASY_ICONS={
                "svg": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": ["tests.test_utils.PACK_ONE"],
                    "icons": {"custom": "custom.svg"},
                },
                "fontawesome": {
                    "renderer": "easy_icons.renderers.ProviderRenderer",
                    "packs": ["tests.test_utils.FONTAWESOME_PACK"],
                    "icons": {},
                },
            }
        ):
            utils.build_icon_registry()

            # SVG renderer icons
            assert utils._icon_registry["home"] == "svg"
            assert utils._icon_registry["custom"] == "svg"

            # FontAwesome icons (note: 'star' will be collision)
            assert utils._icon_registry["heart"] == "fontawesome"

    def test_registry_respects_explicit_icon_precedence(self):
        """Test that explicit icons override pack icons in registry."""
        with override_settings(
            EASY_ICONS={
                "svg": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.PACK_ONE",
                        "tests.test_utils.PACK_TWO",
                    ],
                    "icons": {"user": "user-explicit.svg"},
                }
            }
        ):
            utils.build_icon_registry()

            # Verify icons are registered
            assert "user" in utils._icon_registry
            assert "home" in utils._icon_registry

            # Get renderer and verify icon values
            renderer = utils.get_renderer("svg")
            assert renderer.icons["user"] == "user-explicit.svg"
            assert renderer.icons["home"] == "home-v1.svg"

    def test_default_renderer_wins_collisions(self, caplog):
        """Test that 'default' renderer has priority in collisions."""
        with override_settings(
            EASY_ICONS={
                "default": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": ["tests.test_utils.PACK_ONE"],
                    "icons": {},
                },
                "other": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": ["tests.test_utils.PACK_TWO"],
                    "icons": {},
                },
            }
        ):
            utils.build_icon_registry()

            # 'user' is in both packs - default should win
            assert utils._icon_registry["user"] == "default"

            # Should log collision warning
            assert "Icon name collision" in caplog.text
            assert "user" in caplog.text


class TestIconRenderingWithPacks:
    """Test actual icon rendering using packs."""

    def setup_method(self):
        """Clear cache before each test."""
        utils.clear_cache()

    def test_render_icon_from_pack(self):
        """Test rendering an icon defined in a pack."""
        with override_settings(
            EASY_ICONS={
                "default": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "config": {"svg_dir": "icons"},
                    "packs": ["tests.test_utils.PACK_ONE"],
                    "icons": {},
                }
            },
            EASY_ICONS_FAIL_SILENTLY=False,
        ):
            utils.build_icon_registry()

            # Icon exists in pack, but won't render without actual file
            # Just verify it's found in the renderer
            renderer = utils.get_renderer("default")
            assert "home" in renderer.icons
            assert renderer.icons["home"] == "home-v1.svg"

    def test_explicit_icon_renders_over_pack(self):
        """Test that explicit icon definition is used for rendering."""
        with override_settings(
            EASY_ICONS={
                "fontawesome": {
                    "renderer": "easy_icons.renderers.ProviderRenderer",
                    "config": {"tag": "i"},
                    "packs": ["tests.test_utils.FONTAWESOME_PACK"],
                    "icons": {"custom": "fa-custom"},
                }
            }
        ):
            renderer = utils.get_renderer("fontawesome")

            # Pack icon
            result = renderer.render("heart")
            assert 'class="fa-heart"' in result

            # Explicit icon
            result = renderer.render("custom")
            assert 'class="fa-custom"' in result


class TestPacksEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Clear cache before each test."""
        utils.clear_cache()

    def test_all_packs_invalid_uses_explicit_icons(self, caplog):
        """Test that if all packs fail, explicit icons still work."""
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.INVALID_PACK",
                    ],
                    "icons": {"fallback": "fallback.svg"},
                }
            }
        ):
            renderer = utils.get_renderer("test")

            # Should have only explicit icon
            assert renderer.icons == {"fallback": "fallback.svg"}
            # Should log warning
            assert "is not a dictionary" in caplog.text

    def test_duplicate_pack_paths(self):
        """Test that duplicate pack paths work (just reload same data)."""
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.PACK_ONE",
                        "tests.test_utils.PACK_ONE",  # Duplicate
                    ],
                    "icons": {},
                }
            }
        ):
            renderer = utils.get_renderer("test")

            # Should have PACK_ONE data (loaded twice but identical)
            assert renderer.icons == PACK_ONE

    def test_explicit_icons_override_all_packs(self):
        """Test that explicit icons override all pack definitions."""
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.PACK_ONE",
                        "tests.test_utils.PACK_TWO",
                        "tests.test_utils.PACK_THREE",
                    ],
                    "icons": {
                        "home": "home-final.svg",
                        "user": "user-final.svg",
                        "star": "star-final.svg",
                    },
                }
            }
        ):
            renderer = utils.get_renderer("test")

            # All three icons should use explicit values
            assert renderer.icons["home"] == "home-final.svg"
            assert renderer.icons["user"] == "user-final.svg"
            assert renderer.icons["star"] == "star-final.svg"

            # Pack-only icons should still exist
            assert renderer.icons["heart"] == "heart-v2.svg"
            assert renderer.icons["admin"] == "admin-v3.svg"


class TestIconRegistry:
    """Test cases for the icon registry auto-detection system."""

    def setup_method(self):
        """Clear caches before each test."""
        utils.clear_cache()
        utils._icon_registry.clear()

    def test_build_icon_registry_default_first(self):
        """Test that 'default' renderer is processed first."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {
                    "home": "home.svg",
                    "star": "star-default.svg",
                },
            },
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {
                    "heart": "fas fa-heart",
                    "star": "fas fa-star",  # Collision with default
                },
            },
        }

        with override_settings(EASY_ICONS=config):
            utils.build_icon_registry()

            # Default icons should be registered
            assert utils._icon_registry.get("home") == "default"
            assert utils._icon_registry.get("star") == "default"  # Default wins

            # FontAwesome unique icon should be registered
            assert utils._icon_registry.get("heart") == "fontawesome"

    def test_build_icon_registry_order_matters(self):
        """Test that renderer order matters for collisions."""
        config = {
            "renderer_a": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"duplicate": "a-value"},
            },
            "renderer_b": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "span"},
                "icons": {"duplicate": "b-value"},
            },
        }

        with override_settings(EASY_ICONS=config):
            utils.build_icon_registry()

            # First renderer should win (no 'default', so insertion order)
            assert utils._icon_registry.get("duplicate") == "renderer_a"

    def test_build_icon_registry_skips_uppercase_keys(self):
        """Test that uppercase config keys are skipped."""
        config = {
            "SOME_CONFIG": True,
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            },
        }

        with override_settings(EASY_ICONS=config):
            utils.build_icon_registry()

            assert utils._icon_registry.get("home") == "default"
            assert "SOME_CONFIG" not in utils._icon_registry

    def test_build_icon_registry_handles_invalid_config(self):
        """Test that invalid renderer configs are skipped gracefully."""
        config = {
            "invalid": "not a dict",
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            },
        }

        with override_settings(EASY_ICONS=config):
            utils.build_icon_registry()

            # Should still register valid renderers
            assert utils._icon_registry.get("home") == "default"

    def test_build_icon_registry_collision_logging(self, caplog):
        """Test that icon collisions are logged as warnings."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"star": "star.svg"},
            },
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"star": "fas fa-star"},
            },
        }

        with override_settings(EASY_ICONS=config):
            utils.build_icon_registry()

            # Check that warning was logged
            assert any(
                "Icon name collision" in record.message for record in caplog.records
            )
            assert any("'star'" in record.message for record in caplog.records)


class TestIconAutoDetection:
    """Test cases for automatic renderer detection."""

    def setup_method(self):
        """Clear caches before each test."""
        utils.clear_cache()
        utils._icon_registry.clear()

    def test_icon_auto_detection_from_default(self):
        """Test auto-detecting icon from default renderer."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()
            result = utils.icon("home")

            assert "fas fa-home" in result
            assert "<i" in result

    def test_icon_auto_detection_from_non_default(self):
        """Test auto-detecting icon from non-default renderer."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {"sprite_url": "/sprites.svg"},
                "icons": {"logo": "brand-logo"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()
            result = utils.icon("logo")  # Only in sprites

            assert "brand-logo" in result
            assert "<svg" in result

    def test_icon_explicit_renderer_overrides_auto_detection(self):
        """Test that explicit renderer parameter overrides auto-detection."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"star": "fas fa-star"},
            },
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {"sprite_url": "/sprites.svg"},
                "icons": {"star": "star-sprite"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()

            # Auto-detect uses default
            auto_result = utils.icon("star")
            assert "fas fa-star" in auto_result

            # Explicit renderer uses sprites
            explicit_result = utils.icon("star", renderer="sprites")
            assert "star-sprite" in explicit_result


class TestIconFailSilently:
    """Test cases for EASY_ICONS_FAIL_SILENTLY setting."""

    def setup_method(self):
        """Clear caches before each test."""
        utils.clear_cache()
        utils._icon_registry.clear()

    def test_fail_silently_true_returns_empty_string(self):
        """Test that missing icons return empty string when fail_silently=True."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
        }

        with override_settings(EASY_ICONS=config, EASY_ICONS_FAIL_SILENTLY=True):
            utils.build_icon_registry()
            result = utils.icon("missing-icon")

            assert result == ""

    def test_fail_silently_false_raises_error(self):
        """Test that missing icons raise error when fail_silently=False."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()

            with pytest.raises(IconNotFoundError) as exc_info:
                utils.icon("missing-icon")

            assert "missing-icon" in str(exc_info.value)
            assert "not found in any configured renderer" in str(exc_info.value)

    def test_fail_silently_defaults_to_debug(self):
        """Test that fail_silently defaults to DEBUG setting."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
        }

        # When DEBUG=True, should fail silently
        with override_settings(EASY_ICONS=config, DEBUG=True):
            utils.build_icon_registry()
            result = utils.icon("missing-icon")
            assert result == ""

        # When DEBUG=False, should raise error
        with override_settings(EASY_ICONS=config, DEBUG=False):
            utils.build_icon_registry()
            with pytest.raises(IconNotFoundError):
                utils.icon("missing-icon")

    def test_fail_silently_with_explicit_renderer_not_found(self):
        """Test fail_silently when icon not found in explicit renderer."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
        }

        with override_settings(EASY_ICONS=config, EASY_ICONS_FAIL_SILENTLY=True):
            utils.build_icon_registry()
            # Icon doesn't exist in default renderer
            result = utils.icon("missing-icon", renderer="default")

            assert result == ""

    def test_helpful_error_message_lists_available_icons(self):
        """Test that error message includes available icons."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {
                    "home": "fas fa-home",
                    "heart": "fas fa-heart",
                    "star": "fas fa-star",
                },
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()

            with pytest.raises(IconNotFoundError) as exc_info:
                utils.icon("missing")

            error_message = str(exc_info.value)
            assert "Available icons:" in error_message
            # Should list some available icons
            assert any(icon in error_message for icon in ["home", "heart", "star"])


class TestIconRegistryWithNoDefault:
    """Test cases for icon registry when no 'default' renderer exists."""

    def setup_method(self):
        """Clear caches before each test."""
        utils.clear_cache()
        utils._icon_registry.clear()

    def test_registry_works_without_default_renderer(self):
        """Test that registry works when no 'default' renderer is configured."""
        config = {
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {"sprite_url": "/sprites.svg"},
                "icons": {"logo": "brand-logo"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()

            # Both should auto-detect based on insertion order
            home_result = utils.icon("home")
            assert "fas fa-home" in home_result

            logo_result = utils.icon("logo")
            assert "brand-logo" in logo_result

    def test_first_renderer_wins_without_default(self):
        """Test that first renderer wins when there's no default."""
        config = {
            "renderer_a": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"icon": "a-value"},
            },
            "renderer_b": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "span"},
                "icons": {"icon": "b-value"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()

            result = utils.icon("icon")
            assert "a-value" in result


class TestMultiRendererIntegration:
    """Integration tests using multiple renderers together."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_cache()

    def test_multiple_renderers_in_same_template(self):
        """Test using multiple renderers in the same template."""
        config = {
            "svg": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            },
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i", "default_attrs": {"class": "fas"}},
                "icons": {"heart": "fa-heart", "star": "fa-star"},
            },
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {"sprite_url": "/static/icons.svg"},
                "icons": {"logo": "brand-logo", "menu": "hamburger"},
            },
        }

        template_content = """
        {% load easy_icons %}
        <nav>
            {% icon 'home' renderer='svg' class='nav-icon' %}
            {% icon 'heart' renderer='fontawesome' class='like-btn' %}
            {% icon 'logo' renderer='sprites' class='brand' %}
        </nav>
        """

        with override_settings(EASY_ICONS=config):
            with patch("easy_icons.renderers.render_to_string") as mock_render:
                mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'

                template = Template(template_content)
                result = template.render(Context())

                # Should contain output from all three renderers
                assert "<svg" in result  # SVG renderer
                # FA renderer - class attributes may be separate or merged
                assert "fa-heart" in result and "like-btn" in result  # FA renderer
                assert '<use href="/static/icons.svg#brand-logo"' in result  # Sprites

    def test_icon_function_with_different_renderers(self):
        """Test the icon function with different renderers."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fa-home"},
            },
            "custom": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "span", "default_attrs": {"class": "icon"}},
                "icons": {"settings": "gear-icon"},
            },
        }

        with override_settings(EASY_ICONS=config):
            # Default renderer
            result1 = easy_icon("home")
            assert '<i class="fa-home"' in result1

            # Custom renderer - may have separate class attributes
            result2 = easy_icon("settings", renderer="custom")
            assert "gear-icon" in result2 and 'class="icon"' in result2

    def test_renderer_caching_with_multiple_calls(self):
        """Test that renderer caching works correctly across multiple calls."""
        config = {
            "provider1": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"icon1": "fa-icon1", "icon2": "fa-icon2"},
            },
            "provider2": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "span"},
                "icons": {"icon3": "span-icon3"},
            },
        }

        with override_settings(EASY_ICONS=config):
            # Multiple calls to same renderer should use cached instance
            result1 = easy_icon("icon1", renderer="provider1")
            result2 = easy_icon("icon2", renderer="provider1")
            result3 = easy_icon("icon3", renderer="provider2")

            assert '<i class="fa-icon1"' in result1
            assert '<i class="fa-icon2"' in result2
            assert '<span class="span-icon3"' in result3

    def test_complex_configuration_integration(self):
        """Test integration with complex configuration scenarios."""
        config = {
            "main": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {
                    "svg_dir": "assets/icons",
                    "default_attrs": {
                        "class": "svg-icon",
                        "height": "1em",
                        "fill": "currentColor",
                    },
                },
                "icons": {
                    "home": "house.svg",
                    "user": "person.svg",
                    "search": "magnifying-glass.svg",
                },
            },
            "social": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i", "default_attrs": {"class": "fab"}},
                "icons": {
                    "facebook": "fa-facebook",
                    "twitter": "fa-twitter",
                    "linkedin": "fa-linkedin",
                },
            },
        }

        with override_settings(EASY_ICONS=config):
            with patch("easy_icons.renderers.render_to_string") as mock_render:
                mock_render.return_value = (
                    '<svg viewBox="0 0 24 24"><path d="M0 0L10 10"/></svg>'
                )

                # Test SVG renderer with defaults and overrides
                home_result = easy_icon("home", renderer="main")
                assert 'class="svg-icon"' in home_result
                assert 'height="1em"' in home_result
                assert 'fill="currentColor"' in home_result

                # Test with overrides - use star unpacking
                search_result = easy_icon(
                    "search", renderer="main", width="2em", **{"class": "search-icon"}
                )
                assert (
                    "search-icon" in search_result
                )  # Should override, not merge with svg-icon
                assert "svg-icon" not in search_result  # Should be overridden
                assert 'width="2em"' in search_result

                # Test provider renderer - may have separate class attributes
                fb_result = easy_icon("facebook", renderer="social")
                assert "fa-facebook" in fb_result and "fab" in fb_result

    def test_error_handling_integration(self):
        """Test error handling across different scenarios."""
        config = {
            "test": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"valid": "fa-valid"},
            }
        }

        with override_settings(EASY_ICONS=config):
            # Valid icon should work
            result = easy_icon("valid", renderer="test")
            assert "fa-valid" in result

            # Invalid icon should raise error
            from easy_icons.exceptions import IconNotFoundError

            with pytest.raises(IconNotFoundError):
                easy_icon("invalid", renderer="test")

            # Invalid renderer should raise error
            from django.core.exceptions import ImproperlyConfigured

            with pytest.raises(ImproperlyConfigured):
                easy_icon("valid", renderer="nonexistent")

    def test_template_integration_with_context(self):
        """Test template integration with dynamic context variables."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {
                    "home": "fa-home",
                    "user": "fa-user",
                    "admin": "fa-user-shield",
                    "settings": "fa-cog",
                },
            }
        }

        template_content = """
        {% load easy_icons %}
        <div class="menu">
            {% for item in menu_items %}
                <a href="{{ item.url }}" class="{{ item.css_class }}">
                    {% icon item.icon class=item.icon_class %}
                    {{ item.label }}
                </a>
            {% endfor %}
        </div>
        """

        context_data = {
            "menu_items": [
                {
                    "url": "/",
                    "label": "Home",
                    "icon": "home",
                    "css_class": "nav-link",
                    "icon_class": "nav-icon",
                },
                {
                    "url": "/profile",
                    "label": "Profile",
                    "icon": "user",
                    "css_class": "nav-link active",
                    "icon_class": "nav-icon primary",
                },
                {
                    "url": "/admin",
                    "label": "Admin",
                    "icon": "admin",
                    "css_class": "nav-link admin",
                    "icon_class": "nav-icon admin-icon",
                },
            ]
        }

        with override_settings(EASY_ICONS=config):
            template = Template(template_content)
            result = template.render(Context(context_data))

            # Verify all icons rendered correctly
            assert "fa-home nav-icon" in result
            assert "fa-user nav-icon primary" in result
            assert "fa-user-shield nav-icon admin-icon" in result

            # Verify structure
            assert "nav-link" in result
            assert "nav-link active" in result
            assert "nav-link admin" in result

    def test_attribute_merging_edge_cases(self):
        """Test attribute merging in various edge cases."""
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {
                    "tag": "i",
                    "default_attrs": {
                        "class": "icon base",
                        "role": "img",
                        "aria-hidden": "true",
                    },
                },
                "icons": {"test": "fa-test"},
            }
        }

        with override_settings(EASY_ICONS=config):
            # Test class override - ProviderRenderer creates duplicate class attributes
            result1 = easy_icon("test", **{"class": "additional custom"})
            # Check that provided class appears in the css_class and icon class appears
            assert (
                "fa-test" in result1 and "additional" in result1 and "custom" in result1
            )
            # ProviderRenderer has both classes due to its design (icon class + separate class attribute)
            assert "icon" in result1 and "base" in result1

            # Test attribute override - should override default role
            result2 = easy_icon("test", role="button", **{"data-action": "click"})
            assert 'role="button"' in result2  # Should override default role="img"
            assert 'role="img"' not in result2  # Should be overridden
            assert 'aria-hidden="true"' in result2
            assert 'data-action="click"' in result2

            # Test use_defaults=False
            result3 = easy_icon("test", use_defaults=False, **{"class": "only-this"})
            assert "only-this" in result3 and "fa-test" in result3
            assert 'role="img"' not in result3
            assert 'aria-hidden="true"' not in result3
