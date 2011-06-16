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
