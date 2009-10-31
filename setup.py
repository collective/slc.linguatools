# -*- coding: utf-8 -*-
"""
This module contains the slc.linguatools package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2.5dev'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('slc', 'linguatools', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n'
    )

requires = [
          'setuptools',
          'Products.LinguaPlone',
          'plone.app.z3cform',
          'zope.i18n==3.4.0',
          'z3c.form==1.9.0',
          'zope.testing==3.4.0',
          'zope.component==3.4.0',
          'zope.securitypolicy==3.4.0',
          'zope.app.zcmlfiles==3.4.3'
      ]

install_requires = requires

tests_require= requires +\
               ['zope.testing']

setup(name='slc.linguatools',
      version=version,
      description="A toolset to manage objects in multiple linguaplone trees",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='linguatools linguaplone',
      author='Syslab.com GmbH',
      author_email='info@syslab.com',
      url='https://svn.syslab.com/svn/syslabcom/slc.linguatools',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['slc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'slc.linguatools.tests.test_docs.test_suite',
      entry_points="""
        [z3c.autoinclude.plugin]
        target = plone
      """,
      )
