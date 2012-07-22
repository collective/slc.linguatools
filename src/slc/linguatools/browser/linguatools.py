import logging

import Acquisition
import types

from OFS.event import ObjectClonedEvent

from zope import component
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectCopiedEvent

from zope.app.container.contained import ObjectMovedEvent
from zope.app.container.contained import notifyContainerModified
from zope.app.publisher.interfaces.browser import IBrowserMenu

from plone.app.portlets.utils import assignment_mapping_from_key
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletManager, \
    ILocalPortletAssignmentManager

from Products.CMFCore.utils import getToolByName
from Products.LinguaPlone.interfaces import ITranslatable
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PlacelessTranslationService import getTranslationService
from Products.statusmessages.interfaces import IStatusMessage

from slc.linguatools.interfaces import ILinguaToolsView

try:
    from p4a.subtyper.interfaces import ISubtyper
except ImportError:
    ISubtyper = None

try:
    from slc.subsite.root import getSubsiteRoot
except ImportError:
    getSubsiteRoot = None

log = logging.getLogger('slc.linguatools.browser.linguatools.py')


class LinguaToolsView(BrowserView):
    implements(ILinguaToolsView)
    template = ViewPageTemplateFile('linguatools.pt')

    def __call__(self):
        status = IStatusMessage(self.request)
        context = Acquisition.aq_inner(self.context)
        request = Acquisition.aq_inner(self.request)
        path = '/'.join(context.getPhysicalPath())
        changes_made = None

        if "form.button.UpdateTitle" in request:
            title = request.get('title', "no Title")
            changes_made = self.setTitle(title)

        elif "form.button.propagatePortlets" in request:
            changes_made = self.propagatePortlets()

        elif "form.button.addLanguageTool" in request:
            languages = request.get('languages', [])
            changes_made = self.addLanguageTool(languages)

        elif "form.button.reindexer" in request:
            changes_made = self.reindexer()

        elif "form.button.publisher" in request:
            changes_made = self.publisher()

        elif "form.button.hider" in request:
            changes_made = self.hider()

        elif "form.button.setEnableNextPrevious" in request:
            changes_made = self.setEnableNextPrevious(True)

        elif "form.button.setDisableNextPrevious" in request:
            changes_made = self.setEnableNextPrevious(False)

        elif "form.button.setExcludeFromNav" in request:
            changes_made = self.setExcludeFromNav(True)

        elif "form.button.setIncludeInNav" in request:
            changes_made = self.setExcludeFromNav(False)

        elif 'form.button.setExcludeFromNavInFolder' in request:
            changes_made = self.setExcludeFromNavInFolder(True)

        elif "form.button.setRichDocAttachment" in request:
            changes_made = self.setRichDocAttachment(True)

        elif "form.button.unsetRichDochAttachment" in request:
            changes_made = self.setRichDocAttachment(False)

        elif "form.button.deleter" in request:
            guessLanguage = bool(request.get('guessLanguage', ''))
            id = request.get('id', '')
            changes_made = self.deleter(id, guessLanguage)

        elif "form.button.ChangeId" in request:
            oldid = request.get('oldid', "")
            newid = request.get('newid', '')
            changes_made = self.renamer(oldid, newid)

        elif "form.button.setTranslateTitle" in request:
            label = request.get('label', "")
            domain = request.get('domain', "plone")
            changes_made = self.setTranslatedTitle(label, domain)

        elif "form.button.setTranslateDescription" in request:
            label = request.get('label', "")
            domain = request.get('domain', "plone")
            changes_made = self.setTranslatedDescription(label, domain)

        elif "form.button.createFolder" in request:
            excludeFromNav = request.get('excludeFromNav', 'true')
            id = request.get('id', '')
            changes_made = self.createFolder(id, excludeFromNav)

        elif "form.button.fixTranslationReference" in request:
            recursive = bool(request.get('recursive', False))
            langindex = request.get('langindexoffset', 0)
            changes_made = self.fixTranslationReference(recursive, langindex)

        elif "form.button.addSubtype" in request:
            subtype = request.get('subtype', "")
            changes_made = self.add_subtype(subtype)

        elif "form.button.removeSubtype" in request:
            subtype = request.get('subtype', "")
            changes_made = self.remove_subtype()

        elif "form.button.delProperty" in request:
            id = request.get('id', "")
            changes_made = self.delProperty(id)

        elif "form.button.blockPortlets" in request:
            manager = request.get('manager', "")
            blockstatus = not not request.get('blockstatus', False)
            if manager:
                changes_made = self.blockPortlets(manager, blockstatus)
            else:
                status.addStatusMessage(_(u"No manager selected."),
                    type='info')

        elif "form.button.setProperty" in request:
            id = request.get('id', "")
            typ = request.get('typ', "")
            value = request.get('value', "")
            changes_made = self.setProperty(id, typ, value)

        elif "form.button.cutAndPaste" in request:
            sourcepath = request.get('sourcepath', "")
            id = request.get('id', "")
            targetpath = request.get('targetpath', "")
            changes_made = self.cutAndPaste(sourcepath, id, targetpath)

        elif "form.button.fixOrder" in request:
            order = request.get('order', "")
            orderlist = order.splitlines()
            changes_made = self.fixOrder(orderlist)

        elif "form.button.translateThis" in request:
            attrs = request.get('attrs', "")
            attrslist = attrs.splitlines()
            translationExists = request.get('translationExists', False)
            changes_made = self.translateThis(attrslist, translationExists)

        if changes_made == False:
            status.addStatusMessage(
                            _(u"It seems no changes were made. Consult the "
                            "event.log if you are unsure why"),
                            type='info')

        return self.template()

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal_url = getToolByName(context, 'portal_url')

        # Need to be mindful of a potential subsite!
        self.portal_path = self.portal_url.getPortalPath()
        if getSubsiteRoot is not None:
            self.portal_path = getSubsiteRoot(self.context)
        self.portal = context.restrictedTraverse(self.portal_path)
        self.portal_languages = getToolByName(context, 'portal_languages')
        self.langs = self.portal_languages.getSupportedLanguages()

        portal_path = self.portal.getPhysicalPath()
        context_path = context.getPhysicalPath()

        self.dynamic_path = self.portal_path + '/%s/' + \
                    "/".join(context_path[len(portal_path) + 1:])

        if self.dynamic_path[-1] == "/":
            self.dynamic_path = self.dynamic_path[:-1]

    def is_translatable(self):
        """ Helper method used on the linguatools object tab to see if it
            should render
        """
        context = Acquisition.aq_inner(self.context)
        return ITranslatable.isImplementedBy(context)

    def _forAllLangs(self, method, *args, **kw):
        """ helper method. Takes a method and executes it on all language
            versions of context
        """
        context = Acquisition.aq_inner(self.context)
        status = IStatusMessage(self.request)
        changes_made = False
        for lang in self.langs:
            lpath = self.dynamic_path % lang

            base = context.getTranslation(lang)
            if base is None:
                base = context.restrictedTraverse(lpath, None)
                # make sure that the base found by restrictedTraverse has the
                # same parent as the context!
                if base is None or Acquisition.aq_parent(base) \
                    != Acquisition.aq_parent(context):
                    log.info("Break for lang %s, base is none" % lang)
                    continue
                else:
                    log.warn("Object found at %s which is not linked as a "\
                        "translation of %s"
                        % (lpath, '/'.join(context.getPhysicalPath())))

                    status.addStatusMessage(_(
                        "Object found at %s which is not linked as a "\
                            "translation of %s"
                            % (lpath, '/'.join(context.getPhysicalPath()))),
                            type='info')

            kw['lang'] = lang
            method(base, *args, **kw)
            log.info("Executing for language %s" % lang)
            status.addStatusMessage(_(u"Changes made for language %s" % lang),
                type='info')
            changes_made = True

        return changes_made

    def getPortletManagerNames(self):
        names = [x[0] for x in component.getUtilitiesFor(IPortletManager)]
        # filter out dashboard stuff
        names = [x for x in names if not x.startswith('plone.dashboard')]
        return names

    def blockPortlets(self, manager, blockstatus):
        """ Block the Portlets on a given context, manager, and Category """

        def _setter(ob, *args, **kw):
            manager = kw['manager']
            blockstatus = kw['blockstatus']
            CAT = CONTEXT_CATEGORY
            portletManager = component.getUtility(IPortletManager,
                name=manager)
            assignable = component.getMultiAdapter((ob, portletManager,),
                ILocalPortletAssignmentManager)
            assignable.setBlacklistStatus(CAT, blockstatus)
        return self._forAllLangs(_setter, manager=manager,
            blockstatus=blockstatus)

    def setExcludeFromNav(self, flag):
        """ Sets the Exclude From nav flag """

        def _setter(ob, *args, **kw):
            flag = kw['flag']
            ob.setExcludeFromNav(flag)
        return self._forAllLangs(_setter, flag=flag)

    def setExcludeFromNavInFolder(self, flag):
        "Set the Exclude from Nav flag on all subobjects"

        def _setter(ob, *args, **kw):
            flag = kw['flag']
            subobs = ob.objectValues()
            for subob in subobs:
                if hasattr(Acquisition.aq_base(subob), 'setExcludeFromNav'):
                    state = subob.getExcludeFromNav()
                    subob.setExcludeFromNav(flag)
                    if state != flag or subob.isTranslation():
                        subob.reindexObject()
        return self._forAllLangs(_setter, flag=flag)

    def setEnableNextPrevious(self, flag):
        """ Enables the Next-Previous Navigation Flag """

        def _setter(ob, *args, **kw):
            flag = kw['flag']
            ob.setNextPreviousEnabled(flag)
        return self._forAllLangs(_setter, flag=flag)

    def setTitle(self, title):
        """ simply set the title to a given value. Very primitive! """

        def _setter(ob, *args, **kw):
            title = kw['title']
            ob.setTitle(title)
        return self._forAllLangs(_setter, title=title)

    def renamer(self, oldid, newid):
        """ rename one object within context from oldid to newid """

        def _setter(ob, *args, **kw):
            oldid = kw['oldid']
            newid = kw['newid']
            if oldid in ob.objectIds():
                ob.manage_renameObjects([oldid], [newid])
        return self._forAllLangs(_setter, oldid=oldid, newid=newid)

    def fixOrder(self, ORDER):
        """Move contents of a folter into order
            make sure the ordering of the folders is correct
        """

        plone_utils = getToolByName(self.context, 'plone_utils')

        def _orderIDs(base, *args, **kw):
            """sorts the objects in base in the order given by ids"""
            results = []
            ids = [x for x in kw['ids']]
            base_ids = base.objectIds()
            results.append('  > current order: %s' % str(base_ids))
            flag = 0
            if len(base_ids) >= len(ids) and base_ids[:len(ids)] == ids:
                return

            ids.reverse() # we let the items bubble up, last one first

            for id in ids:
                if id in base_ids:
                    flag = 1
                    base.moveObjectsToTop(id)
            if flag == 1: # only reindex if there is something to do
                plone_utils.reindexOnReorder(base)
            results.append("  > New order: %s " % str(base.objectIds()))
            return results

        return self._forAllLangs(_orderIDs, ids=ORDER)

    def deleter(self, id, guessLanguage=False):
        """ deletes an object with a given id from all language branches """

        def _setter(ob, *args, **kw):
            res = []
            currlang = kw.get('lang', '')
            guessLanguage = kw.get('guessLanguage', False)
            id = kw['id']
            if guessLanguage == True:
                # Try to also delete objects with id "id_lang[.ext]"
                parts = id.rsplit('.', 1)
                if len(parts) > 1:
                    stem, ext = parts
                    name = "%(stem)s_%(lang)s.%(ext)s" % dict(stem=parts[0],
                        lang=currlang, ext=parts[1])
                else:
                    name = "%(stem)s_%(lang)s" % dict(stem=parts[0],
                        lang=currlang)
            else:
                name = id
            if name in ob.objectIds():
                ob._delObject(name)
                res.append("deleted %s" % name)
            return res
        return self._forAllLangs(_setter, id=id, guessLanguage=guessLanguage)

    def propagatePortlets(self):
        """ propagates the portlet config from context to the language versions
        """

        context = Acquisition.aq_inner(self.context)
        path = "/".join(context.getPhysicalPath())

        managers = dict()
        for managername in self.getPortletManagerNames():
            managers[managername] = assignment_mapping_from_key(context,
                managername, CONTEXT_CATEGORY, path)

        def _setter(ob, *args, **kw):
            results = []
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

        return self._forAllLangs(_setter, managers=managers)

    def setProperty(self, id, typ, value):
        """ sets a OFS Property on context """

        def _setter(ob, *args, **kw):
            id = kw['id']
            typ = kw['typ']
            value = kw['value']

            ob = Acquisition.aq_inner(ob)
            if Acquisition.aq_base(ob).hasProperty(id):
                ob._delProperty(id)
            ob._setProperty(id=id, value=value, type=typ)

        return self._forAllLangs(_setter, id=id, typ=typ, value=value)

    def delProperty(self, id):
        """ removes a OFS Property on context """

        def _setter(ob, *args, **kw):
            id = kw['id']
            ob = Acquisition.aq_inner(ob)
            if Acquisition.aq_base(ob).hasProperty(id):
                ob._delProperty(id)

        return self._forAllLangs(_setter, id=id)

    def setTranslatedTitle(self, label, domain):
        """ sets the title based on the translation availble for title in the
            language
        """

        def _setter(ob, *args, **kw):
            translate = getTranslationService().translate
            label = kw['label']
            domain = kw['domain']
            lang = kw['lang']
            title_trans = translate(target_language=lang, msgid=label,
                default=label, context=ob, domain=domain)
            ob.setTitle(title_trans)
        return self._forAllLangs(_setter, label=label, domain=domain)

    def setTranslatedDescription(self, label, domain):
        """ sets the description based on the translation availble for title in
            the language
        """

        def _setter(ob, *args, **kw):
            translate = getTranslationService().translate
            label = kw['label']
            domain = kw['domain']
            lang = kw['lang']
            desc_trans = translate(target_language=lang, msgid=label,
                default=label, context=ob, domain=domain)
            ob.setDescription(desc_trans)
        return self._forAllLangs(_setter, label=label, domain=domain)

    def createFolder(self, id, excludeFromNav=True):
        """ creates a folder and all translations in the language branches """
        self.context.invokeFactory('Folder', id)
        ob = getattr(self.context, id)
        ob.unmarkCreationFlag()
        ob.setExcludeFromNav(excludeFromNav)
        for lang in self.langs:
            if lang == self.context.Language():
                continue
            ob.addTranslation(lang)
        return ['Folder Created']

    def cutAndPaste(self, sourcepath, id, targetpath):
        """ Uses OFS to cut and paste an object.
            Sourecpath must refer to the folder which contains the object to
            move. id must be a string containing the id of the object to move.
            targetpath must be the folder to move to.
            Both paths must contain one single %s to place the language
        """
        context = Acquisition.aq_inner(self.context)
        if '%s' not in sourcepath:
            return ["Wrong sourcepath"]
        if '%s' not in targetpath:
            return ["Wrong targetpath"]

        results = []

        for lang in self.langs:
            results.append("Trying language: %s" % lang)

            spath = sourcepath % lang
            source = context.restrictedTraverse(spath, None)
            if source is None:
                results.append("  # Break, source is none")
                continue
            spathtest = "/".join(source.getPhysicalPath())
            if spath != spathtest:
                results.append("  # Break, requested path not sourcepath "\
                    "(%s != %s)" % (spath, spathtest))
                continue

            tpath = targetpath % lang
            target = context.restrictedTraverse(tpath, None)
            if target is None:
                results.append("  # Break, target is none")
                continue
            tpathtest = "/".join(target.getPhysicalPath())
            if tpath != tpathtest:
                results.append("  # Break, requested path not targetpath "\
                    "(%s != %s)" % (tpath, tpathtest))
                continue

            ob = getattr(source, id, None)
            ob = Acquisition.aq_base(ob)
            if ob is None:
                results.append("  # Break, ob is None!!")
                continue
            source._delObject(id, suppress_events=True)
            target._setObject(id, ob, set_owner=0, suppress_events=True)
            ob = target._getOb(id)

            notify(ObjectMovedEvent(ob, source, id, target, id))
            notifyContainerModified(source)
            if Acquisition.aq_base(source) is not Acquisition.aq_base(target):
                notifyContainerModified(target)
            ob._postCopy(target, op=1)

            results.append("Copy&Paste successful for language %s" % lang)

        return results

    def addLanguageTool(self, languages=[]):
        """ adds a language Tool """

        def _setter(ob, *args, **kw):
            if ob.isPrincipiaFolderish:
                tool = getattr(Acquisition.aq_parent(ob), 'portal_languages')
                if tool.id in ob.objectIds():
                    ob._delObject(tool.id)

                newob = tool._getCopy(tool)
                newob._setId(tool.id)
                notify(ObjectCopiedEvent(newob, tool))

                ob._setOb(tool.id, newob)
                ob._objects = ob._objects + (dict(meta_type=tool.meta_type,
                    id=tool.id),)
                newob = ob._getOb(tool.id)
                newob.wl_clearLocks()
                newob._postCopy(ob, op=0)
                newob.manage_afterClone(newob)

                notify(ObjectClonedEvent(newob))
                languages = kw.get('languages', None)
                if languages:
                    if isinstance(languages, tuple):
                        languages = list(languages)
                    elif isinstance(languages, types.StringType) or \
                        isinstance(languages, types.UnicodeType):
                        languages = [languages]
                    newob.supported_langs = languages
                return ["Added language tool to %s" % ob.getId()]
        return self._forAllLangs(_setter, languages=languages)

    def can_subtype(self):
        return not ISubtyper is None

    def get_available_subtypes(self):
        """ Returns the subtypes available in this context
        """
        request = self.context.REQUEST
        context = Acquisition.aq_inner(self.context)
        subtypes_menu = component.queryUtility(IBrowserMenu, 'subtypes')
        if subtypes_menu:
            return subtypes_menu._get_menus(context, request)

    def add_subtype(self, subtype):
        """ sets ob to given subtype """

        if not self.can_subtype():
            return

        def _setter(ob, *args, **kw):
            subtype = kw['subtype']
            subtyperUtil = component.getUtility(ISubtyper)
            if subtyperUtil.existing_type(ob) is None:
                subtyperUtil.change_type(ob, subtype)
                ob.reindexObject()

        return self._forAllLangs(_setter, subtype=subtype)

    def remove_subtype(self):
        """ sets ob to given subtype """

        if not self.can_subtype():
            return

        def _setter(ob, *args, **kw):
            subtyperUtil = component.getUtility(ISubtyper)
            if subtyperUtil.existing_type(ob) is not None:
                subtyperUtil.remove_type(ob)
                ob.reindexObject()

        return self._forAllLangs(_setter)

    def reindexByPath(self):
        """ reindexes the current context """
        pass

    def reindexer(self):
        """ reindexes an object in all language branches """

        def _setter(ob, *args, **kw):
            ob.reindexObject()
        return self._forAllLangs(_setter)

    def publisher(self):
        """ tries to publish all object languages """
        portal_workflow = getToolByName(self.context, 'portal_workflow')

        def _setter(ob, *args, **kw):
            res = []
            try:
                portal_workflow.doActionFor(ob, 'publish')
                res.append("OK Published %s" % "/".join(ob.getPhysicalPath()))
            except Exception, e:
                res.append("ERR publishing %s: %s"
                    % ("/".join(ob.getPhysicalPath()), str(e)))
            return res
        return self._forAllLangs(_setter)

    def hider(self):
        """ tries to hide object in all languages """
        portal_workflow = getToolByName(self.context, 'portal_workflow')

        def _setter(ob, *args, **kw):
            res = []
            try:
                portal_workflow.doActionFor(ob, 'hide')
                res.append("OK hidden %s" % "/".join(ob.getPhysicalPath()))
            except Exception, e:
                res.append("ERR hiding %s: %s"
                    % ("/".join(ob.getPhysicalPath()), str(e)))
            return res
        return self._forAllLangs(_setter)

    def translateThis(self, attrs=[], translationExists=False):
        """ Translates the current object into all languages and transfers
            the given attributes
        """
        context = Acquisition.aq_inner(self.context)
        status = IStatusMessage(self.request)
        # Only do this from the canonical
        context = context.getCanonical()
        # if context is language-neutral, it must receive a language before
        # it is translated
        if context.Language() == '':
            context.setLanguage(self.portal_languages.getPreferredLanguage())
        canLang = context.Language()

        for lang in self.langs:
            if lang == canLang:
                continue
            res = list()
            if not context.hasTranslation(lang):
                if not translationExists:
                    # need to make lang a string. It is currently unicode so
                    # checkid will freak out and lead to an infinite recursion
                    context.addTranslation(str(lang))
                    newOb = True
                    if 'title' not in attrs:
                        attrs.append('title')
                    res.append("Added Translation for %s" % lang)
                else:
                    status.addStatusMessage(u'Translation for %s does not '\
                        'exist, skipping' % lang, type="warning")
                    continue
            else:
                if not translationExists:
                    status.addStatusMessage(u"Translation for %s already "\
                        "exists, skipping" % lang, type="info")
                    continue
            trans = context.getTranslation(lang)
            res.append(u"Found translation for %s " % lang)

            for attr in attrs:
                field = context.getField(attr)
                if not field:
                    status.addStatusMessage(u"Could not find the field '%s'. '\
                        'Please check your spelling" % attr, type="warning")
                    continue
                val = field.getAccessor(context)()
                trans.getField(attr).getMutator(trans)(val)
                res.append(u"  > Transferred Attribute %s" % attr)
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

                res.append(u"  > Transferred Topic contents")
            status.addStatusMessage(u"\n".join(res), type="info")
        return "ok"

    def setRichDocAttachments(self, flag=False):
        """ Sets the attachment flag on a rich document """

        def _setter(ob, *args, **kw):
            flag = kw['flag']
            res = []
            try:
                ob.setDisplayAttachments(flag)
                res.append("OK: set display attachment on %s to %s"
                    % (ob.getId(), flag))
            except Exception, e:
                res.append("ERR setting display attachment on %s (%s)"
                            % ("/".join(ob.getPhysicalPath()),
                            type(Acquisition.aq_base(ob))))
            return res
        return self._forAllLangs(_setter, flag=flag)

    def _guessLanguage(self, filename):
        """
        try to find a language abbreviation in the string
        acceptable is a two letter language abbreviation at the end of the
        string prefixed by an _ just before the extension
        returns lang, stem, ext
        """
        if callable(filename):
            filename = filename()

        langs = getToolByName(self.context,
            'portal_languages').getSupportedLanguages()

        if len(filename) > 3 and '.' in filename:
            elems = filename.split('.')
            name = ".".join(elems[:-1])
            if len(name) > 3 and name[-3] in ['_', '-']:
                lang = name[-2:].strip()
                lang = lang.lower()
                if lang in langs:
                    namestem = name[:(len(name) - 2)]
                    return lang, namestem, elems[-1]

        return '', filename, ''

    def _getLangOb(self, ob, lang, langindexoffset):
        """ Used by FixTranslationReference
            try to get a matching object in another language path. """
        portal_url = getToolByName(ob, 'portal_url')
        langidx = len(portal_url.getPortalObject().getPhysicalPath()) \
            + langindexoffset
        obpath = ob.getPhysicalPath()
        langpath = list(obpath)
        langpath[langidx] = lang
        filename = langpath[-1]

        specialfilename = ''
        if ob.portal_type in ['File', 'Image']:
            # we try to also accept _xx language abbrevs
            langabbrev, stem, ext = self._guessLanguage(filename)
            if langabbrev != '':
                specialfilename = "%s%s.%s" % (stem, lang, ext)

        root = ob.getPhysicalRoot()
        langob = root
        for i in langpath[1:-1]:
            if i in langob.objectIds():
                langob = getattr(langob, i)
            else:
                return None

        # now only the filename is left. Special handling:
        if specialfilename != '':
            langob = getattr(langob, filename, getattr(langob,
                specialfilename, None))
        else:
            langob = getattr(langob, filename, None)

        return langob

    def fixTranslationReference(self, recursive=False, langindexoffset=0):
        """ fixes translation references to the canonical.
            Assumes that self is always en and canonical
            tries to handle language extensions for files like hwp_xx.swf
        """
        try:
            langindexoffset = int(langindexoffset)
        except:
            langindexoffset = 0
        context = Acquisition.aq_inner(self.context)
        pl = context.portal_languages
        langs = pl.getSupportedLanguages()

        results = []
        if recursive == True:
            targetobs = context.ZopeFind(context, search_sub=1)
        else:
            targetobs = [(context.getId(), context)]
        for id, ob in targetobs:

            print "handling %s" % ob.absolute_url(1)
            if hasattr(Acquisition.aq_base(ob), '_md') and \
                'language' in ob._md and ob._md['language'] == u'':
                ob._md['language'] = u'en'

            if not hasattr(Acquisition.aq_base(ob), 'addTranslationReference'):
                continue

            if not ob.isCanonical():
                results.append("Not Canonical: %s " % ob.absolute_url())
                print "Not Canonical: %s " % ob.absolute_url()

            for lang in langs:
                if ob.hasTranslation(lang):
                    continue
                langob = self._getLangOb(ob, lang, langindexoffset)

                if langob is None:
                    continue

                try:
                    langob.setLanguage('')
                    langob.setLanguage(lang)
                    langob.addTranslationReference(ob)
                    langpath = "/".join(langob.getPhysicalPath())
                    results.append("Adding TransRef for %s" % langpath)
                    print  "Adding TransRef for %s" % langpath
                except Exception, at:
                    results.append("Except %s" % str(at))

        results.append("ok")
        return results
