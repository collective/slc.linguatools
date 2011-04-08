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
from slc.linguatools import ISubtyper

log = logging.getLogger('slc.linguatools.browser.forms.py')


class FormMixin(extensible.ExtensibleForm):
    """ Provide some methods which can be used by all plugins """

    template = ViewPageTemplateFile('templates/form.pt')
    # override this in the form class if needed
    display = True

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

    def handle_status(self, status, info, warnings, errors):
        for msg in info:
            status.addStatusMessage(msg, type='info')
        for msg in warnings:
            status.addStatusMessage(msg, type='warning')
        for msg in errors:
            status.addStatusMessage(msg, type='error')

        self.request.response.redirect(self.request.get('URL'))


class NamingForm(FormMixin, form.Form):
    """ """
    label = u"Naming"
    ignoreContext = True
    fields = field.Fields(interfaces.INamingSchema).select(
                                                'text',
                                                'po_domain',
                                                )

    buttons = button.Buttons(interfaces.INamingSchema).select(
                                                'set_title',
                                                'set_description',
                                                )

    @button.handler(interfaces.INamingSchema['set_title'])
    def set_title(self, action):
        status = IStatusMessage(self.request)
        status.addStatusMessage(_(u"Set text as title"), type="info")
        context = Acquisition.aq_inner(self.context)
        data, error = self.extractData()

        info, warnings, errors = utils.exec_for_all_langs(
                                    context,
                                    utils.set_po_title,
                                    text=data.get('text', ''),
                                    po_domain=data.get('po_domain', ''))

        for msg in info:
            status.addStatusMessage(msg, type='info')
        for msg in warnings:
            status.addStatusMessage(msg, type='warning')
        for msg in errors:
            status.addStatusMessage(msg, type='error')

        self.request.response.redirect(self.context.REQUEST.get('URL'))

    @button.handler(interfaces.INamingSchema['set_description'])
    def set_description(self, action):
        status = IStatusMessage(self.request)
        status.addStatusMessage(_(u"Set text as description"), type="info")
        context = Acquisition.aq_inner(self.context)
        data, error = self.extractData()

        info, warnings, errors = utils.exec_for_all_langs(
                                    context,
                                    utils.set_po_description,
                                    text=data.get('text', ''),
                                    po_domain=data.get('po_domain', ''))

        self.handle_status(status, info, warnings, errors)

    def widgets_and_actions(self):
        ls = [(self.widgets.get('text'), 'widget')]
        ls.append((self.widgets.get('po_domain'), 'widget'))
        ls.append((self.actions.get('set_title'), 'action'))
        ls.append((self.actions.get('set_description'), 'action'))
        return ls


class RenamingForm(FormMixin, form.Form):
    """ Renaming """
    label = u"Rename"
    description = u"Rename an object with current id in this folder to the "\
        "new id."
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
        old_id = data.get('old_id', '')
        new_id = data.get('new_id', '')
        status.addStatusMessage(u'Rename from %s to %s.' % (old_id, new_id),
            type="info")
        info, warnings, errors = utils.exec_for_all_langs(
                                                context,
                                                utils.renamer,
                                                oldid=old_id,
                                                newid=new_id,
                                                )

        self.handle_status(status, info, warnings, errors)


class CutAndPasteForm(FormMixin, form.Form):
    """ Cut and paste """
    label = _(u"Cut and paste (move)")
    description = _(u"Cut and paste (move) an object. Select an object from "\
        u"the current folder to move. Enter the path to the target folder " \
        u"where to object should be moved to.")

    ignoreContext = True
    fields = field.Fields(interfaces.IObjectHandlingSchema).select(
                                                'target_path',
                                                'id_to_move',
                                                )

    buttons = button.Buttons(interfaces.IObjectHandlingSchema).select(
                                                'cut_and_paste')

    @button.handler(interfaces.IObjectHandlingSchema['cut_and_paste'])
    def cut_and_paste(self, action):
        context = Acquisition.aq_inner(self.context)
        data, error = self.extractData()
        target_path = data.get('target_path', '')
        id_to_move = data.get('id_to_move', '')
        status = IStatusMessage(self.request)
        status.addStatusMessage(_(u"Move object %s to %s" % (id_to_move,
            target_path)), type="info")

        info, warnings, errors = utils.exec_for_all_langs(
                                                context,
                                                utils.cut_and_paste,
                                                target_path=target_path,
                                                id_to_move=id_to_move,
                                                target_id=id_to_move)
        self.handle_status(status, info, warnings, errors)

    def widgets_and_actions(self):
        ls = list()
        ls.append((self.widgets.get('id_to_move'), 'widget'))
        ls.append((self.widgets.get('target_path'), 'widget'))
        ls.append((self.actions.get('cut_and_paste'), 'action'))
        return ls


class PortletForm(FormMixin, form.Form):
    """ """
    label = u"Portlets"
    description = u"Propagate the portlets set on the current canonical " \
        u"object to all translations, or change the block status"
    ignoreContext = True
    fields = field.Fields(interfaces.IPortletSchema).select(
                                                'portlet_manager',
                                                'blockstatus',
                                                )

    buttons = button.Buttons(interfaces.IPortletSchema).select(
                                                'propagate_portlets',
                                                'block_portlets',
                                                )

    @button.handler(interfaces.IPortletSchema['propagate_portlets'])
    def propagate_portlets(self, action):
        context = Acquisition.aq_inner(self.context)
        status = IStatusMessage(self.request)

        data, error = self.extractData()

        manager = data.get('portlet_manager', None)
        path = "/".join(context.getPhysicalPath())

        if manager is not None:
            managernames = [manager]
        else:
            managernames = utils.get_portlet_manager_names()

        status.addStatusMessage(u'Propagate portlets on %s' % ', '.join(
            managernames), type='info')
        managers = dict()
        for managername in managernames:
            managers[managername] = assignment_mapping_from_key(
                                            context,
                                            managername,
                                            CONTEXT_CATEGORY,
                                            path,
                                            )

        info, warnings, errors = utils.exec_for_all_langs(
                                                context,
                                                utils.propagate_portlets,
                                                managers=managers,
                                                )
        self.handle_status(status, info, warnings, errors)

    @button.handler(interfaces.IPortletSchema['block_portlets'])
    def block_portlets(self, action):
        status = IStatusMessage(self.request)
        context = Acquisition.aq_inner(self.context)
        data, error = self.extractData()
        portlet_manager = data.get('portlet_manager', None)
        blockstatus = data.get('blockstatus', False)

        manager = data.get('portlet_manager', None)
        path = "/".join(context.getPhysicalPath())

        if manager is not None:
            managernames = [manager]
        else:
            managernames = utils.get_portlet_manager_names()

        status.addStatusMessage(u'Set portlet block status on %s' % ', '.join(
            managernames), type='info')
        managers = dict()
        for managername in managernames:
            managers[managername] = assignment_mapping_from_key(
                                            context,
                                            managername,
                                            CONTEXT_CATEGORY,
                                            path,
                                            )

        info, warnings, errors = utils.exec_for_all_langs(
                                                    context,
                                                    utils.block_portlets,
                                                    managers=managers,
                                                    blockstatus=blockstatus,
                                                    )

        self.handle_status(status, info, warnings, errors)

    def widgets_and_actions(self):
        ls = [(self.widgets.get('portlet_manager'), 'widget')]
        ls.append((self.actions.get('propagate_portlets'), 'action'))
        ls.append((self.widgets.get('blockstatus'), 'widget'))
        ls.append((self.actions.get('block_portlets'), 'action'))
        return ls


class SubtypesForm(FormMixin, form.Form):
    """ """
    display = ISubtyper is not None
    label = u"Subtypes"
    ignoreContext = True
    fields = field.Fields(interfaces.ISubtyperSchema).select(
                                                'subtype',
                                                )

    buttons = button.Buttons(interfaces.ISubtyperSchema).select(
                                                'add_subtype',
                                                'remove_subtype',
                                                )

    @button.handler(interfaces.ISubtyperSchema['add_subtype'])
    def add_subtype(self, action):
        """ sets ob to given subtype """
        status = IStatusMessage(self.request)
        context = Acquisition.aq_inner(self.context)
        data, error = self.extractData()
        subtype = data.get('subtype')
        status.addStatusMessage(u'Subtype object to %s' % subtype, type='info')
        info, warnings, errors = utils.exec_for_all_langs(
                                                context,
                                                utils.add_subtype,
                                                subtype=subtype,
                                                )

        self.handle_status(status, info, warnings, errors)

    @button.handler(interfaces.ISubtyperSchema['remove_subtype'])
    def remove_subtype(self, action):
        """ sets ob to given subtype """
        status = IStatusMessage(self.request)
        context = Acquisition.aq_inner(self.context)
        status.addStatusMessage(u'Remove subtype', type='info')

        info, warnings, errors = utils.exec_for_all_langs(
                                                context,
                                                utils.remove_subtype,
                                                )

        self.handle_status(status, info, warnings, errors)


class ReindexForm(FormMixin, form.Form):
    """ """
    label = u"Reindex"
    description = u"Reindex this object and all its translations."
    buttons = button.Buttons(interfaces.IReindexSchema).select(
                                                'reindex_all',
                                                )

    @button.handler(interfaces.IReindexSchema['reindex_all'])
    def reindex_all(self, action):
        context = Acquisition.aq_inner(self.context)

        def _setter(ob, *args, **kw):
            ob.reindexObject()

        status = IStatusMessage(self.request)
        status.addStatusMessage(_(u"Reindex object"), type='info')

        info, warnings, errors = utils.exec_for_all_langs(context, _setter)

        self.handle_status(status, info, warnings, errors)


class WokflowForm(FormMixin, form.Form):
    """ """
    label = u"Workflow"
    description = u"Change the workflow of this object and all of its " \
        "translations."
    ignoreContext = True

    fields = field.Fields(interfaces.IWorkflowSchema).select(
                                                'transition',
                                                )
    buttons = button.Buttons(interfaces.IWorkflowSchema).select(
                                                'do_action',
                                                )

    @button.handler(interfaces.IWorkflowSchema['do_action'])
    def do_action(self, action):
        data, error = self.extractData()
        transition = data.get('transition')
        status = IStatusMessage(self.request)
        status.addStatusMessage(_(u"Perform workflow-action '%s' on this " \
            u"object and all translations" % transition),
            type="info")
        context = Acquisition.aq_inner(self.context)

        info, warnings, errors = utils.exec_for_all_langs(
                                                context,
                                                utils.workflow_action,
                                                transition=transition,
                                                )

        self.handle_status(status, info, warnings, errors)


class DuplicaterForm(FormMixin, form.Form):
    """ Duplicate current object into all languages"""
    label = u"Translate this object"
    description = u"Create a translation of the current object in the "\
            u"selected languages. Collection criteria are copied as well."
    ignoreContext = True

    buttons = button.Buttons(interfaces.IDuplicaterSchema).select(
        'translate_this')
    fields = field.Fields(interfaces.IDuplicaterSchema).select(
                                                'attributes_to_copy',
                                                'target_languages',
                                                'use_parent_languages',
                                                'translation_exists',
                                                )

    @button.handler(interfaces.IDuplicaterSchema['translate_this'])
    def translate_this(self, action):
        status = IStatusMessage(self.request)
        context = Acquisition.aq_inner(self.context)
        data, error = self.extractData()

        attributes_to_copy = data.get('attributes_to_copy', [])
        translation_exists = data.get('translation_exists', False)
        target_languages = data.get('target_languages', [])
        use_parent_languages = data.get('use_parent_languages', False)
        if use_parent_languages:
            parent = Acquisition.aq_parent(context)
            target_languages = parent.getTranslationLanguages()
            msg = u"Translate this object to the parent folder's languages."
        else:
            msg = u"Translate this object to the manually selected languages."

        status.addStatusMessage(msg, type="info")

        info, warnings, errors = utils.translate_this(context,
            attributes_to_copy, translation_exists, target_languages)

        self.handle_status(status, info, warnings, errors)


class DeleterForm(FormMixin, form.Form):
    """ """
    label = u"Deleter"
    ignoreContext = True
    fields = field.Fields(interfaces.IObjectHandlingSchema).select(
                                                'id_to_delete',
                                                )

    buttons = button.Buttons(interfaces.IObjectHandlingSchema).select(
                                                'delete',
                                                )

    @button.handler(interfaces.IObjectHandlingSchema['delete'])
    def delete(self, action):
        """ sets ob to given subtype """
        status = IStatusMessage(self.request)
        context = Acquisition.aq_inner(self.context)
        data, error = self.extractData()
        id_to_delete = data.get('id_to_delete')
        status.addStatusMessage(u'Delete object %s' % id_to_delete,
            type='info')
        info, warnings, errors = utils.exec_for_all_langs(
                                                context,
                                                utils.delete_this,
                                                id_to_delete=id_to_delete,
                                                target_id=id_to_delete,
                                                )

        self.handle_status(status, info, warnings, errors)


class PropertyForm(FormMixin, form.Form):
    """ """
    label = u"Properties"
    ignoreContext = True
    fields = field.Fields(interfaces.IPropertySchema).select(
                                                'property_id',
                                                'property_type',
                                                'property_value',
                                                'property_to_delete',
                                                )

    buttons = button.Buttons(interfaces.IPropertySchema).select(
                                                'set_property',
                                                'delete_property',
                                                )

    @button.handler(interfaces.IPropertySchema['set_property'])
    def set_property(self, action):
        """ sets the given property """
        status = IStatusMessage(self.request)
        context = Acquisition.aq_inner(self.context)
        data, error = self.extractData()
        property_id = data.get('property_id')
        property_value = data.get('property_value')
        if isinstance(property_value, unicode):
            property_value = property_value.encode('utf-8')
        status.addStatusMessage(u'Set property %s' % property_id, type='info')
        info, warnings, errors = utils.exec_for_all_langs(
                                    context,
                                    utils.set_property,
                                    property_id=property_id,
                                    property_type=data.get('property_type'),
                                    property_value=property_value,
                                    )

        self.handle_status(status, info, warnings, errors)

    @button.handler(interfaces.IPropertySchema['delete_property'])
    def delete_property(self, action):
        """ deletes the given property """
        status = IStatusMessage(self.request)
        context = Acquisition.aq_inner(self.context)
        data, error = self.extractData()
        property_id = data.get('property_to_delete')
        status.addStatusMessage(u'Delete property %s' % property_id,
            type='info')
        info, warnings, errors = utils.exec_for_all_langs(
                                                context,
                                                utils.delete_property,
                                                property_id=property_id,
                                                )

        self.handle_status(status, info, warnings, errors)

    def widgets_and_actions(self):
        ls = [(self.widgets.get('property_id'), 'widget')]
        ls.append((self.widgets.get('property_type'), 'widget'))
        ls.append((self.widgets.get('property_value'), 'widget'))
        ls.append((self.actions.get('set_property'), 'action'))
        ls.append((self.widgets.get('property_to_delete'), 'widget'))
        ls.append((self.actions.get('delete_property'), 'action'))
        return ls


class MarkerInterfaceForm(FormMixin, form.Form):
    """ """
    label = u"Marker Interfaces"
    description = u"Set or remove marker interfaces on this object and all " \
        "of its translations."
    ignoreContext = True

    fields = field.Fields(interfaces.IMarkerInterfacesSchema).select(
                                                'interface_to_add',
                                                'interface_to_remove',
                                                )
    buttons = button.Buttons(interfaces.IMarkerInterfacesSchema).select(
                                                'add_interface',
                                                'remove_interface',
                                                )

    @button.handler(interfaces.IMarkerInterfacesSchema['add_interface'])
    def add_interface(self, action):
        data, error = self.extractData()
        interface_to_add = data.get('interface_to_add')
        status = IStatusMessage(self.request)
        status.addStatusMessage(_(u"Add marker interface '%s' on this " \
            u"object and all translations" % interface_to_add),
            type="info")
        context = Acquisition.aq_inner(self.context)

        info, warnings, errors = utils.exec_for_all_langs(
                                    context,
                                    utils.add_interface,
                                    interface_to_add=interface_to_add,
                                    )

        self.handle_status(status, info, warnings, errors)

    @button.handler(interfaces.IMarkerInterfacesSchema['remove_interface'])
    def remove_interface(self, action):
        data, error = self.extractData()
        interface_to_remove = data.get('interface_to_remove')
        status = IStatusMessage(self.request)
        status.addStatusMessage(_(u"Remove marker interface '%s' on this " \
            u"object and all translations" % interface_to_remove),
            type="info")
        context = Acquisition.aq_inner(self.context)

        info, warnings, errors = utils.exec_for_all_langs(
                                    context,
                                    utils.remove_interface,
                                    interface_to_remove=interface_to_remove,
                                    )

        self.handle_status(status, info, warnings, errors)

    def widgets_and_actions(self):
        ls = [(self.widgets.get('interface_to_add'), 'widget')]
        ls.append((self.actions.get('add_interface'), 'action'))
        ls.append((self.widgets.get('interface_to_remove'), 'widget'))
        ls.append((self.actions.get('remove_interface'), 'action'))
        return ls
