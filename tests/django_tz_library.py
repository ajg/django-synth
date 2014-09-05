##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from django.template import Context
from django_synth.template import SynthTemplate

source = """\
{% load tz %}
{{ dt }}
{{ dt|utc }}
{{ dt|localtime }}
{% localtime on %}(dt: {{ dt }}){% endlocaltime %}
{% localtime off %}(dt: {{ dt }}){% endlocaltime %}
{% get_current_timezone as TIME_ZONE %}({{ TIME_ZONE }})
{% timezone "America/New_York" %}(dt: {{ dt }}){% endtimezone %}
{% timezone "Europe/Paris" %}(dt: {{ dt }}){% endtimezone %}
{% timezone None %}(dt: {{ dt }}){% endtimezone %}
"""

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

expect = '\n1988-09-05 04:03:02+00:00\n1988-09-05 04:03:02+00:00\n1988-09-04 23:03:02-05:00\n(dt: 1988-09-04 23:03:02-05:00)\n(dt: 1988-09-05 04:03:02+00:00)\n(America/Chicago)\n(dt: 1988-09-05 00:03:02-04:00)\n(dt: 1988-09-05 06:03:02+02:00)\n(dt: 1988-09-05 04:03:02+00:00)\n'
actual = SynthTemplate(source).render(Context({
    'dt': datetime(1988, 9, 5, 4, 3, 2, 0, UTC()),
}))

print('expect:', expect)
print('actual:', actual)
assert expect == actual
