from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import layer
from Products.PloneTestCase.layer import onsetup

from plone.browserlayer import utils as browserlayerutils
from slc.linguatools.interfaces import ILinguaToolsLayer

SiteLayer = layer.PloneSite

class SLCLinguatoolsLayer(SiteLayer):
    @classmethod
    def setUp(cls):
        """Set up additional products and ZCML required to test this product.
        """
        #ztc.installProduct('RichDocument')
        ztc.installProduct('LinguaPlone')
        ztc.installProduct('PlacelessTranslationService')
        ztc.installPackage('slc.linguatools')
        ptc.setupPloneSite(products=[
            'LinguaPlone',
            'slc.linguatools',
            'Products.RichDocument',            
            ])

        # Load the ZCML configuration for this package and its dependencies

        # register the Browserlayer from slc.linguatools, so that our schema-extensions
        # using IBrowserLayerAwareExtender work
        browserlayerutils.register_layer(ILinguaToolsLayer, name='slc.linguatools')

        fiveconfigure.debug_mode = True
        import slc.linguatools
        import Products.LinguaPlone
        zcml.load_config('configure.zcml', slc.linguatools)
        import Products.LinguaPlone
        zcml.load_config('configure.zcml', Products.LinguaPlone)
        fiveconfigure.debug_mode = False


        SiteLayer.setUp()

# The order here is important: We first call the deferred function and then
# let PloneTestCase install it during Plone site setup

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
    layer = SLCLinguatoolsLayer

class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
    layer = SLCLinguatoolsLayer
