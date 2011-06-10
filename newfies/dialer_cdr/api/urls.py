from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from piston.doc import documentation_view
from handlers import callrequestHandler, dummyinitcallHandler, dummyanswercallHandler, dummyhangupcallHandler
#from django.views.decorators.cache import cache_page


auth = HttpBasicAuthentication(realm='Newfies Application')

callrequest_handler = Resource(callrequestHandler, authentication=auth)
dummyinitcall_handler = Resource(dummyinitcallHandler, authentication=auth)
dummyanswercall_handler = Resource(dummyanswercallHandler, authentication=auth)
dummyhangupcall_handler = Resource(dummyhangupcallHandler, authentication=auth)

urlpatterns = patterns('',

    url(r'^callrequest[/]$', callrequest_handler),
    url(r'^callrequest/(?P<callrequest_id>[^/]+)', callrequest_handler),

    url(r'^dummyinitcall[/]$', dummyinitcall_handler),
    url(r'^dummyanswercall[/]$', dummyanswercall_handler),
    url(r'^dummyhangupcall[/]$', dummyhangupcall_handler),

    # automated documentation
    url(r'^doc[/]$', documentation_view),
)
