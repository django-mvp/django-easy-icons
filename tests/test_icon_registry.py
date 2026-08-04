"""Tests for icon registry and auto-detection functionality."""

import pytest
from django.test import override_settings

from easy_icons import utils
from easy_icons.exceptions import IconNotFoundError


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
            assert "a-value" in result  # First renderer wins
