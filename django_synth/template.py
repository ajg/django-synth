##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

import re
import synth
import django.template.base as base
import django.utils.timezone as tz

from inspect import getargspec, getsource
from django.conf import settings
from django.core import urlresolvers
from django.template import TemplateSyntaxError


if not settings.configured:
    settings.configure()

# TODO: Make private.
engine      = getattr(settings, 'SYNTH_ENGINE',      'django')
directories = getattr(settings, 'SYNTH_DIRECTORIES', settings.TEMPLATE_DIRS or [])
debug       = getattr(settings, 'SYNTH_DEBUG',       settings.TEMPLATE_DEBUG)
formats     = getattr(settings, 'SYNTH_FORMATS', {
    'TEMPLATE_STRING_IF_INVALID': settings.TEMPLATE_STRING_IF_INVALID,
    'DATE_FORMAT':                settings.DATE_FORMAT,
    'DATETIME_FORMAT':            settings.DATETIME_FORMAT,
    'MONTH_DAY_FORMAT':           settings.MONTH_DAY_FORMAT,
    'SHORT_DATE_FORMAT':          settings.SHORT_DATE_FORMAT,
    'SHORT_DATETIME_FORMAT':      settings.SHORT_DATETIME_FORMAT,
    'TIME_FORMAT':                settings.TIME_FORMAT,
    'YEAR_MONTH_FORMAT':          settings.YEAR_MONTH_FORMAT,
})

print('Loaded synth; version: %s; default engine: %s; debug: %s.' %
    (synth.version(), engine, 'ON' if debug else 'OFF'))


class SynthTemplate(object):
    def __init__(self, source, dirs=None):
        try:
            self.template = synth.Template(
                source,
                engine,
                formats,
                debug,
                dirs or directories,
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
        return self.template.render_to_string(context)


class SynthLibrary(object):
    def __init__(self, library):
        self.tags = {name: wrap_tag(name, tag) for name, tag in getattr(library, 'tags', {}).items()}
        self.filters = getattr(library, 'filters', {})


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
        return self.renderer(context, **to_metadata(context)) # XXX: mark_safe?

def to_metadata(context):
    if context.use_tz or tz.get_current_timezone_name() != tz.get_default_timezone_name():
        timezone = tz.get_current_timezone()
    else:
        timezone = None

    metadata = {
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

    return metadata


def render_node(node, context, caseless=False, safe=False, application=None, timezone=None, language=None, formats=None, **kwargs):
    context.autoescape  = not safe
    context.current_app = application
    context.use_tz      = bool(timezone)
    context.use_i18n    = bool(language)
    context.use_l10n    = bool(formats)

    if language:
        activate(language[0])

    if formats:
        pass # TODO

    if timezone:
        with tz.override(timezone):
            return node.render(context)
    else:
        return node.render(context)


def get_arg_names(name, tag):
    try:
        return tag.func_code.co_varnames # Includes optional args
    except:
        try:
            return tuple(getargspec(tag)[0]) # Excludes optional args
        except:
            raise Exception('Unable to get arguments names for tag: ' + name)


def load_library(name):
    return SynthLibrary(base.get_library(name))


CUSTOM_ARGUMENT_NAMES=('parser', 'token')


string_literal   = r"""\s*(?:'(\w+)'|"(\w+)")\s*"""
string_literals  = string_literal + r'(?:,' + string_literal + r')*,?'
tag_name_pattern = re.compile(r'parser\.parse\(\(' + string_literals + r'\)\)')


def wrap_tag(name, tag):
    arg_names = get_arg_names(name, tag)
    if arg_names[:2] != CUSTOM_ARGUMENT_NAMES:
        raise Exception('Invalid tag argument names: ' + str(arg_names))

    middle_names, last_names = None, None
    source = getsource(tag)
    names = [item for sublist in tag_name_pattern.findall(source) for item in sublist if item]

    if names:
        middle_names = frozenset([name for name in names if not name.startswith('end')])
        last_names   = frozenset([name for name in names if name.startswith('end')] or ['end' + name])

    is_simple   = False
    is_dataless = False

    def tag_wrapper(segments):
        parser = SynthParser(segments)
        node   = tag(parser, parser.next_token())
        return lambda context, *args, **kwargs: render_node(node, context, **kwargs)

    return (tag_wrapper, middle_names, last_names, is_simple, is_dataless)
