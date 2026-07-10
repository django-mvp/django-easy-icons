# ADR 0001 — Renderer strategy architecture

**Status:** accepted (retro-documented at org onboarding, 2026-07-10)

## Decision

Icon output is produced by **Renderers**: concrete classes (`SvgRenderer`, provider/font,
sprite) inheriting from an abstract `BaseRenderer` (`src/easy_icons/base.py`). Each renderer
owns one rendering strategy; renderers are instantiated from the `EASY_ICONS` settings dict
and identified by name (e.g. `"default"`, `"fontawesome"`).

## Why

Icon sources genuinely differ (inline SVG templates, CSS-class fonts, sprite references) but
share alias resolution and attribute handling. The strategy split keeps each output format in
one small class while `BaseRenderer` centralizes the shared behavior; new backends are added by
subclassing without touching existing renderers or the public API (`easy_icons.utils.icon`).

## Revisit if

A renderer needs per-render state or async I/O — the current model assumes cheap, stateless
`render()` calls on cached instances.
