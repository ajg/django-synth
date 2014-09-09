##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from . import check
from django.template import Context
from django_synth.template import SynthTemplate

source = """\
{% load l10n %}
{{ motto|localize }}
{{ motto|unlocalize }}
{% localize on %}(motto: {{ motto }}){% endlocalize %}
{% localize off %}(motto: {{ motto }}){% endlocalize %}
"""

expect = '\nMay the Force be with you.\nMay the Force be with you.\n(motto: May the Force be with you.)\n(motto: May the Force be with you.)\n'
actual = SynthTemplate(source).render(Context({
    'motto': 'May the Force be with you.',
}))

check(__name__, expect, actual)
