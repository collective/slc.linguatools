try:
    from p4a.subtyper.interfaces import ISubtyper
except ImportError:
    ISubtyper = None

import os
if bool(os.environ.get('PATCH_TINYMCE_BREADCRUMBS', False)):
    import patch_tinymce_breadcrumbs

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    from AccessControl import allow_module
    allow_module('slc.linguatools')
