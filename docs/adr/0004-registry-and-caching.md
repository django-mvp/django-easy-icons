# ADR 0004 — Module-level renderer cache + global icon registry

**Status:** accepted (retro-documented at org onboarding, 2026-07-10)

## Decision

Renderer instances are cached in a module-level dict keyed by renderer name; a global
icon→renderer registry is built at app startup so `icon("home")` can auto-detect the owning
renderer without an explicit `renderer=` argument (`src/easy_icons/utils.py`). Auto-detection
searches `default` first, then other renderers. Icon packs (dotted-path imports) merge into a
renderer's mapping sequentially with last-wins precedence; invalid packs log a warning and are
skipped rather than raising.

## Why

Settings are immutable at runtime in Django's model, so instance caching is safe and removes
per-render construction cost. The registry makes the common case (`{% icon "home" %}` with no
renderer name) cheap and unambiguous. Pack failures degrade gracefully because a missing
third-party pack should not take down template rendering.

## Revisit if

Settings become mutable at runtime (tests already need `clear_cache()`), or alias collisions
across renderers become common enough that first-match auto-detection surprises users.
