# Django Easy Icons - Test Suite

This directory contains a comprehensive test suite for the django-easy-icons package using pytest.

## Test Files Overview

### Core Component Tests

1. **`test_config.py`** - Configuration Management Tests
   - Tests the `EasyIconsConfig` class and configuration loading
   - Tests configuration validation and error handling
   - Tests configuration caching and cache invalidation
   - Tests Django settings integration and signal handling
   - Covers configuration edge cases and validation errors

2. **`test_base.py`** - Base Renderer Tests
   - Tests the abstract `BaseRenderer` class functionality
   - Tests icon name resolution and validation
   - Tests attribute building and class merging
   - Tests HTML attribute normalization and safety
   - Tests the renderer callable interface

3. **`test_renderers.py`** - Concrete Renderer Tests
   - **SvgRenderer Tests**: Template-based SVG icon rendering, attribute injection
   - **ProviderRenderer Tests**: Font icon class rendering (FontAwesome, etc.)
   - **SpritesRenderer Tests**: SVG sprite symbol rendering with `<use>` elements
   - Tests renderer initialization, configuration, and rendering output

4. **`test_utils.py`** - Main Icon Function Tests
   - Tests the main `icon()` function that users interact with
   - Tests renderer selection and parameter passing
   - Tests error propagation and edge cases
   - Tests integration with the configuration system

5. **`test_templatetags.py`** - Django Template Tag Tests
   - Tests the `{% icon %}` template tag functionality
   - Tests parameter passing and attribute handling
   - Tests integration with Django template system
   - Tests template context and variable handling

6. **`test_exceptions.py`** - Exception Handling Tests
   - Tests the `IconNotFoundError` exception class
   - Tests exception raising and catching patterns
   - Tests error messages and context information

7. **`test_apps.py`** - Django App Configuration Tests
   - Tests the `EasyIconsConfig` Django app configuration
   - Tests app registration and Django integration
   - Tests app metadata and configuration

8. **`test_integration.py`** - Full Integration Tests
   - Tests complete workflows using multiple components
   - Tests real-world usage scenarios
   - Tests performance with multiple icons and renderers
   - Tests complex attribute merging and configuration scenarios

### Test Utilities

- **`conftest.py`** - Pytest configuration and shared fixtures
  - Provides test configuration fixtures for different renderer types
  - Helper functions for HTML validation and assertion
  - Automatic cache clearing between tests

- **`run_tests.py`** - Standalone test runner
  - Can run tests without pytest if needed
  - Sets up Django environment for testing

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
pytest tests/test_config.py

# Run specific test class
pytest tests/test_config.py::TestEasyIconsConfig

# Run specific test method
pytest tests/test_config.py::TestEasyIconsConfig::test_get_config_caching
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
