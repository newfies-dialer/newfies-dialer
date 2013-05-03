#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from common.utils import BaseAuthenticatedClient
import json


class ApiTestCase(BaseAuthenticatedClient):
    """Test cases for Newfies-Dialer API."""
    fixtures = ['auth_user.json', 'gateway.json', 'survey_template.json',
                'dialer_setting.json', 'phonebook.json', 'contact.json',
                'campaign.json', 'subscriber.json', 'callrequest.json',
                'user_profile.json', 'dnc_list.json', 'dnc_contact.json']

    def test_create_campaign(self):
        """Test Function to create a campaign"""
        response = self.client.post('/api/v1/campaign/', dict(),
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        data = json.dumps({
            "name": "test_campaign",
            "description": "",
            "callerid": "1239876",
            "startingdate": "1301392136.0",
            "expirationdate": "1301332136.0",
            "frequency": "20",
            "callmaxduration": "50",
            "maxretry": "3",
            "intervalretry": "3000",
            "calltimeout": "45",
            "aleg_gateway": "1",
            "content_type": "survey_template",
            "object_id": "1",
            "extra_data": "2000",
            "phonebook_id": "1"
        })
        response = self.client.post('/api/v1/campaign/',
            data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

        # To test dialer settings with campaign data
        data = json.dumps({
            "name": "test_campaign",
            "description": "",
            "callerid": "1239876",
            "startingdate": "1301392136.0",
            "expirationdate": "1301332136.0",
            "frequency": "120",
            "callmaxduration": "2550",
            "maxretry": "5",
            "intervalretry": "3000",
            "calltimeout": "90",
            "aleg_gateway": "5",
            "content_type": "sms",
            "object_id": "",
            "extra_data": "2000",
            "phonebook_id": "5"
        })
        response = self.client.post('/api/v1/campaign/',
            data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        # To test new phonebook dynamically
        data = json.dumps({
            "name": "new test campaign",
            "description": "",
            "callerid": "1239876",
            "startingdate": "1301392136.0",
            "expirationdate": "1301332136.0",
            "frequency": "20",
            "callmaxduration": "50",
            "maxretry": "3",
            "intervalretry": "3000",
            "calltimeout": "45",
            "aleg_gateway": "1",
            "content_type": "survey_template",
            "object_id": "1",
            "extra_data": "2000",
            "phonebook_id": "5"
        })
        response = self.client.post('/api/v1/campaign/',
            data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

    def test_read_campaign(self):
        """Test Function to get all campaigns"""
        response = self.client.get('/api/v1/campaign/?format=json',
                   **self.extra)
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/api/v1/campaign/1/?format=json',
                   **self.extra)
        self.assertEqual(response.status_code, 400)

    def test_update_campaign(self):
        """Test Function to update a campaign"""
        response = self.client.put('/api/v1/campaign/1/',
            json.dumps({
                "status": "2",
                "content_type": "survey_template",
                "object_id": "1",
                "startingdate": "1301392136.0",
                "expirationdate": "1301332136.0"}),
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 204)

    def test_delete_campaign(self):
        """Test Function to delete a campaign"""
        response = self.client.delete('/api/v1/campaign/1/',
            **self.extra)
        self.assertEqual(response.status_code, 204)

    def test_delete_cascade_campaign(self):
        """Test Function to cascade delete a campaign"""
        response = self.client.delete('/api/v1/campaign_delete_cascade/1/',
            **self.extra)
        self.assertEqual(response.status_code, 204)

        response = self.client.delete('/api/v1/campaign_delete_cascade/2/',
            **self.extra)
        self.assertEqual(response.status_code, 204)

        response = self.client.delete('/api/v1/campaign_delete_cascade/1/',
            **self.extra)
        self.assertEqual(response.status_code, 404)

    def test_create_phonebook(self):
        """Test Function to create a phonebook"""
        data = json.dumps({"name": "mylittlephonebook",
                "description": "Test",
                "campaign_id": "1"})
        response = self.client.post('/api/v1/phonebook/', data,
                   content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/api/v1/phonebook/', {},
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        data = json.dumps({"name": "mylittlephonebook",
                                 "description": "Test",
                                 "campaign_id": "5"})
        response = self.client.post('/api/v1/phonebook/', data,
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        self.client.logout()
        self.client.login(username='admin', password='admin1')
        response = self.client.post('/api/v1/phonebook/', data,
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

    def test_read_phonebook(self):
        """Test Function to get all phonebooks"""
        response = self.client.get('/api/v1/phonebook/',
            **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_create_bulk_contact(self):
        """Test Function to bulk create contacts"""
        data = json.dumps({"phoneno_list": "12345,54344",
                                 "phonebook_id": "1"})
        response = self.client.post('/api/v1/bulkcontact/',
            data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/api/v1/bulkcontact/', {},
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        data = json.dumps({"phoneno_list": "12345,54344",
                                 "phonebook_id": "3"})
        response = self.client.post('/api/v1/bulkcontact/', data,
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        # Check duplication
        data = json.dumps({"phoneno_list": "12345,54344",
                                 "phonebook_id": "1"})
        response = self.client.post('/api/v1/bulkcontact/', data,
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

    def test_create_subscriber(self):
        """Test Function to create a subscriber"""
        data = json.dumps({
            "contact": "650784355",
            "last_name": "belaid",
            "first_name": "areski",
            "email": "areski@gmail.com",
            "phonebook_id": "1"})
        response = self.client.post('/api/v1/subscriber/',
            data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/api/v1/subscriber/', dict(),
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        data = json.dumps({
            "contact": "650784355",
            "phonebook_id": "3"
        })
        response = self.client.post('/api/v1/subscriber/', data,
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

    def test_read_subscriber(self):
        """Test Function to get all subscriber"""
        response = self.client.get('/api/v1/subscriber/1/?format=json',
            **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_update_subscriber(self):
        """Test Function to update a subscriber"""
        data = json.dumps({"status": "1",
                                 "contact": "640234000"})
        response = self.client.put('/api/v1/subscriber/1/',
                   data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 204)

        response = self.client.put('/api/v1/subscriber/3/',
            data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        data = json.dumps({"status": "1",
                                 "contact": "640234001"})
        response = self.client.put('/api/v1/subscriber/1/',
            data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

    def test_create_callrequest(self):
        """Test Function to create a callrequest"""
        data = json.dumps({
            "request_uuid": "df8a8478-cc57-11e1-aa17-00231470a30c",
            "call_time": "2011-05-01 11:22:33",
            "phone_number": "8792749823",
            "content_type": "survey",
            "object_id": "1",
            "timeout": "30000",
            "callerid": "650784355",
            "call_type": "1"})
        response = self.client.post('/api/v1/callrequest/',
            data, content_type='application/json', **self.extra)
        #self.assertEqual(response.status_code, 201)
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/api/v1/callrequest/', {},
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        data = json.dumps({
            "request_uuid": "df8a8478-cc57-11e1-aa17-00231470a30c",
            "call_time": "2011-05-01 11:22:33",
            "phone_number": "8792749823",
            "content_type": "sms",
            "object_id": "",
            "timeout": "30000",
            "callerid": "650784355",
            "call_type": "1"})
        response = self.client.post('/api/v1/callrequest/', data,
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

    def test_read_callrequest(self):
        """Test Function to get all callrequests"""
        response = self.client.get('/api/v1/callrequest/?format=json',
            **self.extra)
        self.assertEqual(response.status_code, 200)

    # def test_create_cdr(self):
    #     """Test Function to create a CDR"""
    #     #data = ('cdr=<?xml version="1.0"?><cdr><other></other><variables><request_uuid>e8fee8f6-40dd-11e1-964f-000c296bd875</request_uuid><duration>3</duration></variables><notvariables><request_uuid>TESTc</request_uuid><duration>5</duration></notvariables></cdr>')
    #     #response = self.client.post('/api/v1/store_cdr/', data,
    #     #                content_type='application/json', **self.extra)
    #     #self.assertEqual(response.status_code, 200)

    #     response = self.client.post('/api/v1/store_cdr/', {}, **self.extra)
    #     self.assertEqual(response.status_code, 400)

    def test_subscriber_per_campaign(self):
        """Test Function subscriber per campaign"""
        response = self.client.get(
            '/api/v1/subscriber_per_campaign/1/?format=json',
            **self.extra)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/api/v1/subscriber_per_campaign/1/640234000/?format=json',
            **self.extra)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/api/v1/subscriber_per_campaign/3/?format=json',
            **self.extra)
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            '/api/v1/subscriber_per_campaign/3/640234001/?format=json',
            **self.extra)
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            '/api/v1/subscriber_per_campaign/3/640234000/?format=json',
            **self.extra)
        self.assertEqual(response.status_code, 400)

    def test_create_dnc(self):
        """Test Function to create a dnc"""
        data = json.dumps({"name": "mydnc"})
        response = self.client.post('/api/v1/dnc/', data,
                   content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/api/v1/dnc/', {},
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        data = json.dumps({"name": "mydncNew"})
        response = self.client.post('/api/v1/dnc/', data,
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        self.client.logout()
        self.client.login(username='admin', password='admin1')
        response = self.client.post('/api/v1/dnc/', data,
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

    def test_read_dnc(self):
        """Test Function to get all dnc"""
        response = self.client.get('/api/v1/dnc/',
            **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_create_dnc_contact(self):
        """Test Function to create a dnc contact"""
        data = json.dumps({"phone_number": "12345", "dnc_id": "1"})
        response = self.client.post('/api/v1/dnc_contact/', data,
                   content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/api/v1/dnc_contact/', {},
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        data = json.dumps({"phone_number": "124567"})
        response = self.client.post('/api/v1/dnc_contact/', data,
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

        self.client.logout()
        self.client.login(username='admin', password='admin1')
        response = self.client.post('/api/v1/dnc_contact/', data,
            content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 400)

    def test_read_dnc_contact(self):
        """Test Function to get all dnc contact"""
        response = self.client.get('/api/v1/dnc_contact/1/12345/',
            **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_playground_view(self):
        """Test Function to create a api list view"""
        response = self.client.get("/api-explorer/")
        self.assertEqual(response.status_code, 200)

