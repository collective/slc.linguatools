import os
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
from slc.linguatools.browser.linguatools_view import LinguaToolsView


linguatools_layout = ZopeTwoFormTemplateFactory(
    os.path.join(os.path.dirname(__file__), 'templates/layout.pt'),
    form=LinguaToolsView)
