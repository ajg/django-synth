##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from __future__ import print_function

import datetime
import django.template.base as base
import django.utils.timezone as tz
import django.utils.translation as tr
import functools
import re
import synth
import sys

from inspect import getargspec, getsource
from django.conf import settings
from django.core import urlresolvers
from django.template import generic_tag_compiler, TemplateSyntaxError

if not settings.configured:
    settings.configure()

default_formats = {
    'TEMPLATE_STRING_IF_INVALID': settings.TEMPLATE_STRING_IF_INVALID,
    'DATE_FORMAT':                settings.DATE_FORMAT,
    'DATETIME_FORMAT':            settings.DATETIME_FORMAT,
    'MONTH_DAY_FORMAT':           settings.MONTH_DAY_FORMAT,
    'SHORT_DATE_FORMAT':          settings.SHORT_DATE_FORMAT,
    'SHORT_DATETIME_FORMAT':      settings.SHORT_DATETIME_FORMAT,
    'TIME_FORMAT':                settings.TIME_FORMAT,
    'YEAR_MONTH_FORMAT':          settings.YEAR_MONTH_FORMAT,
}

# TODO: Make variables private.
engine      = getattr(settings, 'SYNTH_ENGINE',      'django')
directories = getattr(settings, 'SYNTH_DIRECTORIES', list(settings.TEMPLATE_DIRS or []))
debug       = getattr(settings, 'SYNTH_DEBUG',       bool(settings.TEMPLATE_DEBUG))
cache       = getattr(settings, 'SYNTH_CACHE',       not debug)
formats     = getattr(settings, 'SYNTH_FORMATS',     default_formats)

print('Loaded synth; version: %s; default engine: %s; debug: %s.' %
    (synth.version(), engine, debug), file=sys.stderr)

def load_library(name):
    return SynthLibrary(base.get_library(name))

caching_off = synth.CACHE_NONE
caching_on  = synth.CACHE_ALL | synth.CACHE_PER_PROCESS
caching     = caching_off if debug else caching_on

synth.Template.set_default_options({
    'formats':     formats,
    'debug':       debug,
    'directories': directories,
    'loaders':     [load_library],
    'resolvers':   [urlresolvers],
    'caching':     caching,
})

class NullContextManager(object):
    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

noop = NullContextManager()

class Timer(object):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = datetime.datetime.now()

    def __exit__(self, type, value, traceback):
        now = datetime.datetime.now()
        ms = (now - self.start).microseconds // 1000
        print('[synth] %s: %dms' % (self.name, ms), file=sys.stderr)

class SynthTemplate(object):
    def __init__(self, source, dirs=None, name=None):
        try:
            options = None if not dirs else {'directories': dirs}
            with Timer('parsing') if debug else noop:
                # TODO: Pass the optional template name for better errors.
                self.template = synth.Template(source, engine, options)
        except RuntimeError as e:
            message = str(e)
            # TODO: Find a less hacky way to translate syntax errors.
            if 'parsing error' in message or 'missing tag' in message:
                location = ' (%s)' % name if name else ''
                raise TemplateSyntaxError(message + location)
            else:
                raise

    def render(self, context):
        with Timer('rendering') if debug else noop:
            return self.template.render_to_string(context)

class SynthLibrary(object):
    def __init__(self, library):
        self.tags    = {name: wrap_tag(name, fn)    for name, fn in getattr(library, 'tags',    {}).items()}
        self.filters = {name: wrap_filter(name, fn) for name, fn in getattr(library, 'filters', {}).items()}


class SynthParser(base.Parser):
    def __init__(self, segments):
        super(SynthParser, self).__init__(map(SynthToken, segments))
        self.index = 0

    def advance_until(self, tag_names):
        while self.index + 1 < len(self.tokens) and self.tokens[self.index + 1].contents not in tag_names:
            self.index += 1

    def parse(self, tag_names=None):
        if tag_names: self.advance_until(tag_names)
        return SynthNodeList(self.tokens[self.index - 1])

    def skip_past(self, tag_name):
        self.advance_until((tag_name,))

    def next_token(self):
        i = self.index
        self.index += 1
        return self.tokens[i]

    def delete_first_token(self):
        self.index += 1


class SynthToken(base.Token):
    def __init__(self, segment):
        self.pieces, self.renderer = segment
        contents = self.pieces[0]
        # self.tag_name = self.pieces[1]
        # TODO: self.lineno?

        super(SynthToken, self).__init__(base.TOKEN_BLOCK, contents)

    def split_contents(self):
        return self.pieces[1:]


class SynthNodeList(base.NodeList):
    def __init__(self, token):
        super(SynthNodeList, self).__init__()
        self.renderer = token.renderer

    def render(self, context):
        return self.renderer(context, get_options_from(context)) # XXX: mark_safe?

def get_options_from(context):
    if context.use_tz or tz.get_current_timezone_name() != tz.get_default_timezone_name():
        timezone = tz.get_current_timezone()
    else:
        timezone = None

    options = {
        'caseless':    False,
        'safe':        not context.autoescape,
        'application': context.current_app,
        'timezone':    timezone,
        'language':    None if not context.use_i18n else (get_language(), get_language_bidi()),
        'formats':     None if not context.use_l10n else {
            # TODO:
            # 'NUMBER_GROUPING': ...,
            # 'DECIMAL_SEPARATOR': ...,
            # 'THOUSAND_SEPARATOR': ...,
        },
    }

    return options



def render_node(node, context, options, args, kwargs):
    if not options:
        return node.render(context)

    safe        = options['safe']
    application = options['application']
    timezone    = options['timezone']
    language    = options['language']
    localized   = options['localized']
  # formats     = options['formats']

    context.autoescape  = not safe
    context.current_app = application
    context.use_tz      = bool(timezone)
    context.use_i18n    = bool(language)
    context.use_l10n    = bool(localized)

    if language:
        tr.activate(language[0])

    if localized:
        pass # TODO

    with tz.override(timezone) if timezone else noop:
        return node.render(context)

def get_arg_names(name, tag):
    try:
        return tag.func_code.co_varnames # Includes optional args
    except:
        try:
            return tuple(getargspec(tag)[0]) # Excludes optional args
        except:
            raise Exception('Unable to get arguments names for tag: ' + name)


CUSTOM_ARGUMENT_NAMES=('parser', 'token')


string_literal   = r"""\s*(?:'(\w+)'|"(\w+)")\s*"""
string_literals  = string_literal + r'(?:,' + string_literal + r')*,?'
tag_name_pattern = re.compile(r'parser\.parse\(\(' + string_literals + r'\)\)')

def wrap_filter(name, fn):
    return lambda value, *args, **kwargs: fn(value, *args)


def wrap_tag(name, fn):
    middle_names, last_names, is_pure = None, None, False

    if isinstance(fn, functools.partial) and fn.func == generic_tag_compiler:
        # is_pure = not fn.keywords['takes_context']
        # is_simple = 'SimpleNode' in str(fn.keywords['node_class'])
        pass
    else:
        arg_names = get_arg_names(name, fn)
        if arg_names[:2] != CUSTOM_ARGUMENT_NAMES:
            raise Exception('Invalid tag argument names: %s' % arg_names)

        # Special-cased because the implementation is bizarre.
        if name == 'blocktrans':
            middle_names = frozenset(('plural',))
            last_names   = frozenset(('endblocktrans',))
        else:
            source = getsource(fn)
            names = [item for sublist in tag_name_pattern.findall(source) for item in sublist if item]

            if names:
                middle_names = frozenset([name for name in names if not name.startswith('end')])
                last_names   = frozenset([name for name in names if name.startswith('end')] or ['end' + name])

    def tag_wrapper(segments):
        parser = SynthParser(segments)
        node   = fn(parser, parser.next_token())
        return lambda context, options, *args, **kwargs: render_node(node, context, options, args, kwargs)

    return (tag_wrapper, middle_names, last_names, is_pure)

class SynthContext(base.Context):
    pass
