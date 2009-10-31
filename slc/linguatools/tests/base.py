from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import layer
from Products.PloneTestCase.layer import onsetup

SiteLayer = layer.PloneSite

class SLCSLinguatoolsLayer(SiteLayer):
    @classmethod
    def setUp(cls):
        """Set up additional products and ZCML required to test this product.
        """
        #ztc.installProduct('RichDocument')
        ztc.installProduct('LinguaPlone')
        ztc.installPackage('slc.linguatools')
        ptc.setupPloneSite(products=[
            'LinguaPlone',
            'slc.linguatools',
            'Products.RichDocument'
            ])

        # Load the ZCML configuration for this package and its dependencies

        fiveconfigure.debug_mode = True
        import slc.linguatools
        zcml.load_config('configure.zcml', slc.linguatools)
        fiveconfigure.debug_mode = False

        SiteLayer.setUp()

# The order here is important: We first call the deferred function and then
# let PloneTestCase install it during Plone site setup

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
    layer = SLCSLinguatoolsLayer

class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
    layer = SLCSLinguatoolsLayer
