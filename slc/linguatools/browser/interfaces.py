from zope import interface, schema
from z3c.form import button


class INamingSchema(interface.Interface):
    """ Base Schema for the edit form. It is dynamically extended by plugins
    """
    text = schema.Text(
            title=u"Text",
            description=u"Type some text. This text will then be written on "\
                u"all translations as Title, as Description or as a " \
                u"translation of a message id, depending on your further "\
                u"choices in this form.",
            required=True,
            )

    po_domain = schema.TextLine(
            title=u"PO Domain",
            description=u"Give a po file domain here, if you have typed a "\
                u"message id in the field above. Then its translation will " \
                u"be written. If you leave the domain empty or state a non-" \
                u"existing one, the text above will be written as-is.",
            default=u"plone",
            required=False,
            )

    set_title = button.Button(title=u'Set text as Title')
    set_description = button.Button(title=u'Set text as Description')


class IObjectHandlingSchema(interface.Interface):
    """ object handling """

    old_id = schema.Choice(
            title=u"Object to rename",
            description=u"Choose an object to rename. The drop-down displays "\
                u"the available objects with title and id in bracktets.",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_ids",
            )

    new_id = schema.TextLine(
            title=u"New id",
            description=u"Enter the id (short name) the object should "\
                u"receive.",
            required=False,
            )

    id_to_delete = schema.Choice(
            title=u"Object to delete",
            description=u"Select an object that should be deleted in all "\
                u"languages.",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_ids",
            )

    id_to_move = schema.Choice(
            title=u"Object to move",
            description=u"Choose an object to move.",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_ids",
            )

    target_path = schema.TextLine(
        title=u"Target path",
        description=u"Enter either an absolute path or a path relative to "\
            u"the current location. Examples: '/en/path/to/folder' " \
            u"(absolute); 'subfolder/from/here' or '../' (relative)",
        required=False,
        )

    rename = button.Button(title=u'Rename')
    delete = button.Button(title=u'Delete')
    cut_and_paste = button.Button(title=u'Cut and paste')


class IPortletSchema(interface.Interface):
    """ Portlet Schema for the edit form. """
    propagate_portlets = button.Button(title=u'Propagate Portlets')

    block_portlets = button.Button(title=u'Block Portlets')

    blockstatus = schema.Bool(
            title=u"Check to block",
            description=u"",
            required=False)

    portlet_manager = schema.Choice(
            title=u"Portlet manager",
            description=u"Select a portlet manager. It is used to determine "\
                u"where to block/unblock portlets on, or which portlets "\
                u"should be propagated. Leave unselected to do the action "\
                u"for all portlet slots.",
            required=False,
            vocabulary="slc.linguatools.vocabularies.portletmanagers",
            )


class ISubtyperSchema(interface.Interface):
    """ Subtyper Schema for the edit form. """

    add_subtype = button.Button(title=u'Add Subtype')
    remove_subtype = button.Button(title=u'Remove Subtype')

    subtype = schema.Choice(
            title=u"Available Subtypes",
            description=u"Use this to subtype the object and its "\
                u"translations.",
            required=False,
            vocabulary="slc.linguatools.vocabularies.subtypes",
            )


class IReindexSchema(interface.Interface):
    """ Schema for the Reindex All form. """
    reindex_all = button.Button(title=u'Reindex all')


class IWorkflowSchema(interface.Interface):
    """ Schema for the Publish All form. """
    do_action = button.Button(title=u'Perform workflow change')

    transition = schema.Choice(
            title=u"Available actions",
            description=u"Use this form to change the workflow of the " \
                u"current object and all translations.",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_wf_transitions",
            )


class IDuplicaterSchema(interface.Interface):
    """ Schema for object duplication"""
    translate_this = button.Button(title=u'Translate this')

    attributes_to_copy = schema.List(title=u'Attributes to copy',
            description=u'Select one or more attributes to have their values '\
                u'copied over to the translations',
            default=list(),
            required=False,
            value_type=schema.Choice(
                vocabulary="slc.linguatools.vocabularies.translatable_fields",
                ),
            )

    target_languages = schema.List(title=u'Manual language selection',
            description=u'Select the languages to which you want to make a '\
            u'copy of the canonical object. Leave blank to select all '\
            u'available languages.',
            default=list(),
            required=False,
            value_type=schema.Choice(
                vocabulary="slc.linguatools.vocabularies.supported_languages",
                ),
            )

    use_parent_languages = schema.Bool(title=u"Use parent folder's languages",
            description=u'Select "yes" to copy the object to all languages in'\
            u' which the folder that contains the canonical object is '\
            u'available. This setting takes precedence over the manual '\
            u'selection above.',
            required=False,
            )

    translation_exists = schema.Bool(
            title=u"Translation exists",
            description=u"Answer yes if a translation alreay exits and "\
                u"you just want to propagate attributes or Collection "\
                u"criteria.",
            required=False,
            )


class IPropertySchema(interface.Interface):
    """ Schema for setting and removing properties """

    property_id = schema.TextLine(
        title=u"Property id",
        description=u"Enter a property id",
        required=False,
        )

    property_type = schema.Choice(
            title=u"Property type",
            description=u"Select the correct property type",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_property_types",
            )

    property_value = schema.TextLine(
        title=u"Property value",
        description=u"Enter a value for the property",
        required=False,
        )

    property_to_delete = schema.Choice(
            title=u"Property to delete",
            description=u"Select a property to delete",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_property_ids",
            )

    set_property = button.Button(title=u'Set property')
    delete_property = button.Button(title=u'Delete property')


class IMarkerInterfacesSchema(interface.Interface):
    """ Schema for the Publish All form. """
    remove_interface = button.Button(title=u'Remove selected interface')
    add_interface = button.Button(title=u'Add selected interface')

    interface_to_add = schema.Choice(
            title=u"Available interfaces",
            description=u"Select a marker interface to add to all " \
                u"translations",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_interfaces",
            )

    interface_to_remove = schema.Choice(
            title=u"Provided interfaces",
            description=u"Select a marker interface to remove from all " \
                u"translations",
            required=False,
            vocabulary="slc.linguatools.vocabularies.provided_interfaces",
            )
