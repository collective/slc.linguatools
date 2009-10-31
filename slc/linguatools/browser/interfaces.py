from zope import interface, schema

from z3c.form import button

class IBaseSchema(interface.Interface):
    """ Base Schema for the edit form. It is dynamically extended by plugins """
    title = schema.TextLine(
            title=u"Set a Title", 
            description= \
                u"Set the given string as title. This is a very "
                "simple action, it sets the same title for all languages.",
            required=False
            )

    id = schema.TextLine(
            title=u"Set the id (shortname)", 
            description= \
                u"Rename an object with old id in this folder to the new id.",
            required=False
            )

    title_from_po = schema.TextLine(
            title=u"Set the id (shortname) from a .po file.", 
            description= \
                u"Set Title or Description on all translations based on the message id of a po file. Specify a message id and a po file domain. The proper translations, if available, will then be set on all translations.",
            required=False
            )

    description_from_po = schema.TextLine(
            title=u"Set the description from a .po file.", 
            description= \
                u"Set Title or Description on all translations based on the message id of a po file. Specify a message id and a po file domain. The proper translations, if available, will then be set on all translations.",
            required=False
            )

    set_title = button.Button(title=u'Set Title')
    set_id = button.Button(title=u'Set the ID')
    set_title_form_po = button.Button(title=u'Set Title')
    set_description_form_po = button.Button(title=u'Set Description')


class IPortletSchema(interface.Interface):
    """ Portlet Schema for the edit form. It is dynamically extended by plugins """
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
