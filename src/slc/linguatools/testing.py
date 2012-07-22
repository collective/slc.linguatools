from Products.CMFCore.utils import getToolByName

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from zope.configuration import xmlconfig


class PloneAppDiscussion(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    MANAGER_USER_NAME = 'manager'
    MANAGER_USER_PASSWORD = 'secret'

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import slc.linguatools
        xmlconfig.file('configure.zcml',
                       slc.linguatools,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'slc.linguatools:default')

        # Creates some users
        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser(
            self.MANAGER_USER_NAME,
            self.MANAGER_USER_PASSWORD,
            ['Manager'],
            [],
        )

SLC_LINGUATOOLS_FIXTURE = PloneAppDiscussion()
SLC_LINGUATOOLS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(SLC_LINGUATOOLS_FIXTURE,),
    name="SlcLinguatools:Integration")
SLC_LINGUATOOLS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SLC_LINGUATOOLS_FIXTURE,),
    name="SlcLinguatools:Functional")
