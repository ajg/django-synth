
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
from django_synth.template import BasicTemplate

context = Context({
  'motto': 'May the Force be with you.',
  'dt': datetime.now(UTC()),
})
source = """

{% load tz %}

{{ dt }}
{{ dt|utc }}
{{ dt|localtime }}

"""

print BasicTemplate(source).render(context)
