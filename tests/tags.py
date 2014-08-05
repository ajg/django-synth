##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from django.template import Template, Context
from django.conf import settings
settings.configure()

def test(s, c):
    print s, '=', Template("`" + s + "`").render(Context(c))


def for_tags(c):
    test("{% for x in var %}({{ x }}){% endfor %}", c)
    test("{% for x, y in var %}({{ x }},{{ y }}){% endfor %}", c)
    test("{% for x, y, z in var %}({{ x }},{{ y }},{{ z }}){% endfor %}", c)
    print


for_tags({'var': 'foo'})
for_tags({'var': [1, 2, 3]})
for_tags({'var': [(1, 2, 3), (11, 22), (111)]})
for_tags({'var': ['abc', 'ab', 'a']})
