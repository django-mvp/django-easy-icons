"""Test utilities and fixtures for django-easy-icons tests."""

import pytest
from django.test import override_settings

from easy_icons import utils


@pytest.fixture(autouse=True)
def clear_cache_between_tests():
    """Automatically clear configuration cache and icon registry between tests."""
    utils.clear_cache()
    utils._icon_registry.clear()
    yield
    utils.clear_cache()
    utils._icon_registry.clear()


@pytest.fixture
def auto_build_registry(request):
    """Automatically build icon registry when using override_settings in test.

    This fixture should be used with tests that rely on auto-detection.
    Tests that explicitly specify renderer= don't need this.
    """
    # This runs after the test function, allowing override_settings to take effect first
    yield
    # Build registry with current settings
    utils.build_icon_registry()


@pytest.fixture
def basic_svg_config():
    """Basic SVG renderer configuration for testing."""
    return {
        "default": {
            "renderer": "easy_icons.renderers.SvgRenderer",
            "config": {
                "svg_dir": "icons",
                "default_attrs": {"height": "1em", "fill": "currentColor"},
            },
            "icons": {
                "home": "home.svg",
                "user": "user.svg",
                "settings": "settings.svg",
            },
        }
    }


@pytest.fixture
def basic_provider_config():
    """Basic provider renderer configuration for testing."""
    return {
        "default": {
            "renderer": "easy_icons.renderers.ProviderRenderer",
            "config": {"tag": "i", "default_attrs": {"class": "icon"}},
            "icons": {"home": "fa-home", "user": "fa-user", "heart": "fa-heart"},
        }
    }


@pytest.fixture
def basic_sprites_config():
    """Basic sprites renderer configuration for testing."""
    return {
        "default": {
            "renderer": "easy_icons.renderers.SpritesRenderer",
            "config": {
                "sprite_url": "/static/icons.svg",
                "default_attrs": {
                    "class": "sprite-icon",
                    "width": "24",
                    "height": "24",
                },
            },
            "icons": {
                "logo": "company-logo",
                "menu": "hamburger-menu",
                "search": "search-icon",
            },
        }
    }


@pytest.fixture
def multi_renderer_config():
    """Multi-renderer configuration for testing."""
    return {
        "default": {
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
            "icons": {"logo": "brand-logo"},
        },
    }


class MockTemplate:
    """Mock template for testing without real template files."""

    def __init__(self, content="<svg><path d='M0 0L10 10'/></svg>"):
        self.content = content

    def render(self, context=None):
        return self.content


def create_test_settings(**easy_icons_config):
    """Create test settings override decorator with EASY_ICONS config."""
    return override_settings(EASY_ICONS=easy_icons_config)


# Test constants
TEST_SVG_CONTENT = '<svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>'
TEST_SVG_WITH_ATTRS = '<svg class="existing" width="16" height="16"><path d="M0 0L10 10"/></svg>'
TEST_COMPLEX_SVG = """<svg
    viewBox="0 0 24 24"
    data-icon="home"
    class="icon-svg"
    fill="none"
    stroke="currentColor">
    <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
</svg>"""


class TestHelpers:
    """Helper methods for testing."""

    @staticmethod
    def assert_html_contains(html, *expected_strings):
        """Assert that HTML contains all expected strings."""
        for expected in expected_strings:
            assert expected in html, f"Expected '{expected}' not found in HTML: {html}"

    @staticmethod
    def assert_html_not_contains(html, *unexpected_strings):
        """Assert that HTML does not contain any unexpected strings."""
        for unexpected in unexpected_strings:
            assert unexpected not in html, f"Unexpected '{unexpected}' found in HTML: {html}"

    @staticmethod
    def assert_valid_html_attributes(html):
        """Basic validation that HTML has properly formed attributes."""
        # Check for unescaped quotes within attribute values (basic check)
        import re

        # Find all attributes
        attr_pattern = r'(\w+(?:-\w+)*)=(["\'])([^"\']*?)\2'
        matches = re.findall(attr_pattern, html)

        for attr_name, quote_char, attr_value in matches:
            # Attribute names should not be empty
            assert attr_name.strip(), f"Empty attribute name in: {html}"

            # Attribute values should not contain unescaped quotes of the same type
            if quote_char == '"':
                assert '"' not in attr_value, f"Unescaped quote in attribute value: {attr_value}"
            else:
                assert "'" not in attr_value, f"Unescaped quote in attribute value: {attr_value}"

    @staticmethod
    def extract_classes(html):
        """Extract class attribute value from HTML."""
        import re

        match = re.search(r'class=(["\'])([^"\']*?)\1', html)
        if match:
            return match.group(2).split()
        return []

    @staticmethod
    def extract_attribute(html, attr_name):
        """Extract specific attribute value from HTML."""
        import re

        pattern = f"{attr_name}=([\"'])([^\"']*?)\\1"
        match = re.search(pattern, html)
        if match:
            return match.group(2)
        return None
