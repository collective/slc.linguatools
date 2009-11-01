from zope import interface, schema

from z3c.form import button

class INamingSchema(interface.Interface):
    """ Base Schema for the edit form. It is dynamically extended by plugins """
    title = schema.TextLine(
            title=u"Set a Title",
            description= \
                u"Set the given string as title. This is a very "
                "simple action, it sets the same title for all languages.",
            required=False
            )

    id = schema.TextLine(
            title=u"Set the id (shortname) [thomasw: does that make sense here?]",
            description= \
                u"Rename an object with old id in this folder to the new id.",
            required=False
            )

    title_from_po = schema.TextLine(
            title=u"Set the Title from a .po file.",
            description= \
                u"Set Title or Description on all translations based on the message id of a po file. Specify a message id and a po file domain. The proper translations, if available, will then be set on all language versions.",
            required=False
            )

    description_from_po = schema.TextLine(
            title=u"Set the description from a .po file.",
            description= \
                u"Set Title or Description on all translations based on the message id of a po file. Specify a message id and a po file domain. The proper translations, if available, will then be set on all language versions.",
            required=False
            )

    set_title = button.Button(title=u'Set Title')
    set_id = button.Button(title=u'Set the ID')
    set_title_form_po = button.Button(title=u'Set Title')
    set_description_form_po = button.Button(title=u'Set Description')



class IObjectHandlingSchema(interface.Interface):
    """ object handling """
    old_id = schema.TextLine(
            title=u"Enter the current id",
            description= \
                u"Rename an object with old id in this folder to the new id.",
            required=False
            )

    new_id = schema.TextLine(
            title=u"Enter the new id",
            description= \
                u"Rename an object with old id in this folder to the new id.",
            required=False
            )

    rename = button.Button(title=u'Rename')
    dummy = button.Button(title=u'tester')


class IPortletSchema(interface.Interface):
    """ Portlet Schema for the edit form. """
    propagate_portlets = button.Button(title=u'Propagate Portlets')

    block_portlets = button.Button(title=u'Block Portlets')

    block = schema.Bool(
            title=u"Check to block",
            description=u"",
            required=False)

    portlet_manager = schema.Choice(
            title=u"Block Portlets",
            description= \
                u"Block or unblock the portlets on the current object. You can select a portlet slot to apply to and whether it should be blocked or unblocked.",
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
