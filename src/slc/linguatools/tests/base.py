from Products.Five import zcml
from Products.Five import fiveconfigure

# import something from LinguaPlone first to avoid circular reference
# see http://dev.plone.org/plone/ticket/10289
# Only seems to affect LinguaPlone 2.2 though
from Products.LinguaPlone.I18NBaseObject import I18NBaseObject
from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import layer
from Products.PloneTestCase.layer import onsetup

from plone.browserlayer import utils as browserlayerutils
from slc.linguatools.interfaces import ILinguaToolsLayer
#from Products.PlacelessTranslationService import make_translation_service,\
# initialize2
#from App.ProductContext import ProductContext
#from Globals import package_home
#import os

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

        # register the Browserlayer from slc.linguatools, so that our
        # schema-extensions using IBrowserLayerAwareExtender work
        browserlayerutils.register_layer(ILinguaToolsLayer,
            name='slc.linguatools')

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

    # def afterSetUp(self):
    #     cp = self.portal.Control_Panel
    #     cp_ts = make_translation_service(cp)
    #     # product_context = ProductContext(cp_ts, self.app,
    #       PlacelessTranslationService)
    #     # initialize2(product_context)
    #
    #     prod = "plone.app.locales"
    #     prod_path = package_home({'__name__' : prod})
    #     cp_ts._load_i18n_dir(os.path.join(prod_path, 'i18n'))
    #
    #     from Products.PlacelessTranslationService.PlacelessTranslationService
    #        import catalogRegistry
    #     print "number of registered MessageCatalogs:", len(catalogRegistry)
