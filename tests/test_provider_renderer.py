"""Tests for the ProviderRenderer class."""

import pytest
from django.utils.safestring import SafeString

from easy_icons.exceptions import IconNotFoundError
from easy_icons.renderers import ProviderRenderer


class TestProviderRenderer:
    """Test cases for the ProviderRenderer class."""

    def test_init_default_tag(self):
        """Test ProviderRenderer initialization with default tag."""
        renderer = ProviderRenderer()
        assert renderer.tag == "i"

    def test_init_custom_tag(self):
        """Test ProviderRenderer initialization with custom tag."""
        renderer = ProviderRenderer(tag="span")
        assert renderer.tag == "span"

    def test_init_with_icons_and_attrs(self):
        """Test ProviderRenderer initialization with icons and default_attrs."""
        icons = {"home": "fa-home", "user": "fa-user"}
        default_attrs = {"class": "icon"}
        renderer = ProviderRenderer(tag="span", icons=icons, default_attrs=default_attrs)

        assert renderer.tag == "span"
        assert renderer.icons == icons
        assert renderer.default_attrs == default_attrs

    def test_render_basic(self):
        """Test basic provider icon rendering."""
        icons = {"home": "fa-home"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("home")

        assert isinstance(result, SafeString)
        assert '<i class="fa-home"' in result
        assert "</i>" in result

    def test_render_custom_tag(self):
        """Test provider icon rendering with custom tag."""
        icons = {"star": "fa-star"}
        renderer = ProviderRenderer(tag="span", icons=icons)

        result = renderer.render("star")

        assert '<span class="fa-star"' in result
        assert "</span>" in result

    def test_render_with_custom_class(self):
        """Test provider icon rendering with additional class."""
        icons = {"heart": "fa-heart"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("heart", **{"class": "large"})

        # Should merge the class attributes properly
        assert 'class="fa-heart large"' in result or ('class="fa-heart"' in result and 'class="large"' in result)

    def test_render_with_attributes(self):
        """Test provider icon rendering with additional attributes."""
        icons = {"user": "fa-user"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("user", id="user-icon", **{"data-role": "button"})

        assert 'id="user-icon"' in result
        assert 'data-role="button"' in result
        assert '<i class="fa-user"' in result

    def test_render_with_default_attrs(self):
        """Test provider icon rendering with default attributes."""
        icons = {"settings": "fa-cog"}
        default_attrs = {"class": "icon", "aria-hidden": "true"}
        renderer = ProviderRenderer(icons=icons, default_attrs=default_attrs)

        result = renderer.render("settings")

        assert 'class="icon"' in result
        assert 'aria-hidden="true"' in result
        assert "fa-cog" in result

    def test_render_merge_classes(self):
        """Test provider icon rendering merging default and custom classes."""
        icons = {"menu": "fa-bars"}
        default_attrs = {"class": "icon"}
        renderer = ProviderRenderer(icons=icons, default_attrs=default_attrs)

        test_attrs = {"class": "large primary"}
        result = renderer.render("menu", **test_attrs)

        # ProviderRenderer concatenates classes differently than the base build_attrs
        assert "fa-bars" in result and "large" in result and "primary" in result
        assert "icon" in result  # from default attrs

    def test_render_override_attributes(self):
        """Test provider icon rendering overriding default attributes."""
        icons = {"close": "fa-times"}
        default_attrs = {"class": "icon", "title": "default"}
        renderer = ProviderRenderer(icons=icons, default_attrs=default_attrs)

        result = renderer.render("close", title="Close Dialog")

        assert 'class="icon"' in result
        # Since attributes are now overridden, we should have "Close Dialog"
        assert 'title="Close Dialog"' in result

    def test_render_missing_icon(self):
        """Test rendering raises error for missing icon."""
        renderer = ProviderRenderer(icons={"home": "fa-home"})

        with pytest.raises(IconNotFoundError):
            renderer.render("missing")

    def test_render_empty_class(self):
        """Test provider icon rendering with empty additional class."""
        icons = {"search": "fa-search"}
        renderer = ProviderRenderer(icons=icons)

        test_attrs = {"class": ""}
        result = renderer.render("search", **test_attrs)

        assert 'class="fa-search"' in result or 'class="fa-search "' in result

    def test_render_use_defaults_false(self):
        """Test rendering without default attributes."""
        icons = {"download": "fa-download"}
        default_attrs = {"class": "icon", "role": "img"}
        renderer = ProviderRenderer(icons=icons, default_attrs=default_attrs)

        test_attrs = {"class": "custom"}
        result = renderer.render("download", use_defaults=False, **test_attrs)

        # When use_defaults=False, should still have the icon class and custom class
        assert "fa-download" in result and "custom" in result
        assert 'role="img"' not in result

    def test_callable_interface(self):
        """Test that ProviderRenderer instances are callable."""
        icons = {"bookmark": "fa-bookmark"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer("bookmark", **{"class": "active"})

        assert isinstance(result, SafeString)
        # Should merge class attributes or have separate class attributes
        assert 'class="fa-bookmark active"' in result or (
            'class="fa-bookmark"' in result and 'class="active"' in result
        )

    def test_template_format(self):
        """Test that the template format is correct."""
        renderer = ProviderRenderer()
        expected_template = '<{tag} class="{css_class}" {attrs}></{tag}>'
        assert renderer.template == expected_template

    def test_render_complex_icon_name(self):
        """Test rendering with complex icon name (multiple parts)."""
        icons = {"arrow-left": "fas fa-arrow-left"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("arrow-left")

        assert 'class="fas fa-arrow-left"' in result

    def test_render_no_additional_attributes(self):
        """Test rendering with no additional attributes."""
        icons = {"info": "fa-info"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("info")

        assert '<i class="fa-info" ></i>' in result or '<i class="fa-info"></i>' in result

    def test_render_with_boolean_attributes(self):
        """Test rendering with boolean-style attributes."""
        icons = {"check": "fa-check"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("check", hidden=True, disabled=False)

        # Django's flatatt handles boolean attributes differently - True values show as just the attribute name
        assert "hidden" in result
        assert "disabled" not in result or 'disabled=""' in result

    def test_render_strips_whitespace(self):
        """Test that rendered output is properly stripped."""
        icons = {"star": "fa-star"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("star")

        # Should not start or end with whitespace
        assert str(result) == str(result).strip()

    def test_render_class_handling_edge_cases(self):
        """Test class handling with various edge cases."""
        icons = {"test": "fa-test"}
        renderer = ProviderRenderer(icons=icons)

        # Test with None class
        test_attrs1 = {"class": None}
        result1 = renderer.render("test", **test_attrs1)
        assert "fa-test" in result1

        # Test with multiple spaces in class
        test_attrs2 = {"class": "  extra   spaces  "}
        result2 = renderer.render("test", **test_attrs2)
        assert "fa-test" in result2
        assert "extra" in result2
        assert "spaces" in result2
