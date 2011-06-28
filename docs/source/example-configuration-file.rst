.. _conf-example:

Sample Configuration
====================

This is an sample configuration to get you started.
It should contain all you need to run a basic set-up.
 
------------------------
The Configuration Module
------------------------

Some of the more important parts of the configuration module for the Newfies,
``settings.py``, are explained below::

  import os.path
  APPLICATION_DIR = os.path.dirname(globals()['__file__'])

``APPLICATION_DIR`` now contains the full path of your project folder and can be used elsewhere
in the ``settings.py`` module so that your project may be moved around the system without you having to
worry about changing any troublesome hard-coded paths. ::

  DEBUG = True

turns on debug mode allowing the browser user to see project settings and temporary variables. ::

  ADMINS = ( ('xyz', 'xyz@abc.com') )

sends all errors from the production server to the admin's email address. ::

      DATABASE_ENGINE = 'mysql'
      DATABASE_NAME = 'db-name'
      DATABASE_USER = 'user'
      DATABASE_PASSWORD = 'password'
      DATABASE_HOST = 'mysql-host'
      DATABASE_PORT = ''

sets up the options required for Django to connect to your database. ::

     MEDIA_ROOT = os.path.join(APPLICATION_DIR, 'static')

tells Django where to find your media files such as images that the ``HTML
templates`` might use. ::

     ROOT_URLCONF = 'urls'

tells Django to start finding URL matches at in the ``urls.py`` module in the ``newfies`` project folder. ::

      TEMPLATE_DIRS = ( os.path.join(APPLICATION_DIR, 'templates'), )

tells Django where to find your HTML template files. ::

     INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    ...
    'dialer_gateway',
    'dialer_campaign',
    'dialer_cdr',
    'dialer_settings',
    'user_profile',
    'voip_server',
    'voip_app',
    ...
    )

tells Django which applications (custom and external) to use in your project.
The custom applications, ``dialer_gateway``, ``dialer_campaign`` etc. are stored
in the project folder along with these custom applications.

----------------
The URLs modules
----------------

The defined URL patterns for the CPI Pilot project are divided into URL patterns specific to the project and URL patterns specific to the applications. For more information on how the pattern matching syntax work or how to write your own url patterns please consult Django's `URL Dispatcher <http://docs.djangoproject.com/en/dev/topics/http/urls/>`_ documentation.


Project specific URL patterns
-----------------------------

The URL patterns specific to the project are applied in the ``urls.py`` file that is
stored in the project directory ``newfies``. The code segments that add these URL
patterns aren't lengthy and are shown below::

  urlpatterns = patterns('',
    # redirect
    ('^$', 'django.views.generic.simple.redirect_to', {'url': '/dialer_campaign/'}),
    (r'^admin/', include(admin.site.urls)),
    (r'^api/dialer_campaign/', include('dialer_campaign.api.urls')),
    (r'^dialer_campaign/', include('dialer_campaign.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
  )


Application specific URL patterns
---------------------------------

The URL patterns specific to the dialer_campaign application are applied in the
``/dialer_campaign/urls.py`` file in the dialer_campaign application folder.
The code segment that adds these URL patterns isn't lengthy either and is shown below::

  urlpatterns = patterns('dialer_campaign.views',
    (r'^phonebook/$', 'phonebook_list'),
    (r'^phonebook/add/$', 'phonebook_add'),
    (r'^phonebook/(.+)/$', 'phonebook_change'),
  )

----------------
The Views module
----------------

The functions defined in ``views.py`` represent the logic behind the webpages.
The view functions (called through the URL matching) decide which data structures need to
be constructed and sent through to the HTML templates.
To do this, each view function uses Django's object relational model (ORM) to query
the database picking out what is needed for any particular page.

.. code-block:: python

    @login_required
    def phonebook_add(request):
        """
        Add new Phonebook
        """
        form = PhonebookForm()
        if request.method == 'POST':
            form = PhonebookForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.user = User.objects.get(username=request.user)
                obj.save()
                request.session["msg"] = _('"%s" is added successfully.' %\
                request.POST['name'])
                return HttpResponseRedirect('/dialer_campaign/phonebook/')
        template = 'dialer_campaign/phonebook/change.html'
        data = {
           'form': form,
           'action': 'add',
        }
        return render_to_response(template, data,
               context_instance=RequestContext(request))

----------------
The Admin Module
----------------

The classes defined in ``admin.py`` tell Django what attributes
are visible and modifiable from the admin site.

Code for naming convention (e.g. Voip -> VoIP) (in admin.py)

**Example:**
::

    def get_urls(self):
        urls = super(VoipAppAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^add/$', self.admin_site.admin_view(self.add_view)),
        )
        return my_urls + urls

    def add_view(self, request, extra_context=None):
        ctx = {
            'app_label': _('VoIP'),
            'title': _('Add VoIP'),
        }
        return super(VoipAppAdmin, self)\
               .add_view(request, extra_context=ctx)

