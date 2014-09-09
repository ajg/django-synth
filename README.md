django-synth
============

A bridge between [Django] and [Synth] that enables fast, efficient parsing and rendering of templates natively. The goal of `django-synth` is to have achieve compatibility with Django's original template system, including support for custom libraries, tags and filters.

[![PyPI Version]](https://pypi.python.org/pypi/django-synth)
[![Build Status]](https://travis-ci.org/ajg/django-synth)

[Django]:       https://djangoproject.com
[Synth]:        https://github.com/ajg/synth
[PyPI Version]: https://pypip.in/v/django-synth/badge.png
[Build Status]: https://travis-ci.org/ajg/django-synth.png?branch=master

Installation
------------

    pip install pip --upgrade          # Ensure pip has wheel support
    pip install django-synth --upgrade # Get the latest and greatest

Usage
-----

 1. Add it to your `requirements.txt` or equivalent:

        django-synth>=0.7.6

 2. Enable it in your `settings.py` or equivalent:

        TEMPLATE_LOADERS = (
            'django_synth.loaders.FilesystemLoader',
            'django_synth.loaders.AppDirectoriesLoader',
        )

Settings
--------

#### `settings.SYNTH_ENGINE`

  Which template syntax to use: `"django"`, `"ssi"` or `"tmpl"`.

  - Type:    `str`
  - Default: `"django"`

#### `settings.SYNTH_DIRECTORIES`

  Where to look for templates.

  - Type:    `list` of `str`
  - Default: `settings.TEMPLATE_DIRS`

#### `settings.SYNTH_DEBUG`

  Whether to enable debugging (slower but more informative.)

  - Type:    `bool`
  - Default: `settings.TEMPLATE_DEBUG`

#### `settings.SYNTH_CACHE`

  Whether to enable caching.

  - Type:    `bool`
  - Default: `False` when debugging, `True` otherwise

#### `settings.SYNTH_FORMATS`

  What formats strings to use.

  - Type:    `dict` of `str`
  - Defaults are taken (eponymously) from:
      * `settings.TEMPLATE_STRING_IF_INVALID`
      * `settings.DATE_FORMAT`
      * `settings.DATETIME_FORMAT`
      * `settings.MONTH_DAY_FORMAT`
      * `settings.SHORT_DATE_FORMAT`
      * `settings.SHORT_DATETIME_FORMAT`
      * `settings.TIME_FORMAT`
      * `settings.YEAR_MONTH_FORMAT`

Future Work
-----------

 - ReadTheDocs-compatible documentation
 - Docstrings for all public types and functions
 - Use paths for top-level templates (in the loaders) rather than
   string sources, to avoid copying and enable caching
 - Example project
