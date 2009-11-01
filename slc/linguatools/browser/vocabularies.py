from plone.portlets.interfaces import IPortletManager

from zope import component 
from zope.app.component.hooks import getSite
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

try:
    # XXX temporarily conditional. Should be done in zcml
    from p4a.subtyper.interfaces import ISubtyper
except:
    ISubtyper = None

class SubtypesVocabulary(object):
    """Vocabulary factory for subtypes.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context

        if ISubtyper is not None:
            subtyper = component.getUtility(ISubtyper)
            terms = [SimpleTerm(x.id, x.name) for x in subtyper.possible_types(context)]
        else:
            terms = [SimpleTerm('', 'Subtyper is not installed')]

        return SimpleVocabulary(terms)

SubtypesVocabularyFactory = SubtypesVocabulary()

class PortletManagerVocabulary(object):
    """Vocabulary factory for portlet managers.
    """
    implements(IVocabularyFactory)
        
    def __call__(self, context):
        self.context = context
        # look up all portlet managers, but filter oit dashboard stuff
        names = [x[0] for x in component.getUtilitiesFor(IPortletManager) if not x[0].startswith('plone.dashboard')]
        terms = [SimpleTerm(x, title=x) for x in names]

        return SimpleVocabulary(terms)

PortletManagerVocabularyFactory = PortletManagerVocabulary()
