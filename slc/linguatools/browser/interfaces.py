from zope import interface, schema

from z3c.form import button

class INamingSchema(interface.Interface):
    """ Base Schema for the edit form. It is dynamically extended by plugins """
    text = schema.Text(
            title=u"Text",
            description= \
                u"Type some text. This text will then be written on all translations as Title, as Description"
                " or as a translation of a message id, depending on your further choices in this form.",
            required=True
            )

    po_domain = schema.TextLine(
            title=u"PO Domain",
            description= \
                u"Give a po file domain here, if you have typed a message id in the field above. Then its translation "
                "will be written. If you leave the domain empty or state a nonexisting one, the text above will be written as-is.",
            default=u"plone",
            required=False
            )

    set_title = button.Button(title=u'Set text as Title')
    set_description = button.Button(title=u'Set text as Description')

class IObjectHandlingSchema(interface.Interface):
    """ object handling """

    old_id = schema.Choice(
            title=u"Object to rename",
            description= \
                u"Choose an object to rename. The drop-down displays the available objects with title " \
                u"and id in bracktets.",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_ids"
            )

    new_id = schema.TextLine(
            title=u"New id",
            description= \
                u"Enter the id (short name) the object should receive.",
            required=False
            )
    

    id_to_delete = schema.Choice(
            title=u"Object to delete",
            description= \
                u"Select an object that should be deleted in all languages.",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_ids"
            )

    id_to_move = schema.Choice(
            title=u"Object to move",
            description= \
                u"Choose an object to move.",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_ids"
            )

    target_path = schema.TextLine(
        title=u"Target path",
        description=u"Enter either an absolute path or a path relative to the current location. " \
            u"Examples: '/en/path/to/folder' (absolute); 'subfolder/from/here' or '../' (relative)",
        required=False
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
            description= \
                u"Select a portlet manager. It is used to determine where to block/unblock portlets on, or which "
                u"portlets should be propagated. Leave unselected to do the action for all portlet slots.",
            required=False,
            vocabulary="slc.linguatools.vocabularies.portletmanagers"
            )


class ISubtyperSchema(interface.Interface):
    """ Subtyper Schema for the edit form. """

    add_subtype = button.Button(title=u'Add Subtype')
    remove_subtype = button.Button(title=u'Remove Subtype')

    subtype = schema.Choice(
            title=u"Available Subtypes",
            description= \
                u"Use this to subtype the object and its translations.",
            required=False,
            vocabulary="slc.linguatools.vocabularies.subtypes"
            )


class IReindexSchema(interface.Interface):
    """ Schema for the Reindex All form. """
    reindex_all = button.Button(title=u'Reindex all')


class IPublishSchema(interface.Interface):
    """ Schema for the Publish All form. """
    publish_all = button.Button(title=u'Publish all')


class IDuplicaterSchema(interface.Interface):
    """ Schema for object duplication"""
    translate_this = button.Button(title=u'Translate this')


    attributes_to_copy = schema.List(title=u'Attributes to copy',
                            description=\
                                u'Select one or more attributes to have their values copied over to the translations',
                            default=list(),
                            required=False,
                            value_type=schema.Choice(
                                vocabulary="slc.linguatools.vocabularies.translatable_fields",
                            )
            )

    translation_exists = schema.Bool(
            title=u"Translation exists",
            description=u"Tick this box if a translation alreay exits and you just want to propagate " \
                u"attributes or Collection criteria",
            required=False,
            )

class IPropertySchema(interface.Interface):
    """ Schema for setting and removing properties """

    property_id = schema.TextLine(
        title=u"Property id",
        description=u"Enter a property id",
        required=False
        )

    property_type = schema.Choice(
            title=u"Property type",
            description= \
                u"Select the correct property type",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_property_types"
            )

    property_value = schema.TextLine(
        title=u"Property value",
        description=u"Enter a value fot the property",
        required=False
        )

    property_to_delete = schema.Choice(
            title=u"Property to delete",
            description= \
                u"Select a property to delete",
            required=False,
            vocabulary="slc.linguatools.vocabularies.available_property_ids"
            )

    set_property = button.Button(title=u'Set property')
    delete_property = button.Button(title=u'Delete property')
