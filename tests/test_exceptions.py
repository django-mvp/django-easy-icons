"""Tests for custom exceptions."""

import pytest

from easy_icons.exceptions import IconNotFoundError, InvalidSvgError


class TestIconNotFoundError:
    """Test cases for IconNotFoundError exception."""

    def test_icon_not_found_error_creation(self):
        """Test creating IconNotFoundError."""
        error = IconNotFoundError("Test message")
        assert str(error) == "Test message"
        assert isinstance(error, Exception)

    def test_icon_not_found_error_inheritance(self):
        """Test IconNotFoundError inherits from Exception."""
        error = IconNotFoundError("Test")
        assert isinstance(error, Exception)

    def test_icon_not_found_error_with_empty_message(self):
        """Test IconNotFoundError with empty message."""
        error = IconNotFoundError("")
        assert str(error) == ""

    def test_icon_not_found_error_with_none_message(self):
        """Test IconNotFoundError with None message."""
        error = IconNotFoundError(None)
        assert str(error) == "None"

    def test_icon_not_found_error_raising(self):
        """Test raising IconNotFoundError."""
        with pytest.raises(IconNotFoundError) as exc_info:
            raise IconNotFoundError("Icon 'missing' not found")

        assert "Icon 'missing' not found" in str(exc_info.value)

    def test_icon_not_found_error_catching(self):
        """Test catching IconNotFoundError."""
        try:
            raise IconNotFoundError("Test error")
        except IconNotFoundError as e:
            assert "Test error" in str(e)
        except Exception:
            pytest.fail("Should have caught IconNotFoundError specifically")

    def test_icon_not_found_error_with_format_string(self):
        """Test IconNotFoundError with formatted message."""
        icon_name = "missing_icon"
        renderer_name = "TestRenderer"
        message = f"Icon '{icon_name}' not found in {renderer_name}"

        error = IconNotFoundError(message)
        assert icon_name in str(error)
        assert renderer_name in str(error)


class TestInvalidSvgError:
    """Test cases for InvalidSvgError exception."""

    def test_invalid_svg_error_creation(self):
        """Test creating InvalidSvgError."""
        error = InvalidSvgError("Test message")
        assert str(error) == "Test message"
        assert isinstance(error, Exception)

    def test_invalid_svg_error_inheritance(self):
        """Test InvalidSvgError inherits from Exception."""
        error = InvalidSvgError("Test")
        assert isinstance(error, Exception)

    def test_invalid_svg_error_with_empty_message(self):
        """Test InvalidSvgError with empty message."""
        error = InvalidSvgError("")
        assert str(error) == ""

    def test_invalid_svg_error_with_none_message(self):
        """Test InvalidSvgError with None message."""
        error = InvalidSvgError(None)
        assert str(error) == "None"

    def test_invalid_svg_error_raising(self):
        """Test raising InvalidSvgError."""
        with pytest.raises(InvalidSvgError) as exc_info:
            raise InvalidSvgError("No <svg> tag found")

        assert "No <svg> tag found" in str(exc_info.value)

    def test_invalid_svg_error_catching(self):
        """Test catching InvalidSvgError."""
        try:
            raise InvalidSvgError("Malformed SVG")
        except InvalidSvgError as e:
            assert "Malformed SVG" in str(e)
        except Exception:
            pytest.fail("Should have caught InvalidSvgError specifically")

    def test_invalid_svg_error_with_format_string(self):
        """Test InvalidSvgError with formatted message."""
        svg_content = "<div>Not SVG</div>"
        message = f"Invalid SVG content: {svg_content}"

        error = InvalidSvgError(message)
        assert svg_content in str(error)
        assert "Invalid SVG content" in str(error)


class TestExceptionHierarchy:
    """Test cases for exception hierarchy and relationships."""

    def test_both_inherit_from_exception(self):
        """Test that both custom exceptions inherit from Exception."""
        icon_error = IconNotFoundError("test")
        svg_error = InvalidSvgError("test")

        assert isinstance(icon_error, Exception)
        assert isinstance(svg_error, Exception)

    def test_exceptions_are_distinct(self):
        """Test that the two exception types are distinct."""
        assert IconNotFoundError != InvalidSvgError
        assert not issubclass(IconNotFoundError, InvalidSvgError)
        assert not issubclass(InvalidSvgError, IconNotFoundError)

    def test_catch_specific_exceptions(self):
        """Test catching specific exception types."""
        # Test IconNotFoundError
        with pytest.raises(IconNotFoundError):
            raise IconNotFoundError("Not found")

        # Test InvalidSvgError
        with pytest.raises(InvalidSvgError):
            raise InvalidSvgError("Invalid")

    def test_catch_as_general_exception(self):
        """Test that custom exceptions can be caught as general Exception."""
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
        """Test that exception args are accessible."""
        icon_error = IconNotFoundError("icon not found")
        svg_error = InvalidSvgError("svg invalid")

        assert icon_error.args == ("icon not found",)
        assert svg_error.args == ("svg invalid",)

    def test_exception_repr(self):
        """Test exception representation."""
        icon_error = IconNotFoundError("test icon error")
        svg_error = InvalidSvgError("test svg error")

        assert "IconNotFoundError" in repr(icon_error)
        assert "test icon error" in repr(icon_error)
        assert "InvalidSvgError" in repr(svg_error)
        assert "test svg error" in repr(svg_error)
