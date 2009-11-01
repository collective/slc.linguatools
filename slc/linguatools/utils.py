import logging
import Acquisition

import zope.component

from plone.portlets.interfaces import IPortletManager, ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY

from plone.app.portlets.utils import assignment_mapping_from_key

log = logging.getLogger('slc.linguatools.browser.utils.py')

def execForAllLangs(context, method, *args, **kw):
    """ helper method. Takes a method and executes it on all language versions of context """
    changed_languages = []
    errors = []

    # Need to be mindful of a potential subsite!
    # XXX: this needs to be moved into the subsite plugin!
    # if getSubsiteRoot is not None:
    #     self.portal_path = getSubsiteRoot(self.context)

    langs = context.portal_languages.getSupportedLanguages()

    context_path = context.getPhysicalPath()
    dynamic_path = context.portal_path + '/%s/' + \
                "/".join(context_path[len(context.portal_path)+1:])
    if dynamic_path[-1]== "/":
        dynamic_path = dynamic_path[:-1]

    for lang in langs:
        lpath = dynamic_path%lang

        base = context.getTranslation(lang)
        if base is None:
            base = context.restrictedTraverse(lpath, None)
            # make sure that the base found by restrictedTraverse has the same parent
            # as the context!
            if base is None or Acquisition.aq_parent(base)!=Acquisition.aq_parent(context):
                log.info("Break for lang %s, base is none" % lang)
                continue
            else:
                log.warn("Object found at %s which is not linked as a translation of %s"
                        % (lpath, '/'.join(context.getPhysicalPath())))

                errors.append(
                    "Object found at %s which is not linked as a translation of %s"
                        % (lpath, '/'.join(context.getPhysicalPath())))

        kw['lang'] = lang
        method(base, *args, **kw)
        log.info("Executing for language %s" %  lang)
        changed_languages.append(lang)

    return changed_languages, errors


def blockPortlets(context, manager, blockstatus):
    """ Block the Portlets on a given context, manager, and Category """
    def _setter(ob, *args, **kw):
        manager = kw['manager']
        blockstatus = kw['blockstatus']
        portletManager = zope.component.getUtility(IPortletManager, name=manager)
        assignable = zope.component.getMultiAdapter(
                                (ob, portletManager,), 
                                ILocalPortletAssignmentManager
                                )
        assignable.setBlacklistStatus(CONTEXT_CATEGORY, blockstatus)
    return execForAllLangs(context, _setter, manager=manager, blockstatus=blockstatus)


def getPortletManagerNames():
    names = [x[0] for x in zope.component.getUtilitiesFor(IPortletManager)]
    # filter out dashboard stuff
    names = [x for x in names if not x.startswith('plone.dashboard')]
    return names


def propagatePortlets(context, manager):
    """ propagates the portlet config from context to the language versions """

    path = "/".join(context.getPhysicalPath())

    if manager is not None:
        managernames = [manager]
    else:
        managernames = getPortletManagerNames()
        
    managers = dict()
    for managername in managernames:
        managers[managername] = assignment_mapping_from_key(
                                        context, 
                                        managername, 
                                        CONTEXT_CATEGORY, 
                                        path
                                        )

    def _setter(ob, *args, **kw):
        canmanagers = kw['managers']

        if ob.getCanonical() == ob:
            return
        if ob.portal_type == 'LinguaLink':
            return
        path = "/".join(ob.getPhysicalPath())

        for canmanagername, canmanager in canmanagers.items():
            manager = assignment_mapping_from_key(ob, canmanagername, CONTEXT_CATEGORY, path)
            for x in list(manager.keys()):
                del manager[x]
            for x in list(canmanager.keys()):
                manager[x] = canmanager[x]

    return execForAllLangs(context, _setter, managers=managers)


def renamer(ob, *args, **kw):
    """ rename one object within context from oldid to newid """
    oldid = kw['oldid']
    newid = kw['newid']
    if oldid in ob.objectIds():
        ob.manage_renameObjects([oldid], [newid])

