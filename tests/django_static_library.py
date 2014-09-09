##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from . import check
from django.template import Context
from django_synth.template import SynthTemplate

source = """\
{% load static %}
<img src="{% static "images/hi.jpg" %}" alt="Hi!" />
"""

expect = '\n<img src="images/hi.jpg" alt="Hi!" />\n'
actual = SynthTemplate(source).render(Context({}))

check(__name__, expect, actual)
