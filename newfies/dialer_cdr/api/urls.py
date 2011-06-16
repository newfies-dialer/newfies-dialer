from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from piston.doc import documentation_view
from handlers import callrequestHandler, testcallHandler, \
answercallHandler, hangupcallHandler, testHandler
#from django.views.decorators.cache import cache_page
import custom_xml_emitter
#from common.custom_xml_emitter import CustomXmlEmitter


auth = HttpBasicAuthentication(realm='Newfies Application')

callrequest_handler = Resource(callrequestHandler, authentication=auth)
testcall_handler = Resource(testcallHandler, authentication=auth)
answercall_handler = Resource(answercallHandler, authentication=auth)
hangupcall_handler = Resource(hangupcallHandler, authentication=auth)
test_handler = Resource(testHandler, authentication=auth)

urlpatterns = patterns('',

    url(r'^callrequest[/]$', callrequest_handler),
    url(r'^callrequest/(?P<callrequest_id>[^/]+)', callrequest_handler),

    url(r'^testcall[/]$', testcall_handler),
    url(r'^answercall[/]$', answercall_handler,
        {'emitter_format': 'custom_xml'}),
    url(r'^hangupcall[/]$', hangupcall_handler),

    url(r'^test[/]$', test_handler, {'emitter_format': 'custom_xml'}),

    # automated documentation
    url(r'^doc[/]$', documentation_view),
)
