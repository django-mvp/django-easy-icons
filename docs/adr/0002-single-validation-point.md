# ADR 0002 — Single validation point in BaseRenderer.get_icon

**Status:** accepted (retro-documented at org onboarding, 2026-07-10)

## Decision

Alias→icon validation happens in exactly one place: `BaseRenderer.get_icon`, which raises
`IconNotFoundError` for unknown aliases. Concrete renderers assume any name they receive has
passed that check and focus purely on output generation (`src/easy_icons/renderers.py`
module docstring states this contract).

## Why

Duplicated validation across renderers drifts; a single choke point gives one consistent error
type and message and keeps concrete renderers minimal. Error handling policy (raise vs
fallback) is decided at the API layer, not per renderer.

## Revisit if

A renderer must accept unmapped/raw identifiers (e.g. pass-through mode) — that would need an
explicit opt-out on the base contract, not a renderer-local bypass.
