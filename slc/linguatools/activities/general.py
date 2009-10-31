from zope import interface, schema
from zope.interface import implements
from zope.component import adapts
from z3c.form import form, field, button, tests, group
from z3c.form.interfaces import INPUT_MODE
from plone.z3cform.fieldsets import group, extensible
from plone.app.z3cform.layout import wrap_form
from zope.annotation import IAttributeAnnotatable

from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from slc.linguatools.browser.linguatools_view import Base

# Extender

from plone.z3cform.fieldsets.interfaces import IFormExtender
from zope.component import adapts, provideAdapter

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