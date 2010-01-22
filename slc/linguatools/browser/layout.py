import os
import plone.z3cform

from slc.linguatools.browser.linguatools_view import LinguaToolsView

linguatools_layout = plone.z3cform.templates.ZopeTwoFormTemplateFactory(
    os.path.join(os.path.dirname(__file__), 'templates/layout.pt'),
    form=LinguaToolsView)
