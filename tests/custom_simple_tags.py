##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from django import template

register = template.Library()

@register.simple_tag
def identity(arg):
    return arg

template.libraries['custom_simple_tags'] = register

from django_synth.template import SynthTemplate

source = """
{% load custom_simple_tags %}
{% identity 1 %}
"""

expect = '\n\n1\n'
actual = SynthTemplate(source).render(template.Context({}))

print('expect:', expect)
print('actual:', actual)
assert expect == actual
