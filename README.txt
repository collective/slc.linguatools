Project Description
*******************

.. contents::

.. Note!
   -----

   - code repository
   - bug tracker
   - questions/comments feedback mail


- Code repository: https://svn.plone.org/svn/collective/slc.linguatools/
- Questions and comments to info (at) syslab (dot) com
- Report bugs at http://plone.org/products/slc.linguatools/issues

Since this package makes use of plone.app.z3cform some other package versions
are pinned in setup.py which are known to work:

    * 'zope.i18n>=3.4.0,<=3.9.9',
    * 'z3c.form>=1.9.0,<=1.9.9',
    * 'zope.testing>=3.4.0,<=3.9.9',
    * 'zope.component>=3.4.0,<3.6.dev',
    * 'zope.securitypolicy>=3.4.0,<3.6dev',
    * 'zope.app.zcmlfiles>=3.4.3,<=3.9.9',


Detailed Documentation
**********************

slc.linguatools offers a set of functions that are designed to make life easier
when dealing with multilingual sites, especially those with several different languages.

Often you have the requirement that you want to do the same action for all translations of an object. In a site with ten, twenty or more languages, doing this manually is not an option any more.


Requirements and Installation
=============================

This package only works and makes sense if you have LinguaPlone installed.

Add "slc.linguatools" to the eggs and zcml sections of your buildout configuration. After running buildout and restarting your instance, go to the Site Setup -> Add-on Products, choose slc.linguatools and click "install".

A tab named "Lingua Tools" will then appear on all translatable objects.

Functions
=========

slc.linguatools offers assistance for the following use cases:

* Set title or description: 
    Set the title / description on all translations;
    either directly to the string you entered, or based on an i18n label and
    domain

* Rename an object
    Rename all translations to the id (short name) you entered

* Set portlets 
    Propagate the portlet settings of the canonical object to all
    translations, either for all slots or the one you chose. Block / unblock
    portlet inheritance per slot.

* Workflow
    Publish all translations

* Catalog reindex
    Reindex all translations of an object

* Deleter
    Delete all translations of an object

* Cut and paste
   Cut all translations of an object and paste them to another folder

* Property handling
    Set a property with id, type and value on all translations.
    Example: Set string property "layout" to "@@my-shiny-view". Delete an
    existing property.

* Marker interfaces
    Set or remove a marker interface on all translations of an object. The
    interfaces available for setting and removing are provided by a vocabulary
    and are the same as on the "Interfaces" tab in the ZMI.

* Subtyping (if p4a.subtyper is installed)
    Set a subtype on all translations; remove a subtype

* Translate an object
    Create a translation of the current object for all available languages.
    The AT attributes that should be copied over can be selected. If the object
    is a Collection, then all criteria are copied as well. This function can
    also be used to copy values of AT attributes and collection criteria to
    already existing translations.

Versions
========

The first version of this tool featured a manually written BrowserView. During the Plone-Conference 2009 sprint, a second version that uses z3c form was written. This is the version visible by default via the "Lingua Tools" tab. The original version is still accessible under @@linguatools-old.
