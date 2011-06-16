from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from piston.doc import documentation_view
from handlers import callrequestHandler, testcallHandler, \
answercallHandler, hangupcallHandler, testHandler
#from django.views.decorators.cache import cache_page


try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
from django.utils.encoding import smart_unicode
from django.utils.xmlutils import SimplerXMLGenerator
from piston.emitters import Emitter
from piston.utils import Mimer

class CustomXmlEmitter(Emitter):
    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):            
            for item in data:
                self._to_xml(xml, item)
        elif isinstance(data, dict):
            for key, value in data.iteritems():
                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key)
        else:
            xml.characters(smart_unicode(data))

    def render(self, request):
        stream = StringIO.StringIO()
        xml = SimplerXMLGenerator(stream, "utf-8")
        xml.startDocument()
        xml.startElement("response", {})
        self._to_xml(xml, self.construct())
        xml.endElement("response")
        xml.endDocument()
        return stream.getvalue()
Emitter.register('custom_xml', CustomXmlEmitter, 'text/xml; charset=utf-8')
Mimer.register(lambda *a: None, ('text/xml',))

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
    url(r'^answercall[/]$', answercall_handler, { 'emitter_format': 'custom_xml' }),
    url(r'^hangupcall[/]$', hangupcall_handler),

    url(r'^test[/]$', test_handler, { 'emitter_format': 'custom_xml' }),

    # automated documentation
    url(r'^doc[/]$', documentation_view),
)
