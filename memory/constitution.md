# django-easy-icons Constitution

<!-- Authored at org onboarding (2026-07-10). Changes go through the constitution pathway
     (human-gated), never mid-feature. Read at the Constitution Check in /plan and by
     reviewers. -->

## Core articles (org defaults)

### Article I — Test-First
No implementation before a failing test exists for the behavior. Tests written by an
Implementer for its own tasks; pre-existing tests are never modified or deleted without an
approved decisions.md entry (tamper-check enforced).

### Article II — Simplicity
Start with the simplest design that satisfies the spec. New dependencies, new abstractions,
and new infrastructure each require a stated justification in plan.md Complexity Tracking.
YAGNI over speculation. This package is deliberately small (~600 LOC of source) — keep it that way.

### Article III — Anti-Abstraction
No wrapper layers, base classes, or "future-proofing" indirection without a present, concrete
second use. Prefer duplication over the wrong abstraction. The one sanctioned abstraction is
the renderer strategy (ADR 0001).

### Article IV — Integration-First
Contracts and integration points are designed and tested before internals are polished.
Acceptance scenarios exercise the package the way users touch it: settings config, the
`{% icon %}` template tag, and the `icon()` function.

## Project articles

### Article V — Public API stability
The public API is `easy_icons.utils.icon`, `get_renderer`, `clear_cache`, the `{% icon %}`
template tag, the `EASY_ICONS` settings shape, and the documented renderer classes. Breaking
changes to any of these require a deprecation path (warn one minor release before removal)
and a CHANGELOG entry. Semver applies (currently 0.x: minor = may break with notice).

### Article VI — Compatibility matrix
Supported: Python 3.11–3.12, Django 4.2 LTS and current stable (CI matrix is authoritative).
New code must pass the full matrix; dropping a version is a constitution-level change.

### Article VII — Renderer contract
New renderers subclass `BaseRenderer`, declare config as explicit `__init__` kwargs
(ADR 0003), perform no alias validation of their own (ADR 0002), and return `SafeString`
only through `safe_return`. HTML output must escape attribute values via the shared
attr-building path — never hand-rolled string interpolation of user input.

## Quality bar

- Coverage may not decrease (codecov tracks; the coverage matrix cell is the reference).
- Every public API change updates README + docs + CHANGELOG in the same PR.
- Type hints on all public functions; mypy clean per repo config.

## Non-negotiables

- One PR per feature; Sam merges; the org never merges.
- Machine verification (tests/build/lint) gates every stage exit; no LLM judgment can
  override a red gate.
