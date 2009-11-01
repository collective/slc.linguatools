import interfaces
import logging

import Acquisition

from zope.app.pagetemplate import ViewPageTemplateFile

from z3c.form import form, field, button

from plone.z3cform.fieldsets import extensible
from plone.portlets.constants import CONTEXT_CATEGORY

from plone.app.portlets.utils import assignment_mapping_from_key

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

from slc.linguatools import utils

log = logging.getLogger('slc.linguatools.browser.forms.py')

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
                                                'description_from_po'
                                                )
    # field = [zope.schema.Int(__name__='id', titile)]

    buttons = button.Buttons(interfaces.INamingSchema).select(
                                                'set_title',
                                                'set_id',
                                                'set_title_form_po',
                                                'set_description_form_po'
                                                )

    @button.handler(interfaces.INamingSchema['set_title'])
    def set_title(self, action):
        data,error = self.extractData()
        #print data

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

    @button.handler(interfaces.IObjectHandlingSchema['rename'])
    def rename(self, action):
        status = IStatusMessage(self.request)
        context = Acquisition.aq_inner(self.context)
        data, error = self.extractData()
        old_id = data.get('old_id', '').encode('utf-8')
        new_id = data.get('new_id', '').encode('utf-8')
        info, warnings, errors =  utils.exec_for_all_langs(
                                                context, 
                                                utils.renamer, 
                                                oldid=old_id, 
                                                newid=new_id
                                                )

        for msg in info:
            status.addStatusMessage(msg, type='info')
        for msg in warnings:
            status.addStatusMessage(msg, type='warning')
        for msg in errors:
            status.addStatusMessage(msg, type='error')

        self.request.response.redirect(self.context.REQUEST.get('URL'))


class CutAndPasteForm(FormMixin, form.Form):
    """ Cut and paste """
    label = _(u"Cut and paste")
    description = _(u"Uses OFS to cut and paste an object. Sourcepath must "
    "refer to the folder which contains the object to move, id must be a "
    "string containing the id of the object to move, targetpath must be "
    "the folder to move to. Both paths must contain one single %s to place the language")

    ignoreContext = True
    fields = field.Fields(interfaces.IObjectHandlingSchema).select(
                                                'source_path',
                                                'target_path',
                                                'id_to_move'
                                                )

    buttons = button.Buttons(interfaces.IObjectHandlingSchema).select(
                                                'cut_and_paste'
                                                )

    @button.handler(interfaces.IObjectHandlingSchema['cut_and_paste'])
    def cut_and_paste(self, action):
        context = Acquisition.aq_inner(self.context)
        status = IStatusMessage(self.request)
        data, error = self.extractData()
        source_path = data.get('source_path', '').encode('utf-8')
        target_path = data.get('target_path', '').encode('utf-8')
        id_to_move = data.get('id_to_move', '').encode('utf-8')
        
        info, warnings, errors = utils.cut_and_paste(context, source_path, target_path, id_to_move)
        for msg in info:
            status.addStatusMessage(msg, type='info')
        for msg in warnings:
            status.addStatusMessage(msg, type='warning')
        for msg in errors:
            status.addStatusMessage(msg, type='error')
        
        self.request.response.redirect(self.context.REQUEST.get('URL'))

    def widgets_and_actions(self):
        ls = [(self.widgets.get('source_path'), 'widget')]
        ls.append((self.widgets.get('target_path'), 'widget'))
        ls.append((self.widgets.get('id_to_move'), 'widget'))
        ls.append((self.actions.get('cut_and_paste'), 'action'))
        return ls
        

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


    @button.handler(interfaces.IPortletSchema['propagate_portlets'])
    def propagate_portlets(self, action):
        context = Acquisition.aq_inner(self.context)
        status = IStatusMessage(self.request)
        data,error = self.extractData()

        manager = data.get('portlet_manager', None)
        path = "/".join(context.getPhysicalPath())

        if manager is not None:
            managernames = [manager]
        else:
            managernames = utils.get_portlet_manager_names()
            
        managers = dict()
        for managername in managernames:
            managers[managername] = assignment_mapping_from_key(
                                            context, 
                                            managername, 
                                            CONTEXT_CATEGORY, 
                                            path
                                            )

        info, warnings, errors =  utils.exec_for_all_langs(
                                                context, 
                                                utils.propagate_portlets, 
                                                managers=managers
                                                )
        for msg in info:
            status.addStatusMessage(msg, type='info')
        for msg in warnings:
            status.addStatusMessage(msg, type='warning')
        for msg in errors:
            status.addStatusMessage(msg, type='error')

        self.request.response.redirect(self.context.REQUEST.get('URL'))
            
            
    @button.handler(interfaces.IPortletSchema['block_portlets'])
    def block_portlets(self, action):
        status = IStatusMessage(self.request)
        context = Acquisition.aq_inner(self.context)
        data,error = self.extractData()
        portlet_manager = data.get('portlet_manager', None)
        blockstatus = data.get('blockstatus', False)
        if portlet_manager is not None:
            info, warnings, errors =  utils.exec_for_all_langs(
                                                    context,
                                                    utils.blockPortlets, 
                                                    manager=portlet_manager, 
                                                    blockstatus=blockstatus
                                                    )

            for msg in info:
                status.addStatusMessage(msg, type='info')
            for msg in warnings:
                status.addStatusMessage(msg, type='warning')
            for msg in errors:
                status.addStatusMessage(msg, type='error')

        else:
            status.addStatusMessage(_(u"Please select a portlet manager."), type='warning')

        self.request.response.redirect(self.context.REQUEST.get('URL'))

    
class SubtypesForm(FormMixin, form.Form):
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
        """ sets ob to given subtype """
        status = IStatusMessage(self.request)
        context = Acquisition.aq_inner(self.context)
        data,error = self.extractData()
        subtype = data.get('subtype')
        if not utils.can_subtype():
            return

        info, warnings, errors =  utils.exec_for_all_langs(
                                                context,
                                                utils.add_subtype, 
                                                subtype=subtype,
                                                )

        for msg in info:
            status.addStatusMessage(msg, type='info')
        for msg in warnings:
            status.addStatusMessage(msg, type='warning')
        for msg in errors:
            status.addStatusMessage(msg, type='error')
            
        self.request.response.redirect(self.context.REQUEST.get('URL'))


    @button.handler(interfaces.ISubtyperSchema['remove_subtype'])
    def remove_subtype(self, action):
        """ sets ob to given subtype """
        context = Acquisition.aq_inner(self.context)
        if not utils.can_subtype():
            return

        info, warnings, errors =  utils.exec_for_all_langs(
                                                context,
                                                utils.remove_subtype, 
                                                )

        for msg in info:
            status.addStatusMessage(msg, type='info')
        for msg in warnings:
            status.addStatusMessage(msg, type='warning')
        for msg in errors:
            status.addStatusMessage(msg, type='error')

        self.request.response.redirect(self.context.REQUEST.get('URL'))


class ReindexForm(FormMixin, form.Form):
    """ """
    label = u"Reindex"
    description=u"Reindex this object and all its translations."
    buttons = button.Buttons(interfaces.IReindexSchema).select(
                                                'reindex_all'
                                                )

    @button.handler(interfaces.IReindexSchema['reindex_all'])
    def reindex_all(self, action):
        context = Acquisition.aq_inner(self.context)

        def _setter(ob, *args, **kw):
            ob.reindexObject()

        status = IStatusMessage(self.request)
        status.addStatusMessage(_(
            u"This object and all its translations have been reindexed."
            ), type='info')

        info, warnings, errors =  utils.exec_for_all_langs(context, _setter)


        for msg in info:
            status.addStatusMessage(msg, type='info')
        for msg in warnings:
            status.addStatusMessage(msg, type='warning')
        for msg in errors:
            status.addStatusMessage(msg, type='error')

        self.request.response.redirect(self.context.REQUEST.get('URL'))


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
        context = Acquisition.aq_inner(self.context)

        info, warnings, errors =  utils.exec_for_all_langs(
                                                context,
                                                utils.publish, 
                                                )

        for msg in info:
            status.addStatusMessage(msg, type='info')
        for msg in warnings:
            status.addStatusMessage(msg, type='warning')
        for msg in errors:
            status.addStatusMessage(msg, type='error')

        self.request.response.redirect(self.context.REQUEST.get('URL'))


