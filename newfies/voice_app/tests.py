#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.contrib.auth.models import User
from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase

from dialer_gateway.models import Gateway
from voice_app.models import VoiceApp
from voice_app.forms import VoiceAppForm
from voice_app.views import voiceapp_list, voiceapp_add,\
                            voiceapp_del, voiceapp_change
from common.utils import BaseAuthenticatedClient


class VoiceAppAdminView(BaseAuthenticatedClient):
    """Test Function to check Voice App Admin pages"""

    def test_admin_voiceapp_view_list(self):
        """Test Function to check admin voiceapp list"""
        response = self.client.get("/admin/voice_app/voiceapp/")
        self.assertEqual(response.status_code, 200)

    def test_admin_voiceapp_view_add(self):
        """Test Function to check admin voiceapp add"""
        response = self.client.get("/admin/voice_app/voiceapp/add/")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/admin/voice_app/voiceapp/add/',
            data={'name': 'Default_Voice_App',
                  'user': '1',
                  'gateway': '1'
                 })
        self.assertEqual(response.status_code, 200)


class VoiceAppCustomerView(BaseAuthenticatedClient):
    """Test Function to check Voice App Customer pages"""
    fixtures = ['auth_user.json', 'gateway.json', 'voiceapp.json']

    def test_voiceapp_view_list(self):
        """Test Function to check voice app list view"""
        response = self.client.get('/voiceapp/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/voiceapp/list.html')

        request = self.factory.get('/voiceapp/')
        request.user = self.user
        request.session = {}
        response = voiceapp_list(request)
        self.assertEqual(response.status_code, 200)


    def test_voiceapp_view_add(self):
        """Test Function to check voice app view to add"""
        response = self.client.get('/voiceapp/add/')
        self.assertEqual(response.context['action'], 'add')
        self.assertTrue(response.context['form'], VoiceAppForm())
        self.assertTemplateUsed(response, 'frontend/voiceapp/change.html')

        request = self.factory.post('/voiceapp/add/',
                {'name': 'vocie_app'}, follow=True)
        request.user = self.user
        request.session = {}
        response = voiceapp_add(request)
        self.assertEqual(response['Location'], '/voiceapp/')

        out = Template(
                '{% block content %}'
                    '{% if msg %}'
                        '{{ msg|safe }}'
                    '{% endif %}'
                '{% endblock %}'
            ).render(Context({
                'msg': request.session.get('msg'),
            }))
        self.assertEqual(out, '"vocie_app" is added.')
        self.assertEqual(response.status_code, 302)


    def test_voiceapp_view_update(self):
        """Test Function to check voice app view to update"""
        response = self.client.get('/voiceapp/1/')
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/voiceapp/1/',
                {'name': 'vocie_app'}, follow=True)
        request.user = self.user
        request.session = {}
        response = voiceapp_change(request, 1)
        self.assertEqual(response['Location'], '/voiceapp/')

        out = Template(
                '{% block content %}'
                    '{% if msg %}'
                        '{{ msg|safe }}'
                    '{% endif %}'
                '{% endblock %}'
            ).render(Context({
                'msg': request.session.get('msg'),
            }))
        self.assertEqual(out, '"vocie_app" is updated.')
        self.assertEqual(response.status_code, 302)

        response = voiceapp_del(request, 1)
        self.assertEqual(response.status_code, 302)


class VoiceAppModel(TestCase):
    """Test Voice app Model"""

    fixtures = ['auth_user.json', 'gateway.json', 'voiceapp.json']

    def setUp(self):
        self.user = User.objects.get(username='admin')
        self.gateway = Gateway.objects.get(pk=1)
        self.voiceapp = VoiceApp(
            name='test voiceapp',
            type=1,
            gateway=self.gateway,
            user=self.user,
            )
        self.voiceapp.set_name("MyVoiceapp")
        self.voiceapp.save()

    def test_voice_app_form(self):
        self.assertEqual(self.voiceapp.name, "MyVoiceapp")

        form = VoiceAppForm()
        obj = form.save(commit=False)
        obj.name="new_voice_app"
        obj.user = self.user
        obj.description = ""
        obj.gateway = self.gateway
        obj.save()

    def teardown(self):
        self.voiceapp.delete()
