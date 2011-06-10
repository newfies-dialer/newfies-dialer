from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from piston.doc import documentation_view
from handlers import *
#from django.views.decorators.cache import cache_page


auth = HttpBasicAuthentication(realm='Newfies Application')

campaign_handler = Resource(campaignHandler, authentication=auth)
phonebook_handler = Resource(phonebookHandler, authentication=auth)
contact_handler = Resource(contactHandler, authentication=auth)
bulkcontact_handler = Resource(bulkcontactHandler, authentication=auth)
#campaignsubscriber_handler = Resource(campaignsubscriberHandler,
#                                       authentication=auth)
campaign_delete_cascade_handler = Resource(campaignDeleteCascadeHandler,
                                           authentication=auth)

urlpatterns = patterns('',

    url(r'^campaign/delete_cascade/(?P<campaign_id>[^/]+)',
    campaign_delete_cascade_handler),

    url(r'^campaign[/]$', campaign_handler),
    url(r'^campaign/(?P<campaign_id>[^/]+)', campaign_handler),

    url(r'^phonebook[/]$', phonebook_handler),
    url(r'^phonebook/(?P<phonebook_id>[^/]+)', phonebook_handler),

    url(r'^contact[/]$', contact_handler),
    url(r'^contact/(?P<campaign_id>[^/]+)/(?P<contact>[^/]+)',
        contact_handler),
    url(r'^contact/(?P<campaign_id>[^/]+)', contact_handler),

    url(r'^bulkcontact[/]$', bulkcontact_handler),
    #url(r'^campaignsubscriber/(?P<campaign_id>[^/]+)/(?P<contact>[^/]+)',
    #    campaignsubscriber_handler),
    #url(r'^campaignsubscriber/(?P<campaign_id>[^/]+)',
    #    campaignsubscriber_handler),

    # automated documentation
    url(r'^doc[/]$', documentation_view),
)
