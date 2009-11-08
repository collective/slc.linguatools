import logging
from Acquisition import aq_inner
from plone.z3cform.layout import FormWrapper
import forms

log = logging.getLogger('slc.linguatools.browser.linguatools.py')

class LinguaToolsView(FormWrapper):

    id = u'linguatools'
    form = None # override this with a form class.
    forms = [
            forms.NamingForm,
            forms.PortletForm,
            forms.RenamingForm,
            forms.CutAndPasteForm,
            forms.DeleterForm,
            forms.ReindexForm,
            forms.PublishForm,
            forms.SubtypesForm,
            forms.PropertyForm,
            forms.DuplicaterForm,
            ]

    def __init__(self, context, request):
        super(LinguaToolsView, self).__init__(context, request)
        self.form_instances = \
            [form(aq_inner(self.context), self.request) for form in self.forms]

    def render_form(self):
        """This method combines the individual forms and renders them.
        """
        return ''.join([fi() for fi in self.form_instances])

    def label(self):
        """ """
        return  u"LinguaTools - do ONE thing for ALL language versions"

