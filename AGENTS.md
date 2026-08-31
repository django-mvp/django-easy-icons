# AGENTS.md - Agent Configuration for django-easy-icons

Easy, flexible icons for Django templates: aliases resolve through named renderers (SVG,
provider/font, sprite) configured in the `EASY_ICONS` settings dict. See `CONTEXT.md` for the
domain glossary — use its vocabulary.

## Stack & commands

- **Stack:** Python 3.11–3.12, Django 4.2/5.2, Poetry-managed, src layout (`src/easy_icons/`)
- **Install:** `poetry install`
- **Test:** `poetry run pytest` (coverage: `poetry run pytest --cov=easy_icons`)
- **Type-check:** `poetry run mypy src`
- **Build:** `poetry build`
- **Docs:** Sphinx under `docs/`; example project under `example/`

## Agent skills

### Issue tracker

Issues tracked in GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary mapped 1:1 to canonical roles (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — one `CONTEXT.md` at root and `docs/adr/` for architectural decisions. See `docs/agents/domain.md`.

### CI checks

Required status checks (ruleset-enforced, exact names): `checks-complete` (tests matrix
summary), `Code Quality`, `Security Scan`. Workflows: `tests.yml`, `build.yml` — both run on
every PR (no paths filter on `pull_request`; required checks must always report).

## Engineering org

This repo is operated by the autonomous engineering org (Forge). Feature work runs
spec→plan→tasks→implement→review→PR through org-side skills — there is no Spec Kit install
here; `specs/NNN-slug/` directories are generated per feature. Constitution:
`CONSTITUTION.md`. Budget overrides: none (org defaults apply).
