##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from django_synth.template import SynthContext, SynthTemplate

source = 'This is foo: {{ foo }}; bar is {% if bar %}on{% else %}off{% endif %}.'
expect = 'This is foo: 123; bar is on.'
actual = SynthTemplate(source).render(SynthContext({'foo': 123, 'bar': True}))

assert expect == actual
