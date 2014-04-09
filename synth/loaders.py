##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

import synth

import django.core.urlresolvers
from django.conf import settings
from django.template.loaders import app_directories, filesystem
from django.template.base import get_library

default_engine = getattr(settings, 'SYNTH_DEFAULT_ENGINE', 'django')
default_value  = getattr(settings, 'SYNTH_DEFAULT_VALUE',  settings.TEMPLATE_STRING_IF_INVALID)
autoescape     = getattr(settings, 'SYNTH_AUTOESCAPE',     True)
debug          = getattr(settings, 'SYNTH_DEBUG',          settings.TEMPLATE_DEBUG)
formats        = getattr(settings, 'SYNTH_FORMATS', {
    'DATE_FORMAT':           settings.DATE_FORMAT,
    'DATETIME_FORMAT':       settings.DATETIME_FORMAT,
    'MONTH_DAY_FORMAT':      settings.MONTH_DAY_FORMAT,
    'SHORT_DATE_FORMAT':     settings.SHORT_DATE_FORMAT,
    'SHORT_DATETIME_FORMAT': settings.SHORT_DATETIME_FORMAT,
    'TIME_FORMAT':           settings.TIME_FORMAT,
    'YEAR_MONTH_FORMAT':     settings.YEAR_MONTH_FORMAT,
})

print('Loaded synth; version: %s; default engine: %s.' %
    (synth.version(), default_engine))

class SynthTemplate(object):
    def __init__(self, source, engine_name=default_engine, directories=None):
        self.template = synth.StringTemplate(source.encode('utf-8'),
            engine_name, auto_escape, default_value, formats, debug,
            directories, {}, [get_library], [urlresolvers])

    def render(self, context):
        # Flatten the django context into a single dictionary.
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)

        return self.template.render_to_string(context_dict)

class AppDirectoriesLoader(app_directories.Loader):
    is_usable = True

    def load_template(self, template_name, template_dirs=None):
        source, origin = self.load_template_source(template_name, template_dirs)
        template = SynthTemplate(source, default_engine, template_dirs)
        return template, origin

class FilesystemLoader(filesystem.Loader):
    is_usable = True

    def load_template(self, template_name, template_dirs=None):
        source, origin = self.load_template_source(template_name, template_dirs)
        template = SynthTemplate(source, default_engine, template_dirs)
        return template, origin
