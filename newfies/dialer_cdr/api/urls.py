from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from piston.doc import documentation_view
from handlers import callrequestHandler, testcallHandler, \
answercallHandler, hangupcallHandler, cdrHandler
from common.custom_xml_emitter import *


class CsrfExemptResource(Resource):
    """A Custom Resource that is csrf exempt"""
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)
        

auth = HttpBasicAuthentication(realm='Newfies Application')
auth_ip = IpAuthentication()

callrequest_handler = CsrfExemptResource(callrequestHandler, authentication=auth)
answercall_handler = CsrfExemptResource(answercallHandler, authentication=auth_ip)
hangupcall_handler = CsrfExemptResource(hangupcallHandler, authentication=auth_ip)
cdr_handler = CsrfExemptResource(cdrHandler, authentication=auth_ip)
testcall_handler = CsrfExemptResource(testcallHandler, authentication=auth_ip)


urlpatterns = patterns('',

    url(r'^callrequest[/]$', callrequest_handler),
    url(r'^callrequest/(?P<callrequest_id>[^/]+)', callrequest_handler),

    url(r'^store_cdr/', cdr_handler),

    url(r'^answercall[/]$', answercall_handler,
                                    {'emitter_format': 'custom_xml'}),
    url(r'^hangupcall[/]$', hangupcall_handler,
                                    {'emitter_format': 'custom_xml'}),
    
    url(r'^testcall[/]$', testcall_handler),

    # automated documentation
    url(r'^doc[/]$', documentation_view),
)
