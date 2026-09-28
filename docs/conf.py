import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "docs"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

from fairdm_docs.conf import *

extensions.append("autodoc2")
autodoc2_packages = ["../easy_icons"]
autodoc2_render_plugin = "myst"
autodoc2_output_dir = "api"
autodoc2_docstring_parser_regexes = [(r".*", "google_docstrings")]

html_logo = None
html_favicon = None
html_short_title = "Easy Icons"
html_theme_options["path_to_docs"] = "docs"
html_theme_options["home_page_in_toc"] = False
