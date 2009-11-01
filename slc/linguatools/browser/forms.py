import interfaces
import logging
import Acquisition

from z3c.form import form, field, button

from plone.z3cform.fieldsets import extensible

from Products.CMFCore.utils import getToolByName
from zope.app.pagetemplate import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

from z3c.form import form, field, button, group

# portlet imports
from zope import component
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletManager, ILocalPortletAssignmentManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.Translatable import ITranslatable
from Products.CMFPlone import PloneMessageFactory as _


log = logging.getLogger('slc.linguatools.browser.form.py')


class FormMixin(extensible.ExtensibleForm):
    """ Provide some methods which can be used by all plugins """

    template = ViewPageTemplateFile('templates/form.pt')

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

    def widgets_and_actions(self):
        ls = []
        ls += [(w, 'widget') for w in self.widgets.values()]
        ls += [(a, 'action') for a in self.actions.values()]
        return ls


class NamingForm(FormMixin, form.Form):
    """ """
    label = u"Naming"
    ignoreContext = True
    fields = field.Fields(interfaces.INamingSchema).select(
                                                'title', 'id',
                                                'title_from_po',
                                                'description_from_po',
                                                )
    # field = [zope.schema.Int(__name__='id', titile)]

    buttons = button.Buttons(interfaces.INamingSchema).select(
                                                'set_title',
                                                'set_id',
                                                'set_title_form_po',
                                                'set_description_form_po',
                                                )

    @button.handler(interfaces.INamingSchema['set_title'])
    def set_title(self, action):
        print 'successfully applied'
        data,error = self.extractData()
        print data

    @button.handler(interfaces.INamingSchema['set_id'])
    def set_id(self, action):
        self.request.response.redirect('index.html')

    @button.handler(interfaces.INamingSchema['set_title_form_po'])
    def set_title_form_po(self, action):
        self.request.response.redirect('index.html')

    @button.handler(interfaces.INamingSchema['set_description_form_po'])
    def set_description_form_po(self, action):
        self.request.response.redirect('index.html')

    def widgets_and_actions(self):
        ls = [(self.widgets.get('title'), 'widget')]
        ls.append((self.actions.get('set_title'), 'action'))

        ls.append((self.widgets.get('id'), 'widget'))
        ls.append((self.actions.get('set_id'), 'action'))

        ls.append((self.widgets.get('title_from_po'), 'widget'))
        ls.append((self.actions.get('set_title_form_po'), 'action'))

        ls.append((self.widgets.get('description_from_po'), 'widget'))
        ls.append((self.actions.get('set_description_form_po'), 'action'))
        return ls
        


class RenamingForm(FormMixin, form.Form):
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

    def renamer(self, oldid, newid):
        """ rename one object within context from oldid to newid """
        def _setter(ob, *args, **kw):
            oldid = kw['oldid']
            newid = kw['newid']
            if oldid in ob.objectIds():
                ob.manage_renameObjects([oldid], [newid])
        return self._forAllLangs(_setter, oldid=oldid, newid=newid)


    @button.handler(interfaces.IObjectHandlingSchema['rename'])
    def rename(self, action):
        status = IStatusMessage(self.request)
        data, error = self.extractData()
        old_id = data.get('old_id', '').encode('utf-8')
        new_id = data.get('new_id', '').encode('utf-8')

        changes_made = self.renamer(old_id, new_id)
        self.request.response.redirect(self.context.REQUEST.get('URL'))



class PortletForm(FormMixin, form.Form):
    """ """
    label = u"Portlets"
    ignoreContext = True
    fields = field.Fields(interfaces.IPortletSchema).select(
                                                'portlet_manager',
                                                'blockstatus',
                                                )

    buttons = button.Buttons(interfaces.IPortletSchema).select(
                                                'propagate_portlets',
                                                'block_portlets'
                                                )

    def blockPortlets(self, manager, blockstatus):
        """ Block the Portlets on a given context, manager, and Category """
        def _setter(ob, *args, **kw):
            manager = kw['manager']
            blockstatus = kw['blockstatus']
            portletManager = component.getUtility(IPortletManager, name=manager)
            assignable = component.getMultiAdapter((ob, portletManager,), ILocalPortletAssignmentManager)
            assignable.setBlacklistStatus(CONTEXT_CATEGORY, blockstatus)
        return self._forAllLangs(_setter, manager=manager, blockstatus=blockstatus)

    def propagatePortlets(self, manager):
        """ propagates the portlet config from context to the language versions """

        context = Acquisition.aq_inner(self.context)
        path = "/".join(context.getPhysicalPath())

        if manager is not None:
            managernames = [manager]
        else:
            managernames = self.getPortletManagerNames()
            
        managers = dict()
        for managername in managernames:
            managers[managername] = assignment_mapping_from_key(context, managername, CONTEXT_CATEGORY, path)

        def _setter(ob, *args, **kw):
            results = []
            canmanagers = kw['managers']

            if ob.getCanonical() == ob:
                return
            if ob.portal_type == 'LinguaLink':
                return
            path = "/".join(ob.getPhysicalPath())

            for canmanagername, canmanager in canmanagers.items():
                manager = assignment_mapping_from_key(ob, canmanagername, CONTEXT_CATEGORY, path)
                for x in list(manager.keys()):
                    del manager[x]
                for x in list(canmanager.keys()):
                    manager[x] = canmanager[x]

        return self._forAllLangs(_setter, managers=managers)

    def getPortletManagerNames(self):
        return [x[0] for x in component.getUtilitiesFor(IPortletManager)]

    @button.handler(interfaces.IPortletSchema['propagate_portlets'])
    def propagate_portlets(self, action):
        status = IStatusMessage(self.request)
        data,error = self.extractData()

        manager = data.get('portlet_manager', None)
        changes_made = self.propagatePortlets(manager)
        
        self.request.response.redirect(self.context.REQUEST.get('URL'))
            
            
    @button.handler(interfaces.IPortletSchema['block_portlets'])
    def block_portlets(self, action):
        status = IStatusMessage(self.request)
        data,error = self.extractData()
        portlet_manager = data.get('portlet_manager', None)
        blockstatus = data.get('blockstatus', False)
        if portlet_manager is not None:
            self.blockPortlets(portlet_manager, blockstatus)
        else:
            status.addStatusMessage(_(u"Please select a portlet manager."), type='warning')

        self.request.response.redirect(self.context.REQUEST.get('URL'))

    

class AddSubtypesForm(FormMixin, form.Form):
    """ """
    label = u"Add Subtypes"
    ignoreContext = True
    fields = field.Fields(interfaces.ISubtyperSchema).select(
                                                'subtypes_list'
                                                )

    buttons = button.Buttons(interfaces.ISubtyperSchema).select(
                                                'add_subtype'
                                                )

    @button.handler(interfaces.ISubtyperSchema['add_subtype'])
    def add_subtype(self, action):
        print 'successfully applied'


class RemoveSubtypesForm(FormMixin, form.Form):
    """ """
    label = u"Remove Subtypes"
    ignoreContext = True 

    buttons = button.Buttons(interfaces.ISubtyperSchema).select(
                                                'remove_subtype'
                                                )

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
