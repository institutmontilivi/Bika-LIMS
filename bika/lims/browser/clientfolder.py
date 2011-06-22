from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IClientFolder
from plone.app.content.browser.interfaces import IFolderContentsView
from Products.Five.browser import BrowserView
from zope.interface import implements

class ClientFolderContentsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'Client'}
    content_add_actions = {_('Client'): "createObject?type_name=Client"}
    title = _("Clients")
    description = ""
    show_editable_border = False
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = False
    batch = True
    pagesize = 20

    columns = {
               'title_or_id': {'title': _('Name')},
               'getEmailAddress': {'title': _('Email Address')},
               'getPhone': {'title': _('Phone')},
               'getFax': {'title': _('Fax')},
              }

    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns':['title_or_id',
                                'getEmailAddress',
                                'getPhone',
                                'getFax', ],
                     'buttons':[{'cssclass': 'context',
                                 'title': _('Delete'),
                                 'url': 'folder_delete:method'}],
                      }
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            items[x]['links'] = {
                'title_or_id': items[x]['url'],
                'getEmailAddress': items[x]['getEmailAddress'] and 'mailto:%s' % items[x]['getEmailAddress'] or "",
            }

        return items

    def __call__(self):
        return self.template()

class Clients(BrowserView):
    """ autocomplete data source for clients
        return JSON data [string,string]
    """
    def __call__(self):
        pc = getToolByName(self, 'portal_catalog')
        term = self.request.get('term', '')
        items = pc(portal_type = "Client")
        items = [s.Title for s in items if s.Title.lower().find(term.lower()) > -1]
        return json.dumps(items)