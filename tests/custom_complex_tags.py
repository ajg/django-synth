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

template.libraries['custom_complex_tags'] = register

from django_synth.template import SynthTemplate

source = """
{% load custom_complex_tags %}
{% ifswitch 2 1 1 %}A{% endifswitch %}
{% ifswitch 1 1 2 %}A{% endifswitch %}
{% ifswitch 2 2 2 %}B{% else %}C{% endifswitch %}
{% ifswitch 1 2 3 %}B{% else %}C{% endifswitch %}
"""

print SynthTemplate(source).render(template.Context({}))
