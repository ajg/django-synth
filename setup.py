##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

# from distutils.core import setup
from setuptools import setup

long_description='''
This package provides a module with template loaders designed to seamlessly
connect Django to Synth, taking into account the appropriate settings, etc.
'''

classifiers = [
    'Development Status :: 4 - Beta',
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
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries',
    'Topic :: Scientific/Engineering',
]

requirements = [
    'synth >=1.0.4',
    'django >=1.5',
]

setup(
    name             = 'django-synth',
    version          = '0.7.1',
    description      = 'A Simple Integration Between Django and Synth',
    long_description = long_description,
    keywords         = 'django, tmpl, ssi, template, framework',
    author           = 'Alvaro J. Genial',
    author_email     = 'genial@alva.ro',
    license          = 'BSD',
    url              = 'https://github.com/ajg/django-synth',
    install_requires = requirements,
    classifiers      = classifiers,
    packages         = ["django_synth"],
    package_dir      = {"django_synth": "django_synth"},
    zip_safe         = True,
)
