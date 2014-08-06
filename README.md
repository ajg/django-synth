django-synth
============

A bridge between [Django] and [Synth] that enables fast, efficient parsing and rendering of templates natively, with the goal of requiring no changes.

[![Build Status]](https://travis-ci.org/ajg/django-synth)

[Django]:       https://djangoproject.com
[Synth]:        https://github.com/ajg/synth
[Build Status]: https://travis-ci.org/ajg/django-synth.png?branch=master

Installation
------------

    pip install django-synth

Usage
-----

 1. Add it to your `requirements.txt` or equivalent:

        django-synth>=0.7.0

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

 - More tests
 - Better documentation
 - Example project
