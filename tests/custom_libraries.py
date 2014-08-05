##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from datetime import tzinfo, timedelta, datetime
from django.template import Context
from django_synth.template import SynthTemplate

source = """

{% load l10n %}
{% load tz %}

{{ motto|localize }}
{{ motto|unlocalize }}

{{ dt }}
{{ dt|utc }}
{{ dt|localtime }}

{% localize on %}
(motto: {{ motto }})
{% endlocalize %}

{% localize off %}
(motto: {{ motto }})
{% endlocalize %}

{% localtime on %}
(dt: {{ dt }})
{% endlocaltime %}

{% localtime off %}
(dt: {{ dt }})
{% endlocaltime %}

{% get_current_timezone as TIME_ZONE %}
({{ TIME_ZONE }})

{% timezone "America/New_York" %}
(dt: {{ dt }})
{% endtimezone %}

{% timezone "Europe/Paris" %}
(dt: {{ dt }})
{% endtimezone %}

{% timezone None %}
(dt: {{ dt }})
{% endtimezone %}

{% load static %}
<img src="{% static "images/hi.jpg" %}" alt="Hi!" />

"""

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

print SynthTemplate(source).render(Context({
    'motto': 'May the Force be with you.',
    'dt': datetime.now(UTC()),
}))
