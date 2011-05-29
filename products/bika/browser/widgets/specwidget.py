from AccessControl import ClassSecurityInfo, ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.ATExtensions.widget.records import RecordsWidget
from Products.Archetypes.Registry import registerWidget, registerPropertyType
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.utils import shasattr, DisplayList
from Products.CMFCore.utils import getToolByName
from archetypes.referencebrowserwidget import utils

class SpecWidget(RecordsWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/specwidget",
        'helper_js': ("bika_widgets/specwidget.js",),
        'helper_css': ("bika_widgets/specwidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None,
                     emptyReturnsMarker = False):
        """ Services that were rendered with form inputs when a category was expanded,
            but which were not filled in, are stripped off here.
        """
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker

        for idx in range(len(value) - 1, -1, -1): #  XXX this can't be right.. - signals bad data (batching machine in folder view)
            if len(value[idx].keys()) == 1: del value[idx]
        return value, {}

    security.declarePublic('getResultsRangeDict')
    def getResultsRangeDict(self):
        """convert ResultsRange to a dictionary
        """
        specs = {}
        for spec in self.getResultsRange():
            uid = spec['service']
            specs[uid] = {}
            specs[uid]['min'] = spec['min']
            specs[uid]['max'] = spec['max']
            specs[uid]['error'] = spec['error']
        return specs

    # XXX Memoize
    security.declarePublic('getCategories')
    def getCategories(self, field, allservices = True):
        """Returns a dictionary of AnalysisCategory[service,service,...]
        """
        categories = {}
        services = self.portal_catalog(portal_type = 'AnalysisService')
        tool = getToolByName(self, REFERENCE_CATALOG)

        if allservices:
            for service in services:
                if categories.has_key(service.getCategoryName):
                    categories[service.getCategoryName].append(service)
                else:
                    categories[service.getCategoryName] = [service, ]
        else:
            records = getattr(field, field.accessor)()
            for record in records:
                service = tool.lookupObject(record['service'])
                if categories.has_key(service.getCategoryName()):
                    categories[service.getCategoryName()].append(service)
                else:
                    categories[service.getCategoryName()] = [service, ]

        return categories

    security.declarePublic('getSpecCategories')
    def getSpecCategories(self, field):
        """list of Category UIDS for services specified in ResultsRange
        """
        tool = getToolByName(self, REFERENCE_CATALOG)
        categories = []

        for spec in field.getResultsRange():
            service = tool.lookupObject(spec['service'])
            if service.getCategoryUID() not in categories:
                categories.append({'UID': service.getCategoryUID(), 'Title': service.getCategoryName()})
        return categories

    security.declarePublic('getCategorySpecs')
    def getCategorySpecs(self, field, category_title):
        """Return a list of services with specs in a category
        """
        tool = getToolByName(self, REFERENCE_CATALOG)
        services = []
        for spec in field.getResultsRange():
            service = tool.lookupObject(spec['service'])
            if service.getCategoryName() == category_title:
                services.append(spec)
        return services

    security.declarePublic('getCategoryUID')
    def getCategoryUID(self, category_title):
        catalog = getToolByName(self, 'portal_catalog')
        cats = catalog(portal_type = "AnalysisCategory")
        cats = [cat.UID for cat in cats if cat.Title == category_title]
        if cats:
            return cats[0]
        else:
            return ""

    security.declarePublic('getRemainingSampleTypes')
    def getRemainingSampleTypes(self, field):
        """ Return a DisplayList containing all sampletypes with no analysis specs defined
           XXX  AnalysisSpec or LabAnalysisSec is decided from the type of the field parameter
        """
        unavailable_sampletypes = []

        for spec in self.portal_catalog(portal_type = 'LabAnalysisSpec'):
            if spec.UID != self.UID():
                st = spec.getSampleType()
                if st:
                    unavailable_sampletypes.append(st.UID())

        available_sampletypes = []
        for st in self.portal_catalog(portal_type = 'SampleType'):
            if st.UID not in unavailable_sampletypes:
                available_sampletypes.append((st.UID, st.Title))

        return DisplayList(available_sampletypes)

registerWidget(SpecWidget,
               title = 'Analysis Services',
               description = ('AnalysisSpec selector.'),
               used_for = ('Products.Archetypes.Field.ReferenceField',)
               )

#registerPropertyType('default_search_index', 'string', AnalysisSpecsWidget)