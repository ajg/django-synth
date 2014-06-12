##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

import re
import synth
import django.template.base as base

from inspect import getargspec, getsource
from django.conf import settings
from django.core import urlresolvers
from django.template import TemplateSyntaxError

if not settings.configured:
    settings.configure()

# TODO: Make private.
default_engine = getattr(settings, 'SYNTH_DEFAULT_ENGINE', 'django')
default_value  = getattr(settings, 'SYNTH_DEFAULT_VALUE',  settings.TEMPLATE_STRING_IF_INVALID)
debug          = getattr(settings, 'SYNTH_DEBUG',          settings.TEMPLATE_DEBUG)
formats        = getattr(settings, 'SYNTH_FORMATS', {
    'DATE_FORMAT':           settings.DATE_FORMAT,
    'DATETIME_FORMAT':       settings.DATETIME_FORMAT,
    'MONTH_DAY_FORMAT':      settings.MONTH_DAY_FORMAT,
    'SHORT_DATE_FORMAT':     settings.SHORT_DATE_FORMAT,
    'SHORT_DATETIME_FORMAT': settings.SHORT_DATETIME_FORMAT,
    'TIME_FORMAT':           settings.TIME_FORMAT,
    'YEAR_MONTH_FORMAT':     settings.YEAR_MONTH_FORMAT,
    'SPACE_FORMAT':          '\xa0',
})

print('Loaded synth; version: %s; default engine: %s.' % (synth.version(), default_engine))

class SynthTemplate(object):
    def __init__(self, source, engine_name=default_engine, directories=[]):
        try:
            self.template = synth.Template(
                source,
                engine_name,
                default_value,
                formats,
                debug,
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

    def render(self, context_data):
        print '# SynthTemplate.render', context_data
        return self.template.render_to_string(context_data) # (SynthContext(context_data))

'''
class SynthContext(dict): # (base.Context)
    def __init__(self, dict):
        super(SynthContext, self).__init__(dict)
        self.autoescape  = None
        self.current_app = None
        self.use_l10n    = None
        self.use_tz      = None
'''

def get_arg_names(name, tag):
    try:
        return tag.func_code.co_varnames # Includes optional args
    except:
        try:
            return tuple(getargspec(tag)[0]) # Excludes optional args
        except:
            raise Exception('Unable to get arguments names for tag: ' + name)


def load_library(name):
    print '# SynthLoad', repr(name)
    return SynthLibrary(base.get_library(name))


CUSTOM_ARGUMENT_NAMES=('parser', 'token')


string_literal   = r"""\s*(?:'(\w+)'|"(\w+)")\s*"""
string_literals  = string_literal + r'(?:,' + string_literal + r')*,?'
tag_name_pattern = re.compile(r'parser\.parse\(\(' + string_literals + r'\)\)')


def wrap_tag(name, tag):
    print '# SynthWrap', repr(name), tag

    arg_names = get_arg_names(name, tag)
    if arg_names[:2] != CUSTOM_ARGUMENT_NAMES:
        raise Exception('Invalid tag argument names: ' + str(arg_names))

    middle_names, last_names = None, None
    source = getsource(tag)
    names = [item for sublist in tag_name_pattern.findall(source) for item in sublist if item]
    # print name, arg_names, names, tag

    if names:
        middle_names = frozenset([name for name in names if not name.startswith('end')])
        last_names   = frozenset([name for name in names if name.startswith('end')] or ['end' + name])

    def tag_wrapper(segments):
        parser = SynthParser(segments)
        node   = tag(parser, parser.next_token())
        return lambda context_data, *args, **kwargs: node.render(context_data)

    return (tag_wrapper, middle_names, last_names)


class SynthLibrary(object):
    def __init__(self, library):
        print '# SynthLibrary.__init__', library

        self.tags = {name: wrap_tag(name, tag) for name, tag in getattr(library, 'tags', {}).items()}
        self.filters = getattr(library, 'filters', {})


class SynthParser(base.Parser):
    def __init__(self, segments):
        print '# SynthParser.__init__'

        super(SynthParser, self).__init__(map(SynthToken, segments))
        self.index = 0

    def advance_until(self, tag_names):
        while self.index + 1 < len(self.tokens) and self.tokens[self.index + 1].contents not in tag_names:
            self.index += 1

    def parse(self, tag_names=None):
        print '# SynthParser.parse', self.index, tag_names

        if tag_names: self.advance_until(tag_names)
        return SynthNodeList(self.tokens[self.index - 1])

    def skip_past(self, tag_name):
        print '# SynthParser.skip_past', self.index, tag_name

        self.advance_until((tag_name,))

    def next_token(self):
        print '# SynthParser.next_token', self.index

        i = self.index
        self.index += 1
        return self.tokens[i]

    def delete_first_token(self):
        print '# SynthParser.delete_first_token', self.index

        self.index += 1


class SynthNodeList(base.NodeList):
    def __init__(self, token):
        print '# SynthNodeList.__init__', token

        super(SynthNodeList, self).__init__()
        self.renderer = token.renderer

    def render(self, context_data):
        print '# SynthNodeList.render'

        return self.renderer(context_data) # XXX: mark_safe(...) ?


class SynthToken(base.Token):
    def __init__(self, segment):
        print '# SynthToken.__init__', segment

        self.pieces, self.renderer = segment
        contents = self.pieces[0]
        # self.tag_name = self.pieces[1]
        # TODO: self.lineno?

        super(SynthToken, self).__init__(base.TOKEN_BLOCK, contents)

    def split_contents(self):
        print '# SynthToken.split_contents', self.pieces

        return self.pieces[1:]

