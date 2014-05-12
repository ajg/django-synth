##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

import synth

from inspect import getargspec
from django.conf import settings
from django.core import urlresolvers
from django.template import TemplateSyntaxError
from django.template.base import get_library

settings.configure() # TODO: if not settings.configured

# TODO: Make private.
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

print('Loaded synth; version: %s; default engine: %s.' % (synth.version(), default_engine))

def load_library(name):
    print 'load_library', name
    return LibraryWrapper(get_library(name))

CUSTOM_ARGUMENT_NAMES=('parser', 'token')

def load_tag(name, tag):
    print 'tag', name, tag, tag.func_code.co_varnames

    try:
        arg_names = tag.func_code.co_varnames[:2] # Includes optional args
    except:
        try:
            arg_names = tuple(getargspec(tag)[0]) # Excludes optional args
        except:
            print 'Unable to get arguments names for tag:', name
            return tag

    if arg_names != CUSTOM_ARGUMENT_NAMES:
        return tag

    return lambda *matches: tag(ParserWrapper(), TokenWrapper(matches))

class ParserWrapper(object):
    def __init__(self):
        pass

    def parse(self, tag_names):
        nodelist = []
        return nodelist

    def skip_past(self, tag_name):
        raise NotImplementedError('skip_past')

    def delete_first_token(self):
        pass

class TokenWrapper(object):
    def __init__(self, matches):
        self.contents = matches[0]
        self.tokens = matches[1:]

        print '  contents', self.contents
        print '  tokens', self.tokens

    def split_contents(self):
        return self.tokens

class LibraryWrapper(object):
    def __init__(self, library):
        self.tags = {k: load_tag(k, v) for k, v in getattr(library, 'tags', {}).items()}
        self.filters = getattr(library, 'filters', {})

class BasicTemplate(object):
    def __init__(self, source, engine_name=default_engine, directories=[]):
        try:
            self.template = synth.Template(
                source,
                engine_name,
                autoescape,
                default_value,
                formats,
                debug or True, # FIXME: Temporary hack for django-synth.
                directories,
                {},
                [load_library],
                [urlresolvers],
            )
        except RuntimeError as e:
            message = str(e)
            if 'parsing error' in message:
                raise TemplateSyntaxError(message)
            else:
                raise

    def render(self, context):
        # Flatten the django context into a single dictionary.
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)

        return self.template.render_to_string(context_dict)
