try:
    from p4a.subtyper.interfaces import ISubtyper
except ImportError:
    ISubtyper = None
try:
    from slc.outdated.interfaces import IAddOnInstalled \
        as ISlcOutdatedInstalled
except ImportError:
    ISlcOutdatedInstalled = None


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    from AccessControl import allow_module
    allow_module('slc.linguatools')
