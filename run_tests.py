##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

import sys
import tests
import tests.custom_complex_tags
import tests.custom_inclusion_tags
import tests.custom_simple_tags
import tests.django_l10n_library
import tests.django_static_library
# TODO: Currently fails on Linux & Windows, and might be locale-dependent:
# import tests.django_tz_library
import tests.trivial_template

sys.exit(tests.failing)
