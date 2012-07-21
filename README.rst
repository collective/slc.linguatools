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

Plone 4 is supported starting with version 1.4.0 - Bugfix releases for Plone
3 will be continued in the 1.3.x series.


Overview
********

slc.linguatools offers a set of functions that are designed to make life easier
when dealing with multilingual sites, especially those with several different languages.

Often you have the requirement that you want to do the same action for all
translations of an object. In a site with ten, twenty or more languages, doing
this manually is not an option any more.

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
    Publish / retract / etc. all translations

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
    is a Collection, then all criteria are copied as well.

* Copy the values of individual fields
    Using the "Translate this object" function mentioned above and selecting the
    "Translation exists" option, you can copy the values of individual AT fields
    to all translations, such as dates, tags (Subject) and Collection criteria.


Requirements and Installation
=============================

This package only works and makes sense if you have LinguaPlone installed.

Add "slc.linguatools" to the eggs and zcml sections of your buildout
configuration. After running buildout and restarting your instance, go to the
Site Setup -> Add-on Products, choose slc.linguatools and click "install".

A tab named "Lingua Tools" will then appear on all translatable objects.

Enabling support for language neutral folders in TinyMCE
--------------------------------------------------------

If you have the default language folder structure (e.g. created by LinguaPlone's
@@language-setup-folders), you will have a top-level folder that provides
INavigationRoot for every language in your site (/en, /de, /fr, etc.). In this case
it will not be possible to have a common language-neutral
folder (e.g. for images) that is accessible in TinyMCE. For details see:
http://plone.org/products/linguaplone/issues/275

In this same ticket, a patch to the getBreadcrumbs method of TinyMCE was 
provided by Robert Niederreiter. This patch is included in slc.linguatools,
but not activated by default. To activate it, you need to set an environment
variable called PATCH_TINYMCE_BREADCRUMBS.

You can do this by adding the following to your zope.conf::

   <environment>
   PATCH_TINYMCE_BREADCRUMBS true
   </environment>

If you use Buildout, you don't want to edit zope.conf directly, since it will
be overwritten by the next buildout. Rather, edit your buildout configuration
and add the following to the [instance] section::

  zope-conf-additional =
    <environment>
      PATCH_TINYMCE_BREADCRUMBS true
    </environment>


A note on Plone 4.0 vs Plone 4.1
--------------------------------

For the 4.0-lastest series, you probably need to pin z3c.form to 2.0.0 -
otherwise a version conflict for zope.schema might occur during buildout::

 Error: There is a version conflict.
 We already have: zope.schema 3.5.4
 but z3c.form 2.4.3 requires 'zope.schema>=3.6.0'.
	
If you don't already have a versions section in your buildout, add::

    [buildout]
    ...
    versions = versions

and::

    [versions]
    z3c.form=2.0.0



Versions
========

The first version of this tool featured a manually written BrowserView. During
the Plone-Conference 2009 sprint, a second version that uses z3c form was
written. This is the version visible by default via the "Lingua Tools" tab. The
original version is still accessible under @@linguatools-old.



Documentation
=============

Please also see test/lttest.txt for a doctest that guides you through the basic
functionalities.
