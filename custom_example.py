
from datetime import tzinfo, timedelta, datetime

ZERO = timedelta(0)
HOUR = timedelta(hours=1)

class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO



from django.template import Context
from django_synth.template import SynthTemplate

context = Context({
  'motto': 'May the Force be with you.',
  'dt': datetime.now(UTC()),
})
source = """

{% load l10n %}
{% load tz %}

{{ motto|localize }}
{{ motto|unlocalize }}

{{ dt }}
{{ dt|utc }}
{{ dt|localtime }}

{% localize on %}
(value: {{ value }})
{% endlocalize %}

{% localize off %}
(value: {{ value }})
{% endlocalize %}
"""

'''
{% comment %}
{% localize on %}
(value: {{ value }})
{% endlocalize %}
{% endcomment %}
'''

print SynthTemplate(source).render(context)
