slc.linguatools Changelog
=========================

1.4.4 (2013-12-06)
------------------

- Added a commit after every clone

1.4.3 (2013-04-10)
------------------

- Cleanup, don't require a REQUEST obj in exec_for_all_langs [pysailor]


1.4.2 (2012-07-22)
------------------

- Switched to using plone.app.testing instead of zope.testing [thomasw]
- Copied support for slc.outdated from the Plone3-branch [thomasw]
- Moved repository from svn to github [thomasw]

1.4.1 (2012-02-04)
------------------

- If an item has a text_format property (e.g. documents), copy its value to
  all translations in the "Translate this obejct" function [thomasw]
- Added Robert Niederreiter's patch to the getBreadcrumbs() method of TinyMCE
  to allow for common language-neutral folders (e.g. for images). See LP issue
  275 for details. The patch needs to be activated by an environment setting.
  See the README.txt [thomasw]


1.4.0 (2011-07-01)
------------------

- Removed version pinnings for dependencies [thomasw]
- Slight CSS adjustments for main view [thomasw]
- Added missing import of CMF permissions package [thomasw]

1.4.0b1 (2011-04-08)
--------------------

- Updated the doctest setup to run in Plone4 [thomasw]
- Added possibility to make displaying a form optional, e.g. only if a
  certain component is installed [thomasw]


1.3.6 (2010-07-18)
------------------

- Bugfix in PropertyForm: encode unicode to utf-8, otherwise setting the
  property default_page breaks [thomasw]
- allow module utils for import in python scripts [pilz]

1.3.5 (2010-03-31)
------------------

- In plone.z3cform version 0.5.8 a major change was introduced that affects our
  product. By overwriting update() and contents() of FormWrapper, we enable
  support for versions >=0.5.8; with an ugly hack in contents(), we maintain
  support for versions <=0.5.7 [thomasw]
- Fixed broken doctest for changing the workflow, introduced in 1.3.3 [thomasw]
- The AvailableIdsVocabulary now only returns translatable items [thomasw]
- New functionality: Add and remove marker interfaces [thomasw]
- Don't show the canonical lang in the vocabulary of avaiable langs [thomasw]

1.3.4 (2010-02-09)
------------------

- In the AvailableWorkflowTransitions vocabulary, return all available
  transitions of a workflow, not just those available for the canonical's
  state. The canonical might be published, while some translations are still
  private [thomasw]

1.3.3 (2010-01-27)
------------------

- Reworked workflow handling. Instead of only "publish", now all transactions
  available on the current object can be triggered [thomasw]
- "Translate this" now has an additional language field, so that only a subset
  of the available languages may be chosen [thomasw]
- Ran the pep8 script and fixed most issues [thomasw]


1.3.2 (2009-12-17)
------------------

- Bugfix in linguatools.css: missing closing bracket. Thanks for the
  heads-up, do3cc! [thomasw]

1.3.1 (2009-12-11)
------------------

- Be more relaxed with version pinning needed for plone.app.z3cform [thomasw]

1.3 (2009-11-29)
----------------

- Major revamp at Plone Conference 2009 sprint: moved from static BrowserView
  to z3c form; brushed up test coverage; clearer interface; more user-friendly,
  less typing necessary; easier to plug in new functionality [cillian, jcbrand,
  pilz, thomasw, Andreas Schmid]

1.2.5 (unreleased)
------------------

- make sure that lang is ascii when using it to create objectids. Otherwise we get an infinite recursion [pilz]
- D'oh another bug in "block portlets", this time in the status message [thomasw]
- better status reporting for translateThis; collection criteria are now also copied when
  "translation exists" is ticked; more graceful handling for unknown fields [thomasw]

1.2.4 (2009-10-27)
------------------

- Continuing my fix for ambiguous variable name [thomasw]


1.2.3 (2009-10-25)
------------------

- 2 bugs fixed for "block portlets": ambiguous variable name, wrong button name [thomasw]

1.2.2 (2009-10-08)
------------------

- 2 bugfixes in cutAndPaste (don't despair if object is not available) [thomasw]
- Added a contenview tab for Lingua Tools on ITranslatable objects [jcbrand]
- In lingatools.pt moved the legends into the fieldsets, added labels and reorganised a bit [jcbrand]
- Added new option to remove subtypes [jcbrand]
- Use the default plone status messages for messaging and added event.log logging [jcbrand]

slc.linguatools 1.2.1 (2009-08-13)
----------------------------------

- made compatible with current version of LinguaPlone [gerken/thomasw]

slc.linguatools 1.2 (2009-06-17)
--------------------------------

- built a proper framework for the already existing doctest linguatests.txt [thomasw]

slc.linguatools 1.1 (2009-05-12)
--------------------------------

- Packaged egg [pilz]

slc.linguatools 1.0 (2008-03-31)
--------------------------------

- Initial port
