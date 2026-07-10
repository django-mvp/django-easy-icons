# ADR 0003 — Renderer config via star-expansion into __init__

**Status:** accepted (retro-documented at org onboarding, 2026-07-10)

## Decision

Each renderer declares its configuration explicitly as keyword arguments on `__init__`
(e.g. `SvgRenderer(*, svg_dir="icons", ...)`). The settings loader star-expands the user's
`config` dict directly into the initializer; shared data (`icons` mapping, `default_attrs`)
flows through `BaseRenderer.__init__`, which tolerates and ignores unknown extras.

## Why

Renderer config surface is self-documenting (it *is* the signature), type-checkable, and fails
loudly on typos at instantiation rather than silently at render time. No parallel
config-schema layer to keep in sync.

## Revisit if

Config needs validation beyond what keyword arguments express (cross-field constraints), or
the ignored-extras tolerance in `BaseRenderer.__init__` starts masking real typos in practice.
