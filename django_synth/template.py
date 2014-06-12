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

    def render(self, context):
        # print 'context', context, dir(context)
        return self.template.render_to_string(context)

        '''
        flat = SynthContext({})
        # Flatten the django context into a single dictionary.
        for d in context.dicts:
            flat.update(d)

        return self.template.render_to_string(flat)
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
    # print 'load_library', name
    return SynthLibrary(base.get_library(name))


CUSTOM_ARGUMENT_NAMES=('parser', 'token')

class SynthContext(dict):
    def __init__(self, dict):
        super(SynthContext, self).__init__(dict)
        self.autoescape  = None
        self.current_app = None
        self.use_l10n    = None
        self.use_tz      = None


class SynthTag(object):
    def __init__(self, name, tag):
        self.name = name
        self.tag  = tag

    def __call__(self, segments):
        tokens = []
        nodelists = []

        for pieces, renderer in segments:
            contents, tag_name, arguments = pieces[0], pieces[1], pieces[1:]
            tokens.append(SynthToken(tag_name, contents, arguments))
            nodelists.append(SynthNodeList(tag_name, renderer))

        parser = SynthParser(tokens, nodelists)
        return SynthNode(self.tag(parser, parser.next_token()), nodelists)


class SynthNode(base.Node):
    def __init__(self, node, nodelists):
        super(SynthNode, self).__init__()
        self.node = node
        self.nodelists = nodelists

    def __repr__(self):
        return '<SynthNode>'

    def __call__(self, context, match, *args, **kwargs):
        # print 'SynthNode.__call__', match, args, kwargs

        for nodelist in self.nodelists:
            nodelist.match = match
            # print 'sss', repr(nodelist.render(context))

        return self.node.render(context)

string_literal = r"""\s*(?:'(\w+)'|"(\w+)")\s*"""
string_literals = string_literal + r'(?:,' + string_literal + r')*,?'
tag_name_pattern = re.compile(r'parser\.parse\(\(' + string_literals + r'\)\)')


def make_tag(name, t):
    arg_names = get_arg_names(name, t)
    if arg_names[:2] != CUSTOM_ARGUMENT_NAMES:
        raise Exception('Invalid argument names: ' + str(arg_names))

    middle_names, last_names = None, None
    source = getsource(t)
    names = [item for sublist in tag_name_pattern.findall(source) for item in sublist if item]
    # print name, arg_names, names, t

    if names:
        middle_names = frozenset([name for name in names if not name.startswith('end')])
        last_names = frozenset([name for name in names if name.startswith('end')] or ['end' + name])

    return (SynthTag(name, t), middle_names, last_names)


class SynthLibrary(object):
    def __init__(self, library):
        self.tags = {name: make_tag(name, t) for name, t in getattr(library, 'tags', {}).items()}
        self.filters = getattr(library, 'filters', {})


class SynthParser(base.Parser):
    def __init__(self, tokens, nodelists):
        super(SynthParser, self).__init__(tokens)
        # self.tokens    = tokens
        self.nodelists = nodelists
        self.t         = 0
        self.n         = 0

    def parse(self, until=None):
        print 'SynthParser.parse', until

        if until:
            while self.n + 1 < len(self.nodelists) and self.nodelists[self.n + 1].tag_name not in until:
                self.n += 1
                self.t += 1

        return self.nodelists[self.n]

    def skip_past(self, endtag):
        print 'SynthParser.skip_past', endtag

        while self.n + 1 < len(self.nodelists) and self.nodelists[self.n + 1].tag_name != endtag:
            self.n += 1
            self.t += 1

    def next_token(self):
        print 'SynthParser.next_token'
        self.t += 1
        return self.tokens[self.t - 1]

    def delete_first_token(self):
        print 'SynthParser.delete_first_token'
        self.t += 1



class SynthNodeList(base.NodeList):
    def __init__(self, tag_name, renderer):
        super(SynthNodeList, self).__init__()
        self.tag_name = tag_name
        self.renderer = renderer
        self.match    = None

    def render_node(self, node, context):
        print 'SynthNodeList.render_node', node
        return node.render(context)

    def render(self, context):
        print 'SynthNodeList.render', self.match
        return self.renderer(context, self.match) # XXX: mark_safe(...) ?


class SynthToken(base.Token):
    def __init__(self, tag_name, contents, arguments):
        super(SynthToken, self).__init__(base.TOKEN_BLOCK, contents)
        # self.tag_name = tag_name
        # self.token_type = None     # TODO
        # self.token_name = tag_name # TODO: TOKEN_MAPPING[token_type]
        # self.lineno = None         # TODO
        # self.contents = contents
        self.arguments = arguments

        print '  tag_name', tag_name
        print '  contents', self.contents
        print '  arguments', self.arguments

    def split_contents(self):
        return self.arguments

