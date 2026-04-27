from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PYTHON_SOURCE = ROOT / "python"
DOCS_EXT = ROOT / "docs" / "_ext"

sys.path.insert(0, str(PYTHON_SOURCE))
sys.path.insert(0, str(DOCS_EXT))

# Mock the Rust extension for Read the Docs builds
# The _core module is a Rust extension that can't be built in RTD environment
import sys as _sys
from unittest.mock import MagicMock

class MockCoreModule(MagicMock):
    """Mock for the Rust _core extension."""
    CoreMessage = MagicMock
    deep_merge_json = lambda a, b: b  # type: ignore
    next_event_id = lambda: "mock_event_id"  # type: ignore
    normalize_onebot11_event = lambda raw, adapter, platform: raw  # type: ignore

_sys.modules["asterline._core"] = MockCoreModule()

project = "Asterline"
author = "Asterline contributors"
language = "zh_CN"
locale_dirs = ["locales"]
gettext_compact = False
gettext_uuid = True

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "asterline_mermaid",
    "asterline_blog",
    "asterline_store",
    "asterline_i18n_versions",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autosummary_generate = True
autosummary_imported_members = False
autodoc_member_order = "bysource"
autoclass_content = "both"
autodoc_typehints = "description"
autodoc_mock_imports = ["openai"]
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

html_theme = "furo"
html_title = "Asterline Documentation"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_logo = "_static/brand/asterline-logo.svg"
html_favicon = "_static/brand/favicon.ico"
asterline_store_registry_paths = ["ecosystem/entries"]
asterline_store_github_repo = "asterline/asterline"
asterline_blog_registry_paths = ["community/blog/posts"]
asterline_docs_current_version = "dev"
asterline_docs_current_language = "zh_CN"
asterline_docs_versions = [
    {"name": "dev", "label": "Development", "url": "#", "current": True},
    {"name": "latest", "label": "Latest", "url": "/latest/zh_CN/"},
    {"name": "0.1", "label": "0.1", "url": "/0.1/zh_CN/"},
]
asterline_docs_languages = [
    {"name": "zh_CN", "label": "中文", "url": "#", "current": True},
    {"name": "en", "label": "English", "url": "/dev/en/"},
]
html_theme_options = {
    "navigation_with_keys": True,
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#0f766e",
        "color-brand-content": "#0d9488",
    },
    "dark_css_variables": {
        "color-brand-primary": "#5eead4",
        "color-brand-content": "#2dd4bf",
    },
}
