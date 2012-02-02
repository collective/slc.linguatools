import logging
import Acquisition

import zope.component

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr
from zope.i18n import translate

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY
from OFS.event import ObjectClonedEvent

from plone.app.portlets.utils import assignment_mapping_from_key
from zope.event import notify
from zope.app.container.contained import notifyContainerModified
from zope.lifecycleevent import ObjectCopiedEvent
from zope.app.container.contained import ObjectMovedEvent
from Products.Five.utilities.interfaces import IMarkerInterfaces
from Products.LinguaPlone.interfaces import ITranslatable

from Products.CMFCore.utils import getToolByName
from zope.app.publisher.interfaces.browser import IBrowserMenu
from Products.Archetypes.interfaces.base import IBaseFolder
try:
    from p4a.subtyper.interfaces import ISubtyper
except ImportError:
    ISubtyper = None

log = logging.getLogger('slc.linguatools.browser.utils.py')


def exec_for_all_langs(context, method, *args, **kw):
    """ helper method. Takes a method and executes it on all language
    versions of context
    """
    info = []
    warnings = []
    errors = []
    changed_languages = []
    skipped_languages = []

    request = context.REQUEST
    portal_url = getToolByName(context, 'portal_url')
    portal_path = portal_url.getPortalPath()
    portal = portal_url.getPortalObject()

    # Need to be mindful of a potential subsite!
    # XXX: this needs to be moved into the subsite plugin!
    # if getSubsiteRoot is not None:
    #     self.portal_path = getSubsiteRoot(self.context)
    supported_langs = context.portal_languages.getSupportedLanguages()
    canonical = context.getCanonical()
    canonical_lang = canonical.Language()
    langs = [x for x in supported_langs if x != canonical_lang]
    langs.append(canonical_lang)

    context_path = context.getPhysicalPath()
    dynamic_path = portal_path + '/%s/' + \
                "/".join(context_path[len(portal_path) + 1:])
    portal_path = context.portal_url.getPortalPath()
    if dynamic_path[-1] == "/":
        dynamic_path = dynamic_path[:-1]

    # if the special keyword 'target_id' is passed, try to retrieve an object
    # of that name from the canonical and save it to the keyword argument.
    # This object can the used in the method for getTranslation
    if kw.get('target_id', None):
        target_object = getattr(canonical, kw.get('target_id'), None)
        if target_object:
            kw['target_object'] = target_object

    # add the portal_path to the keywords
    kw['portal_path'] = portal_path

    for lang in langs:
        lpath = dynamic_path % lang

        base = context.getTranslation(lang)
        if base is None:
            base = context.restrictedTraverse(lpath, None)
            # make sure that the base found by restrictedTraverse
            # has the same parent as the context!
            if base is None or \
                Acquisition.aq_parent(base) != Acquisition.aq_parent(context):
                log.info("Break for lang %s, base is none" % lang)
                skipped_languages.append(lang)
                continue
            else:
                log.warn("Object found at %s which is not linked as a " \
                    "translation of %s"
                        % (lpath, '/'.join(context.getPhysicalPath())))

                errors.append(
                    "Object found at %s which is not linked as a " \
                        "translation of %s"
                        % (lpath, '/'.join(context.getPhysicalPath())))

        kw['lang'] = lang
        err = method(base, *args, **kw)
        log.info("Executing for language %s" % lang)
        if err:
            errors.extend(err)
        else:
            changed_languages.append(lang)

    if changed_languages:
        info.append('Executed for the following languages: %s' \
                % ' '.join(changed_languages))

    if skipped_languages:
        warnings.append('No candidates for the following languages: %s' \
                % ' '.join(skipped_languages))

    return info, warnings, errors


def block_portlets(ob, *args, **kw):
    """ Block the Portlets on a given context, manager, and Category """
    canmanagers = kw['managers']
    blockstatus = kw['blockstatus']
    for canmanagername, canmanager in canmanagers.items():
        portletManager = zope.component.getUtility(IPortletManager,
            name=canmanagername)
        assignable = zope.component.getMultiAdapter(
                                (ob, portletManager, ),
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
        manager = assignment_mapping_from_key(ob, canmanagername,
            CONTEXT_CATEGORY, path)
        for x in list(manager.keys()):
            del manager[x]
        for x in list(canmanager.keys()):
            manager[x] = canmanager[x]


def renamer(ob, *args, **kw):
    """ rename one object within context from oldid to newid """
    err = list()
    oldid = kw['oldid']
    newid = kw['newid']
    if not oldid:
        err.append(u'Current id must not be empty')
    else:
        oldid = oldid.encode('utf-8')
    if not newid:
        err.append(u'New id must not be empty')
    else:
        newid = newid.encode('utf-8')
    if not err:
        if oldid in ob.objectIds():
            ob.manage_renameObjects([oldid], [newid])
        else:
            err.append('No object with id %s found in folder %s' \
                % (oldid, '/'.join(ob.getPhysicalPath())))
    return err


def set_po_title(ob, *args, **kw):
    """ simply set the title to a given value. Very primitive! """
    err = list()
    text = kw['text']
    lang = kw['lang']
    po_domain = kw['po_domain']
    if text == '':
        err.append(u"It is not allowed to set an empty title.")
    else:
        if po_domain != '':
            text = translate(target_language=lang, msgid=text, default=text,
                context=ob, domain=po_domain)
        ob.setTitle(text)
    return err


def set_po_description(ob, *args, **kw):
    """ simply set the title to a given value. Very primitive! """
    text = kw['text']
    po_domain = kw['po_domain']
    lang = kw['lang']
    if po_domain != '':
        text = translate(target_language=lang, msgid=text, default=text,
            context=ob, domain=po_domain)
    ob.setDescription(text)


def can_subtype():
    return not ISubtyper is None


def add_subtype(ob, *args, **kw):
    """ sets ob to given subtype """
    err = list()
    subtype = kw['subtype']
    if not can_subtype():
        err.append('Subtyper is not installed')
    if not subtype:
        err.append('Please select a subtype')
    if not err:
        subtyperUtil = zope.component.getUtility(ISubtyper)
        if subtyperUtil.existing_type(ob) is None:
            subtyperUtil.change_type(ob, subtype)
            ob.reindexObject()
        else:
            err.append(u'The object at %s is already subtyped to %s' \
                % ('/'.join(ob.getPhysicalPath()),
                    subtyperUtil.existing_type(ob).descriptor.title))
    return err


def remove_subtype(ob, *args, **kw):
    err = list()
    if not can_subtype():
        err.append('Subtyper is not installed')
    else:
        subtyperUtil = zope.component.getUtility(ISubtyper)
        if subtyperUtil.existing_type(ob) is not None:
            subtyperUtil.remove_type(ob)
            ob.reindexObject()
        else:
            err.append('The object at %s is not subtyped' \
                % '/'.join(ob.getPhysicalPath()))
    return err


def workflow_action(ob, *args, **kw):
    """ Changes the object's workflow state
    """
    err = list()
    transition = kw['transition']
    if not transition:
        err.append('Please select a workflow action.')
    if not err:
        portal_workflow = getToolByName(ob, 'portal_workflow')
        try:
            portal_workflow.doActionFor(ob, transition)
        except Exception, e:
            err.append("Could not %(transition)s %(path)s. Error: %(error)s" \
                % dict(transition=transition,
                path="/".join(ob.getPhysicalPath()),
                error=str(e)))
    return err


def set_property(ob, *args, **kw):
    err = list()
    id = kw['property_id']
    value = kw['property_value']
    type_ = kw['property_type']
    if not id:
        err.append('Property id must not be empty')
    if not value:
        err.append('Property value must not be emtpy')
    if not type_:
        err.append('Property type must not be emtpy')
    if not err:
        ob = Acquisition.aq_inner(ob)
        if Acquisition.aq_base(ob).hasProperty(id):
            try:
                ob._delProperty(id)
            except:
                err.append('Could not delete existing property %s on %s' \
                    % (id, kw['lang']))
        try:
            ob._setProperty(id=id, value=value, type=type_)
        except:
            err.append('Could not set property %s on %s' \
                % (id, "/".join(ob.getPhysicalPath())))
    return err


def delete_property(ob, *args, **kw):
    err = list()
    id = kw['property_id']
    if not id:
        err.append('Property id must not be empty')
    if not err:
        ob = Acquisition.aq_inner(ob)
        if Acquisition.aq_base(ob).hasProperty(id):
            ob._delProperty(id)
        else:
            err.append('The property %s does not exists on %s' \
                % (id, "/".join(ob.getPhysicalPath())))
    return err


def cut_and_paste(ob, *args, **kw):
    """ Uses OFS to cut and paste an object.
    """
    err = list()
    targetpath = kw['target_path']
    if not targetpath:
        err.append('You must specify a target path')
    id = kw['id_to_move']
    if not id:
        err.append(u'You must select an object to move')
    targetpath = targetpath.encode('utf-8')
    id = id.encode('utf-8')
    lang = kw['lang']
    portal_path = kw['portal_path']

    if not err:
        if targetpath.startswith('/'):
            if not targetpath.startswith(portal_path):
                targetpath = portal_path + targetpath
        target_base = ob.restrictedTraverse(targetpath, None)
        if target_base is None:
            err.append(u'No object was found at the given taget path %s' \
               % targetpath)
            return err
        if ITranslatable.providedBy(target_base):
            target = target_base.getTranslation(lang)
        else:
            err.append(u'The target object is not translatable. Please '\
                'choose a different target that is translatable.')
            return err
        if target is None:
            err.append(u'No translation in language "%s" was found of '\
                'the target %s' % (lang, targetpath))
            return err
        if not IBaseFolder.providedBy(target):
            err.append(u'The target object is not folderish - pasting is '\
                'not possible.')
            return err
        name = None
        if id in ob.objectIds():
            name = id
            trans_object = getattr(ob, name)
        else:
            # look for translation via getTranslation
            target_object = kw.get('target_object', None)
            if target_object:
                trans_object = target_object.getTranslation(lang)
                if trans_object:
                    if Acquisition.aq_parent(trans_object) == ob:
                        name = trans_object.getId()

        if name is None:
            err.append(u'No translation of the requested object for language '\
                '%s found in %s' % (
                lang, '/'.join(ob.getPhysicalPath())))
            return err
        if target == trans_object:
            err.append(u'The target cannot be identical to the object you '\
                'want to move')
            return err

        ob._delObject(name, suppress_events=True)
        target._setObject(id, trans_object, set_owner=0, suppress_events=True)
        trans_object = target._getOb(id)

        notify(ObjectMovedEvent(trans_object, ob, id, target, id))
        notifyContainerModified(ob)
        if Acquisition.aq_base(ob) is not Acquisition.aq_base(target):
            notifyContainerModified(target)
        trans_object._postCopy(target, op=1)
        trans_object.reindexObject()

    return err


def get_available_subtypes(context):
    """ Returns the subtypes available in this context
    """
    request = context.request
    subtypes_menu = zope.component.queryUtility(IBrowserMenu, 'subtypes')
    if subtypes_menu:
        return subtypes_menu._get_menus(context, request)


def delete_this(ob, *args, **kw):
    err = list()
    lang = kw.get('lang', '')
    id_to_delete = kw['id_to_delete']
    name = ''

    if id_to_delete in ob.objectIds():
        name = id_to_delete
    else:
        # look for translation via getTranslation
        target_object = kw.get('target_object', None)
        if target_object:
            trans_object = target_object.getTranslation(lang)
            if trans_object:
                name = trans_object.getId()

    if not name:
        err.append(u'No translation for language %s found' % lang)
    else:
        try:
            ob._delObject(name)
        except Exception, e:
            err.append(u'Could not delete %s for language %s. Message: %s' \
                % (id_to_delete, lang, str(e)))
    return err


def translate_this(context, attrs=[], translation_exists=False,
    target_languages=[]):
    """ Translates the current object into all languages and transfers the
        given attributes
    """
    info = list()
    warnings = list()
    errors = list()

    # Only do this from the canonical
    context = context.getCanonical()
    # if context is language-neutral, it must receive a language before
    # it is translated
    if context.Language() == '':
        context.setLanguage(context.portal_languages.getPreferredLanguage())
    canLang = context.Language()

    # if the user didn't select target languages, get all supported languages
    # from the language tool
    if not target_languages:
        portal_languages = getToolByName(context, 'portal_languages')
        target_languages = portal_languages.getSupportedLanguages()
    for lang in target_languages:
        if lang == canLang:
            continue
        res = list()
        if not context.hasTranslation(lang):
            if not translation_exists:
                # need to make lang a string. It can be unicode so checkid will
                # freak out and lead to an infinite recursion
                context.addTranslation(str(lang))
                newOb = True
                if 'title' not in attrs:
                    attrs.append('title')
                res.append("Added Translation for %s" % lang)
            else:
                warnings.append(u'Translation in language %s does not exist, '\
                    'skipping' % lang)
                continue
        else:
            if not translation_exists:
                warnings.append(u'Translation for language %s already '\
                    'exists, skipping' % lang)
                continue
            res.append(u"Found translation for %s " % lang)
        trans = context.getTranslation(lang)

        for attr in attrs:
            field = context.getField(attr)
            if not field:
                warnings.append(u"Could not find the field '%s'. Please "\
                    "check your spelling" % attr)
                continue
            val = field.getAccessor(context)()
            trans.getField(attr).getMutator(trans)(val)
            res.append(u"  > Transferred attribute '%s'" % attr)
        # Set the correct format
        if shasattr(context, 'text_format'):
            trans.setFormat(context.text_format)
        if context.portal_type == 'Topic':
            # copy the contents as well
            ids = context.objectIds()
            ids.remove('syndication_information')

            # first delete all existing criteria on the translation
            for existingid in trans.objectIds():
                if existingid.startswith('crit__'):
                    trans._delObject(existingid)

            for id in ids:
                orig_ob = getattr(context, id)
                ob = orig_ob._getCopy(context)
                ob._setId(id)
                notify(ObjectCopiedEvent(ob, orig_ob))

                trans._setObject(id, ob)
                ob = trans._getOb(id)
                ob.wl_clearLocks()
                ob._postCopy(trans, op=0)
                ob.manage_afterClone(ob)
                notify(ObjectClonedEvent(ob))

            res.append(u"  > Transferred collection contents")
        info.append(u"\n".join(res))
    return (info, warnings, errors)


def add_interface(ob, *args, **kw):
    """ Changes the object's workflow state
    """
    err = list()
    interface_to_add = kw['interface_to_add']
    if not interface_to_add:
        err.append('Please select an interface to add.')
    if not err:
        if type(interface_to_add) != list and type(interface_to_add) != tuple:
            interface_to_add = [interface_to_add]
        adapted = IMarkerInterfaces(ob)
        add = adapted.dottedToInterfaces(interface_to_add)
        adapted.update(add=add, remove=list())
    return err


def remove_interface(ob, *args, **kw):
    """ Changes the object's workflow state
    """
    err = list()
    interface_to_remove = kw['interface_to_remove']
    if not interface_to_remove:
        err.append('Please select an interface to remove.')
    if not err:
        if type(interface_to_remove) != list and \
            type(interface_to_remove) != tuple:
            interface_to_remove = [interface_to_remove]
        adapted = IMarkerInterfaces(ob)
        remove = adapted.dottedToInterfaces(interface_to_remove)
        adapted.update(add=list(), remove=remove)
    return err
