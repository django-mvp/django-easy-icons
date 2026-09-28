"""Tests for easy_icons.renderers."""

from unittest.mock import patch

import pytest
from django.template.loader import TemplateDoesNotExist
from django.utils.safestring import SafeString

from easy_icons.exceptions import IconNotFoundError, InvalidSvgError
from easy_icons.renderers import ProviderRenderer, SpritesRenderer, SvgRenderer


class TestSvgRenderer:
    def test_init_default_svg_dir(self):
        renderer = SvgRenderer()
        assert renderer.svg_dir == "icons"

    def test_init_custom_svg_dir(self):
        renderer = SvgRenderer(svg_dir="custom/icons")
        assert renderer.svg_dir == "custom/icons"

    def test_init_with_icons_and_attrs(self):
        icons = {"home": "house.svg", "user": "profile.svg"}
        default_attrs = {"class": "svg-icon", "height": "24px"}
        renderer = SvgRenderer(
            svg_dir="assets", icons=icons, default_attrs=default_attrs
        )

        assert renderer.svg_dir == "assets"
        assert renderer.icons == icons
        assert renderer.default_attrs == default_attrs

    @patch("easy_icons.renderers.render_to_string")
    def test_render_basic(self, mock_render):
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"home": "home.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer.render("home")

        mock_render.assert_called_once_with("icons/home.svg")
        assert isinstance(result, SafeString)
        assert "<svg>" in result

    @patch("easy_icons.renderers.render_to_string")
    def test_render_with_custom_svg_dir(self, mock_render):
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"logo": "brand.svg"}
        renderer = SvgRenderer(svg_dir="assets/graphics", icons=icons)

        result = renderer.render("logo")

        mock_render.assert_called_once_with("assets/graphics/brand.svg")

    @patch("easy_icons.renderers.render_to_string")
    def test_render_with_attributes(self, mock_render):
        mock_render.return_value = (
            '<svg viewBox="0 0 24 24"><path d="M0 0L10 10"/></svg>'
        )
        icons = {"star": "star.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer.render("star", **{"class": "highlight", "width": "32"})

        assert 'class="highlight"' in result
        assert 'width="32"' in result

    @patch("easy_icons.renderers.render_to_string")
    def test_render_with_default_attrs(self, mock_render):
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"heart": "heart.svg"}
        default_attrs = {"class": "icon", "fill": "currentColor"}
        renderer = SvgRenderer(icons=icons, default_attrs=default_attrs)

        result = renderer.render("heart")

        assert 'class="icon"' in result
        assert 'fill="currentColor"' in result

    @patch("easy_icons.renderers.render_to_string")
    def test_render_merge_attributes(self, mock_render):
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"settings": "cog.svg"}
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = SvgRenderer(icons=icons, default_attrs=default_attrs)

        result = renderer.render("settings", **{"class": "large", "width": "2em"})

        assert 'class="large"' in result  # Should override, not merge
        assert 'height="1em"' in result
        assert 'width="2em"' in result

    def test_render_missing_icon(self):
        renderer = SvgRenderer(icons={"home": "home.svg"})

        with pytest.raises(IconNotFoundError):
            renderer.render("missing")

    @patch("easy_icons.renderers.render_to_string")
    def test_inject_svg_attrs_basic(self, mock_render):
        svg_content = '<svg viewBox="0 0 24 24"><path d="M0 0L10 10"/></svg>'
        icons = {"test": "test.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer._inject_svg_attrs(svg_content, **{"class": "custom"})

        assert 'class="custom"' in result
        assert 'class="custom"' in result and 'viewBox="0 0 24 24"' in result

    @patch("easy_icons.renderers.render_to_string")
    def test_inject_svg_attrs_with_existing_attrs(self, mock_render):
        svg_content = '<svg class="existing" width="16"><path d="M0 0L10 10"/></svg>'
        icons = {"test": "test.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer._inject_svg_attrs(svg_content, height="20")

        assert 'height="20"' in result
        assert 'class="existing"' in result  # Should preserve existing
        assert 'width="16"' in result  # Should preserve existing

    def test_inject_svg_attrs_no_svg_tag(self):
        content = "<div>Not an SVG</div>"
        renderer = SvgRenderer()

        with pytest.raises(InvalidSvgError) as exc_info:
            test_attrs = {"class": "test"}
            renderer._inject_svg_attrs(content, **test_attrs)

        assert "No <svg> tag found" in str(exc_info.value)

    @patch("easy_icons.renderers.render_to_string")
    def test_inject_svg_attrs_no_attributes(self, mock_render):
        svg_content = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"test": "test.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer._inject_svg_attrs(svg_content)

        assert result == svg_content

    @patch("easy_icons.renderers.render_to_string")
    def test_inject_svg_attrs_complex_svg(self, mock_render):
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
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"home": "home.svg"}
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = SvgRenderer(icons=icons, default_attrs=default_attrs)

        result = renderer.render("home", use_defaults=False, **{"class": "custom"})

        assert 'class="custom"' in result
        assert 'height="1em"' not in result  # Default should not be applied

    @patch("easy_icons.renderers.render_to_string")
    def test_callable_interface(self, mock_render):
        mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'
        icons = {"home": "home.svg"}
        renderer = SvgRenderer(icons=icons)

        result = renderer("home", **{"class": "test"})

        assert isinstance(result, SafeString)
        assert 'class="test"' in result

    @patch("easy_icons.renderers.render_to_string")
    def test_render_template_does_not_exist(self, mock_render):
        mock_render.side_effect = TemplateDoesNotExist("icons/missing.svg")
        icons = {"test": "missing.svg"}
        renderer = SvgRenderer(icons=icons)

        with pytest.raises(TemplateDoesNotExist):
            renderer.render("test")

    @patch("easy_icons.renderers.render_to_string")
    def test_render_multiline_svg(self, mock_render):
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


class TestProviderRenderer:
    def test_init_default_tag(self):
        renderer = ProviderRenderer()
        assert renderer.tag == "i"

    def test_init_custom_tag(self):
        renderer = ProviderRenderer(tag="span")
        assert renderer.tag == "span"

    def test_init_with_icons_and_attrs(self):
        icons = {"home": "fa-home", "user": "fa-user"}
        default_attrs = {"class": "icon"}
        renderer = ProviderRenderer(
            tag="span", icons=icons, default_attrs=default_attrs
        )

        assert renderer.tag == "span"
        assert renderer.icons == icons
        assert renderer.default_attrs == default_attrs

    def test_render_basic(self):
        icons = {"home": "fa-home"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("home")

        assert isinstance(result, SafeString)
        assert '<i class="fa-home"' in result
        assert "</i>" in result

    def test_render_custom_tag(self):
        icons = {"star": "fa-star"}
        renderer = ProviderRenderer(tag="span", icons=icons)

        result = renderer.render("star")

        assert '<span class="fa-star"' in result
        assert "</span>" in result

    def test_render_with_custom_class(self):
        icons = {"heart": "fa-heart"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("heart", **{"class": "large"})

        assert 'class="fa-heart large"' in result or (
            'class="fa-heart"' in result and 'class="large"' in result
        )

    def test_render_with_attributes(self):
        icons = {"user": "fa-user"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("user", id="user-icon", **{"data-role": "button"})

        assert 'id="user-icon"' in result
        assert 'data-role="button"' in result
        assert '<i class="fa-user"' in result

    def test_render_with_default_attrs(self):
        icons = {"settings": "fa-cog"}
        default_attrs = {"class": "icon", "aria-hidden": "true"}
        renderer = ProviderRenderer(icons=icons, default_attrs=default_attrs)

        result = renderer.render("settings")

        assert 'class="icon"' in result
        assert 'aria-hidden="true"' in result
        assert "fa-cog" in result

    def test_render_merge_classes(self):
        icons = {"menu": "fa-bars"}
        default_attrs = {"class": "icon"}
        renderer = ProviderRenderer(icons=icons, default_attrs=default_attrs)

        test_attrs = {"class": "large primary"}
        result = renderer.render("menu", **test_attrs)

        # ProviderRenderer concatenates classes differently than the base build_attrs
        assert "fa-bars" in result and "large" in result and "primary" in result
        assert "icon" in result  # from default attrs

    def test_render_override_attributes(self):
        icons = {"close": "fa-times"}
        default_attrs = {"class": "icon", "title": "default"}
        renderer = ProviderRenderer(icons=icons, default_attrs=default_attrs)

        result = renderer.render("close", title="Close Dialog")

        assert 'class="icon"' in result
        assert 'title="Close Dialog"' in result

    def test_render_missing_icon(self):
        renderer = ProviderRenderer(icons={"home": "fa-home"})

        with pytest.raises(IconNotFoundError):
            renderer.render("missing")

    def test_render_empty_class(self):
        icons = {"search": "fa-search"}
        renderer = ProviderRenderer(icons=icons)

        test_attrs = {"class": ""}
        result = renderer.render("search", **test_attrs)

        assert 'class="fa-search"' in result or 'class="fa-search "' in result

    def test_render_use_defaults_false(self):
        icons = {"download": "fa-download"}
        default_attrs = {"class": "icon", "role": "img"}
        renderer = ProviderRenderer(icons=icons, default_attrs=default_attrs)

        test_attrs = {"class": "custom"}
        result = renderer.render("download", use_defaults=False, **test_attrs)

        assert "fa-download" in result and "custom" in result
        assert 'role="img"' not in result

    def test_callable_interface(self):
        icons = {"bookmark": "fa-bookmark"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer("bookmark", **{"class": "active"})

        assert isinstance(result, SafeString)
        assert 'class="fa-bookmark active"' in result or (
            'class="fa-bookmark"' in result and 'class="active"' in result
        )

    def test_template_format(self):
        renderer = ProviderRenderer()
        expected_template = '<{tag} class="{css_class}" {attrs}></{tag}>'
        assert renderer.template == expected_template

    def test_render_complex_icon_name(self):
        icons = {"arrow-left": "fas fa-arrow-left"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("arrow-left")

        assert 'class="fas fa-arrow-left"' in result

    def test_render_no_additional_attributes(self):
        icons = {"info": "fa-info"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("info")

        assert (
            '<i class="fa-info" ></i>' in result or '<i class="fa-info"></i>' in result
        )

    def test_render_with_boolean_attributes(self):
        icons = {"check": "fa-check"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("check", hidden=True, disabled=False)

        # Django's flatatt handles boolean attributes differently - True values show as just the attribute name
        assert "hidden" in result
        assert "disabled" not in result or 'disabled=""' in result

    def test_render_strips_whitespace(self):
        icons = {"star": "fa-star"}
        renderer = ProviderRenderer(icons=icons)

        result = renderer.render("star")

        assert str(result) == str(result).strip()

    def test_render_class_handling_edge_cases(self):
        icons = {"test": "fa-test"}
        renderer = ProviderRenderer(icons=icons)

        test_attrs1 = {"class": None}
        result1 = renderer.render("test", **test_attrs1)
        assert "fa-test" in result1

        test_attrs2 = {"class": "  extra   spaces  "}
        result2 = renderer.render("test", **test_attrs2)
        assert "fa-test" in result2
        assert "extra" in result2
        assert "spaces" in result2


class TestSpritesRenderer:
    def test_init_requires_sprite_url(self):
        with pytest.raises(ValueError) as exc_info:
            SpritesRenderer()

        assert "SpritesRenderer requires 'sprite_url' keyword argument" in str(
            exc_info.value
        )

    def test_init_with_none_sprite_url(self):
        with pytest.raises(ValueError) as exc_info:
            SpritesRenderer(sprite_url=None)

        assert "SpritesRenderer requires 'sprite_url' keyword argument" in str(
            exc_info.value
        )

    def test_init_with_sprite_url(self):
        renderer = SpritesRenderer(sprite_url="/static/icons.svg")
        assert renderer.sprite_url == "/static/icons.svg"

    def test_init_with_icons_and_attrs(self):
        icons = {"logo": "brand-logo", "menu": "hamburger"}
        default_attrs = {"class": "sprite-icon", "width": "24", "height": "24"}
        renderer = SpritesRenderer(
            sprite_url="/assets/sprites.svg", icons=icons, default_attrs=default_attrs
        )

        assert renderer.sprite_url == "/assets/sprites.svg"
        assert renderer.icons == icons
        assert renderer.default_attrs == default_attrs

    def test_render_basic(self):
        icons = {"home": "home-icon"}
        renderer = SpritesRenderer(sprite_url="/static/icons.svg", icons=icons)

        result = renderer.render("home")

        assert isinstance(result, SafeString)
        assert "<svg" in result
        assert '<use href="/static/icons.svg#home-icon">' in result
        assert "</svg>" in result

    def test_render_with_attributes(self):
        icons = {"star": "star-filled"}
        renderer = SpritesRenderer(sprite_url="/icons.svg", icons=icons)

        test_attrs = {"class": "highlight"}
        result = renderer.render("star", width="32", **test_attrs)

        assert 'class="highlight"' in result
        assert 'width="32"' in result
        assert '<use href="/icons.svg#star-filled">' in result

    def test_render_with_default_attrs(self):
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
        renderer = SpritesRenderer(sprite_url="/icons.svg", icons={"home": "home-icon"})

        with pytest.raises(IconNotFoundError):
            renderer.render("missing")

    def test_render_use_defaults_false(self):
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
        icons = {"bookmark": "bookmark-outline"}
        renderer = SpritesRenderer(sprite_url="/icons.svg", icons=icons)

        test_attrs = {"class": "active"}
        result = renderer("bookmark", **test_attrs)

        assert isinstance(result, SafeString)
        assert 'class="active"' in result
        assert '<use href="/icons.svg#bookmark-outline">' in result

    def test_template_format(self):
        renderer = SpritesRenderer(sprite_url="/test.svg")
        expected_lines = [
            "<svg {attrs}>",
            '<use href="{sprite_url}#{resolved_name}"></use>',
            "</svg>",
        ]

        for line in expected_lines:
            assert line.strip() in renderer.template

    def test_render_complex_sprite_url(self):
        icons = {"arrow": "arrow-right"}
        sprite_url = "https://cdn.example.com/assets/sprites.svg?v=1.2.3"
        renderer = SpritesRenderer(sprite_url=sprite_url, icons=icons)

        result = renderer.render("arrow")

        assert f'<use href="{sprite_url}#arrow-right">' in result

    def test_render_relative_sprite_url(self):
        icons = {"close": "x-mark"}
        renderer = SpritesRenderer(sprite_url="../assets/icons.svg", icons=icons)

        result = renderer.render("close")

        assert '<use href="../assets/icons.svg#x-mark">' in result

    def test_render_absolute_sprite_url(self):
        icons = {"search": "magnifying-glass"}
        renderer = SpritesRenderer(sprite_url="/static/sprites/icons.svg", icons=icons)

        result = renderer.render("search")

        assert '<use href="/static/sprites/icons.svg#magnifying-glass">' in result

    def test_render_no_additional_attributes(self):
        icons = {"info": "info-circle"}
        renderer = SpritesRenderer(sprite_url="/icons.svg", icons=icons)

        result = renderer.render("info")

        assert "<svg >" in result or "<svg>" in result
        assert '<use href="/icons.svg#info-circle">' in result

    def test_render_strips_whitespace(self):
        icons = {"star": "star-filled"}
        renderer = SpritesRenderer(sprite_url="/icons.svg", icons=icons)

        result = renderer.render("star")

        assert str(result) == str(result).strip()

    def test_render_multiline_output(self):
        icons = {"heart": "heart-solid"}
        renderer = SpritesRenderer(sprite_url="/sprites.svg", icons=icons)

        result = renderer.render("heart")

        assert "<svg" in result
        assert '<use href="/sprites.svg#heart-solid"' in result
        assert "</svg>" in result

    def test_render_with_fragment_identifier(self):
        icons = {"warning": "warning-triangle"}
        renderer = SpritesRenderer(sprite_url="/icons.svg#base", icons=icons)

        result = renderer.render("warning")

        assert "/icons.svg#base#warning-triangle" in result

    def test_render_escaped_characters_in_sprite_url(self):
        icons = {"test": "test-icon"}
        sprite_url = "/assets/icons with spaces.svg"
        renderer = SpritesRenderer(sprite_url=sprite_url, icons=icons)

        result = renderer.render("test")

        assert sprite_url in result
        assert "test-icon" in result
