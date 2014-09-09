##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from . import check
from django import template
from django.template import loader

register = template.Library()


def _get_template(name, dirs=None):
    if name == 'experiments/goal.html':
        return SynthTemplate('[{{ url }}]')
    else:
        return get_template(name, dirs)


get_template = loader.get_template
loader.get_template = _get_template

# Adapted from mixcloud/django-experiments:
@register.inclusion_tag('experiments/goal.html')
def experiment_goal(goal_name):
    return {'url': 'http://localhost/' + goal_name}

template.libraries['custom_inclusion_tags'] = register

from django_synth.template import SynthTemplate

source = """
{% load custom_inclusion_tags %}
Foo: {% experiment_goal 'foo_experiment' %}
Bar: {% experiment_goal 'bar_experiment' %}
"""

expect = '\n\nFoo: [http://localhost/foo_experiment]\nBar: [http://localhost/bar_experiment]\n'
actual = SynthTemplate(source).render(template.Context({}))

check(__name__, expect, actual)
