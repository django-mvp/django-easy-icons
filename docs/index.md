# Django Easy Icons

Django Easy Icons is a flexible icon rendering system for Django that supports multiple icon sources and rendering methods. It provides a unified interface for working with different types of icons in your Django templates and Python code.

## Key Features

- **Configurable**: Supports multiple icon sets across multiple rendering strategies (e.g. SVG files, fontawesome, sprites).
- **Flexible**: Easily switch icons or rendering strategies at any time across your entire project.
- **Customisable**: Define default attributes in your settings, override them (if required) in templates.
- **Template Integration**: Simple, unified `{% icon %}` template tag that handles everything.
- **Type Safety**: Full type hints throughout the codebase for better IDE support
- **Comprehensive test suite**: 135+ tests covering all functionality.

## Quick Start

### Installation

```bash
pip install django-easy-icons
```

### Add `easy_icons` to your `INSTALLED_APPS`:

```python   
INSTALLED_APPS = [
    # ... other apps
    'easy_icons',
]
```

### Configure Icon Renderers

Add configuration to your Django settings:

```python
EASY_ICONS = {
    "default": {
        "renderer": "easy_icons.renderers.SvgRenderer",
        "config": {
            "svg_dir": "icons",  # default template directory for SVG files
            "default_attrs": {
                "height": "1em",
                "fill": "currentColor"
            }
        },
    }
}
```

### Use in Templates

```html
<!-- template.html -->
{% load easy_icons %}
{% icon "home" class="text-primary nav-icon" height="1em" width="auto" %}
```

### Use in Python Code

```python
from easy_icons import icon

html_icon = icon("home", height="1em", width="auto")
```

```{toctree}
renderers
usage-examples
```

```{toctree}
:caption: API reference
:maxdepth: 1

api/easy_icons/easy_icons
```

```{toctree}
:caption: Contributing
:maxdepth: 1

contributing/standards/testing
contributing/standards/code-documentation
```
