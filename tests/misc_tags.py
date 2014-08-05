##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from django.template import Template, Context
from django.conf import settings
settings.configure()

c = Context({})

def test(s):
    print s, '=', Template("`" + s + "`").render(c)

test("{% widthratio 100 100 100 %}")
test("{% widthratio 100 100 200 %}")
test("{% widthratio 100 100 300 %}")
test("{% widthratio 100 300 200 %}")
test("{% widthratio 100 200 100 %}")
test("{% widthratio 100 200 200 %}")
test("{% widthratio 100 200 300 %}")
test("{% widthratio 200 100 300 %}")
test("{% widthratio 200 300 100 %}")
test("{% widthratio 300 100 100 %}")
test("{% widthratio 300 100 200 %}")
test("{% widthratio 300 100 300 %}")
test("{% widthratio 300 200 100 %}")
