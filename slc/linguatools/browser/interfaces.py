from zope import interface, schema

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
                "Rename an object with old id in this folder to the new id.",
            required=False
            )
