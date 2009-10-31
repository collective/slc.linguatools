import logging
from Acquisition import aq_inner

import zope.interface
from zope.annotation import IAttributeAnnotatable
from plone.z3cform.layout import FormWrapper

import interfaces
import forms

log = logging.getLogger('slc.linguatools.browser.linguatools.py')

class Base(object):
    """ Base class to store data - something we actually don't do (Dummy) """
    zope.interface.implements(interfaces.IBaseSchema, IAttributeAnnotatable)
    title = u""

class LinguaToolsView(FormWrapper):
    
    forms = [forms.BaseForm, forms.NamingForm]

    def __init__(self, context, request):
        super(LinguaToolsView, self).__init__(context, request)
        self.form_instance = self.form(aq_inner(self.context), self.request)
        self.form_instance.__name__ = self.__name__

    def render_form(self):
        """This method returns the rendered z3c.form form.

        Override this method if you need to pass a different context
        to your form, or if you need to render a number of forms.
        """
        return self.form_instance()

