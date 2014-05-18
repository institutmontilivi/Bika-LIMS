from bika.lims.browser import BrowserView
from Products.CMFCore.utils import getToolByName
import plone
import json

class ajaxGetDependents(BrowserView):
    
    def __call__(self):
        dependents = []
        try:
            plone.protect.CheckAuthenticator(self.request)
        except Forbidden:
            return json.dumps(dependents)
        uc = getToolByName(self, 'uid_catalog')
        analysis = uc(UID=self.request.get("uid", '0'))
        if analysis and len(analysis) == 1:
            analysis = analysis[0].getObject()
            ans = analysis.getDependents()
            dependents = [an.UID() for an in ans]
        return json.dumps(dependents)
        


