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
    old_id = schema.TextLine(
            title=u"Current id",
            description= \
                u"Enter the id (short name) the object currently has.",
            required=False
            )

    new_id = schema.TextLine(
            title=u"New id",
            description= \
                u"Enter the id (short name) the object should receive.",
            required=False
            )
    
    id_to_delete = schema.TextLine(
            title=u"Delete by id",
            description= \
                u"Delete an object by id.",
            required=False
            )
            
    
    source_path = schema.TextLine(
        title=u"Source path",
        description=u"Must contain %s to denote the language",
        required=False
        )

    target_path = schema.TextLine(
        title=u"Target path",
        description=u"Must contain %s to denote the language",
        required=False
        )

    id_to_move = schema.TextLine(
        title=u"Id",
        description=u"Id of the object you want to move",
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

    subtypes_list = schema.Choice(
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


