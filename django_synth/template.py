##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

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


xxx_original_context = None

class TemplateWrapper(object):
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
        print 'context', context, dir(context)
        global xxx_original_context
        xxx_original_context = context
        ### TODO: return self.template.render_to_string(context)

        # Flatten the django context into a single dictionary.
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)

        return self.template.render_to_string(context_dict)




def get_arg_names(name, tag):
    try:
        return tag.func_code.co_varnames # Includes optional args
    except:
        try:
            return tuple(getargspec(tag)[0]) # Excludes optional args
        except:
            raise Exception('Unable to get arguments names for tag: ' + name)




def load_library(name):
    print 'load_library', name
    return LibraryWrapper(base.get_library(name))



'''
def load_tag(name, tag):
    arg_names = get_arg_names(name, tag)
    if arg_names != CUSTOM_ARGUMENT_NAMES:
        raise Exception('Invalid argument names: ' + str(arg_names))

    print name, arg_names, tag




    return TagWrapper(tag)

    # tag_stack = []
    # return lambda *args, **kwargs: (tag(*args, **kwargs), tag_stack)[1]

    # wrap_tag(name, (lambda *pieces: tag(ParserWrapper(tag_stack), TokenWrapper(name, pieces))), tag_stack)
'''

CUSTOM_ARGUMENT_NAMES=('parser', 'token')

'''
class ContextWrapper(dict):
    def __init__(self, dict):
        super(ContextWrapper, self).__init__(dict)
        self.autoescape  = None
        self.current_app = None
        self.use_l10n    = None
        self.use_tz      = None

'''


class TagWrapper(object):
    def __init__(self, name, tag):
        self.name = name
        self.tag  = tag

    def __call__(self, segments):
        print 'segments', len(segments), segments

        tokens = []
        nodelists = []

        for pieces, renderer in segments:
            contents, tag_name, arguments = pieces[0], pieces[1], pieces[2:]
            tokens.append(TokenWrapper(tag_name, contents, arguments))
            nodelists.append(NodeListWrapper(tag_name, renderer))

        parser = ParserWrapper(tokens, nodelists)
        return NodeWrapper(self.tag(parser, parser.next_token()), nodelists)

        '''
        node   = self.tag(parser, parser.next_token())

        def renderer(match, *args, **kwargs):
            print 'renderer', match, args, kwargs

            for nodelist in nodelists:
                nodelist.match = match
                print 'sss', repr(nodelist.render(xxx_original_context))
            return node.render(xxx_original_context)

        return renderer
        '''


'''
class NodeWrapper(object): # TODO: (base.Node)
    def __init__(self, nodelist):
        super(NodeWrapper, self).__init__()
        self.nodelist = nodelist

    def __repr__(self):
        return '<NodeWrapper>'

    def __iter__(self):
        yield self

    def render(self, context):
        return self.nodelist.render(context)

    """
    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        for attr in self.child_nodelists:
            nodelist = getattr(self, attr, None)
            if nodelist:
                nodes.extend(nodelist.get_nodes_by_type(nodetype))
        return nodes
    """
'''


class NodeWrapper(base.Node):
    def __init__(self, node, nodelists):
        super(NodeWrapper, self).__init__()
        self.node = node
        self.nodelists = nodelists

    def __call__(self, match, *args, **kwargs):
        print 'NodeWrapper.__call__', match, args, kwargs

        for nodelist in self.nodelists:
            nodelist.match = match
            # print 'sss', repr(nodelist.render(xxx_original_context))

        return self.node.render(xxx_original_context)

def wrap_tag(name, t):
    arg_names = get_arg_names(name, t)
    if arg_names[:2] != CUSTOM_ARGUMENT_NAMES:
        raise Exception('Invalid argument names: ' + str(arg_names))

    print name, arg_names, t

    until = ('end' + name,) # TODO
    # source = getsource(t)


    return (TagWrapper(name, t), until)


class LibraryWrapper(object):
    def __init__(self, library):
        self.tags = {name: wrap_tag(name, t) for name, t in getattr(library, 'tags', {}).items()}
        self.filters = getattr(library, 'filters', {})


class ParserWrapper(base.Parser):
    def __init__(self, tokens, nodelists):
        super(ParserWrapper, self).__init__(tokens)
        # self.tokens    = tokens
        self.nodelists = nodelists
        self.t         = 0
        self.n         = 0

    def parse(self, until=None):
        print 'ParserWrapper.parse', until

        if until:
            while self.n + 1 < len(self.nodelists) and self.nodelists[self.n + 1].tag_name not in until:
                self.n += 1
                self.t += 1

        return self.nodelists[self.n]

    def skip_past(self, endtag):
        print 'ParserWrapper.skip_past', endtag

        while self.n + 1 < len(self.nodelists) and self.nodelists[self.n + 1].tag_name != endtag:
            self.n += 1
            self.t += 1

    def next_token(self):
        print 'ParserWrapper.next_token'
        self.t += 1
        return self.tokens[self.t - 1]

    def delete_first_token(self):
        print 'ParserWrapper.delete_first_token'
        self.t += 1



class NodeListWrapper(base.NodeList):
    def __init__(self, tag_name, renderer):
        super(NodeListWrapper, self).__init__()
        self.tag_name = tag_name
        self.renderer = renderer
        self.match    = None

    def render_node(self, node, context):
        print 'NodeListWrapper.render_node', node
        return node.render(context)

    def render(self, context):
        print 'NodeListWrapper.render', self.match
        s = self.renderer(self.match) # TODO: Pass the context
        print '    s:', repr(s)
        return s

        """
        bits = []
        for node in self:
            if isinstance(node, Node):
                bit = self.render_node(node, context)
            else:
                bit = node
            bits.append(force_text(bit))
        return mark_safe(''.join(bits))
        """

    """
    def get_nodes_by_type(self, nodetype):
        nodes = []
        for node in self:
            nodes.extend(node.get_nodes_by_type(nodetype))
        return nodes
    """



class TokenWrapper(base.Token):
    def __init__(self, tag_name, contents, arguments):
        super(TokenWrapper, self).__init__(base.TOKEN_BLOCK, contents)
        # self.tag_name = tag_name
        # self.token_type = None     # TODO
        # self.token_name = tag_name # TODO: TOKEN_MAPPING[token_type]
        # self.lineno = None         # TODO
        # self.contents = contents
        self.arguments = arguments

        print '  tag_name', tag_name
        print '  contents', self.contents
        print '  arguments', self.arguments

    # def __str__(self):
    #     return ('<%s token: "%s...">' % (self.token_name, self.contents[:20].replace('\n', '')))

    def split_contents(self):
        return self.arguments

