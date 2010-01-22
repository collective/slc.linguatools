from zope.interface import implements

from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from slc.linguatools.interfaces import ILinguaCompareView


class LinguaCompareView(BrowserView):
    implements(ILinguaCompareView)
    template = ViewPageTemplateFile('compare.pt')
    security = ClassSecurityInfo()


    security.declareProtected(View, 'getNameForLanguageCode')

    def getNameForLanguageCode(self, langCode):
        """Returns the name for a language code."""
        lt = getToolByName(self.context, 'portal_languages')
        return lt.getNameForLanguageCode(langCode)

    def getTranslations(self):
        """ Retrieve all the translations of the current context
            XXX: Add doctest here
        """
        return
