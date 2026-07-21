"""Tests for icon pack loading and merging functionality."""

from django.test import override_settings

from easy_icons import utils

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


class TestPackLoading:
    """Test basic pack loading functionality."""

    def test_load_single_pack(self):
        """Test loading a single pack."""
        result = utils.load_and_merge_packs(["tests.test_icon_packs.PACK_ONE"], "test_renderer")
        assert result == PACK_ONE

    def test_load_multiple_packs_last_wins(self):
        """Test that later packs override earlier packs."""
        result = utils.load_and_merge_packs(
            [
                "tests.test_icon_packs.PACK_ONE",
                "tests.test_icon_packs.PACK_TWO",
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
                "tests.test_icon_packs.PACK_ONE",
                "tests.test_icon_packs.PACK_TWO",
                "tests.test_icon_packs.PACK_THREE",
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
                "tests.test_icon_packs.PACK_ONE",
                "tests.test_icon_packs.NONEXISTENT_PACK",
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
                "tests.test_icon_packs.PACK_ONE",
                "tests.test_icon_packs.INVALID_PACK",
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
                "packs": ["tests.test_icon_packs.PACK_ONE"],
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
                        "tests.test_icon_packs.PACK_ONE",
                        "tests.test_icon_packs.PACK_TWO",
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
                        "tests.test_icon_packs.PACK_ONE",
                        "tests.test_icon_packs.PACK_TWO",
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
                    "packs": ["tests.test_icon_packs.PACK_ONE"],
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
                    "packs": ["tests.test_icon_packs.PACK_ONE"],
                    "icons": {"custom": "custom.svg"},
                },
                "fontawesome": {
                    "renderer": "easy_icons.renderers.ProviderRenderer",
                    "packs": ["tests.test_icon_packs.FONTAWESOME_PACK"],
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
                        "tests.test_icon_packs.PACK_ONE",
                        "tests.test_icon_packs.PACK_TWO",
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
                    "packs": ["tests.test_icon_packs.PACK_ONE"],
                    "icons": {},
                },
                "other": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": ["tests.test_icon_packs.PACK_TWO"],
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
                    "packs": ["tests.test_icon_packs.PACK_ONE"],
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
                    "packs": ["tests.test_icon_packs.FONTAWESOME_PACK"],
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
                        "tests.test_icon_packs.INVALID_PACK",
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
                        "tests.test_icon_packs.PACK_ONE",
                        "tests.test_icon_packs.PACK_ONE",  # Duplicate
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
                        "tests.test_icon_packs.PACK_ONE",
                        "tests.test_icon_packs.PACK_TWO",
                        "tests.test_icon_packs.PACK_THREE",
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
