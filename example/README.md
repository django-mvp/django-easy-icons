# Django Easy Icons - Example App

This is a comprehensive Django application demonstrating all the features of Django Easy Icons with multiple renderer types, static file integration, and best practices for template usage.

## Running the Example

1. **Start the development server:**
   ```bash
   cd /path/to/django-easy-icons
   python manage.py runserver --settings=example.settings
   ```

2. **Visit the demo:**
   - Main demo: http://127.0.0.1:8000/

## Features Demonstrated

### 1. SVG Renderer (Default)
- Renders SVG files from the `example/templates/icons/` directory
- Supports custom attributes and styling
- Demonstrates icon mappings and custom paths

### 2. Font Awesome Provider Renderer
- Renders Font Awesome icons using `<i>` tags
- Shows class-based styling and custom attributes
- Demonstrates icon name mapping

### 3. SVG Sprites Renderer
- Shows sprite-based icon rendering (conceptual example)
- Demonstrates `<svg><use>` element generation

## Configuration

The example uses this configuration in `example/settings.py`:

```python
EASY_ICONS = {
    # Default SVG renderer
    "default": {
        "renderer": "easy_icons.renderers.SvgRenderer",
        "config": {
            "svg_dir": "icons",
            "default_attrs": {"height": "1em", "fill": "currentColor"},
        },
        "icons": {
            "home": "home.svg",
            "alt_dir": "../alt_dir/alt_dir.svg",
        },
    },
    # Font Awesome provider renderer
    "fontawesome": {
        "renderer": "easy_icons.renderers.ProviderRenderer",
        "config": {
            "tag": "i",
            "default_attrs": {"class": "fas"},
        },
        "icons": {
            "heart": "fa-heart",
            "star": "fa-star",
            "admin": "fa-toolbox",
        },
    },
    # SVG sprite renderer (example)
    "sprites": {
        "renderer": "easy_icons.renderers.SpritesRenderer",
        "config": {
            "sprite_path": "sprites/icons.svg",
            "default_attrs": {"class": "icon"},
        },
        "icons": {
            "logo": "company-logo",
            "menu": "hamburger-menu",
        },
    },
}
```

## Template Usage

```django
{% load easy_icons %}

<!-- Default renderer (SVG) -->
{% icon "home" %}
{% icon "home" width="32" height="32" class="large" %}

<!-- Specific renderer -->
{% icon "heart" renderer="fontawesome" %}
{% icon "star" renderer="fontawesome" class="gold" %}

<!-- Sprites -->
{% icon "logo" renderer="sprites" width="24" height="24" %}
```

## Programmatic Usage

```python
import easy_icons
from easy_icons.utils import get_renderer

# Render icons
svg_icon = easy_icons.icon("home")
fa_icon = easy_icons.icon("heart", renderer="fontawesome")
styled_icon = easy_icons.icon("star", renderer="fontawesome", class_="gold")

# Get renderer info (if needed)
fontawesome_renderer = get_renderer("fontawesome")
```

## Key Improvements

1. **Class-based architecture** - Better encapsulation and extensibility
2. **Django STORAGES-like configuration** - Familiar pattern for Django developers
3. **Per-renderer settings** - Each renderer can have its own configuration
4. **Icon mappings** - Map logical names to actual icon identifiers
5. **Flexible attributes** - Easy customization of generated HTML
6. **Comprehensive validation** - Better error handling and debugging

## File Structure

```
example/
├── templates/
│   ├── base.html              # Main demo page
│   ├── icons/                 # SVG files for default renderer
│   │   ├── home.svg
│   │   ├── user.svg
│   │   └── star.svg
│   └── alt_dir/               # Alternative directory example
│       └── alt_dir.svg
├── apps.py                    # Django app configuration
├── settings.py                # Example-specific settings
├── urls.py                    # URL patterns with demo views
└── README.md                  # This file
```
