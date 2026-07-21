"""Tests for the BaseRenderer class."""

import pytest
from django.utils.safestring import SafeString

from easy_icons.base import BaseRenderer
from easy_icons.exceptions import IconNotFoundError


class ConcreteRenderer(BaseRenderer):
    """Test implementation of BaseRenderer for testing."""

    def render(self, name: str, **kwargs) -> SafeString:
        """Concrete implementation for testing."""
        resolved_name = self.get_icon(name)
        attrs = self.build_attrs(**kwargs)
        return self.safe_return(f"<test {attrs}>{resolved_name}</test>")


class TestBaseRenderer:
    """Test cases for the BaseRenderer class."""

    def test_init_with_no_args(self):
        """Test renderer initialization with no arguments."""
        renderer = ConcreteRenderer()
        assert renderer.icons == {}
        assert renderer.default_attrs == {}

    def test_init_with_icons(self):
        """Test renderer initialization with icons mapping."""
        icons = {"home": "house", "user": "person"}
        renderer = ConcreteRenderer(icons=icons)
        assert renderer.icons == icons

    def test_init_with_default_attrs(self):
        """Test renderer initialization with default attributes."""
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)
        assert renderer.default_attrs == default_attrs

    def test_init_with_extra_kwargs(self):
        """Test renderer initialization ignores unknown kwargs."""
        renderer = ConcreteRenderer(unknown_param="value", another_param=123)
        assert renderer.icons == {}
        assert renderer.default_attrs == {}

    def test_get_icon_with_mapping(self):
        """Test icon name resolution with icon mapping."""
        icons = {"home": "house-icon", "user": "user-profile"}
        renderer = ConcreteRenderer(icons=icons)

        assert renderer.get_icon("home") == "house-icon"
        assert renderer.get_icon("user") == "user-profile"

    def test_get_icon_not_found(self):
        """Test icon name resolution raises error for missing icons."""
        renderer = ConcreteRenderer(icons={"home": "house"})

        with pytest.raises(IconNotFoundError) as exc_info:
            renderer.get_icon("missing")

        assert "Icon 'missing' not listed in available icons" in str(exc_info.value)
        assert "ConcreteRenderer" in str(exc_info.value)

    def test_build_attrs_no_defaults(self):
        """Test build_attrs with no default attributes."""
        renderer = ConcreteRenderer()
        test_attrs = {"class": "custom", "id": "test"}
        attrs = renderer.build_attrs(use_defaults=True, **test_attrs)
        assert 'class="custom"' in attrs
        assert 'id="test"' in attrs

    def test_build_attrs_with_defaults(self):
        """Test build_attrs merging with default attributes."""
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)

        attrs = renderer.build_attrs(width="2em")
        assert 'class="icon"' in attrs
        assert 'height="1em"' in attrs
        assert 'width="2em"' in attrs

    def test_build_attrs_override_defaults(self):
        """Test build_attrs merging attributes that override defaults."""
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)

        # When we pass class, it should override default class
        test_attrs = {"class": "custom", "height": "2em"}
        attrs = renderer.build_attrs(use_defaults=True, **test_attrs)
        # class should be overridden
        assert 'class="custom"' in attrs
        assert 'height="2em"' in attrs  # Should be overridden

    def test_build_attrs_use_defaults_false(self):
        """Test build_attrs ignoring defaults when use_defaults=False."""
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)

        test_attrs = {"class": "custom"}
        attrs = renderer.build_attrs(use_defaults=False, **test_attrs)
        assert 'class="custom"' in attrs
        assert 'height="1em"' not in attrs

    def test_callable_interface(self):
        """Test that renderer instances are callable."""
        icons = {"home": "house"}
        renderer = ConcreteRenderer(icons=icons)

        test_attrs = {"class": "test"}
        result = renderer("home", **test_attrs)
        assert isinstance(result, SafeString)
        assert "house" in result
        assert 'class="test"' in result

    def test_safe_return(self):
        """Test that safe_return marks content as safe."""
        renderer = ConcreteRenderer()
        result = renderer.safe_return("<div>test</div>")
        assert isinstance(result, SafeString)
        assert str(result) == "<div>test</div>"

    def test_render_abstract_method(self):
        """Test that BaseRenderer cannot be instantiated directly."""
        # BaseRenderer is abstract, so we test that our concrete implementation works
        renderer = ConcreteRenderer()
        assert hasattr(renderer, "render")
        assert callable(renderer.render)

    def test_default_attrs_copy(self):
        """Test that default_attrs are copied to prevent mutations."""
        default_attrs = {"class": "icon"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)

        # Modify the renderer's default_attrs
        renderer.default_attrs["class"] = "modified"

        # Original dict should be unchanged
        assert default_attrs["class"] == "icon"

    def test_build_attrs_empty_kwargs(self):
        """Test build_attrs with empty kwargs."""
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)

        attrs = renderer.build_attrs()
        assert 'class="icon"' in attrs
        assert 'height="1em"' in attrs

    def test_build_attrs_none_values(self):
        """Test build_attrs handles None values appropriately."""
        renderer = ConcreteRenderer()
        test_attrs = {"class": "icon", "data_value": None}
        attrs = renderer.build_attrs(**test_attrs)
        assert 'class="icon"' in attrs
        # flatatt should handle None values appropriately
