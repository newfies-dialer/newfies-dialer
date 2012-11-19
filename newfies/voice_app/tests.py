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
from django.template import Template, Context
from django.test import TestCase

from dialer_campaign.models import Campaign
from dialer_gateway.models import Gateway
from voice_app.models import VoiceApp, VoiceApp_template
from voice_app.forms import VoiceAppForm
from voice_app.views import voiceapp_list, voiceapp_add,\
                            voiceapp_del, voiceapp_change,\
                            voiceapp_view
from voice_app.function_def import check_voiceapp_campaign
from utils.helper import grid_test_data
from common.utils import BaseAuthenticatedClient


class VoiceAppAdminView(BaseAuthenticatedClient):
    """Test Function to check Voice App Admin pages"""

    def test_admin_voiceapp_view_list(self):
        """Test Function to check admin voiceapp list"""
        response = self.client.get("/admin/voice_app/voiceapp_template/")
        self.assertEqual(response.status_code, 200)

    def test_admin_voiceapp_view_add(self):
        """Test Function to check admin voiceapp add"""
        response = self.client.get("/admin/voice_app/voiceapp_template/add/")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/admin/voice_app/voiceapp_template/add/',
            data={'name': 'Default_Voice_App',
                  'user': '1',
                  'gateway': '1'
                 })
        self.assertEqual(response.status_code, 200)


class VoiceAppCustomerView(BaseAuthenticatedClient):
    """Test Function to check Voice App Customer pages"""
    fixtures = ['auth_user.json', 'gateway.json', 'voiceapp_template.json',
                'voiceapp.json', 'dialer_setting.json', 'phonebook.json',
                'contact.json', 'campaign.json',]

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
                {'name': 'voice_app'}, follow=True)
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
        self.assertEqual(out, '"voice_app" added.')
        self.assertEqual(response.status_code, 302)

    def test_voiceapp_view_update(self):
        """Test Function to check voice app view to update"""
        response = self.client.get('/voiceapp/1/')
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/voiceapp/1/',
                {'name': 'voice_app'}, follow=True)
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
        self.assertEqual(out, '"voice_app" is updated.')
        self.assertEqual(response.status_code, 302)

        # delete voiceapp through voiceapp_change
        request = self.factory.post('/voiceapp/1/',
                {'delete': True}, follow=True)
        request.user = self.user
        request.session = {}
        response = voiceapp_change(request, 1)
        self.assertEqual(response['Location'], '/voiceapp/')

    def test_voiceapp_view_delete(self):
        """Test Function to check delete contact"""
        request = self.factory.get('/voiceapp/del/1/')
        request.user = self.user
        request.session = {}
        response = voiceapp_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/voiceapp/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = voiceapp_del(request, 0)
        self.assertEqual(response['Location'], '/voiceapp/')
        self.assertEqual(response.status_code, 302)

    def test_voiceapp_view(self):
        """Test Function to check delete contact"""
        request = self.factory.get('/voiceapp_view/1/')
        request.user = self.user
        request.session = {}
        response = voiceapp_view(request, 1)
        self.assertEqual(response.status_code, 200)

        check_voiceapp_campaign(request, 1)


class VoiceAppModel(TestCase):
    """Test Voice app Model"""

    fixtures = ['auth_user.json', 'gateway.json', 'voiceapp_template.json',
                'dialer_setting.json', 'phonebook.json', 'contact.json',
                'campaign.json', 'voiceapp.json', ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.gateway = Gateway.objects.get(pk=1)
        self.campaign = Campaign.objects.get(pk=1)

        self.voiceapp_template = VoiceApp_template(
            name='test voiceapp',
            type=1,
            gateway=self.gateway,
            user=self.user,
        )
        self.voiceapp_template.save()
        self.voiceapp_template.__unicode__()
        self.voiceapp_template.set_name('test voiceapp')
        self.voiceapp_template.copy_voiceapp_template(self.campaign)

        self.voiceapp = VoiceApp(
            name='test voiceapp',
            type=1,
            gateway=self.gateway,
            user=self.user,
            campaign=self.campaign,
            )
        self.voiceapp.set_name("MyVoiceapp")
        self.voiceapp.save()
        self.voiceapp.__unicode__()

    def test_voice_app_form(self):
        self.assertEqual(self.voiceapp.name, "MyVoiceapp")
        self.assertEqual(self.voiceapp.__unicode__(), u'MyVoiceapp')

        form = VoiceAppForm()
        obj = form.save(commit=False)
        obj.name = "new_voice_app"
        obj.user = self.user
        obj.description = ""
        obj.gateway = self.gateway
        obj.save()

    def teardown(self):
        self.voiceapp.delete()
        self.voiceapp_template.delete()
