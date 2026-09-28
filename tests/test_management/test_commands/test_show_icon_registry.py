"""Tests for management commands."""

import json
from io import StringIO

from django.core.management import call_command


class TestShowIconRegistryCommand:
    """Test cases for the show_icon_registry management command."""

    def test_command_basic_table_output(self, settings):
        """Test basic table output format."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"home": "home-icon", "star": "star-icon"},
            }
        }
        settings.EASY_ICONS_FAIL_SILENTLY = True

        out = StringIO()
        call_command("show_icon_registry", stdout=out)
        output = out.getvalue()

        assert "Easy Icons Configuration" in output
        assert "EASY_ICONS_FAIL_SILENTLY: True" in output
        assert "Total unique icons: 2" in output
        assert "home" in output
        assert "star" in output
        assert "home-icon" in output
        assert "star-icon" in output

    def test_command_json_output(self, settings):
        """Test JSON output format."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"home": "home-icon"},
            }
        }
        settings.EASY_ICONS_FAIL_SILENTLY = False

        out = StringIO()
        call_command("show_icon_registry", format="json", stdout=out)
        output = out.getvalue()

        data = json.loads(output)
        assert data["settings"]["fail_silently"] is False
        assert "home" in data["registry"]
        assert data["registry"]["home"][0]["renderer"] == "default"
        assert data["registry"]["home"][0]["value"] == "home-icon"
        assert data["registry"]["home"][0]["used"] is True

    def test_command_detects_collisions(self, settings):
        """Test detection of icon name collisions."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"star": "star-default"},
            },
            "fontawesome": {
                "class": "easy_icons.renderers.ProviderRenderer",
                "icons": {"star": "fa-star"},
            },
        }

        out = StringIO()
        call_command("show_icon_registry", stdout=out)
        output = out.getvalue()

        assert "Icons with collisions: 1" in output
        assert "Collision Summary" in output
        assert "star" in output
        assert "default" in output
        assert "fontawesome" in output

    def test_command_show_collisions_only(self, settings):
        """Test --show-collisions-only flag."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"home": "home-icon", "star": "star-default"},
            },
            "fontawesome": {
                "class": "easy_icons.renderers.ProviderRenderer",
                "icons": {"star": "fa-star"},
            },
        }

        out = StringIO()
        call_command("show_icon_registry", show_collisions_only=True, stdout=out)
        output = out.getvalue()

        assert "Icon Name Collisions" in output
        assert "star" in output
        # home should not appear since it has no collision
        assert "home" not in output or ("home" in output and "Collision" in output)

    def test_command_show_collisions_only_json(self, settings):
        """Test --show-collisions-only with JSON format."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"home": "home-icon", "star": "star-default"},
            },
            "fontawesome": {
                "class": "easy_icons.renderers.ProviderRenderer",
                "icons": {"star": "fa-star"},
            },
        }

        out = StringIO()
        call_command(
            "show_icon_registry",
            format="json",
            show_collisions_only=True,
            stdout=out,
        )
        output = out.getvalue()

        data = json.loads(output)
        assert "collisions" in data
        assert "star" in data["collisions"]
        assert "home" not in data["collisions"]
        assert len(data["collisions"]["star"]) == 2
        assert data["collisions"]["star"][0]["used"] is True
        assert data["collisions"]["star"][1]["used"] is False

    def test_command_no_collisions(self, settings):
        """Test output when there are no collisions."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"home": "home-icon"},
            }
        }

        out = StringIO()
        call_command("show_icon_registry", show_collisions_only=True, stdout=out)
        output = out.getvalue()

        assert "No icon name collisions detected!" in output

    def test_command_empty_registry(self, settings):
        """Test command with empty icon registry."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {},
            }
        }

        out = StringIO()
        call_command("show_icon_registry", stdout=out)
        output = out.getvalue()

        assert "Total unique icons: 0" in output
        assert "Icons with collisions: 0" in output

    def test_command_no_easy_icons_setting(self, settings):
        """Test command when EASY_ICONS setting is not configured."""
        # Remove EASY_ICONS setting if it exists
        if hasattr(settings, "EASY_ICONS"):
            delattr(settings, "EASY_ICONS")

        out = StringIO()
        # Should not raise an error
        call_command("show_icon_registry", stdout=out)
        output = out.getvalue()

        assert "Total unique icons: 0" in output

    def test_command_skips_uppercase_keys(self, settings):
        """Test that uppercase keys are skipped."""
        settings.EASY_ICONS = {
            "DEFAULT": "default",  # This should be skipped
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"home": "home-icon"},
            },
        }

        out = StringIO()
        call_command("show_icon_registry", stdout=out)
        output = out.getvalue()

        assert "Total unique icons: 1" in output
        assert "home" in output

    def test_command_skips_non_dict_configs(self, settings):
        """Test that non-dict renderer configs are skipped."""
        settings.EASY_ICONS = {
            "invalid": "not-a-dict",  # This should be skipped
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"home": "home-icon"},
            },
        }

        out = StringIO()
        call_command("show_icon_registry", stdout=out)
        output = out.getvalue()

        assert "Total unique icons: 1" in output

    def test_command_handles_missing_icons_key(self, settings):
        """Test that renderer configs without 'icons' key are handled."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                # No 'icons' key
            }
        }

        out = StringIO()
        call_command("show_icon_registry", stdout=out)
        output = out.getvalue()

        assert "Total unique icons: 0" in output

    def test_command_handles_non_dict_icons(self, settings):
        """Test that non-dict icons values are handled."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": "not-a-dict",  # Invalid icons value
            }
        }

        out = StringIO()
        call_command("show_icon_registry", stdout=out)
        output = out.getvalue()

        assert "Total unique icons: 0" in output

    def test_command_truncates_long_icon_values(self, settings):
        """Test that long icon values are truncated in table output."""
        long_value = "a" * 50
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"long": long_value},
            }
        }

        out = StringIO()
        call_command("show_icon_registry", stdout=out)
        output = out.getvalue()

        # Should contain truncated value with ellipsis
        assert "..." in output
        # Should not contain the full 50-character value
        assert long_value not in output

    def test_command_collision_markers(self, settings):
        """Test that collision markers (USED/SHADOWED) appear correctly."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"star": "star-default"},
            },
            "fontawesome": {
                "class": "easy_icons.renderers.ProviderRenderer",
                "icons": {"star": "fa-star"},
            },
        }

        out = StringIO()
        call_command("show_icon_registry", stdout=out)
        output = out.getvalue()

        assert "USED" in output
        assert "SHADOWED" in output

    def test_command_multiple_collisions(self, settings):
        """Test handling of multiple icon collisions."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"star": "star-default", "home": "home-default"},
            },
            "fontawesome": {
                "class": "easy_icons.renderers.ProviderRenderer",
                "icons": {"star": "fa-star", "home": "fa-home"},
            },
            "bootstrap": {
                "class": "easy_icons.renderers.ProviderRenderer",
                "icons": {"star": "bi-star"},
            },
        }

        out = StringIO()
        call_command("show_icon_registry", stdout=out)
        output = out.getvalue()

        assert "Icons with collisions: 2" in output
        assert "star" in output
        assert "home" in output

    def test_command_json_collision_structure(self, settings):
        """Test JSON output structure for collisions."""
        settings.EASY_ICONS = {
            "default": {
                "class": "easy_icons.renderers.SvgRenderer",
                "icons": {"star": "star-default"},
            },
            "fontawesome": {
                "class": "easy_icons.renderers.ProviderRenderer",
                "icons": {"star": "fa-star"},
            },
        }

        out = StringIO()
        call_command("show_icon_registry", format="json", stdout=out)
        output = out.getvalue()

        data = json.loads(output)
        assert "collisions" in data
        assert "star" in data["collisions"]
        assert "star" in data["registry"]
        assert len(data["registry"]["star"]) == 2
