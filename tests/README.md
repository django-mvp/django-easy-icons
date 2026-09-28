# Django Easy Icons - Test Suite

This directory contains a comprehensive test suite for the django-easy-icons package using pytest.

## Test Files Overview

Each test module mirrors the source module it exercises, with one `Test<Subject>` class per unit.
The rules are in [`docs/contributing/standards/testing.md`](../docs/contributing/standards/testing.md).

| Test module | Source module |
|---|---|
| `test_base.py` | `easy_icons/base.py` |
| `test_exceptions.py` | `easy_icons/exceptions.py` |
| `test_renderers.py` | `easy_icons/renderers.py` |
| `test_templatetags.py` | `easy_icons/templatetags/easy_icons.py` |
| `test_utils.py` | `easy_icons/utils.py` |
| `test_management/test_commands/test_show_icon_registry.py` | `easy_icons/management/commands/show_icon_registry.py` |

`conftest.py` holds the shared fixtures: renderer configurations and cache clearing between
tests.

## Running Tests

### Using Pytest (Recommended)

The project is configured to use pytest with the settings in `pyproject.toml`:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run tests with coverage
pytest --cov=easy_icons

# Run specific test file
pytest tests/test_utils.py

# Run specific test class
pytest tests/test_utils.py::TestGetRenderer

# Run specific test method
pytest tests/test_utils.py::TestGetRenderer::test_get_renderer_caching
```

### Test Configuration

The tests are configured in `pyproject.toml` with:

- Django settings module: `tests.settings`
- Test discovery patterns: `test_*.py`, `*_test.py`, `tests.py`
- Coverage reporting for the `easy_icons` package
- Automatic cache clearing between tests

### Environment Setup

Tests require:
- Django (configured automatically via `tests.settings`)
- The `easy_icons` package in the Python path
- Test dependencies: pytest, pytest-django, pytest-cov

## Test Coverage Areas

### Configuration System
- ✅ Configuration loading and validation
- ✅ Multiple renderer configuration
- ✅ Settings change handling
- ✅ Error cases and edge conditions
- ✅ Cache management

### Base Renderer Functionality
- ✅ Icon name resolution and mapping
- ✅ HTML attribute building and merging
- ✅ Class attribute handling
- ✅ Input validation and sanitization
- ✅ SafeString handling

### Renderer Implementations
- ✅ **SvgRenderer**: Template loading, attribute injection, SVG manipulation
- ✅ **ProviderRenderer**: Font icon rendering, tag customization
- ✅ **SpritesRenderer**: SVG sprite handling, URL construction

### Main API
- ✅ `icon()` function parameter handling
- ✅ Renderer selection and configuration
- ✅ Error propagation
- ✅ Django template tag integration

### Django Integration
- ✅ Template tag functionality
- ✅ Context variable handling
- ✅ SafeString preservation
- ✅ App configuration and registration

### Error Handling
- ✅ Custom exception behavior
- ✅ Error message clarity
- ✅ Exception chaining and context

## Test Examples

### Testing a Custom Renderer

```python
def test_custom_renderer():
    renderer = ProviderRenderer(
        tag="span",
        icons={"home": "custom-home"},
        default_attrs={"class": "icon"}
    )

    result = renderer.render("home", **{"class": "large"})

    assert '<span' in result
    assert 'custom-home' in result
    assert 'icon large' in result
```

### Testing Configuration

```python
@override_settings(EASY_ICONS={
    "default": {
        "renderer": "easy_icons.renderers.SvgRenderer",
        "config": {"svg_dir": "icons"}
    }
})
def test_configuration():
    clear_config_cache()
    config = get_config()
    assert config["default"]["renderer"] == "easy_icons.renderers.SvgRenderer"
```

### Testing Template Tags

```python
def test_template_tag():
    template = Template("{% load easy_icons %}{% icon 'home' class='nav' %}")
    result = template.render(Context())
    assert 'nav' in result
```

## Verification

A verification script `verify_tests.py` is available to test the basic functionality:

```bash
python verify_tests.py
```

This script:
1. Tests basic imports without Django
2. Tests renderer functionality
3. Tests Django integration
4. Provides a quick health check

## Test Philosophy

The test suite follows these principles:

1. **Comprehensive Coverage**: Tests cover all public APIs and common usage patterns
2. **Isolation**: Tests are independent and don't rely on external resources
3. **Realistic Scenarios**: Tests include real-world usage patterns
4. **Edge Case Coverage**: Tests handle error conditions and edge cases
5. **Performance Awareness**: Tests consider performance implications
6. **Django Integration**: Tests work within Django's testing framework

## Continuous Integration

The tests are designed to work in CI environments with:
- Automatic Django setup
- No external dependencies (templates, files)
- Cross-platform compatibility
- Clear error messages for debugging

For production use, you may want to add tests with actual SVG template files to test the full SvgRenderer functionality.
