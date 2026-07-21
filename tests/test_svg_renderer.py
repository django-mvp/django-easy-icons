"""Tests for the SvgRenderer class."""

from unittest.mock import patch

import pytest
from django.template.loader import TemplateDoesNotExist
from django.utils.safestring import SafeString

from easy_icons.exceptions import IconNotFoundError, InvalidSvgError
from easy_icons.renderers import SvgRenderer


class TestSvgRenderer:
    """Test cases for the SvgRenderer class."""

    def test_init_default_svg_dir(self):
        """Test SvgRenderer initialization with default svg_dir."""
        renderer = SvgRenderer()
        assert renderer.svg_dir == "icons"

    def test_init_custom_svg_dir(self):
        """Test SvgRenderer initialization with custom svg_dir."""
        renderer = SvgRenderer(svg_dir="custom/icons")
        assert renderer.svg_dir == "custom/icons"

    def test_init_with_icons_and_attrs(self):
        """Test SvgRenderer initialization with icons and default_attrs."""
        icons = {"home": "house.svg", "user": "profile.svg"}
        default_attrs = {"class": "svg-icon", "height": "24px"}
        renderer = SvgRenderer(svg_dir="assets", icons=icons, default_attrs=default_attrs)

        assert renderer.svg_dir == "assets"
        assert renderer.icons == icons
        assert renderer.default_attrs == default_attrs

    @patch("easy_icons.renderers.render_to_string")
    def test_render_basic(self, mock_render):
        """Test basic SVG rendering."""
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"home": "home.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer.render("home")

        mock_render.assert_called_once_with("icons/home.svg")
        assert isinstance(result, SafeString)
        assert "<svg>" in result

    @patch("easy_icons.renderers.render_to_string")
    def test_render_with_custom_svg_dir(self, mock_render):
        """Test SVG rendering with custom svg_dir."""
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"logo": "brand.svg"}
        renderer = SvgRenderer(svg_dir="assets/graphics", icons=icons)

        result = renderer.render("logo")

        mock_render.assert_called_once_with("assets/graphics/brand.svg")

    @patch("easy_icons.renderers.render_to_string")
    def test_render_with_attributes(self, mock_render):
        """Test SVG rendering with additional attributes."""
        mock_render.return_value = '<svg viewBox="0 0 24 24"><path d="M0 0L10 10"/></svg>'
        icons = {"star": "star.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer.render("star", **{"class": "highlight", "width": "32"})

        assert 'class="highlight"' in result
        assert 'width="32"' in result

    @patch("easy_icons.renderers.render_to_string")
    def test_render_with_default_attrs(self, mock_render):
        """Test SVG rendering with default attributes."""
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"heart": "heart.svg"}
        default_attrs = {"class": "icon", "fill": "currentColor"}
        renderer = SvgRenderer(icons=icons, default_attrs=default_attrs)

        result = renderer.render("heart")

        assert 'class="icon"' in result
        assert 'fill="currentColor"' in result

    @patch("easy_icons.renderers.render_to_string")
    def test_render_merge_attributes(self, mock_render):
        """Test SVG rendering overriding default attributes."""
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"settings": "cog.svg"}
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = SvgRenderer(icons=icons, default_attrs=default_attrs)

        result = renderer.render("settings", **{"class": "large", "width": "2em"})

        assert 'class="large"' in result  # Should override, not merge
        assert 'height="1em"' in result
        assert 'width="2em"' in result

    def test_render_missing_icon(self):
        """Test rendering raises error for missing icon."""
        renderer = SvgRenderer(icons={"home": "home.svg"})

        with pytest.raises(IconNotFoundError):
            renderer.render("missing")

    @patch("easy_icons.renderers.render_to_string")
    def test_inject_svg_attrs_basic(self, mock_render):
        """Test _inject_svg_attrs with basic SVG content."""
        svg_content = '<svg viewBox="0 0 24 24"><path d="M0 0L10 10"/></svg>'
        icons = {"test": "test.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer._inject_svg_attrs(svg_content, **{"class": "custom"})

        assert 'class="custom"' in result
        assert 'class="custom"' in result and 'viewBox="0 0 24 24"' in result

    @patch("easy_icons.renderers.render_to_string")
    def test_inject_svg_attrs_with_existing_attrs(self, mock_render):
        """Test _inject_svg_attrs preserves existing SVG attributes."""
        svg_content = '<svg class="existing" width="16"><path d="M0 0L10 10"/></svg>'
        icons = {"test": "test.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer._inject_svg_attrs(svg_content, height="20")

        assert 'height="20"' in result
        assert 'class="existing"' in result  # Should preserve existing
        assert 'width="16"' in result  # Should preserve existing

    def test_inject_svg_attrs_no_svg_tag(self):
        """Test _inject_svg_attrs raises error when no SVG tag found."""
        content = "<div>Not an SVG</div>"
        renderer = SvgRenderer()

        with pytest.raises(InvalidSvgError) as exc_info:
            test_attrs = {"class": "test"}
            renderer._inject_svg_attrs(content, **test_attrs)

        assert "No <svg> tag found" in str(exc_info.value)

    @patch("easy_icons.renderers.render_to_string")
    def test_inject_svg_attrs_no_attributes(self, mock_render):
        """Test _inject_svg_attrs with no attributes to inject."""
        svg_content = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"test": "test.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer._inject_svg_attrs(svg_content)

        # Should return original content unchanged
        assert result == svg_content

    @patch("easy_icons.renderers.render_to_string")
    def test_inject_svg_attrs_complex_svg(self, mock_render):
        """Test _inject_svg_attrs with complex SVG structure."""
        svg_content = """<svg
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
    class="existing">
    <path d="M0 0L10 10"/>
</svg>"""
        icons = {"test": "test.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer._inject_svg_attrs(svg_content, **{"data-icon": "test"})

        assert 'data-icon="test"' in result
        assert 'viewBox="0 0 24 24"' in result
        assert 'xmlns="http://www.w3.org/2000/svg"' in result

    @patch("easy_icons.renderers.render_to_string")
    def test_render_use_defaults_false(self, mock_render):
        """Test rendering without default attributes."""
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"home": "home.svg"}
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = SvgRenderer(icons=icons, default_attrs=default_attrs)

        result = renderer.render("home", use_defaults=False, **{"class": "custom"})

        assert 'class="custom"' in result
        assert 'height="1em"' not in result  # Default should not be applied

    @patch("easy_icons.renderers.render_to_string")
    def test_callable_interface(self, mock_render):
        """Test that SvgRenderer instances are callable."""
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"home": "home.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer("home", **{"class": "test"})

        assert isinstance(result, SafeString)
        assert 'class="test"' in result

    @patch("easy_icons.renderers.render_to_string")
    def test_render_template_does_not_exist(self, mock_render):
        """Test handling of template not found errors."""
        mock_render.side_effect = TemplateDoesNotExist("icons/missing.svg")
        icons = {"test": "missing.svg"}
        renderer = SvgRenderer(icons=icons)

        with pytest.raises(TemplateDoesNotExist):
            renderer.render("test")

    @patch("easy_icons.renderers.render_to_string")
    def test_render_multiline_svg(self, mock_render):
        """Test rendering with multiline SVG content."""
        svg_content = """<svg viewBox="0 0 24 24">
    <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
    <circle cx="12" cy="12" r="2"/>
</svg>"""
        mock_render.return_value = svg_content
        icons = {"complex": "complex.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer.render("complex", **{"data-test": "value"})

        assert 'data-test="value"' in result
        assert 'viewBox="0 0 24 24"' in result
        assert "<path d=" in result
        assert "<circle cx=" in result
