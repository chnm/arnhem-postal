# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#path-setup
import os
import sys

# import django

sys.path.insert(0, os.path.abspath("."))
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
# django.setup()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Arnhem Postal History"
copyright = "2024, Roy Rosenzweig Center for History and New Media"
author = "The Roy Rosenzweig Center for History and New Media"
description = "Django web application for the Arnhem Postal History Project"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

html_theme_options = {
    "description": description,
    "github_user": "chnm",
    "github_repo": "arnhem-postal",
    "codecov_button": True,
}

# html_sidebars = {
#     "**": [
#         "about.html",
#         "navigation.html",
#         "localtoc.html",
#         "searchbox.html",
#         "sidebar_footer.html",
#     ],
# }

# Configure for intersphinx for Python standard library, Django,
# and local dependencies with sphinx docs.
intersphinx_mapping = {
    "https://docs.python.org/3/": None,
    "django": ("https://django.readthedocs.org/en/latest/", None),
    "viapy": ("https://viapy.readthedocs.io/en/latest/", None),
}


coverage_ignore_pyobjects = [
    # django auto-generated model methods
    "clean_fields",
    "get_deferred_fields",
    "get_(next|previous)_by_(created|last_modified|modified)",
    "refresh_from_db",
    "get_.*_display",  # django auto-generated method for choice fields
    "get_doc_relation_list",  # multiselectfield auto method
]

# coverage_statistics_to_report = coverage_statistics_to_stdout = False
