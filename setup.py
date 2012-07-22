# -*- coding: utf-8 -*-
"""
This module contains the slc.linguatools package
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.4.2'

long_description = (
    read('README.rst')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs/CHANGES.rst')
    + '\n' +
    read('CONTRIBUTORS.rst')
    + '\n' +
    read('TODO.rst')
    + '\n')

install_requires = [
        'setuptools',
        'Products.LinguaPlone',
        'plone.app.z3cform',
        'zope.i18n',
        'z3c.form',
        'zope.app.schema',
    ]


setup(name='slc.linguatools',
    version=version,
    description="A set of tools that simplify handling multilingual "\
    "content in Plone based on LinguaPlone",
    long_description=long_description,
    classifiers=[
    "Framework :: Plone",
    "Framework :: Plone :: 3.3",
    "Framework :: Plone :: 4.0",
    "Framework :: Plone :: 4.1",
    "Framework :: Plone :: 4.2",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "License :: OSI Approved :: European Union Public Licence "\
        "1.1 (EUPL 1.1)",
    ],
    keywords='linguatools internationalization linguaplone',
    author='Syslab.com GmbH',
    author_email='thomas@syslab.com',
    url='http://pypi.python.org/pypi/slc.linguatools/',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['slc'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require=dict(test=['plone.app.testing']),
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )
