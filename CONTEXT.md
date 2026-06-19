# Django Easy Icons — Domain Model

## Glossary

### Alias

A user-facing logical name that maps to an icon. Multiple aliases may point to the same icon. This is the key in the `icons` mapping and what users pass to `{% icon "home" %}`.

### Icon

The resolved identifier — the renderer-specific value (e.g. `"home.svg"`, `"fas fa-heart"`, `"0-circle"`). This is the actual underlying asset that a renderer consumes.

### Renderer

A configured instance responsible for producing HTML output from an icon. Each renderer has a **renderer type** (SVG, Provider, or Sprite), a configuration, and a set of alias→icon mappings. Renderers are identified by a name (e.g. `"default"`, `"fontawesome"`) in the `EASY_ICONS` settings dict.

### Renderer Type

The rendering strategy used by a renderer. There are three types:

- **SVG** — loads SVG template files and injects attributes into the `<svg>` element
- **Provider** — outputs HTML elements with CSS class strings for font icon libraries (e.g., Font Awesome)
- **Sprite** — outputs `<svg><use href="...#icon"></use></svg>` referencing an external sprite sheet

### Icon Pack

A Python module that exports a raw dictionary of icon definitions (alias→icon). Packs are a **distribution mechanism** — third-party packages ship a dict and tell users to add the pack path to their renderer config. Packs are merged with last-wins precedence among themselves, and explicit icons always override pack icons. A pack has no opinion on renderer type; it is just a dict.

### Icon Registry

A global mapping from alias names to renderer names, built at Django startup. It enables auto-detection — when a user calls `{% icon "home" %}` without specifying a renderer, the registry determines which renderer owns that alias. The first renderer (in settings order) that defines an alias wins in the registry, but aliases are **per-renderer** — the same alias can exist in multiple renderers and be disambiguated via the explicit `renderer=` parameter.

### Discoverability

An alias is **discoverable** if it can be resolved by the `icon()` function — i.e., it exists in some renderer's icon mapping and can be looked up by name. The management command `show_icon_registry` serves both as a diagnostic tool (debugging configuration) and a discovery mechanism (learning what icons are available).

### Renderer Cache

A module-level cache of instantiated renderer objects, keyed by renderer name. Renderers are cached to avoid re-instantiation on every render call. Cleared via `clear_cache()`.

### Icon Mapping

A dictionary that maps aliases to icons within a single renderer. This is the alias→icon lookup table that each renderer holds as `self.icons`. It is built by merging icon packs (last-wins) and then overlaying explicit icons on top.

### Configuration

The top-level `EASY_ICONS` Django setting — a dict that defines all renderers, their types, icon mappings, packs, and defaults. Each key in the configuration is a renderer name, and each value contains the renderer's class path, config options, icon packs, and explicit icon definitions.

### Render Operation

The act of rendering an icon — taking an alias and producing HTML output. This is the unified concept exposed by the `icon()` function and the `{% icon %}` template tag. It internally resolves a renderer and delegates to that renderer's `render()` method, but these stages are not exposed as separate domain concepts.

### Initialization

The startup phase where Django loads the app configuration, merges icon packs, builds the icon registry, and instantiates cached renderers. This happens once when the Django app starts, via `EasyIconsConfig.ready()`.

### Rendering

The runtime phase where icons are produced — templates call `{% icon %}`, Python code calls `icon()`, and renderers produce HTML output from aliases.

### Default Attribute

An HTML attribute defined in a renderer's `default_attrs` config. These are **always** applied to every render for that renderer as the baseline, but can be overridden at render time by explicit kwargs. They serve as the renderer's default styling (e.g., SVG fill, height).

### Call-Level Default

A dict of attributes passed via the template tag's `defaults` parameter (or `extrakwargs`). This is a **render-time override mechanism** — it allows users to pass a dictionary of attributes that gets unpacked into kwargs. It exists because Django templates cannot expand dicts natively, so packages like django-cotton that group attrs as dicts need a way to pass them through. Call-level defaults are merged with explicit kwargs at render time, with explicit kwargs winning on conflict.

### Override

A replacement relationship where one value completely supersedes another — the preceding value is no longer discoverable. Used when explicit icons replace pack icons, or when render-time kwargs replace default attributes. Override means the old value is gone, not layered.

### Asset

The underlying resource an icon points to after resolution. The type of asset depends on the renderer: SVG template files (SvgRenderer), CSS class strings (ProviderRenderer), or sprite sheet symbols (SpritesRenderer). Assets are what renderers actually consume to produce HTML output.
