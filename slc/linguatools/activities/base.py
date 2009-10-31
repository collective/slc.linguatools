from zope import interface, schema
from zope.interface import implements
from zope.component import adapts
from zope.component import provideAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from z3c.form import form, field, button, tests, group

from plone.z3cform.fieldsets import extensible

from slc.linguatools.browser.linguatools_view import Base

class IExtraBehavior(interface.Interface):
    foo = schema.TextLine(title=u"Foo")


class ExtraBehavior(object):
    implements(IExtraBehavior)
    adapts(Base)
    foo = u""

from zope.annotation import factory
ExtraBehavior = factory(ExtraBehavior)

class ExtraBehaviorExtender(extensible.FormExtender):
    adapts(interface.Interface, IDefaultBrowserLayer, interface.Interface)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form
        
    def update(self):
        # Add all fields from an interface
        self.add(IExtraBehavior, prefix="extra")
        
provideAdapter(factory=ExtraBehaviorExtender, name=u"test.extender")


