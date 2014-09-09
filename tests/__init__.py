##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

failing, passing, running = (0, 0, 0)

def normalize(s):
	return s.replace('\r\n', '\n')

def check(name, expect, actual):
	global failing, passing, running
	running += 1
	expect = normalize(expect)
	actual = normalize(actual)

	if expect == actual:
		passing += 1
		print('PASS [%s]' % name)
	else:
		failing += 1
		print('FAIL [%s]' % name)
		print('    expect: %s' % repr(expect))
		print('    actual: %s' % repr(actual))

