##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from distutils.core import setup

long_description='''
This package provides a module with template loaders designed to seamlessly
connect Django to Synth, taking into account the appropriate settings, etc.
'''

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Intended Audience :: Other Audience',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: C++',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries',
    'Topic :: Scientific/Engineering',
]

requirements = [
    'synth >=0.60',
    'django >=1.4',
]

setup(
    name = 'django-synth',
    version = '0.3.0',
    description = 'A Simple Integration Between Django and Synth',
    long_description = long_description,
    keywords = 'django, tmpl, ssi, template, framework',
    author = 'Alvaro J. Genial',
    author_email = 'genial@alva.ro',
    license = 'BSD',
    url = 'https://github.com/ajg/django-synth',
    install_requires = requirements,
    classifiers = classifiers,
)
