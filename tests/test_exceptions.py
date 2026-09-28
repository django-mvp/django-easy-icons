"""Tests for custom exceptions."""

import pytest

from easy_icons.exceptions import IconNotFoundError, InvalidSvgError


class TestIconNotFoundError:
    def test_icon_not_found_error_creation(self):
        error = IconNotFoundError("Test message")
        assert str(error) == "Test message"
        assert isinstance(error, Exception)

    def test_icon_not_found_error_inheritance(self):
        error = IconNotFoundError("Test")
        assert isinstance(error, Exception)

    def test_icon_not_found_error_with_empty_message(self):
        error = IconNotFoundError("")
        assert str(error) == ""

    def test_icon_not_found_error_with_none_message(self):
        error = IconNotFoundError(None)
        assert str(error) == "None"

    def test_icon_not_found_error_raising(self):
        with pytest.raises(IconNotFoundError) as exc_info:
            raise IconNotFoundError("Icon 'missing' not found")

        assert "Icon 'missing' not found" in str(exc_info.value)

    def test_icon_not_found_error_catching(self):
        try:
            raise IconNotFoundError("Test error")
        except IconNotFoundError as e:
            assert "Test error" in str(e)
        except Exception:
            pytest.fail("Should have caught IconNotFoundError specifically")

    def test_icon_not_found_error_with_format_string(self):
        icon_name = "missing_icon"
        renderer_name = "TestRenderer"
        message = f"Icon '{icon_name}' not found in {renderer_name}"

        error = IconNotFoundError(message)
        assert icon_name in str(error)
        assert renderer_name in str(error)


class TestInvalidSvgError:
    def test_invalid_svg_error_creation(self):
        error = InvalidSvgError("Test message")
        assert str(error) == "Test message"
        assert isinstance(error, Exception)

    def test_invalid_svg_error_inheritance(self):
        error = InvalidSvgError("Test")
        assert isinstance(error, Exception)

    def test_invalid_svg_error_with_empty_message(self):
        error = InvalidSvgError("")
        assert str(error) == ""

    def test_invalid_svg_error_with_none_message(self):
        error = InvalidSvgError(None)
        assert str(error) == "None"

    def test_invalid_svg_error_raising(self):
        with pytest.raises(InvalidSvgError) as exc_info:
            raise InvalidSvgError("No <svg> tag found")

        assert "No <svg> tag found" in str(exc_info.value)

    def test_invalid_svg_error_catching(self):
        try:
            raise InvalidSvgError("Malformed SVG")
        except InvalidSvgError as e:
            assert "Malformed SVG" in str(e)
        except Exception:
            pytest.fail("Should have caught InvalidSvgError specifically")

    def test_invalid_svg_error_with_format_string(self):
        svg_content = "<div>Not SVG</div>"
        message = f"Invalid SVG content: {svg_content}"

        error = InvalidSvgError(message)
        assert svg_content in str(error)
        assert "Invalid SVG content" in str(error)


class TestExceptionHierarchy:
    def test_both_inherit_from_exception(self):
        icon_error = IconNotFoundError("test")
        svg_error = InvalidSvgError("test")

        assert isinstance(icon_error, Exception)
        assert isinstance(svg_error, Exception)

    def test_exceptions_are_distinct(self):
        assert IconNotFoundError != InvalidSvgError
        assert not issubclass(IconNotFoundError, InvalidSvgError)
        assert not issubclass(InvalidSvgError, IconNotFoundError)

    def test_catch_specific_exceptions(self):
        # Test IconNotFoundError
        with pytest.raises(IconNotFoundError):
            raise IconNotFoundError("Not found")

        # Test InvalidSvgError
        with pytest.raises(InvalidSvgError):
            raise InvalidSvgError("Invalid")

    def test_catch_as_general_exception(self):
        # IconNotFoundError
        try:
            raise IconNotFoundError("Not found")
        except Exception as e:
            assert isinstance(e, IconNotFoundError)

        # InvalidSvgError
        try:
            raise InvalidSvgError("Invalid")
        except Exception as e:
            assert isinstance(e, InvalidSvgError)

    def test_exception_args_property(self):
        icon_error = IconNotFoundError("icon not found")
        svg_error = InvalidSvgError("svg invalid")

        assert icon_error.args == ("icon not found",)
        assert svg_error.args == ("svg invalid",)

    def test_exception_repr(self):
        icon_error = IconNotFoundError("test icon error")
        svg_error = InvalidSvgError("test svg error")

        assert "IconNotFoundError" in repr(icon_error)
        assert "test icon error" in repr(icon_error)
        assert "InvalidSvgError" in repr(svg_error)
        assert "test svg error" in repr(svg_error)
