import logging
import Acquisition

import zope.component

from plone.portlets.interfaces import IPortletManager, ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY

from plone.app.portlets.utils import assignment_mapping_from_key
from zope.event import notify
from zope.app.container.contained import notifyContainerModified
from zope.lifecycleevent import ObjectCopiedEvent
from zope.app.container.contained import ObjectMovedEvent

from Products.CMFCore.utils import getToolByName
from zope.app.publisher.interfaces.browser import IBrowserMenu

try:
    from p4a.subtyper.interfaces import ISubtyper
except ImportError:
    ISubtyper = None

log = logging.getLogger('slc.linguatools.browser.utils.py')

def exec_for_all_langs(context, method, *args, **kw):
    """ helper method. Takes a method and executes it on all language versions of context """
    info = []
    warnings = []
    errors = []
    changed_languages = []
    skipped_languages = []

    # Need to be mindful of a potential subsite!
    # XXX: this needs to be moved into the subsite plugin!
    # if getSubsiteRoot is not None:
    #     self.portal_path = getSubsiteRoot(self.context)
    langs = context.portal_languages.getSupportedLanguages()

    context_path = context.getPhysicalPath()
    portal_path = context.portal_url.getPortalPath()
    dynamic_path = portal_path + '/%s/' + \
                "/".join(context_path[len(portal_path)+1:])
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
                skipped_languages.append(lang)
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

    info.append('Executed for the following languages: %s' \
                % ' '.join(changed_languages))

    warnings.append('No candidates for the following languages: %s' \
                % ' '.join(skipped_languages))

    return info, warnings, errors


def block_portlets(ob, *args, **kw):
    """ Block the Portlets on a given context, manager, and Category """
    manager = kw['manager']
    blockstatus = kw['blockstatus']
    portletManager = zope.component.getUtility(IPortletManager, name=manager)
    assignable = zope.component.getMultiAdapter(
                            (ob, portletManager,), 
                            ILocalPortletAssignmentManager
                            )
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, blockstatus)


def get_portlet_manager_names():
    names = [x[0] for x in zope.component.getUtilitiesFor(IPortletManager)]
    # filter out dashboard stuff
    names = [x for x in names if not x.startswith('plone.dashboard')]
    return names


def propagate_portlets(ob, *args, **kw):
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


def renamer(ob, *args, **kw):
    """ rename one object within context from oldid to newid """
    oldid = kw['oldid']
    newid = kw['newid']
    if oldid in ob.objectIds():
        ob.manage_renameObjects([oldid], [newid])


def can_subtype():
    return not ISubtyper is None

def add_subtype(ob, *args, **kw):
    """ sets ob to given subtype """
    subtype = kw['subtype']
    subtyperUtil = zope.component.getUtility(ISubtyper)
    if subtyperUtil.existing_type(ob) is None:
        subtyperUtil.change_type(ob, subtype)
        ob.reindexObject()


def remove_subtype(ob, *args, **kw):
    subtyperUtil = zope.component.getUtility(ISubtyper)
    if subtyperUtil.existing_type(ob) is not None:
        subtyperUtil.remove_type(ob)
        ob.reindexObject()


def publish(ob, *args, **kw):
    """ Publishes the object's workflow state
    """
    res = []
    portal_workflow = getToolByName(ob, 'portal_workflow')
    try:
        portal_workflow.doActionFor(ob, 'publish')
        res.append("OK Published %s" % "/".join(ob.getPhysicalPath()))
    except Exception, e:
        res.append("ERR publishing %s: %s" % ("/".join(ob.getPhysicalPath()), str(e) ))
    return res



def cut_and_paste(context, sourcepath, targetpath, id):
    """ Uses OFS to cut and paste an object.
        Sourecpath must refer to the folder which contains the object to move
        id must be a string containing the id of the object to move
        targetpath must be the folder to move to
        both paths must contain one single %s to place the language
    """
    info = list()
    warnings = list()
    errors = list()
    if '%s' not in sourcepath:
        errors.append(u"Wrong source path - does not contain %s")
    if '%s' not in targetpath:
        errors.append(u"Wrong target path - does not contain %s")

    if not errors:
        langs = context.portal_languages.getSupportedLanguages()
        for lang in langs:

            spath = sourcepath%lang
            source = context.restrictedTraverse(spath, None)
            if source is None:
                warnings.append(u"  # Break, source not found for language %s" %lang)
                continue
            spathtest = "/".join(source.getPhysicalPath())
            if spath != spathtest:
                warnings.append(u"  # Break, requested path not sourcepath (%s != %s)" % (spath,spathtest))
                continue

            tpath = targetpath%lang
            target = context.restrictedTraverse(tpath, None)
            if target is None:
                warnings.append(u"  # Break, target is none")
                continue
            tpathtest = "/".join(target.getPhysicalPath())
            if tpath != tpathtest:
                warnings.append(u"  # Break, requested path not targetpath (%s != %s)" % (tpath,tpathtest))
                continue

            ob = getattr(source, id, None)
            ob = Acquisition.aq_base(ob)
            if ob is None:
                warnings.append(u"  # Break, no object found at %s/%s"%(spath, id))
                continue
            source._delObject(id, suppress_events=True)
            target._setObject(id, ob, set_owner=0, suppress_events=True)
            ob = target._getOb(id)

            notify(ObjectMovedEvent(ob, source, id, target, id))
            notifyContainerModified(source)
            if Acquisition.aq_base(source) is not Acquisition.aq_base(target):
                notifyContainerModified(target)
            ob._postCopy(target, op=1)

            info.append(u"Cut & Paste successful for language %s" %lang)

    return (info, warnings, errors)


def get_available_subtypes(context):
    """ Returns the subtypes available in this context
    """
    request = context.request
    subtypes_menu = zope.component.queryUtility(IBrowserMenu, 'subtypes')
    if subtypes_menu:
        return subtypes_menu._get_menus(context, request)

