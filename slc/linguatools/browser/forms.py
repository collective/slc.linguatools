import Acquisition
import interfaces
import logging

from plone.app.z3cform.layout import wrap_form
from plone.z3cform.fieldsets import extensible

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

from z3c.form import form, field, button

log = logging.getLogger('slc.linguatools.browser.form.py')


class FormMixin(extensible.ExtensibleForm):
    """ Provide some methods which can be used by all plugins """

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


class BaseForm(FormMixin, form.Form):
    """ This is the main linguatools edit form. It is extended by other
        components dynamically.
    """
    label = u"LinguaTools - do ONE thing for ALL language versions"
    ignoreContext = True


class NamingForm(FormMixin, form.Form):
    """ """
    label = u"Naming"
    ignoreContext = True
    fields = field.Fields(interfaces.IBaseSchema).select(
                                                'title', 'id',
                                                'title_from_po',
                                                'description_from_po',
                                                )
    # field = [zope.schema.Int(__name__='id', titile)]

    buttons = button.Buttons(interfaces.IBaseSchema).select(
                                                'set_title',
                                                'set_id',
                                                'set_title_form_po',
                                                'set_description_form_po',
                                                )

    @button.handler(interfaces.IBaseSchema['set_title'])
    def set_title(self, action):
        print 'successfully applied'

    @button.handler(interfaces.IBaseSchema['set_id'])
    def set_id(self, action):
        self.request.response.redirect('index.html')

    @button.handler(interfaces.IBaseSchema['set_title_form_po'])
    def set_title_form_po(self, action):
        self.request.response.redirect('index.html')

    @button.handler(interfaces.IBaseSchema['set_description_form_po'])
    def set_description_form_po(self, action):
        self.request.response.redirect('index.html')


class ObjectHandlingForm(FormMixin, form.Form):
    """ object handling """
    label=u"Object handling"
    description=u"Delete, rename, cut and paste"
    ignoreContext = True

    fields = field.Fields(interfaces.IObjectHandlingSchema).select(
                                            'old_id',
                                            'new_id',
                                            )

    buttons = button.Buttons(interfaces.IObjectHandlingSchema).select(
                                            'rename',
                                            )

    @button.handler(interfaces.IObjectHandlingSchema['rename'])
    def rename(self, action):
        self.request.response.redirect('index.html')



class PortletForm(FormMixin, form.Form):
    """ """
    label = u"Portlets"
    ignoreContext = True
    fields = field.Fields(interfaces.IPortletSchema).select(
                                                'block',
                                                'portlet_manager'
                                                )

    buttons = button.Buttons(interfaces.IPortletSchema).select(
                                                'propagate_portlets',
                                                'block_portlets'
                                                )

    @button.handler(interfaces.IPortletSchema['propagate_portlets'])
    def propagate_portlets(self, action):
        print 'successfully applied'

    @button.handler(interfaces.IPortletSchema['block_portlets'])
    def block_portlets(self, action):
        self.request.response.redirect('index.html')


class SubtyperForm(FormMixin, form.Form):
    """ """
    label = u"Subtypes"
    ignoreContext = True
    fields = field.Fields(interfaces.ISubtyperSchema).select(
                                                'subtypes_list'
                                                )

    buttons = button.Buttons(interfaces.ISubtyperSchema).select(
                                                'add_subtype',
                                                'remove_subtype'
                                                )

    @button.handler(interfaces.ISubtyperSchema['add_subtype'])
    def add_subtype(self, action):
        print 'successfully applied'

    @button.handler(interfaces.ISubtyperSchema['remove_subtype'])
    def remove_subtype(self, action):
        self.request.response.redirect('index.html')


class ReindexForm(FormMixin, form.Form):
    """ """
    label = u"Reindex"
    description=u"Reindex this object and all its translations."
    buttons = button.Buttons(interfaces.IReindexSchema).select(
                                                'reindex_all'
                                                )

    @button.handler(interfaces.IReindexSchema['reindex_all'])
    def reindex_all(self, action):
        def _setter(ob, *args, **kw):
            ob.reindexObject()
        status = IStatusMessage(self.request)
        status.addStatusMessage(_(
            u"This object and all its translations have been reindexed."
            ), type='info')
        return self._forAllLangs(_setter)


class PublishForm(FormMixin, form.Form):
    """ """
    label = u"Publish"
    description=u"Publish this object and all of its translations."
    buttons = button.Buttons(interfaces.IPublishSchema).select(
                                                'publish_all'
                                                )

    @button.handler(interfaces.IPublishSchema['publish_all'])
    def publish_all(self, action):
        print 'This object and all of its translations have been published.'
        portal_workflow = getToolByName(self.context, 'portal_workflow')
        def _setter(ob, *args, **kw):
            res = []
            try:
                portal_workflow.doActionFor(ob, 'publish')
                res.append("OK Published %s" % "/".join(ob.getPhysicalPath()))
            except Exception, e:
                res.append("ERR publishing %s: %s" % ("/".join(ob.getPhysicalPath()), str(e) ))
            return res
        status = IStatusMessage(self.request)
        status.addStatusMessage(_(
            u"This object and all its translations have been published."
            ), type='info')
        return self._forAllLangs(_setter)
