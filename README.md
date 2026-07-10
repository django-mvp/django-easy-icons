# Django Easy Icons

Easy, flexible icons for Django templates with support for multiple rendering backends.

## Overview

Django Easy Icons provides a simple, consistent way to include icons in your Django templates. It supports multiple icon sources including SVG files, font icon libraries (like Font Awesome), and SVG sprite sheets.

## Features

- **Multiple Renderers**: Support for SVG files, font icons, and sprite sheets
- **Template Integration**: Simple `{% icon %}` template tag
- **Flexible Configuration**: Configure multiple icon sets with different renderers
- **Attribute Merging**: Easily add classes and attributes to icons
- **Caching**: Built-in renderer caching for performance
- **Dict Attributes**: Pass a dict of extra attributes to the template tag via `extrakwargs`

## Installation

```bash
pip install django-easy-icons
```

Add `easy_icons` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'easy_icons',
]
```

## Quick Start

### 1. Configure Icon Renderers

Add configuration to your Django settings:

```python
EASY_ICONS = {
    "default": {
        "renderer": "easy_icons.renderers.SvgRenderer",
        "config": {
            "svg_dir": "icons",  # Template directory for SVG files
            "default_attrs": {
                "height": "1em",
                "fill": "currentColor"
            }
        },
        "icons": {
            "home": "home.svg",
            "user": "user.svg",
            "settings": "cog.svg"
        }
    }
}
```

### 2. Use in Templates

```html
{% load easy_icons %}

<!-- Basic usage -->
{% icon "home" %}

<!-- With additional attributes -->
{% icon "user" class="nav-icon" height="2em" %}

<!-- Using specific renderer -->
{% icon "heart" renderer="fontawesome" %}

<!-- Passing a dictionary of attributes (e.g. from another library) -->
{% icon "user" extrakwargs=attr_dict %}

<!-- Dictionary + explicit overrides (explicit wins) -->
{% icon "user" extrakwargs=attr_dict class="avatar" %}
```

### 3. Use in Python Code

```python
from easy_icons import icon

# Basic usage
home_icon = icon("home")

# With attributes
user_icon = icon("user", **{"class": "large", "data-role": "button"})

# Using specific renderer
fa_icon = icon("heart", renderer="fontawesome")
```

## Renderers

### SVG Renderer

Renders icons from SVG template files:

```python
EASY_ICONS = {
    "svg": {
        "renderer": "easy_icons.renderers.SvgRenderer",
        "config": {
            "svg_dir": "icons",
            "default_attrs": {"class": "svg-icon"}
        },
        "icons": {
            "home": "house.svg",
            "user": "person.svg"
        }
    }
}
```

### Provider Renderer

For font icon libraries like Font Awesome:

```python
EASY_ICONS = {
    "fontawesome": {
        "renderer": "easy_icons.renderers.ProviderRenderer",
        "config": {
            "tag": "i"
        },
        "icons": {
            "home": "fas fa-home",
            "user": "fas fa-user",
            "heart": "fas fa-heart"
        }
    }
}
```

### Sprites Renderer

For SVG sprite sheets:

```python
EASY_ICONS = {
    "sprites": {
        "renderer": "easy_icons.renderers.SpritesRenderer",
        "config": {
            "sprite_url": "/static/icons.svg"
        },
        "icons": {
            "logo": "brand-logo",
            "menu": "hamburger-menu"
        }
    }
}
```

## Configuration

### Multiple Renderers

You can configure multiple renderers and choose which one to use:

```python
EASY_ICONS = {
    "default": {
        "renderer": "easy_icons.renderers.SvgRenderer",
        "config": {"svg_dir": "icons"},
        "icons": {"home": "home.svg"}
    },
    "fontawesome": {
        "renderer": "easy_icons.renderers.ProviderRenderer",
        "config": {"tag": "i"},
        "icons": {"heart": "fas fa-heart"}
    },
    "sprites": {
        "renderer": "easy_icons.renderers.SpritesRenderer",
        "config": {"sprite_url": "/static/icons.svg"},
        "icons": {"logo": "brand"}
    }
}
```

Use in templates:

```html
{% icon "home" %}  <!-- Uses default renderer -->
{% icon "heart" renderer="fontawesome" %}
{% icon "logo" renderer="sprites" %}
```

### Icon Aliases

A single icon is often referred to by several names ("plus", "create", "add",
"new", ...). Instead of repeating the value once per name, declare the aliases
as a comma-separated key — it is expanded into individual entries at load time:

```python
EASY_ICONS = {
    "default": {
        "renderer": "easy_icons.renderers.ProviderRenderer",
        "config": {"tag": "i"},
        "icons": {
            "plus,create,add,new": "bi bi-plus",  # one icon, four names
            "trash,delete,remove": "bi bi-trash",
        },
    }
}
```

All of the following now resolve to the same icon:

```html
{% icon "plus" %}
{% icon "create" %}
{% icon "add" %}
```

Notes:

- Whitespace around each alias is ignored, so `"plus, create, add"` works too.
- Aliases work in both the `icons` mapping and in icon packs; explicit `icons`
  still override pack values on a per-name basis.
- Because the comma is the delimiter, a logical icon name cannot itself contain
  a comma.

### Default Attributes

Configure default attributes that will be applied to all icons from a renderer:

```python
"config": {
    "default_attrs": {
        "class": "icon",
        "aria-hidden": "true",
        "height": "1em"
    }
}
```

**Note**: Template tag attributes completely override default attributes - they don't merge.

### Attribute Overriding

Template tag attributes override default attributes:

- Provided attributes completely replace defaults: `height="1em"` + `height="2em"` = `height="2em"`
- This includes class attributes: `class="icon"` + `class="large"` = `class="large"`

## Advanced Usage

### Custom Renderers

Create custom renderers by extending `BaseRenderer`:

```python
from easy_icons.base import BaseRenderer
from django.utils.safestring import SafeString

class CustomRenderer(BaseRenderer):
    def render(self, name: str, **kwargs) -> SafeString:
        resolved_name = self.get_icon(name)
        attrs = self.build_attrs(**kwargs)
        html = f'<custom-icon {attrs}>{resolved_name}</custom-icon>'
        return self.safe_return(html)
```

### Disable Default Attributes

Use `use_defaults=False` to ignore default attributes:

```html
{% icon "home" use_defaults=False class="only-this-class" %}
```

```python
icon("home", use_defaults=False, **{"class": "only-this-class"})
```

## Testing

Run the test suite:

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=easy_icons --cov-report=html
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full changelog.
