"""The ``show_icon_registry`` command: list registered icons and name collisions."""

import json
from collections import defaultdict
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Display the global icon registry and detect collisions."""

    help = "Show all registered icons and their renderer mappings"

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--format",
            type=str,
            default="table",
            choices=["table", "json"],
            help="Output format (default: table)",
        )
        parser.add_argument(
            "--show-collisions-only",
            action="store_true",
            help="Only show icons with collisions",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        output_format = options["format"]
        show_collisions_only = options["show_collisions_only"]

        config = getattr(settings, "EASY_ICONS", {})
        fail_silently = getattr(settings, "EASY_ICONS_FAIL_SILENTLY", settings.DEBUG)

        icon_to_renderers = defaultdict(list)
        for renderer_name, renderer_config in config.items():
            if renderer_name.isupper() or not isinstance(renderer_config, dict):
                continue

            icons = renderer_config.get("icons", {})
            if not isinstance(icons, dict):
                continue

            for icon_name, icon_value in icons.items():
                icon_to_renderers[icon_name].append(
                    {"renderer": renderer_name, "value": icon_value}
                )

        collisions = {
            icon: renderers
            for icon, renderers in icon_to_renderers.items()
            if len(renderers) > 1
        }

        if output_format == "json":
            self._output_json(
                icon_to_renderers, collisions, fail_silently, show_collisions_only
            )
        else:
            self._output_table(
                icon_to_renderers, collisions, fail_silently, show_collisions_only
            )

    def _output_table(
        self,
        icon_to_renderers: dict[str, list[dict[str, str]]],
        collisions: dict[str, list[dict[str, str]]],
        fail_silently: bool,
        show_collisions_only: bool,
    ) -> None:
        """Write the registry, or only its collisions, as a text table.

        Args:
            icon_to_renderers: Each icon name mapped to every renderer entry that
                defines it, in lookup order.
            collisions: The subset of ``icon_to_renderers`` defined more than once.
            fail_silently: The effective ``EASY_ICONS_FAIL_SILENTLY`` value.
            show_collisions_only: Write only the colliding icons.
        """
        self.stdout.write(self.style.SUCCESS("\n=== Easy Icons Configuration ==="))
        self.stdout.write(f"EASY_ICONS_FAIL_SILENTLY: {fail_silently}")
        self.stdout.write(f"Total unique icons: {len(icon_to_renderers)}")
        self.stdout.write(f"Icons with collisions: {len(collisions)}\n")

        if show_collisions_only:
            if not collisions:
                self.stdout.write(
                    self.style.SUCCESS("No icon name collisions detected!")
                )
                return

            self.stdout.write(self.style.WARNING("=== Icon Name Collisions ===\n"))
            for icon_name in sorted(collisions.keys()):
                renderers = collisions[icon_name]
                self.stdout.write(self.style.WARNING(f"\n'{icon_name}':"))
                for i, renderer_info in enumerate(renderers):
                    marker = "✓ USED" if i == 0 else "✗ shadowed"
                    style = self.style.SUCCESS if i == 0 else self.style.ERROR
                    self.stdout.write(
                        f"  {style(marker)} {renderer_info['renderer']:15} → {renderer_info['value']}"
                    )
        else:
            self.stdout.write(self.style.SUCCESS("=== Icon Registry ==="))
            self.stdout.write(
                f"{'Icon Name':<25} | {'Renderer':<15} | {'Icon Value':<30} | {'Status'}"
            )
            self.stdout.write("-" * 90)

            for icon_name in sorted(icon_to_renderers.keys()):
                renderers = icon_to_renderers[icon_name]
                for i, renderer_info in enumerate(renderers):
                    if len(renderers) > 1:
                        status = "USED" if i == 0 else "SHADOWED"
                        style = self.style.SUCCESS if i == 0 else self.style.ERROR
                    else:
                        status = "OK"
                        style = self.style.SUCCESS

                    icon_value = renderer_info["value"]
                    if len(icon_value) > 30:
                        icon_value = icon_value[:27] + "..."

                    self.stdout.write(
                        f"{icon_name:<25} | {renderer_info['renderer']:<15} | {icon_value:<30} | {style(status)}"
                    )

            if collisions:
                self.stdout.write(
                    "\n" + self.style.WARNING("=== Collision Summary ===")
                )
                for icon_name, renderers in sorted(collisions.items()):
                    renderer_names = [r["renderer"] for r in renderers]
                    self.stdout.write(
                        self.style.WARNING(
                            f"  '{icon_name}': {', '.join(renderer_names)} (using '{renderer_names[0]}')"
                        )
                    )

    def _output_json(
        self,
        icon_to_renderers: dict[str, list[dict[str, str]]],
        collisions: dict[str, list[dict[str, str]]],
        fail_silently: bool,
        show_collisions_only: bool,
    ) -> None:
        """Write the registry, or only its collisions, as JSON.

        Args:
            icon_to_renderers: Each icon name mapped to every renderer entry that
                defines it, in lookup order.
            collisions: The subset of ``icon_to_renderers`` defined more than once.
            fail_silently: The effective ``EASY_ICONS_FAIL_SILENTLY`` value.
            show_collisions_only: Write only the colliding icons.
        """
        output: dict[str, Any]
        if show_collisions_only:
            output = {
                "collisions": {
                    icon: [
                        {
                            "renderer": r["renderer"],
                            "value": r["value"],
                            "used": i == 0,
                        }
                        for i, r in enumerate(renderers)
                    ]
                    for icon, renderers in collisions.items()
                }
            }
        else:
            output = {
                "settings": {
                    "fail_silently": fail_silently,
                },
                "registry": {
                    icon: [
                        {
                            "renderer": r["renderer"],
                            "value": r["value"],
                            "used": i == 0,
                        }
                        for i, r in enumerate(renderers)
                    ]
                    for icon, renderers in icon_to_renderers.items()
                },
                "collisions": list(collisions.keys()),
            }

        self.stdout.write(json.dumps(output, indent=2))
