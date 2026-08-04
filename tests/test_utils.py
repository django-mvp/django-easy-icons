"""Tests for the utils module."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.utils.safestring import SafeString

from easy_icons import utils
from easy_icons.renderers import ProviderRenderer, SpritesRenderer, SvgRenderer


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
        config = {"other": {"renderer": "easy_icons.renderers.SvgRenderer", "config": {}, "icons": {}}}

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
        config = {"default": {"renderer": "nonexistent.module.RendererClass", "config": {}, "icons": {}}}

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
        config = {"default": {"renderer": "easy_icons.renderers.SvgRenderer", "config": None, "icons": None}}

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
                "config": {"sprite_url": "/static/icons.svg", "default_attrs": {"class": "sprite", "width": "24"}},
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
        config = {"default": {"renderer": "easy_icons.renderers.SvgRenderer", "config": {}, "icons": {}}}

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
        utils.clear_cache()  # Should not raise error


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
            "default": {"renderer": "easy_icons.renderers.SvgRenderer", "config": {}, "icons": {"home": "home.svg"}},
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
        config = {"default": {"renderer": "easy_icons.renderers.SvgRenderer", "config": {}, "icons": {}}}

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
