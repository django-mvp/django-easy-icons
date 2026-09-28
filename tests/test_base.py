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
    def test_init_with_no_args(self):
        renderer = ConcreteRenderer()
        assert renderer.icons == {}
        assert renderer.default_attrs == {}

    def test_init_with_icons(self):
        icons = {"home": "house", "user": "person"}
        renderer = ConcreteRenderer(icons=icons)
        assert renderer.icons == icons

    def test_init_with_default_attrs(self):
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)
        assert renderer.default_attrs == default_attrs

    def test_init_with_extra_kwargs(self):
        renderer = ConcreteRenderer(unknown_param="value", another_param=123)
        assert renderer.icons == {}
        assert renderer.default_attrs == {}

    def test_get_icon_with_mapping(self):
        icons = {"home": "house-icon", "user": "user-profile"}
        renderer = ConcreteRenderer(icons=icons)

        assert renderer.get_icon("home") == "house-icon"
        assert renderer.get_icon("user") == "user-profile"

    def test_get_icon_not_found(self):
        renderer = ConcreteRenderer(icons={"home": "house"})

        with pytest.raises(IconNotFoundError) as exc_info:
            renderer.get_icon("missing")

        assert "ConcreteRenderer" in str(exc_info.value)

    def test_build_attrs_no_defaults(self):
        renderer = ConcreteRenderer()
        test_attrs = {"class": "custom", "id": "test"}
        attrs = renderer.build_attrs(use_defaults=True, **test_attrs)
        assert 'class="custom"' in attrs
        assert 'id="test"' in attrs

    def test_build_attrs_with_defaults(self):
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)

        attrs = renderer.build_attrs(width="2em")
        assert 'class="icon"' in attrs
        assert 'height="1em"' in attrs
        assert 'width="2em"' in attrs

    def test_build_attrs_override_defaults(self):
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)

        # When we pass class, it should override default class
        test_attrs = {"class": "custom", "height": "2em"}
        attrs = renderer.build_attrs(use_defaults=True, **test_attrs)
        # class should be overridden
        assert 'class="custom"' in attrs
        assert 'height="2em"' in attrs  # Should be overridden

    def test_build_attrs_use_defaults_false(self):
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)

        test_attrs = {"class": "custom"}
        attrs = renderer.build_attrs(use_defaults=False, **test_attrs)
        assert 'class="custom"' in attrs
        assert 'height="1em"' not in attrs

    def test_callable_interface(self):
        icons = {"home": "house"}
        renderer = ConcreteRenderer(icons=icons)

        test_attrs = {"class": "test"}
        result = renderer("home", **test_attrs)
        assert isinstance(result, SafeString)
        assert "house" in result
        assert 'class="test"' in result

    def test_safe_return(self):
        renderer = ConcreteRenderer()
        result = renderer.safe_return("<div>test</div>")
        assert isinstance(result, SafeString)
        assert str(result) == "<div>test</div>"

    def test_render_abstract_method(self):
        # BaseRenderer is abstract, so we test that our concrete implementation works
        renderer = ConcreteRenderer()
        assert hasattr(renderer, "render")
        assert callable(renderer.render)

    def test_default_attrs_copy(self):
        default_attrs = {"class": "icon"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)

        # Modify the renderer's default_attrs
        renderer.default_attrs["class"] = "modified"

        # Original dict should be unchanged
        assert default_attrs["class"] == "icon"

    def test_build_attrs_empty_kwargs(self):
        default_attrs = {"class": "icon", "height": "1em"}
        renderer = ConcreteRenderer(default_attrs=default_attrs)

        attrs = renderer.build_attrs()
        assert 'class="icon"' in attrs
        assert 'height="1em"' in attrs

    def test_build_attrs_none_values(self):
        renderer = ConcreteRenderer()
        test_attrs = {"class": "icon", "data_value": None}
        attrs = renderer.build_attrs(**test_attrs)
        assert 'class="icon"' in attrs
        # flatatt should handle None values appropriately
