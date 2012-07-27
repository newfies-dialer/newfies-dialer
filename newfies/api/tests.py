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

from common.test_utils import BaseAuthenticatedClient
import simplejson


class ApiTestCase(BaseAuthenticatedClient):
    """Test cases for Newfies-Dialer API."""
    fixtures = ['gateway.json', 'voiceapp', 'phonebook', 
                'dialer_setting', 'campaign', 'campaign_subscriber',
                'callrequest', 'survey', 'survey_question',
                'survey_response']

    def test_create_campaign(self):
        """Test Function to create a campaign"""
        data = simplejson.dumps({
                "name": "mycampaign",
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
                "content_type": "voice_app",
                "object_id": "1",
                "extra_data": "2000",
                "phonebook_id": "1"})
        response = self.client.post('/api/v1/campaign/',
            data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

    def test_read_campaign(self):
        """Test Function to get all campaigns"""
        response = self.client.get('/api/v1/campaign/?format=json',
                   **self.extra)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/v1/campaign/1/?format=json',
                   **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_update_campaign(self):
        """Test Function to update a campaign"""
        response = self.client.put('/api/v1/campaign/1/',
                   simplejson.dumps({
                        "status": "2",
                        "content_type": "voice_app",
                        "object_id": "1"}),
                   content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 204)

    def test_delete_campaign(self):
        """Test Function to delete a campaign"""
        response = self.client.delete('/api/v1/campaign/1/',
        **self.extra)
        self.assertEqual(response.status_code, 204)

    def test_delete_cascade_campaign(self):
        """Test Function to cascade delete a campaign"""
        response = \
        self.client.delete('/api/v1/campaign_delete_cascade/1/',
        **self.extra)
        self.assertEqual(response.status_code, 204)

    def test_create_phonebook(self):
        """Test Function to create a phonebook"""
        data = simplejson.dumps({"name": "mylittlephonebook",
                "description": "Test",
                "campaign_id": "1"})
        response = self.client.post('/api/v1/phonebook/', data,
                   content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

    def test_read_phonebook(self):
        """Test Function to get all phonebooks"""
        response = self.client.get('/api/v1/phonebook/',
        **self.extra)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/v1/phonebook/1/',
        **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_create_bulk_contact(self):
        """Test Function to bulk create contacts"""
        data = simplejson.dumps({"phoneno_list": "12345,54344",
                "phonebook_id": "1"})
        response = self.client.post('/api/v1/bulkcontact/',
        data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

    def test_create_campaign_subscriber(self):
        """Test Function to create a campaign subscriber"""
        data = simplejson.dumps({
                "contact": "650784355",
                "last_name": "belaid",
                "first_name": "areski",
                "email": "areski@gmail.com",
                "phonebook_id": "1"})
        response = self.client.post('/api/v1/campaignsubscriber/',
        data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

    def test_read_campaign_subscriber(self):
        """Test Function to get all campaign subscriber"""
        response = self.client.get('/api/v1/campaignsubscriber/1/?format=json',
                   **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_update_campaign_subscriber(self):
        """Test Function to update a campaign subscriber"""
        data = simplejson.dumps({"status": "1",
                "contact": "640234000"})
        response = self.client.put('/api/v1/campaignsubscriber/1/',
                   data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 204)

    def test_create_callrequest(self):
        """Test Function to create a callrequest"""
        data = simplejson.dumps({
                    "request_uuid": "df8a8478-cc57-11e1-aa17-00231470a30c",
                    "call_time": "2011-05-01 11:22:33",
                    "phone_number": "8792749823",
                    "content_type": "voice_app",
                    "object_id": "1",
                    "timeout": "30000",
                    "callerid": "650784355",
                    "call_type": "1"})
        response = self.client.post('/api/v1/callrequest/',
        data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

    def test_read_callrequest(self):
        """Test Function to get all callrequests"""
        response = self.client.get('/api/v1/callrequest/?format=json',
        **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_create_answercall(self):
        """Test Function to create a answercall"""
        data = {"ALegRequestUUID": "e8fee8f6-40dd-11e1-964f-000c296bd875",
                "CallUUID": "e8fee8f6-40dd-11e1-964f-000c296bd875"}
        response = self.client.post('/api/v1/answercall/', data, **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_create_hangupcall(self):
        """Test Function to create a hangupcall"""
        data = {"RequestUUID": "e8fee8f6-40dd-11e1-964f-000c296bd875",
         "HangupCause": "SUBSCRIBER_ABSENT"}
        response = self.client.post('/api/v1/hangupcall/', data, **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_create_cdr(self):
        """Test Function to create a CDR"""
        data = ('cdr=<?xml version="1.0"?><cdr><other></other><variables><plivo_request_uuid>e8fee8f6-40dd-11e1-964f-000c296bd875</plivo_request_uuid><duration>3</duration></variables><notvariables><plivo_request_uuid>TESTc</plivo_request_uuid><duration>5</duration></notvariables></cdr>')
        response = self.client.post('/api/v1/store_cdr/', data,
                        content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_create_survey(self):
        """Test Function to create a survey"""
        data = simplejson.dumps({"name": "mysurvey",
                "description": "Test"})
        response = self.client.post('/api/v1/survey/', data,
                   content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

    def test_read_survey(self):
        """Test Function to get all surveys"""
        response = self.client.get('/api/v1/survey/?format=json',
        **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_update_survey(self):
        """Test Function to update a survey"""
        data = simplejson.dumps({
                "name": "mysurvey",
                "description": "test",
                "user": "1"})
        response = self.client.put('/api/v1/survey/1/',
                   data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 204)

    def test_create_survey_question(self):
        """Test Function to create a survey question"""
        data = simplejson.dumps({
                "question": "survey que",
                "tags": "",
                "user": "1",
                "surveyapp": "1",
                "message_type": "1"})
        response = self.client.post('/api/v1/survey_question/', data,
                   content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

    def test_read_survey_question(self):
        """Test Function to get all survey questions"""
        response = self.client.get('/api/v1/survey_question/?format=json',
        **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_update_survey_question(self):
        """Test Function to update a survey question"""
        data = simplejson.dumps({
                "question": "survey que",
                "tags": "",
                "surveyapp": "1",
                "message_type": "1"})
        response = self.client.put('/api/v1/survey_question/1/',
                   data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 204)

    def test_create_survey_response(self):
        """Test Function to create a survey response"""
        data = simplejson.dumps({"key": "orange",
                "keyvalue": "1",
                "surveyquestion": "1"})
        response = self.client.post('/api/v1/survey_response/', data,
                   content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 201)

    def test_read_survey_response(self):
        """Test Function to get all survey response"""
        response = self.client.get('/api/v1/survey_response/?format=json',
        **self.extra)
        self.assertEqual(response.status_code, 200)

    def test_update_survey_response(self):
        """Test Function to update a survey response"""
        data = simplejson.dumps({"key": "Apple",
                "keyvalue": "1",
                "surveyquestion": "1"})
        response = self.client.put('/api/v1/survey_response/1/',
                   data, content_type='application/json', **self.extra)
        self.assertEqual(response.status_code, 204)
