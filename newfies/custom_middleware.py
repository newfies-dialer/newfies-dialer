
from sentry.client.models import sentry_exception_handler

class SentryMiddleware(object):
    def process_exception(self, request, exception):
        # Make sure the exception signal is fired for Sentry
        sentry_exception_handler(request=request)
        return HttpResponse('foo')
    
from django.conf.urls.defaults import *

from django.views.defaults import page_not_found, server_error

def handler500(request):
    """
    500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """
    from django.template import Context, loader
    from django.http import HttpResponseServerError

    t = loader.get_template('500.html') # You need to create a 500.html template.
    return HttpResponseServerError(t.render(Context({
        'request': request,
    })))