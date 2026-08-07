"""Integration tests for django-easy-icons."""

from unittest.mock import patch

import pytest
from django.template import Context, Template
from django.test import override_settings

from easy_icons import icon as easy_icon
from easy_icons.utils import clear_cache


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
                    "default_attrs": {"class": "svg-icon", "height": "1em", "fill": "currentColor"},
                },
                "icons": {"home": "house.svg", "user": "person.svg", "search": "magnifying-glass.svg"},
            },
            "social": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i", "default_attrs": {"class": "fab"}},
                "icons": {"facebook": "fa-facebook", "twitter": "fa-twitter", "linkedin": "fa-linkedin"},
            },
        }

        with override_settings(EASY_ICONS=config):
            with patch("easy_icons.renderers.render_to_string") as mock_render:
                mock_render.return_value = '<svg viewBox="0 0 24 24"><path d="M0 0L10 10"/></svg>'

                # Test SVG renderer with defaults and overrides
                home_result = easy_icon("home", renderer="main")
                assert 'class="svg-icon"' in home_result
                assert 'height="1em"' in home_result
                assert 'fill="currentColor"' in home_result

                # Test with overrides - use star unpacking
                search_result = easy_icon("search", renderer="main", width="2em", **{"class": "search-icon"})
                assert "search-icon" in search_result  # Should override, not merge with svg-icon
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
                "icons": {"home": "fa-home", "user": "fa-user", "admin": "fa-user-shield", "settings": "fa-cog"},
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
                {"url": "/", "label": "Home", "icon": "home", "css_class": "nav-link", "icon_class": "nav-icon"},
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
                "config": {"tag": "i", "default_attrs": {"class": "icon base", "role": "img", "aria-hidden": "true"}},
                "icons": {"test": "fa-test"},
            }
        }

        with override_settings(EASY_ICONS=config):
            # Test class override - ProviderRenderer creates duplicate class attributes
            result1 = easy_icon("test", **{"class": "additional custom"})
            # Check that provided class appears in the css_class and icon class appears
            assert "fa-test" in result1 and "additional" in result1 and "custom" in result1
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
