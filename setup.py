# -*- coding: utf-8 -*-
"""
This module contains the slc.linguatools package
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.4.1'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    read('TODO.txt')
    + '\n')

requires = [
          'setuptools',
          'Products.LinguaPlone',
          'plone.app.z3cform',
          'plone.browserlayer',
          'zope.i18n',
          'z3c.form',
          'zope.testing',
          'zope.app.schema'
      ]

install_requires = requires

tests_require = requires +\
               ['zope.testing']

setup(name='slc.linguatools',
      version=version,
      description="A set of tools that simplify handling multilingual "\
        "content in Plone",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?
      # %3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
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
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='slc.linguatools.tests.test_docs.test_suite',
      entry_points="""
        [z3c.autoinclude.plugin]
        target = plone
      """,
      )
