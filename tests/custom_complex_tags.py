##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from django import template

register = template.Library()

@register.tag
def ifswitch(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError("%r tag requires an argument" % token.contents.split()[0])

    name = bits[1]
    instances = bits[2:]

    nodelist_true = parser.parse(('else', 'endifswitch'))
    token = parser.next_token()

    if token.contents == 'else':
        nodelist_false = parser.parse(('endifswitch',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return SwitchNode(nodelist_true, nodelist_false, name, instances)


class SwitchNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, name, instances):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.name = name
        self.instances = [template.Variable(i) for i in instances]

    def render(self, context):
        instances = [i.resolve(context) for i in self.instances]
        if 'request' in context:
            instances.append(context['request'])

        if not is_active(self.name, *instances):
            return self.nodelist_false.render(context)

        return self.nodelist_true.render(context)

def is_active(name, *instances):
    return str(name) in map(str, instances)

def is_enrolled(experiment_name, alternative, weight, user_variable):
    return True


class ExperimentNode(template.Node):
    def __init__(self, node_list, experiment_name, alternative, weight, user_variable):
        self.node_list = node_list
        self.experiment_name = experiment_name
        self.alternative = alternative
        self.weight = weight
        self.user_variable = user_variable

    def render(self, context):
        # Should we render?
        if is_enrolled(self.experiment_name, self.alternative, self.weight, self.user_variable):
            response = self.experiment_name + ': ' + self.node_list.render(context)
        else:
            response = ""

        return response


def _parse_token_contents(token_contents):
    (_, experiment_name, alternative), remaining_tokens = token_contents[:3], token_contents[3:]
    weight = None
    user_variable = None

    for offset, token in enumerate(remaining_tokens):
        if '=' in token:
            name, expression = token.split('=', 1)
            if name == 'weight':
                weight = expression
            elif name == 'user':
                user_variable = template.Variable(expression)
            else:
                raise ValueError()
        elif offset == 0:
            # Backwards compatibility, weight as positional argument
            weight = token
        else:
            raise ValueError()

    return experiment_name, alternative, weight, user_variable


# Adapted from mixcloud/django-experiments:
@register.tag('experiment')
def experiment(parser, token):
    """
    Split Testing experiment tag has the following syntax :

    {% experiment <experiment_name> <alternative>  %}
    experiment content goes here
    {% endexperiment %}

    If the alternative name is neither 'test' nor 'control' an exception is raised
    during rendering.
    """
    try:
        token_contents = token.split_contents()
        experiment_name, alternative, weight, user_variable = _parse_token_contents(token_contents)

        node_list = parser.parse(('endexperiment', ))
        parser.delete_first_token()
    except ValueError:
        raise template.TemplateSyntaxError("Syntax should be like :"
                "{% experiment experiment_name alternative [weight=val] [user=val] %}")

    return ExperimentNode(node_list, experiment_name, alternative, weight, user_variable)



template.libraries['custom_complex_tags'] = register

from . import check
from django_synth.template import SynthTemplate

source = """
{% load custom_complex_tags %}
{% ifswitch 2 1 1 %}A{% endifswitch %}
{% ifswitch 1 1 2 %}A{% endifswitch %}
{% ifswitch 2 2 2 %}B{% else %}C{% endifswitch %}
{% ifswitch 1 2 3 %}B{% else %}C{% endifswitch %}
{% experiment Foo Bar %}Experiment{% endexperiment %}
"""

expect = '\n\n\nA\nB\nC\nFoo: Experiment\n'
actual = SynthTemplate(source).render(template.Context({}))

check(__name__, expect, actual)

