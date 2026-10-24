import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from hitherdither.__version__ import __version__  # noqa: E402

project = "hitherdither"
author = "Henrik Blidh"
copyright = "2016-2026, Henrik Blidh"
release = version = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "pillow": ("https://pillow.readthedocs.io/en/stable", None),
}
autodoc_member_order = "bysource"
exclude_patterns = ["_build"]
html_theme = "sphinx_rtd_theme"
