"""Tests for the SpritesRenderer class."""

import pytest
from django.utils.safestring import SafeString

from easy_icons.exceptions import IconNotFoundError
from easy_icons.renderers import SpritesRenderer


class TestSpritesRenderer:
    """Test cases for the SpritesRenderer class."""

    def test_init_requires_sprite_url(self):
        """Test SpritesRenderer requires sprite_url parameter."""
        with pytest.raises(ValueError) as exc_info:
            SpritesRenderer()

        assert "SpritesRenderer requires 'sprite_url' keyword argument" in str(
            exc_info.value
        )

    def test_init_with_none_sprite_url(self):
        """Test SpritesRenderer raises error with None sprite_url."""
        with pytest.raises(ValueError) as exc_info:
            SpritesRenderer(sprite_url=None)

        assert "SpritesRenderer requires 'sprite_url' keyword argument" in str(
            exc_info.value
        )

    def test_init_with_sprite_url(self):
        """Test SpritesRenderer initialization with sprite_url."""
        renderer = SpritesRenderer(sprite_url="/static/icons.svg")
        assert renderer.sprite_url == "/static/icons.svg"

    def test_init_with_icons_and_attrs(self):
        """Test SpritesRenderer initialization with all parameters."""
        icons = {"logo": "brand-logo", "menu": "hamburger"}
        default_attrs = {"class": "sprite-icon", "width": "24", "height": "24"}
        renderer = SpritesRenderer(
            sprite_url="/assets/sprites.svg", icons=icons, default_attrs=default_attrs
        )

        assert renderer.sprite_url == "/assets/sprites.svg"
        assert renderer.icons == icons
        assert renderer.default_attrs == default_attrs

    def test_render_basic(self):
        """Test basic sprite rendering."""
        icons = {"home": "home-icon"}
        renderer = SpritesRenderer(sprite_url="/static/icons.svg", icons=icons)

        result = renderer.render("home")

        assert isinstance(result, SafeString)
        assert "<svg" in result
        assert '<use href="/static/icons.svg#home-icon">' in result
        assert "</svg>" in result

    def test_render_with_attributes(self):
        """Test sprite rendering with additional attributes."""
        icons = {"star": "star-filled"}
        renderer = SpritesRenderer(sprite_url="/icons.svg", icons=icons)

        test_attrs = {"class": "highlight"}
        result = renderer.render("star", width="32", **test_attrs)

        assert 'class="highlight"' in result
        assert 'width="32"' in result
        assert '<use href="/icons.svg#star-filled">' in result

    def test_render_with_default_attrs(self):
        """Test sprite rendering with default attributes."""
        icons = {"user": "user-profile"}
        default_attrs = {"class": "icon", "width": "24", "height": "24"}
        renderer = SpritesRenderer(
            sprite_url="/sprites.svg", icons=icons, default_attrs=default_attrs
        )

        result = renderer.render("user")

        assert 'class="icon"' in result
        assert 'width="24"' in result
        assert 'height="24"' in result
        assert '<use href="/sprites.svg#user-profile">' in result

    def test_render_merge_attributes(self):
        """Test sprite rendering merging default and custom attributes."""
        icons = {"settings": "settings"}
        default_attrs = {"class": "sprite", "width": "16"}
        renderer = SpritesRenderer(
            sprite_url="/icons.svg", icons=icons, default_attrs=default_attrs
        )

        test_attrs = {"class": "large"}
        result = renderer.render("settings", height="32", **test_attrs)

        assert 'class="large"' in result  # Should override, not merge
        assert 'width="16"' in result
        assert 'height="32"' in result

    def test_render_missing_icon(self):
        """Test rendering raises error for missing icon."""
        renderer = SpritesRenderer(sprite_url="/icons.svg", icons={"home": "home-icon"})

        with pytest.raises(IconNotFoundError):
            renderer.render("missing")

    def test_render_use_defaults_false(self):
        """Test rendering without default attributes."""
        icons = {"download": "download-arrow"}
        default_attrs = {"class": "sprite", "width": "20"}
        renderer = SpritesRenderer(
            sprite_url="/sprites.svg", icons=icons, default_attrs=default_attrs
        )

        test_attrs = {"class": "custom"}
        result = renderer.render("download", use_defaults=False, **test_attrs)

        assert 'class="custom"' in result
        assert 'width="20"' not in result

    def test_callable_interface(self):
        """Test that SpritesRenderer instances are callable."""
        icons = {"bookmark": "bookmark-outline"}
        renderer = SpritesRenderer(sprite_url="/icons.svg", icons=icons)

        test_attrs = {"class": "active"}
        result = renderer("bookmark", **test_attrs)

        assert isinstance(result, SafeString)
        assert 'class="active"' in result
        assert '<use href="/icons.svg#bookmark-outline">' in result

    def test_template_format(self):
        """Test that the template format is correct."""
        renderer = SpritesRenderer(sprite_url="/test.svg")
        expected_lines = [
            "<svg {attrs}>",
            '<use href="{sprite_url}#{resolved_name}"></use>',
            "</svg>",
        ]

        # Check that template contains expected structure
        for line in expected_lines:
            assert line.strip() in renderer.template

    def test_render_complex_sprite_url(self):
        """Test rendering with complex sprite URL."""
        icons = {"arrow": "arrow-right"}
        sprite_url = "https://cdn.example.com/assets/sprites.svg?v=1.2.3"
        renderer = SpritesRenderer(sprite_url=sprite_url, icons=icons)

        result = renderer.render("arrow")

        assert f'<use href="{sprite_url}#arrow-right">' in result

    def test_render_relative_sprite_url(self):
        """Test rendering with relative sprite URL."""
        icons = {"close": "x-mark"}
        renderer = SpritesRenderer(sprite_url="../assets/icons.svg", icons=icons)

        result = renderer.render("close")

        assert '<use href="../assets/icons.svg#x-mark">' in result

    def test_render_absolute_sprite_url(self):
        """Test rendering with absolute sprite URL."""
        icons = {"search": "magnifying-glass"}
        renderer = SpritesRenderer(sprite_url="/static/sprites/icons.svg", icons=icons)

        result = renderer.render("search")

        assert '<use href="/static/sprites/icons.svg#magnifying-glass">' in result

    def test_render_no_additional_attributes(self):
        """Test rendering with no additional attributes."""
        icons = {"info": "info-circle"}
        renderer = SpritesRenderer(sprite_url="/icons.svg", icons=icons)

        result = renderer.render("info")

        # Should have basic structure without extra attributes
        assert "<svg >" in result or "<svg>" in result
        assert '<use href="/icons.svg#info-circle">' in result

    def test_render_strips_whitespace(self):
        """Test that rendered output is properly stripped."""
        icons = {"star": "star-filled"}
        renderer = SpritesRenderer(sprite_url="/icons.svg", icons=icons)

        result = renderer.render("star")

        # Should not start or end with whitespace
        assert str(result) == str(result).strip()

    def test_render_multiline_output(self):
        """Test that rendered output handles multiline template correctly."""
        icons = {"heart": "heart-solid"}
        renderer = SpritesRenderer(sprite_url="/sprites.svg", icons=icons)

        result = renderer.render("heart")

        # Should contain all parts of the template
        assert "<svg" in result
        assert '<use href="/sprites.svg#heart-solid"' in result
        assert "</svg>" in result

    def test_render_with_fragment_identifier(self):
        """Test rendering with sprite URL that already has fragment."""
        icons = {"warning": "warning-triangle"}
        # Note: This might be an edge case - sprite_url with existing fragment
        renderer = SpritesRenderer(sprite_url="/icons.svg#base", icons=icons)

        result = renderer.render("warning")

        # The fragment should be appended (though this might not be intended behavior)
        assert "/icons.svg#base#warning-triangle" in result

    def test_render_escaped_characters_in_sprite_url(self):
        """Test rendering with special characters in sprite URL."""
        icons = {"test": "test-icon"}
        sprite_url = "/assets/icons with spaces.svg"
        renderer = SpritesRenderer(sprite_url=sprite_url, icons=icons)

        result = renderer.render("test")

        assert sprite_url in result
        assert "test-icon" in result
