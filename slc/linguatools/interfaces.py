from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer


class ILinguaToolsLayer(IDefaultPloneLayer):
    """Marker Interface used by BrowserLayer
    """


class ILinguaToolsForm(Interface):
    """ Marker interface for the linguatool form
    """

    def is_translatable():
        """ Helper method used for the linguatools object tab to see if it
            should render
        """


class ILinguaToolsView(Interface):
    """ A tool to manage lingua specific tasks
        This interface is used for the OLD version!
    """

    def propagatePortlets():
        """ propagates the portlet config from context to the language
        versions
        """

    def deleter(id, guessLanguage=False):
        """ deletes an object with a given id from all language branches """

    def fixOrder(ORDER):
        """Move contents of a folter into order
        make sure the ordering of the folders is correct
        """

    def renamer(oldid, newid):
        """ rename one object within context from oldid to newid
        """

    def setTitle(title):
        """ simply set the title to a given value. Very primitive!
        """

    def setEnableNextPrevious(flag=True):
        """ Enables the Next-Previous Navigation Flag
        """

    def setExcludeFromNav(flag=True):
        """ Sets the Exclude From nav flag
        """

    def setProperty(id, typ, value):
        """ sets a OFS Property on context
        """

    def delProperty(id):
        """ removes a OFS Property on context
        """

    def setTranslatedTitle(label, domain):
        """ sets the title based on the translation availble for title in the
        language
        """

    def setTranslatedDescription(self, label, domain):
        """ sets the description based on the translation availble for title
        in the language
        """

    def createFolder(id, excludeFromNav=True):
        """ creates a folder and all translations in the language branches
        """

    def cutAndPaste(self, sourcepath, id, targetpath):
        """ Uses OFS to cut and paste an object.
            sourecpath must refer to the folder which contains the object
            to move.
            id must be a string containing the id of the object to move.
            targetpath must be the folder to move to.
            both paths must contain one single %s to place the language.
        """

    def addLanguageTool(languages=[]):
        """ adds a language Tool. Sets the given languages, if given ;)
        """

    def subtyper(subtype):
        """ subtypes object to the given subtype
        """

    def reindexer():
        """ reindexes an object in all language branches
        """

    def publisher():
        """ tries to publish all object languages
        """

    def hider():
        """ tries to hide object in all languages
        """

    def translateThis(attrs=[]):
        """ Translates the current object into all languages and transferres
        the given attributes
        """

    def setRichDocAttachments(flag=False):
        """ Sets the attachment flag on a rich document
        """

    def blockPortlets(manager, CAT, status):
        """ Helper. Block the Portlets on a given context, manager, and
        category
        """

    def fixTranslationReference(recursive=False):
        """ fixes translation references to the canonical.
            Assumes that self is always en and canonical
            tries to handle language extensions for files like hwp_xx.swf
        """


class ILinguaCompareView(Interface):
    """
    """
