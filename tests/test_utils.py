"""Tests for easy_icons.utils."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template
from django.test import override_settings
from django.utils.safestring import SafeString

from easy_icons import icon as easy_icon
from easy_icons import utils
from easy_icons.exceptions import IconNotFoundError
from easy_icons.renderers import ProviderRenderer, SpritesRenderer, SvgRenderer
from easy_icons.utils import clear_cache

# Packs used to verify per-layer precedence during alias expansion.
PACK_WITH_ALIASES = {
    "plus,create,add": "pack-plus",
    "home": "pack-home",
}

PACK_ONE = {
    "home": "home-v1.svg",
    "user": "user-v1.svg",
    "star": "star-v1.svg",
}

PACK_TWO = {
    "user": "user-v2.svg",  # Override from PACK_ONE
    "heart": "heart-v2.svg",  # New icon
}

PACK_THREE = {
    "star": "star-v3.svg",  # Override from PACK_ONE
    "admin": "admin-v3.svg",  # New icon
}

FONTAWESOME_PACK = {
    "heart": "fa-heart",
    "star": "fa-star",
}

INVALID_PACK = ["not", "a", "dictionary"]


class TestGetRenderer:
    def setup_method(self):
        utils.clear_cache()

    def test_get_renderer_default(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer()

            assert isinstance(renderer, SvgRenderer)
            assert renderer.svg_dir == "icons"
            assert renderer.icons == {"home": "home.svg"}

    def test_get_renderer_named(self):
        config = {
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"heart": "fa-heart"},
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer("fontawesome")

            assert isinstance(renderer, ProviderRenderer)
            assert renderer.tag == "i"
            assert renderer.icons == {"heart": "fa-heart"}

    def test_get_renderer_caching(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer1 = utils.get_renderer()
            renderer2 = utils.get_renderer()

            assert renderer1 is renderer2  # Same instance

    def test_get_renderer_no_easy_icons_setting(self):
        with override_settings(EASY_ICONS={}):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "Renderer 'default' is not configured" in str(exc_info.value)

    def test_get_renderer_invalid_setting_type(self):
        with override_settings(EASY_ICONS="not a dict"):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "EASY_ICONS setting must be a dictionary" in str(exc_info.value)

    def test_get_renderer_missing_renderer_config(self):
        config = {
            "other": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {},
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer("missing")

            assert "Renderer 'missing' is not configured" in str(exc_info.value)

    def test_get_renderer_invalid_renderer_config_type(self):
        config = {"default": "not a dict"}

        with override_settings(EASY_ICONS=config):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "EASY_ICONS['default'] must be a dictionary" in str(exc_info.value)

    def test_get_renderer_missing_renderer_class(self):
        config = {"default": {"config": {}, "icons": {}}}

        with override_settings(EASY_ICONS=config):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "must specify a 'renderer' class path" in str(exc_info.value)

    def test_get_renderer_invalid_renderer_class(self):
        config = {
            "default": {
                "renderer": "nonexistent.module.RendererClass",
                "config": {},
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "Cannot import renderer class" in str(exc_info.value)

    def test_get_renderer_renderer_instantiation_error(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {},  # Missing required sprite_url
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config):
            with pytest.raises(ImproperlyConfigured) as exc_info:
                utils.get_renderer()

            assert "Cannot instantiate renderer" in str(exc_info.value)

    def test_get_renderer_config_none(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": None,
                "icons": None,
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer()

            assert isinstance(renderer, SvgRenderer)
            assert renderer.icons == {}

    def test_get_renderer_missing_config_and_icons(self):
        config = {"default": {"renderer": "easy_icons.renderers.SvgRenderer"}}

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer()

            assert isinstance(renderer, SvgRenderer)
            assert renderer.icons == {}
            assert renderer.default_attrs == {}

    def test_get_renderer_complex_config(self):
        config = {
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {
                    "sprite_url": "/static/icons.svg",
                    "default_attrs": {"class": "sprite", "width": "24"},
                },
                "icons": {"logo": "brand-logo", "menu": "hamburger"},
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer("sprites")

            assert isinstance(renderer, SpritesRenderer)
            assert renderer.sprite_url == "/static/icons.svg"
            assert renderer.default_attrs == {"class": "sprite", "width": "24"}
            assert renderer.icons == {"logo": "brand-logo", "menu": "hamburger"}


class TestClearCache:
    def test_clear_cache(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {},
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer1 = utils.get_renderer()

            utils.clear_cache()

            renderer2 = utils.get_renderer()

            assert renderer1 is not renderer2

    def test_clear_cache_empty(self):
        utils.clear_cache()
        utils.clear_cache()


class TestIcon:
    def test_icon_default_renderer(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            }
        }

        with override_settings(EASY_ICONS=config):
            with patch("easy_icons.renderers.render_to_string") as mock_render:
                mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'

                result = utils.icon("home")

                assert isinstance(result, SafeString)
                mock_render.assert_called_once_with("icons/home.svg")

    def test_icon_named_renderer(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {},
                "icons": {"home": "home.svg"},
            },
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"heart": "fa-heart"},
            },
        }

        with override_settings(EASY_ICONS=config):
            result = utils.icon("heart", renderer="fontawesome")

            assert isinstance(result, SafeString)
            assert '<i class="fa-heart"' in result

    def test_icon_with_attributes(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"star": "fa-star"},
            }
        }

        with override_settings(EASY_ICONS=config):
            result = utils.icon("star", **{"class": "large", "data-role": "button"})

            assert "fa-star" in result and "large" in result
            assert 'data-role="button"' in result

    def test_icon_use_defaults_false(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i", "default_attrs": {"class": "icon"}},
                "icons": {"check": "fa-check"},
            }
        }

        with override_settings(EASY_ICONS=config):
            test_attrs = {"class": "custom"}
            result = utils.icon("check", use_defaults=False, **test_attrs)

            assert "fa-check" in result and "custom" in result
            assert 'class="icon' not in result

    def test_icon_renderer_not_found(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {},
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config), pytest.raises(ImproperlyConfigured):
            utils.icon("test", renderer="nonexistent")

    def test_icon_caching_across_calls(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fa-home", "user": "fa-user"},
            }
        }

        with override_settings(EASY_ICONS=config):
            result1 = utils.icon("home")
            result2 = utils.icon("user")

            assert "fa-home" in result1
            assert "fa-user" in result2

    def test_icon_multiple_renderers(self):
        config = {
            "svg": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            },
            "fa": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"heart": "fa-heart"},
            },
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {"sprite_url": "/icons.svg"},
                "icons": {"logo": "brand"},
            },
        }

        with override_settings(EASY_ICONS=config):
            with patch("easy_icons.renderers.render_to_string") as mock_render:
                mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'

                svg_result = utils.icon("home", renderer="svg")
                fa_result = utils.icon("heart", renderer="fa")
                sprite_result = utils.icon("logo", renderer="sprites")

                assert "<svg" in svg_result
                assert '<i class="fa-heart"' in fa_result
                assert '<use href="/icons.svg#brand"' in sprite_result


class TestExpandAliases:
    def test_key_without_comma_unchanged(self):
        assert utils._expand_aliases({"home": "home.svg"}) == {"home": "home.svg"}

    def test_empty_mapping(self):
        assert utils._expand_aliases({}) == {}

    def test_comma_key_expands_to_each_alias(self):
        result = utils._expand_aliases({"plus,create,add,new": "bi bi-plus"})
        assert result == {
            "plus": "bi bi-plus",
            "create": "bi bi-plus",
            "add": "bi bi-plus",
            "new": "bi bi-plus",
        }

    def test_whitespace_around_aliases_is_stripped(self):
        result = utils._expand_aliases({" plus , create ,add ": "bi bi-plus"})
        assert result == {
            "plus": "bi bi-plus",
            "create": "bi bi-plus",
            "add": "bi bi-plus",
        }

    def test_empty_aliases_are_dropped(self):
        result = utils._expand_aliases({"plus,,create,": "bi bi-plus"})
        assert result == {"plus": "bi bi-plus", "create": "bi bi-plus"}

    def test_mixed_plain_and_alias_keys(self):
        result = utils._expand_aliases({"home": "home.svg", "plus,add": "plus.svg"})
        assert result == {
            "home": "home.svg",
            "plus": "plus.svg",
            "add": "plus.svg",
        }


class TestResolveIconsWithAliases:
    def test_explicit_icons_aliases_expanded(self):
        config = {"icons": {"plus,create,add": "bi bi-plus"}}
        resolved = utils.resolve_icons(config, "default")
        assert resolved["plus"] == "bi bi-plus"
        assert resolved["create"] == "bi bi-plus"
        assert resolved["add"] == "bi bi-plus"

    def test_pack_aliases_expanded(self):
        config = {"packs": ["tests.test_utils.PACK_WITH_ALIASES"]}
        resolved = utils.resolve_icons(config, "default")
        assert resolved["plus"] == "pack-plus"
        assert resolved["create"] == "pack-plus"
        assert resolved["add"] == "pack-plus"
        assert resolved["home"] == "pack-home"

    def test_explicit_alias_overrides_pack_per_name(self):
        config = {
            "packs": ["tests.test_utils.PACK_WITH_ALIASES"],
            "icons": {"add,remove": "explicit-value"},
        }
        resolved = utils.resolve_icons(config, "default")
        assert resolved["add"] == "explicit-value"  # explicit wins
        assert resolved["remove"] == "explicit-value"
        assert resolved["plus"] == "pack-plus"  # untouched pack aliases remain
        assert resolved["create"] == "pack-plus"


class TestAliasesEndToEnd:
    def _config(self):
        return {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"plus,create,add,new": "bi bi-plus"},
            }
        }

    def test_get_renderer_resolves_every_alias(self):
        with override_settings(EASY_ICONS=self._config()):
            renderer = utils.get_renderer("default")
            for alias in ("plus", "create", "add", "new"):
                assert renderer.get_icon(alias) == "bi bi-plus"

    def test_registry_registers_every_alias(self):
        with override_settings(EASY_ICONS=self._config()):
            utils.build_icon_registry()
            for alias in ("plus", "create", "add", "new"):
                assert utils._icon_registry.get(alias) == "default"

    def test_icon_renders_via_any_alias(self):
        with override_settings(EASY_ICONS=self._config()):
            utils.build_icon_registry()
            html_plus = utils.icon("plus")
            html_add = utils.icon("add")
            assert "bi bi-plus" in html_plus
            assert "bi bi-plus" in html_add


class TestPackLoading:
    def test_load_single_pack(self):
        result = utils.load_and_merge_packs(
            ["tests.test_utils.PACK_ONE"], "test_renderer"
        )
        assert result == PACK_ONE

    def test_load_multiple_packs_last_wins(self):
        result = utils.load_and_merge_packs(
            [
                "tests.test_utils.PACK_ONE",
                "tests.test_utils.PACK_TWO",
            ],
            "test_renderer",
        )

        assert result["user"] == "user-v2.svg"
        assert result["home"] == "home-v1.svg"
        assert result["star"] == "star-v1.svg"
        assert result["heart"] == "heart-v2.svg"

    def test_load_three_packs_sequential_override(self):
        result = utils.load_and_merge_packs(
            [
                "tests.test_utils.PACK_ONE",
                "tests.test_utils.PACK_TWO",
                "tests.test_utils.PACK_THREE",
            ],
            "test_renderer",
        )

        assert result["star"] == "star-v3.svg"
        assert result["user"] == "user-v2.svg"
        assert result["home"] == "home-v1.svg"
        assert result["heart"] == "heart-v2.svg"
        assert result["admin"] == "admin-v3.svg"

    def test_load_invalid_import_path(self, caplog):
        result = utils.load_and_merge_packs(
            [
                "tests.test_utils.PACK_ONE",
                "tests.test_utils.NONEXISTENT_PACK",
            ],
            "test_renderer",
        )

        assert result == PACK_ONE
        assert any(record.levelname == "WARNING" for record in caplog.records)
        assert "NONEXISTENT_PACK" in caplog.text

    def test_load_non_dict_pack(self, caplog):
        result = utils.load_and_merge_packs(
            [
                "tests.test_utils.PACK_ONE",
                "tests.test_utils.INVALID_PACK",
            ],
            "test_renderer",
        )

        assert result == PACK_ONE
        assert any(record.levelname == "WARNING" for record in caplog.records)
        assert "INVALID_PACK" in caplog.text

    def test_load_empty_packs_list(self):
        result = utils.load_and_merge_packs([], "test_renderer")
        assert result == {}


class TestPacksInRendererConfig:
    def setup_method(self):
        utils.clear_cache()

    def test_renderer_with_single_pack(self):
        config = {
            "test": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "packs": ["tests.test_utils.PACK_ONE"],
                "icons": {},
            }
        }

        with override_settings(EASY_ICONS=config):
            renderer = utils.get_renderer("test")
            assert renderer.icons == PACK_ONE

    def test_renderer_with_multiple_packs(self):
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.PACK_ONE",
                        "tests.test_utils.PACK_TWO",
                    ],
                    "icons": {},
                }
            }
        ):
            renderer = utils.get_renderer("test")

            assert renderer.icons["user"] == "user-v2.svg"
            assert renderer.icons["home"] == "home-v1.svg"
            assert renderer.icons["heart"] == "heart-v2.svg"

    def test_explicit_icons_override_packs(self):
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.PACK_ONE",
                        "tests.test_utils.PACK_TWO",
                    ],
                    "icons": {
                        "user": "user-explicit.svg",
                        "custom": "custom.svg",
                    },
                }
            }
        ):
            renderer = utils.get_renderer("test")

            assert renderer.icons["user"] == "user-explicit.svg"
            assert renderer.icons["home"] == "home-v1.svg"
            assert renderer.icons["heart"] == "heart-v2.svg"
            assert renderer.icons["custom"] == "custom.svg"

    def test_renderer_without_packs_key(self):
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "icons": {
                        "only": "explicit.svg",
                    },
                }
            }
        ):
            renderer = utils.get_renderer("test")

            assert renderer.icons == {"only": "explicit.svg"}

    def test_renderer_with_empty_packs_list(self):
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [],
                    "icons": {"only": "explicit.svg"},
                }
            }
        ):
            renderer = utils.get_renderer("test")

            assert renderer.icons == {"only": "explicit.svg"}


class TestIconRegistryWithPacks:
    def setup_method(self):
        utils.clear_cache()

    def test_registry_builds_with_packs(self):
        with override_settings(
            EASY_ICONS={
                "svg": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": ["tests.test_utils.PACK_ONE"],
                    "icons": {},
                }
            }
        ):
            utils.build_icon_registry()

            assert utils._icon_registry["home"] == "svg"
            assert utils._icon_registry["user"] == "svg"
            assert utils._icon_registry["star"] == "svg"

    def test_registry_with_multiple_renderers_and_packs(self):
        with override_settings(
            EASY_ICONS={
                "svg": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": ["tests.test_utils.PACK_ONE"],
                    "icons": {"custom": "custom.svg"},
                },
                "fontawesome": {
                    "renderer": "easy_icons.renderers.ProviderRenderer",
                    "packs": ["tests.test_utils.FONTAWESOME_PACK"],
                    "icons": {},
                },
            }
        ):
            utils.build_icon_registry()

            assert utils._icon_registry["home"] == "svg"
            assert utils._icon_registry["custom"] == "svg"

            assert utils._icon_registry["heart"] == "fontawesome"

    def test_registry_respects_explicit_icon_precedence(self):
        with override_settings(
            EASY_ICONS={
                "svg": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.PACK_ONE",
                        "tests.test_utils.PACK_TWO",
                    ],
                    "icons": {"user": "user-explicit.svg"},
                }
            }
        ):
            utils.build_icon_registry()

            assert "user" in utils._icon_registry
            assert "home" in utils._icon_registry

            renderer = utils.get_renderer("svg")
            assert renderer.icons["user"] == "user-explicit.svg"
            assert renderer.icons["home"] == "home-v1.svg"

    def test_default_renderer_wins_collisions(self, caplog):
        with override_settings(
            EASY_ICONS={
                "default": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": ["tests.test_utils.PACK_ONE"],
                    "icons": {},
                },
                "other": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": ["tests.test_utils.PACK_TWO"],
                    "icons": {},
                },
            }
        ):
            utils.build_icon_registry()

            assert utils._icon_registry["user"] == "default"

            assert any(record.levelname == "WARNING" for record in caplog.records)
            assert "user" in caplog.text


class TestIconRenderingWithPacks:
    def setup_method(self):
        utils.clear_cache()

    def test_render_icon_from_pack(self):
        with override_settings(
            EASY_ICONS={
                "default": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "config": {"svg_dir": "icons"},
                    "packs": ["tests.test_utils.PACK_ONE"],
                    "icons": {},
                }
            },
            EASY_ICONS_FAIL_SILENTLY=False,
        ):
            utils.build_icon_registry()

            # Icon exists in pack, but won't render without actual file
            renderer = utils.get_renderer("default")
            assert "home" in renderer.icons
            assert renderer.icons["home"] == "home-v1.svg"

    def test_explicit_icon_renders_over_pack(self):
        with override_settings(
            EASY_ICONS={
                "fontawesome": {
                    "renderer": "easy_icons.renderers.ProviderRenderer",
                    "config": {"tag": "i"},
                    "packs": ["tests.test_utils.FONTAWESOME_PACK"],
                    "icons": {"custom": "fa-custom"},
                }
            }
        ):
            renderer = utils.get_renderer("fontawesome")

            result = renderer.render("heart")
            assert 'class="fa-heart"' in result

            result = renderer.render("custom")
            assert 'class="fa-custom"' in result


class TestPacksEdgeCases:
    def setup_method(self):
        utils.clear_cache()

    def test_all_packs_invalid_uses_explicit_icons(self, caplog):
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.INVALID_PACK",
                    ],
                    "icons": {"fallback": "fallback.svg"},
                }
            }
        ):
            renderer = utils.get_renderer("test")

            assert renderer.icons == {"fallback": "fallback.svg"}
            assert any(record.levelname == "WARNING" for record in caplog.records)

    def test_duplicate_pack_paths(self):
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.PACK_ONE",
                        "tests.test_utils.PACK_ONE",  # Duplicate
                    ],
                    "icons": {},
                }
            }
        ):
            renderer = utils.get_renderer("test")

            assert renderer.icons == PACK_ONE

    def test_explicit_icons_override_all_packs(self):
        with override_settings(
            EASY_ICONS={
                "test": {
                    "renderer": "easy_icons.renderers.SvgRenderer",
                    "packs": [
                        "tests.test_utils.PACK_ONE",
                        "tests.test_utils.PACK_TWO",
                        "tests.test_utils.PACK_THREE",
                    ],
                    "icons": {
                        "home": "home-final.svg",
                        "user": "user-final.svg",
                        "star": "star-final.svg",
                    },
                }
            }
        ):
            renderer = utils.get_renderer("test")

            assert renderer.icons["home"] == "home-final.svg"
            assert renderer.icons["user"] == "user-final.svg"
            assert renderer.icons["star"] == "star-final.svg"

            assert renderer.icons["heart"] == "heart-v2.svg"
            assert renderer.icons["admin"] == "admin-v3.svg"


class TestIconRegistry:
    def setup_method(self):
        utils.clear_cache()
        utils._icon_registry.clear()

    def test_build_icon_registry_default_first(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {
                    "home": "home.svg",
                    "star": "star-default.svg",
                },
            },
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {
                    "heart": "fas fa-heart",
                    "star": "fas fa-star",  # Collision with default
                },
            },
        }

        with override_settings(EASY_ICONS=config):
            utils.build_icon_registry()

            assert utils._icon_registry.get("home") == "default"
            assert utils._icon_registry.get("star") == "default"  # Default wins

            assert utils._icon_registry.get("heart") == "fontawesome"

    def test_build_icon_registry_order_matters(self):
        config = {
            "renderer_a": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"duplicate": "a-value"},
            },
            "renderer_b": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "span"},
                "icons": {"duplicate": "b-value"},
            },
        }

        with override_settings(EASY_ICONS=config):
            utils.build_icon_registry()

            # First renderer should win (no 'default', so insertion order)
            assert utils._icon_registry.get("duplicate") == "renderer_a"

    def test_build_icon_registry_skips_uppercase_keys(self):
        config = {
            "SOME_CONFIG": True,
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            },
        }

        with override_settings(EASY_ICONS=config):
            utils.build_icon_registry()

            assert utils._icon_registry.get("home") == "default"
            assert "SOME_CONFIG" not in utils._icon_registry

    def test_build_icon_registry_handles_invalid_config(self):
        config = {
            "invalid": "not a dict",
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            },
        }

        with override_settings(EASY_ICONS=config):
            utils.build_icon_registry()

            assert utils._icon_registry.get("home") == "default"

    def test_build_icon_registry_collision_logging(self, caplog):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"star": "star.svg"},
            },
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"star": "fas fa-star"},
            },
        }

        with override_settings(EASY_ICONS=config):
            utils.build_icon_registry()

            assert any(record.levelname == "WARNING" for record in caplog.records)
            assert any("'star'" in record.message for record in caplog.records)


class TestIconAutoDetection:
    def setup_method(self):
        utils.clear_cache()
        utils._icon_registry.clear()

    def test_icon_auto_detection_from_default(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()
            result = utils.icon("home")

            assert "fas fa-home" in result
            assert "<i" in result

    def test_icon_auto_detection_from_non_default(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {"sprite_url": "/sprites.svg"},
                "icons": {"logo": "brand-logo"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()
            result = utils.icon("logo")  # Only in sprites

            assert "brand-logo" in result
            assert "<svg" in result

    def test_icon_explicit_renderer_overrides_auto_detection(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"star": "fas fa-star"},
            },
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {"sprite_url": "/sprites.svg"},
                "icons": {"star": "star-sprite"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()

            auto_result = utils.icon("star")
            assert "fas fa-star" in auto_result

            explicit_result = utils.icon("star", renderer="sprites")
            assert "star-sprite" in explicit_result


class TestIconFailSilently:
    def setup_method(self):
        utils.clear_cache()
        utils._icon_registry.clear()

    def test_fail_silently_true_returns_empty_string(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
        }

        with override_settings(EASY_ICONS=config, EASY_ICONS_FAIL_SILENTLY=True):
            utils.build_icon_registry()
            result = utils.icon("missing-icon")

            assert result == ""

    def test_fail_silently_false_raises_error(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()

            with pytest.raises(IconNotFoundError) as exc_info:
                utils.icon("missing-icon")

            assert "missing-icon" in str(exc_info.value)

    def test_fail_silently_defaults_to_debug(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
        }

        with override_settings(EASY_ICONS=config, DEBUG=True):
            utils.build_icon_registry()
            result = utils.icon("missing-icon")
            assert result == ""

        with override_settings(EASY_ICONS=config, DEBUG=False):
            utils.build_icon_registry()
            with pytest.raises(IconNotFoundError):
                utils.icon("missing-icon")

    def test_fail_silently_with_explicit_renderer_not_found(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
        }

        with override_settings(EASY_ICONS=config, EASY_ICONS_FAIL_SILENTLY=True):
            utils.build_icon_registry()
            result = utils.icon("missing-icon", renderer="default")

            assert result == ""

    def test_helpful_error_message_lists_available_icons(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {
                    "home": "fas fa-home",
                    "heart": "fas fa-heart",
                    "star": "fas fa-star",
                },
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()

            with pytest.raises(IconNotFoundError) as exc_info:
                utils.icon("missing")

            error_message = str(exc_info.value)
            assert any(icon in error_message for icon in ["home", "heart", "star"])


class TestIconRegistryWithNoDefault:
    def setup_method(self):
        utils.clear_cache()
        utils._icon_registry.clear()

    def test_registry_works_without_default_renderer(self):
        config = {
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fas fa-home"},
            },
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {"sprite_url": "/sprites.svg"},
                "icons": {"logo": "brand-logo"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()

            home_result = utils.icon("home")
            assert "fas fa-home" in home_result

            logo_result = utils.icon("logo")
            assert "brand-logo" in logo_result

    def test_first_renderer_wins_without_default(self):
        config = {
            "renderer_a": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"icon": "a-value"},
            },
            "renderer_b": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "span"},
                "icons": {"icon": "b-value"},
            },
        }

        with override_settings(
            EASY_ICONS=config, DEBUG=False, EASY_ICONS_FAIL_SILENTLY=False
        ):
            utils.build_icon_registry()

            result = utils.icon("icon")
            assert "a-value" in result


class TestMultiRendererIntegration:
    def setup_method(self):
        clear_cache()

    def test_multiple_renderers_in_same_template(self):
        config = {
            "svg": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {"svg_dir": "icons"},
                "icons": {"home": "home.svg"},
            },
            "fontawesome": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i", "default_attrs": {"class": "fas"}},
                "icons": {"heart": "fa-heart", "star": "fa-star"},
            },
            "sprites": {
                "renderer": "easy_icons.renderers.SpritesRenderer",
                "config": {"sprite_url": "/static/icons.svg"},
                "icons": {"logo": "brand-logo", "menu": "hamburger"},
            },
        }

        template_content = """
        {% load easy_icons %}
        <nav>
            {% icon 'home' renderer='svg' class='nav-icon' %}
            {% icon 'heart' renderer='fontawesome' class='like-btn' %}
            {% icon 'logo' renderer='sprites' class='brand' %}
        </nav>
        """

        with override_settings(EASY_ICONS=config):
            with patch("easy_icons.renderers.render_to_string") as mock_render:
                mock_render.return_value = '<svg><path d="M0 0L10 10"/></svg>'

                template = Template(template_content)
                result = template.render(Context())

                assert "<svg" in result  # SVG renderer
                assert "fa-heart" in result and "like-btn" in result  # FA renderer
                assert '<use href="/static/icons.svg#brand-logo"' in result  # Sprites

    def test_icon_function_with_different_renderers(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"home": "fa-home"},
            },
            "custom": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "span", "default_attrs": {"class": "icon"}},
                "icons": {"settings": "gear-icon"},
            },
        }

        with override_settings(EASY_ICONS=config):
            result1 = easy_icon("home")
            assert '<i class="fa-home"' in result1

            result2 = easy_icon("settings", renderer="custom")
            assert "gear-icon" in result2 and 'class="icon"' in result2

    def test_renderer_caching_with_multiple_calls(self):
        config = {
            "provider1": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"icon1": "fa-icon1", "icon2": "fa-icon2"},
            },
            "provider2": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "span"},
                "icons": {"icon3": "span-icon3"},
            },
        }

        with override_settings(EASY_ICONS=config):
            result1 = easy_icon("icon1", renderer="provider1")
            result2 = easy_icon("icon2", renderer="provider1")
            result3 = easy_icon("icon3", renderer="provider2")

            assert '<i class="fa-icon1"' in result1
            assert '<i class="fa-icon2"' in result2
            assert '<span class="span-icon3"' in result3

    def test_complex_configuration_integration(self):
        config = {
            "main": {
                "renderer": "easy_icons.renderers.SvgRenderer",
                "config": {
                    "svg_dir": "assets/icons",
                    "default_attrs": {
                        "class": "svg-icon",
                        "height": "1em",
                        "fill": "currentColor",
                    },
                },
                "icons": {
                    "home": "house.svg",
                    "user": "person.svg",
                    "search": "magnifying-glass.svg",
                },
            },
            "social": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i", "default_attrs": {"class": "fab"}},
                "icons": {
                    "facebook": "fa-facebook",
                    "twitter": "fa-twitter",
                    "linkedin": "fa-linkedin",
                },
            },
        }

        with override_settings(EASY_ICONS=config):
            with patch("easy_icons.renderers.render_to_string") as mock_render:
                mock_render.return_value = (
                    '<svg viewBox="0 0 24 24"><path d="M0 0L10 10"/></svg>'
                )

                home_result = easy_icon("home", renderer="main")
                assert 'class="svg-icon"' in home_result
                assert 'height="1em"' in home_result
                assert 'fill="currentColor"' in home_result

                search_result = easy_icon(
                    "search", renderer="main", width="2em", **{"class": "search-icon"}
                )
                assert (
                    "search-icon" in search_result
                )  # Should override, not merge with svg-icon
                assert "svg-icon" not in search_result  # Should be overridden
                assert 'width="2em"' in search_result

                fb_result = easy_icon("facebook", renderer="social")
                assert "fa-facebook" in fb_result and "fab" in fb_result

    def test_error_handling_integration(self):
        config = {
            "test": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {"valid": "fa-valid"},
            }
        }

        with override_settings(EASY_ICONS=config):
            result = easy_icon("valid", renderer="test")
            assert "fa-valid" in result

            from easy_icons.exceptions import IconNotFoundError

            with pytest.raises(IconNotFoundError):
                easy_icon("invalid", renderer="test")

            from django.core.exceptions import ImproperlyConfigured

            with pytest.raises(ImproperlyConfigured):
                easy_icon("valid", renderer="nonexistent")

    def test_template_integration_with_context(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {"tag": "i"},
                "icons": {
                    "home": "fa-home",
                    "user": "fa-user",
                    "admin": "fa-user-shield",
                    "settings": "fa-cog",
                },
            }
        }

        template_content = """
        {% load easy_icons %}
        <div class="menu">
            {% for item in menu_items %}
                <a href="{{ item.url }}" class="{{ item.css_class }}">
                    {% icon item.icon class=item.icon_class %}
                    {{ item.label }}
                </a>
            {% endfor %}
        </div>
        """

        context_data = {
            "menu_items": [
                {
                    "url": "/",
                    "label": "Home",
                    "icon": "home",
                    "css_class": "nav-link",
                    "icon_class": "nav-icon",
                },
                {
                    "url": "/profile",
                    "label": "Profile",
                    "icon": "user",
                    "css_class": "nav-link active",
                    "icon_class": "nav-icon primary",
                },
                {
                    "url": "/admin",
                    "label": "Admin",
                    "icon": "admin",
                    "css_class": "nav-link admin",
                    "icon_class": "nav-icon admin-icon",
                },
            ]
        }

        with override_settings(EASY_ICONS=config):
            template = Template(template_content)
            result = template.render(Context(context_data))

            assert "fa-home nav-icon" in result
            assert "fa-user nav-icon primary" in result
            assert "fa-user-shield nav-icon admin-icon" in result

            assert "nav-link" in result
            assert "nav-link active" in result
            assert "nav-link admin" in result

    def test_attribute_merging_edge_cases(self):
        config = {
            "default": {
                "renderer": "easy_icons.renderers.ProviderRenderer",
                "config": {
                    "tag": "i",
                    "default_attrs": {
                        "class": "icon base",
                        "role": "img",
                        "aria-hidden": "true",
                    },
                },
                "icons": {"test": "fa-test"},
            }
        }

        with override_settings(EASY_ICONS=config):
            result1 = easy_icon("test", **{"class": "additional custom"})
            assert (
                "fa-test" in result1 and "additional" in result1 and "custom" in result1
            )
            # ProviderRenderer has both classes due to its design (icon class + separate class attribute)
            assert "icon" in result1 and "base" in result1

            result2 = easy_icon("test", role="button", **{"data-action": "click"})
            assert 'role="button"' in result2  # Should override default role="img"
            assert 'role="img"' not in result2  # Should be overridden
            assert 'aria-hidden="true"' in result2
            assert 'data-action="click"' in result2

            result3 = easy_icon("test", use_defaults=False, **{"class": "only-this"})
            assert "only-this" in result3 and "fa-test" in result3
            assert 'role="img"' not in result3
            assert 'aria-hidden="true"' not in result3
