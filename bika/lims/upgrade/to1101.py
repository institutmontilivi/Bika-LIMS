import logging

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore import permissions
from bika.lims.permissions import *

from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """
    issue #29: L analista no te privilegis suficients per afegir fitxers adjunts a WS.
    """

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')

    #Folder permissions
    mp = portal.clients.manage_permission
    mp(AddAttachment, ['Manager', 'LabManager', 'Owner' 'Analyst'], 0)
    portal.clients.reindexObject()

    #Subfolder permissions   
    for obj in portal.clients.objectValues():
        mp = obj.manage_permission
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Analyst'], 0)
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Analyst'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Analyst'], 0)
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Analyst'], 0)
        mp(permissions.View, ['Manager', 'Member', 'Authenticated', 'Anonymous','Analyst'], 1)
        mp('Access contents information', ['Manager', 'Member', 'Authenticated', 'Anonymous', 'Analyst'], 1)
        obj.reindexObject()

    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()

    return True
