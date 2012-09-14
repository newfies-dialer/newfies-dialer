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
from common.utils import BaseAuthenticatedClient
from survey2.models import Survey, Section, Branching, Result, \
    ResultAggregate
from survey2.forms import SurveyForm, VoiceSectionForm,\
    MultipleChoiceSectionForm, RatingSectionForm,\
    EnterNumberSectionForm, RecordMessageSectionForm,\
    PatchThroughSectionForm, BranchingForm, PhrasingForm,\
    SurveyDetailReportForm
from survey2.views import survey_list, survey_grid, survey_add, \
    survey_change, survey_del, section_add, section_change,\
    section_phrasing_change, section_branch_change, survey_report,\
    survey_finestatemachine, export_surveycall_report
from survey2.ajax import section_sort
from utils.helper import grid_test_data
from datetime import datetime
import simplejson


class SurveyAdminView(BaseAuthenticatedClient):
    """Test Function to check Survey, SurveyQuestion,
       SurveyResponse Admin pages
    """

    def test_admin_survey_view_list(self):
        """Test Function to check admin surveyapp list"""
        response = self.client.get('/admin/survey2/survey/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_survey_view_add(self):
        """Test Function to check admin surveyapp add"""
        response = self.client.get('/admin/survey2/survey/add/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_survey_section_view_list(self):
        """Test Function to check admin surveyquestion list"""
        response = self.client.get('/admin/survey2/section/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_survey_section_view_add(self):
        """Test Function to check admin surveyquestion add"""
        response = self.client.get('/admin/survey2/section/add/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_survey_branching_view_list(self):
        """Test Function to check admin surveyresponse list"""
        response = self.client.get('/admin/survey2/branching/')
        self.failUnlessEqual(response.status_code, 200)


class SurveyCustomerView(BaseAuthenticatedClient):
    """Test Function to check Survey, SurveyQuestion,
       SurveyResponse Customer pages
    """

    fixtures = ['auth_user.json', 'gateway.json', 'voiceapp.json',
                'dialer_setting.json', 'phonebook.json', 'contact.json',
                'campaign.json', 'campaign_subscriber.json',
                'callrequest.json',
                'survey.json', 'section.json', 'branching.json',
                'user_profile.json']

    def test_survey_view_list(self):
        """Test Function survey view list"""
        request = self.factory.post('/survey2_grid/', grid_test_data)
        request.user = self.user
        request.session = {}
        response = survey_grid(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/survey2/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/survey2/survey_list.html')

        request = self.factory.get('/survey2/')
        request.user = self.user
        request.session = {}
        response = survey_list(request)
        self.assertEqual(response.status_code, 200)

    def test_survey_view_add(self):
        """Test Function survey view add"""
        response = self.client.get('/survey2/add/')
        self.assertTrue(response.context['form'], SurveyForm())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/survey2/survey_change.html')

        request = self.factory.post('/survey2/add/',
                {'name': 'test_survey'}, follow=True)
        request.user = self.user
        request.session = {}
        response = survey_add(request)
        self.assertEqual(response.status_code, 302)

    def test_survey_view_update(self):
        """Test Function survey view get"""
        response = self.client.get('/survey2/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/survey2/survey_change.html')

        request = self.factory.post('/survey2/1/',
                {'name': 'test_survey'}, follow=True)
        request.user = self.user
        request.session = {}
        response = survey_change(request, 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/survey2/')

        response = survey_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/survey2/1/', follow=True)
        request.user = self.user
        request.session = {}
        response = section_sort(request, 1, 2)
        self.assertTrue(response)


    def test_survey_view_delete(self):
        """Test Function to check delete survey"""
        request = self.factory.get('/survey2/del/1/')
        request.user = self.user
        request.session = {}
        response = survey_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/survey2/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = survey_del(request, 0)
        self.assertEqual(response['Location'], '/survey2/')
        self.assertEqual(response.status_code, 302)


class SurveyModel(TestCase):
    """Test Survey, Section, Branching, Result, ResultAggregate Model"""

    fixtures = ['gateway.json', 'auth_user.json', 'contenttype.json',
                'phonebook.json', 'contact.json',
                'campaign.json', 'campaign_subscriber.json',
                'survey.json', 'section.json', 'branching.json',
                'callrequest.json']

    def setUp(self):
        self.user = User.objects.get(username='admin')

        # Survey model
        self.survey = Survey(
            name='test_survey',
            user=self.user,
        )
        self.survey.save()
        self.assertEqual(self.survey.__unicode__(), u'test_survey')

        # Section model
        self.section = Section(
            question='test_question',
            survey=self.survey,
        )
        self.section.save()
        self.assertEqual(self.section.__unicode__(), u'[4] test_question')


        # Branching model
        self.branching = Branching(
            keys=5,
            section=self.section,
        )
        self.branching.save()
        self.assertEqual(self.branching.__unicode__(), u'[3] 5')

        self.section.get_branching_count_per_section()

        # Result model
        self.result = Result(
            survey=self.survey,
            campaign_id=1,
            section=self.section,
            callrequest_id=None,
            response='xyz'
        )
        self.result.save()
        self.assertEqual(
            self.result.__unicode__(), u'[1] [4] test_question = xyz')

        # ResultAggregate model
        self.result_aggregate = ResultAggregate(
            survey=self.survey,
            campaign_id=1,
            section=self.section,
            count=1,
            response='xyz'
        )
        self.result_aggregate.save()
        self.assertEqual(
            self.result_aggregate.__unicode__(), u'[1] [4] test_question = xyz')

    def test_survey_forms(self):
        self.assertEqual(self.survey.name, "test_survey")
        self.assertEqual(self.section.survey, self.survey)
        self.assertEqual(self.branching.section, self.section)
        self.assertEqual(self.result.survey, self.survey)

        form = VoiceSectionForm(self.user, instance=self.section)
        obj = form.save(commit=False)
        obj.question = "test question"
        obj.type = 1
        obj.survey = self.survey
        obj.save()

        form = BranchingForm(self.survey.id, self.section.id)
        obj = form.save(commit=False)
        obj.keys = 0
        obj.section = self.section
        obj.goto = self.section
        obj.save()

        form = MultipleChoiceSectionForm(self.user, instance=self.section)
        obj = form.save(commit=False)
        obj.type = 2
        obj.question = "test question"
        obj.key_0 = "apple"
        obj.survey = self.survey
        obj.save()

        form = BranchingForm(self.survey.id, self.section.id)
        obj = form.save(commit=False)
        obj.keys = 1
        obj.section = self.section
        obj.goto = self.section
        obj.save()

        form = RatingSectionForm(self.user,
                                 instance= self.section)
        obj = form.save(commit=False)
        obj.type = 3
        obj.question = "test question"
        obj.rating_laps = 5
        obj.survey = self.survey
        obj.save()

        form = BranchingForm(self.survey.id, self.section.id)
        obj = form.save(commit=False)
        obj.keys = 2
        obj.section = self.section
        obj.goto = self.section
        obj.save()

        form = EnterNumberSectionForm(self.user,
                                      instance=self.section)
        obj = form.save(commit=False)
        obj.type = 4
        obj.question = "test question"
        obj.number_digits = 2
        obj.min_number = 1
        obj.max_number = 100
        obj.survey = self.survey
        obj.save()

        form = BranchingForm(2, 2)
        obj = form.save(commit=False)
        obj.keys = 3
        obj.section = self.section
        obj.goto = self.section
        obj.save()

        form = RecordMessageSectionForm(self.user)
        obj = form.save(commit=False)
        obj.type = 5
        obj.question = "test question"
        obj.continue_survey = 1
        obj.survey = self.survey
        obj.save()

        form = PatchThroughSectionForm(self.user)
        obj = form.save(commit=False)
        obj.type = 6
        obj.question = "test question"
        obj.dial_phonenumber = 1234567890
        obj.survey = self.survey
        obj.save()

        form = PhrasingForm()
        obj = form.save(commit=False)
        obj.phrasing = 'xyz'
        obj.survey = self.survey
        obj.save()

        form = SurveyDetailReportForm(self.user,
                                      initial={'campaign': 1})

    def teardown(self):
        self.survey.delete()
        self.section.delete()
        self.branching.delete()
        self.result.delete()
        self.result_aggregate.delete()
