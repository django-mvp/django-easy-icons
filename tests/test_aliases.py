"""Tests for comma-separated alias expansion in icon mappings.

Aliases let a single ``EASY_ICONS`` entry declare several logical names for the
same icon by comma-separating the key, e.g. ``{"plus,create,add": "bi bi-plus"}``.
Expansion happens per configuration layer (each pack, then explicit icons) so
last-wins precedence is applied at the level of individual icon names.
"""

from django.test import override_settings

from easy_icons import utils

# Packs used to verify per-layer precedence during alias expansion.
PACK_WITH_ALIASES = {
    "plus,create,add": "pack-plus",
    "home": "pack-home",
}


class TestExpandAliases:
    """Unit tests for the low-level ``_expand_aliases`` helper."""

    def test_key_without_comma_unchanged(self):
        """A plain key is copied through untouched."""
        assert utils._expand_aliases({"home": "home.svg"}) == {"home": "home.svg"}

    def test_empty_mapping(self):
        """An empty mapping expands to an empty mapping."""
        assert utils._expand_aliases({}) == {}

    def test_comma_key_expands_to_each_alias(self):
        """Every comma-separated alias maps to the shared value."""
        result = utils._expand_aliases({"plus,create,add,new": "bi bi-plus"})
        assert result == {
            "plus": "bi bi-plus",
            "create": "bi bi-plus",
            "add": "bi bi-plus",
            "new": "bi bi-plus",
        }

    def test_whitespace_around_aliases_is_stripped(self):
        """Surrounding whitespace on each alias is ignored."""
        result = utils._expand_aliases({" plus , create ,add ": "bi bi-plus"})
        assert result == {
            "plus": "bi bi-plus",
            "create": "bi bi-plus",
            "add": "bi bi-plus",
        }

    def test_empty_aliases_are_dropped(self):
        """Blank tokens from stray/trailing commas are discarded."""
        result = utils._expand_aliases({"plus,,create,": "bi bi-plus"})
        assert result == {"plus": "bi bi-plus", "create": "bi bi-plus"}

    def test_mixed_plain_and_alias_keys(self):
        """Plain and aliased keys coexist in one mapping."""
        result = utils._expand_aliases({"home": "home.svg", "plus,add": "plus.svg"})
        assert result == {
            "home": "home.svg",
            "plus": "plus.svg",
            "add": "plus.svg",
        }


class TestResolveIconsWithAliases:
    """Alias behaviour through the ``resolve_icons`` merge path."""

    def test_explicit_icons_aliases_expanded(self):
        """Aliases declared in explicit ``icons`` are expanded."""
        config = {"icons": {"plus,create,add": "bi bi-plus"}}
        resolved = utils.resolve_icons(config, "default")
        assert resolved["plus"] == "bi bi-plus"
        assert resolved["create"] == "bi bi-plus"
        assert resolved["add"] == "bi bi-plus"

    def test_pack_aliases_expanded(self):
        """Aliases declared inside a pack are expanded."""
        config = {"packs": ["tests.test_aliases.PACK_WITH_ALIASES"]}
        resolved = utils.resolve_icons(config, "default")
        assert resolved["plus"] == "pack-plus"
        assert resolved["create"] == "pack-plus"
        assert resolved["add"] == "pack-plus"
        assert resolved["home"] == "pack-home"

    def test_explicit_alias_overrides_pack_per_name(self):
        """Explicit icons override pack values at the individual-name level.

        The pack aliases ``plus``/``create``/``add`` to ``pack-plus``; the
        explicit config re-aliases only ``add``/``remove``. ``add`` must take
        the explicit value while the untouched pack aliases survive.
        """
        config = {
            "packs": ["tests.test_aliases.PACK_WITH_ALIASES"],
            "icons": {"add,remove": "explicit-value"},
        }
        resolved = utils.resolve_icons(config, "default")
        assert resolved["add"] == "explicit-value"  # explicit wins
        assert resolved["remove"] == "explicit-value"
        assert resolved["plus"] == "pack-plus"  # untouched pack aliases remain
        assert resolved["create"] == "pack-plus"


class TestAliasesEndToEnd:
    """Aliases resolve through the public renderer and registry paths."""

    def _config(self):
        return {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"plus,create,add,new": "bi bi-plus"},
            }
        }

    def test_get_renderer_resolves_every_alias(self):
        """A renderer instance resolves each alias to the same identifier."""
        with override_settings(EASY_ICONS=self._config()):
            renderer = utils.get_renderer("default")
            for alias in ("plus", "create", "add", "new"):
                assert renderer.get_icon(alias) == "bi bi-plus"

    def test_registry_registers_every_alias(self):
        """The auto-detection registry indexes each alias name."""
        with override_settings(EASY_ICONS=self._config()):
            utils.build_icon_registry()
            for alias in ("plus", "create", "add", "new"):
                assert utils._icon_registry.get(alias) == "default"

    def test_icon_renders_via_any_alias(self):
        """The public ``icon()`` helper renders through any alias."""
        with override_settings(EASY_ICONS=self._config()):
            utils.build_icon_registry()
            html_plus = utils.icon("plus")
            html_add = utils.icon("add")
            assert "bi bi-plus" in html_plus
            assert "bi bi-plus" in html_add
