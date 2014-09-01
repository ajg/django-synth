##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from datetime import tzinfo, timedelta, datetime
from django import template

register = template.Library()

@register.simple_tag
def identity(arg):
    return arg

template.libraries['custom_test'] = register

from django_synth.template import SynthTemplate

source = """
{% load custom_test %}
{% identity 1 %}
"""

print SynthTemplate(source).render(template.Context({}))
