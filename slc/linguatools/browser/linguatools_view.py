import logging
import Acquisition

from plone.app.z3cform.layout import wrap_form
from plone.z3cform.fieldsets import group, extensible

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from z3c.form import form, field, button, group

import zope.interface
from zope.annotation import IAttributeAnnotatable

import interfaces

log = logging.getLogger('slc.linguatools.browser.linguatools.py')

class NamingGroup(group.Group):
    label = u'Naming'
    fields = field.Fields(interfaces.IBaseSchema).select(
                                                'title', 'id',
                                                'title_from_po', 
                                                'description_from_po',
                                                )

class NavigationGroup(group.Group):
    label = u'Navigation'
    fields = field.Fields(interfaces.IBaseSchema).select()


class Base(object):
    """ Base class to store data - something we actually don't do (Dummy) """
    zope.interface.implements(interfaces.IBaseSchema, IAttributeAnnotatable)
    title = u""


class UtilityMixin(object):
    """ Provide some methods which can be used by all plugins """
    
    def _forAllLangs(self, method, *args, **kw):
        """ helper method. Takes a method and executes it on all language versions of context """
        context = Acquisition.aq_inner(self.context)
        status = IStatusMessage(self.request)
        changes_made = False
        for lang in self.langs:
            lpath = self.dynamic_path%lang

            base = context.getTranslation(lang)
            if base is None:
                base = context.restrictedTraverse(lpath, None)
                # make sure that the base found by restrictedTraverse has the same parent
                # as the context!
                if base is None or Acquisition.aq_parent(base)!=Acquisition.aq_parent(context):
                    log.info("Break for lang %s, base is none" % lang)
                    continue
                else:
                    log.warn("Object found at %s which is not linked as a translation of %s"
                            % (lpath, '/'.join(context.getPhysicalPath())))

                    status.addStatusMessage(_(
                        "Object found at %s which is not linked as a translation of %s" 
                            % (lpath, '/'.join(context.getPhysicalPath()))), type='info')

            kw['lang'] = lang
            method(base, *args, **kw)
            log.info("Executing for language %s" %  lang)
            status.addStatusMessage(_(u"Changes made for language %s" % lang), type='info')
            changes_made = True

        return changes_made
    

class BaseForm(extensible.ExtensibleForm, form.Form, UtilityMixin):
    """ This is the main linguatools edit form. It is extended by other 
        components dynamically.
    """
    fields = field.Fields(interfaces.IBaseSchema).select()

    groups = (NamingGroup, NavigationGroup)

    ignoreContext = True 
    label = u"LinguaTools"

    def __init__(self, context, request):
        """ get some useful context for the plugins to work with """
        self.context = context
        self.request = request
        self.portal_url = getToolByName(context, 'portal_url')
        self.portal_path = self.portal_url.getPortalPath()
        self.portal = self.portal_url.getPortalObject()
        
        # Need to be mindful of a potential subsite!
        # XXX: this needs to be moved into the subsite plugin!
        # if getSubsiteRoot is not None:
        #     self.portal_path = getSubsiteRoot(self.context)

        self.portal_languages = getToolByName(context, 'portal_languages')
        self.langs = self.portal_languages.getSupportedLanguages()

        context_path = context.getPhysicalPath()
        self.dynamic_path = self.portal_path + '/%s/' + \
                    "/".join(context_path[len(self.portal_path)+1:])
        if self.dynamic_path[-1]== "/":
            self.dynamic_path = self.dynamic_path[:-1]
    

    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        # This is the main Submit button at the end of the Form. Each Form should have it own button, so this is not really doing something
        # 
        print action 

# Wrap the Plone Edit Form
LinguatoolsView = wrap_form(BaseForm, label=u'Linguatools edit form')

