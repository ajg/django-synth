##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from datetime import tzinfo, timedelta, datetime
from django.template import Context
from django_synth.template import SynthTemplate

source = """\
{% load l10n %}
{% load tz %}
{% load static %}
{{ motto|localize }}
{{ motto|unlocalize }}
{{ dt }}
{{ dt|utc }}
{{ dt|localtime }}
{% localize on %}(motto: {{ motto }}){% endlocalize %}
{% localize off %}(motto: {{ motto }}){% endlocalize %}
{% localtime on %}(dt: {{ dt }}){% endlocaltime %}
{% localtime off %}(dt: {{ dt }}){% endlocaltime %}
{% get_current_timezone as TIME_ZONE %}({{ TIME_ZONE }})
{% timezone "America/New_York" %}(dt: {{ dt }}){% endtimezone %}
{% timezone "Europe/Paris" %}(dt: {{ dt }}){% endtimezone %}
{% timezone None %}(dt: {{ dt }}){% endtimezone %}
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

expect = '\n\n\nMay the Force be with you.\nMay the Force be with you.\n1988-09-05 04:03:02+00:00\n1988-09-05 04:03:02+00:00\n1988-09-04 23:03:02-05:00\n(motto: May the Force be with you.)\n(motto: May the Force be with you.)\n(dt: 1988-09-04 23:03:02-05:00)\n(dt: 1988-09-05 04:03:02+00:00)\n(America/Chicago)\n(dt: 1988-09-05 00:03:02-04:00)\n(dt: 1988-09-05 06:03:02+02:00)\n(dt: 1988-09-05 04:03:02+00:00)\n<img src="images/hi.jpg" alt="Hi!" />\n'
actual = SynthTemplate(source).render(Context({
    'motto': 'May the Force be with you.',
    'dt': datetime(1988, 9, 5, 4, 3, 2, 0, UTC()),
}))

print('expect:', expect)
print('actual:', actual)
assert expect == actual
