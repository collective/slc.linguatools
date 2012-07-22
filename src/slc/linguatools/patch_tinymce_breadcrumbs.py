# -*- coding: utf-8 -*-
"""
This patch was written by Robert Niederreiter and provided in
http://plone.org/products/linguaplone/issues/275, linking to pastebin
http://pastebin.com/EhPhWpdw
"""
from Acquisition import aq_inner
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.interfaces import IFolderish
from Products.TinyMCE.adapters.JSONFolderListing import JSONFolderListing


def getBreadcrumbs(self, path=None):
    """Patch for displaying plone root in tiny mce breadcrumbs for
    browsing language neutral folders located next to language folders.
    """
    result = []

    root = getUtility(ISiteRoot)
    root_url = root.absolute_url()

    if path is not None:
        root_abs_url = root.absolute_url()
        path = path.replace(root_abs_url, '', 1)
        path = path.strip('/')
        root = aq_inner(root.restrictedTraverse(path))

    relative = aq_inner(self.context).getPhysicalPath()[len(
        root.getPhysicalPath()):]
    if path is None:
        # Add siteroot
        result.append({'title': 'Root',
            'url': '/'.join(root.getPhysicalPath())})

    for i in range(len(relative)):
        now = relative[:i + 1]
        obj = aq_inner(root.restrictedTraverse(now))

        if IFolderish.providedBy(obj):
            if not now[-1] == 'talkback':
                result.append({'title': obj.title_or_id(),
                    'url': root_url + '/' + '/'.join(now)})
    return result

JSONFolderListing.getBreadcrumbs = getBreadcrumbs
