#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.contrib.auth.models import User
from django.test import TestCase
from django.http import Http404
from common.utils import BaseAuthenticatedClient
from django.db.models.signals import post_save
from survey.models import Survey, Survey_template, Section,\
    Section_template, Branching, Branching_template, Result, \
    ResultAggregate, post_save_add_script
from survey.forms import SurveyForm, PlayMessageSectionForm,\
    MultipleChoiceSectionForm, RatingSectionForm,\
    CaptureDigitsSectionForm, RecordMessageSectionForm,\
    CallTransferSectionForm, ScriptForm, SMSSectionForm,\
    SurveyDetailReportForm
from survey.views import survey_list, survey_add, \
    survey_change, survey_del, section_add, section_change,\
    section_script_change, section_branch_change, \
    section_branch_add, section_delete, section_script_play, \
    sealed_survey_view, survey_campaign_result, import_survey, export_survey,\
    sealed_survey_list, seal_survey
#from survey.ajax import section_sort

post_save.disconnect(post_save_add_script, sender=Section_template)


class SurveyAdminView(BaseAuthenticatedClient):
    """Test Function to check Survey, SurveyQuestion,
       SurveyResponse Admin pages
    """

    def test_admin_survey_view_list(self):
        """Test Function to check admin surveyapp list"""
        response = self.client.get('/admin/survey/survey_template/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_survey_view_add(self):
        """Test Function to check admin surveyapp add"""
        response = self.client.get('/admin/survey/survey_template/add/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_survey_section_view_list(self):
        """Test Function to check admin surveyquestion list"""
        response = self.client.get('/admin/survey/section_template/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_survey_section_view_add(self):
        """Test Function to check admin surveyquestion add"""
        response = self.client.get('/admin/survey/section_template/add/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_survey_branching_view_list(self):
        """Test Function to check admin surveyresponse list"""
        response = self.client.get('/admin/survey/branching_template/')
        self.failUnlessEqual(response.status_code, 200)

    def test_admin_survey_branching_view_add(self):
        """Test Function to check admin surveyresponse list"""
        response = self.client.get('/admin/survey/branching_template/add/')
        self.failUnlessEqual(response.status_code, 200)


class SurveyCustomerView(BaseAuthenticatedClient):
    """Test Function to check Survey, Section, Branching, Result,
       ResultAggregate Customer pages
    """

    fixtures = ['auth_user.json', 'gateway.json', 'dialer_setting.json',
                'user_profile.json',  # 'contenttype.json',
                'phonebook.json', 'contact.json',
                'dnc_list.json', 'dnc_contact.json',
                'campaign.json', 'subscriber.json',
                'callrequest.json', 'voipcall.json',
                'survey_template.json', 'survey.json',
                'section_template.json', 'section.json',
                'branching.json',
                ]

    def test_sealed_survey_view_list(self):
        """Test Function survey view list"""
        response = self.client.get('/module/sealed_survey/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/survey/sealed_survey_list.html')

        request = self.factory.get('/module/sealed_survey/')
        request.user = self.user
        request.session = {}
        response = sealed_survey_list(request)
        self.assertEqual(response.status_code, 200)

    def test_survey_view_list(self):
        """Test Function survey view list"""
        response = self.client.get('/module/survey/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/survey/survey_list.html')

        request = self.factory.get('/module/survey/')
        request.user = self.user
        request.session = {}
        response = survey_list(request)
        self.assertEqual(response.status_code, 200)

    def test_survey_view_add(self):
        """Test Function survey view add"""
        response = self.client.get('/module/survey/add/')
        self.assertTrue(response.context['form'], SurveyForm())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/survey/survey_change.html')

        request = self.factory.post('/module/survey/add/', {'name': 'test_survey'}, follow=True)
        request.user = self.user
        request.session = {}
        response = survey_add(request)
        self.assertEqual(response.status_code, 302)

    def test_survey_view_update(self):
        """Test Function survey view update"""
        response = self.client.get('/module/survey/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/survey/survey_change.html')

        request = self.factory.post('/module/survey/1/', {'name': 'test_survey'}, follow=True)
        request.user = self.user
        request.session = {}
        response = survey_change(request, 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/module/survey/')

        response = survey_del(request, 1)
        self.assertEqual(response.status_code, 302)

        #request = self.factory.post('/survey/1/')
        #request.user = self.user
        #request.session = {}
        #response = section_sort(request, 1, 1)
        #self.assertTrue(response)

    def test_survey_view_delete(self):
        """Test Function to check delete survey"""
        request = self.factory.get('/module/survey/del/1/')
        request.user = self.user
        request.session = {}
        response = survey_del(request, 1)
        self.assertEqual(response.status_code, 302)

        request = self.factory.post('/module/survey/del/', {'select': '1'})
        request.user = self.user
        request.session = {}
        response = survey_del(request, 0)
        self.assertEqual(response['Location'], '/module/survey/')
        self.assertEqual(response.status_code, 302)

    def test_survey_section_view_add(self):
        """Test Function survey section add"""
        #self.survey = Survey.objects.get(pk=1)
        request = self.factory.get('/section/add/?survey_id=1')
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 1, 'question': 'xyz', 'add': 'true'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 1, 'question': 'xyz'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 2, 'question': 'xyz', 'add': 'true',
             'key_0': 'apple'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 2, 'question': 'xyz',
             'key_0': 'apple'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 3, 'question': 'xyz', 'add': 'true',
             'rating_laps': 5}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 3, 'question': 'xyz',
             'rating_laps': 5}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 4, 'question': 'xyz', 'add': 'true',
             'number_digits': 2,
             'min_number': 1}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 4, 'question': 'xyz',
             'number_digits': 2,
             'min_number': 1}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 5, 'question': 'xyz', 'add': 'true'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 5, 'question': 'xyz'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 6, 'question': 'xyz', 'add': 'true'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/add/?survey_id=1',
            {'type': 6, 'question': 'xyz'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_add(request)
        self.assertEqual(response.status_code, 200)

    def test_survey_section_view_update(self):
        """Test Function survey section update"""
        #self.survey = Survey.objects.get(pk=1)
        request = self.factory.get('/section/1/')
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 1, 'question': 'xyz', 'update': 'true'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 1, 'question': 'xyz'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 2, 'question': 'xyz', 'update': 'true',
             'key_0': 'apple'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 2, 'question': 'xyz',
             'key_0': 'apple'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 3, 'question': 'xyz', 'update': 'true',
             'rating_laps': 5}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 3, 'question': 'xyz',
             'rating_laps': 5}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 4, 'question': 'xyz', 'update': 'true',
             'number_digits': 2,
             'min_number': 1}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 4, 'question': 'xyz',
             'number_digits': 2,
             'min_number': 1}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 5, 'question': 'xyz', 'update': 'true'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 5, 'question': 'xyz'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 6, 'question': 'xyz', 'update': 'true'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 6, 'question': 'xyz'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 10, 'question': 'test question',
             'update': 'true', 'sms_text': 'this is test sms'}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/1/',
            {'type': 10, 'question': 'xyz', 'sms_text': 'this is test sms'},
            follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

    def test_section_script_play(self):
        """Test Function survey section script play"""
        request = self.factory.get('/section/script_play/1/')
        request.user = self.user
        request.session = {}
        response = section_script_play(request, 1)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/section/script_play/1/')
        self.assertRaises(Http404)

    def test_survey_section_view_delete(self):
        """Test Function survey section delete"""
        request = self.factory.post('/section/1/?delete=true',
            {}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_change(request, 1)
        self.assertEqual(response.status_code, 200)

    def test_survey_section_delete(self):
        """Test Function survey section delete"""
        request = self.factory.post('/section/1/?delete=true',
            {}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_delete(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_survey_view(self):
        """Test Function survey view"""
        request = self.factory.get('/sealed_survey_view/1/')
        request.user = self.user
        request.session = {}
        response = sealed_survey_view(request, 1)
        self.assertEqual(response.status_code, 200)

    def test_section_script_change(self):
        """Test Function section script update"""
        request = self.factory.get('/section/script/1/')
        request.user = self.user
        request.session = {}
        response = section_script_change(request, 1)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/script/1/',
            {'script': 'xyz', 'section': 1}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_script_change(request, 1)
        self.assertEqual(response.status_code, 302)

    def test_section_branch_add(self):
        """Test Function section branching add"""
        self.section_template = Section_template.objects.get(pk=1)
        self.goto = Section_template.objects.get(pk=1)

        request = self.factory.get('/section/branch/add/?section_id=1')
        request.user = self.user
        request.session = {}
        response = section_branch_add(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/section/branch/add/?section_id=1',
            {'keys': 1, 'section': 1,
             'goto': 1})
        request.user = self.user
        request.session = {}
        response = section_branch_add(request)
        self.assertEqual(response.status_code, 200)

    def test_section_branch_change(self):
        """Test Function section branching update"""
        self.section = Section_template.objects.get(pk=1)
        self.goto = Section_template.objects.get(pk=2)

        branching_obj = Branching_template.objects.create(keys=34,
            section=self.section,
            goto=self.goto)

        request = self.factory.get('/section/branch/'+str(branching_obj.id)+'/')
        request.user = self.user
        request.session = {}
        response = section_branch_change(request, branching_obj.id)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/branch/'+str(branching_obj.id)+'/',
            {'keys': 1, 'section': self.section,
             'goto': self.goto}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_branch_change(request, branching_obj.id)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/branch/'+str(branching_obj.id)+'/',
            {}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_branch_change(request, branching_obj.id)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('/section/branch/'+str(branching_obj.id)+'/?delete=true',
            {'keys': 1, 'section': self.section,
             'goto': self.goto}, follow=True)
        request.user = self.user
        request.session = {}
        response = section_branch_change(request, branching_obj.id)
        self.assertEqual(response.status_code, 302)

    def test_survey_campaign_result(self):
        request = self.factory.get('/survey_campaign_result/1/')
        request.user = self.user
        request.session = {}
        response = survey_campaign_result(request, 1)
        self.assertEqual(response.status_code, 200)

    def test_export_survey(self):
        request = self.factory.get('/export_survey/1/')
        request.user = self.user
        request.session = {}
        response = export_survey(request, 1)
        self.assertEqual(response.status_code, 200)

    def test_import_survey(self):
        request = self.factory.get('/import_survey/')
        request.user = self.user
        request.session = {}
        response = import_survey(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/module/import_survey/',
            data={'survey_file': '', 'name': 'new survey'})
        self.assertEqual(response.status_code, 200)

    def test_seal_survey(self):
        request = self.factory.get('/module/seal_survey/1/')
        request.user = self.user
        request.session = {}
        response = seal_survey(request, 1)
        self.assertEqual(response.status_code, 200)


class SurveyModel(TestCase):
    """Test Survey, Section, Branching, Result, ResultAggregate Model"""

    fixtures = ['auth_user.json', 'gateway.json', 'dialer_setting.json',
                'user_profile.json',  # 'contenttype.json',
                'phonebook.json', 'contact.json',
                'dnc_list.json', 'dnc_contact.json',
                'campaign.json', 'subscriber.json',
                'callrequest.json', 'voipcall.json',
                'survey_template.json', 'survey.json',
                'section_template.json', 'section.json',
                'branching.json',
                ]

    def setUp(self):
        self.user = User.objects.get(username='admin')

        # Survey_template model
        self.survey_template = Survey_template(
            name='test_survey',
            user=self.user,
        )
        self.survey_template.save()

        # Survey model
        self.survey = Survey(
            name='test_survey',
            user=self.user,
        )
        self.survey.save()
        self.assertEqual(self.survey.__unicode__(), u'test_survey')

        # Section_template
        self.section_template = Section_template.objects.get(pk=1)
        self.section_template.survey.name = 'New Survey'
        self.section_template.save()

        # Section model
        self.section = Section.objects.get(pk=1)
        self.section.save()
        self.assertTrue(self.section.__unicode__())

        # Branching_template model
        self.branching_template = Branching_template(
            keys=5,
            section=self.section_template,
        )
        self.branching_template.save()

        # Branching model
        self.branching = Branching(
            keys=5,
            section=self.section,
        )
        self.branching.save()
        self.assertTrue(self.branching.__unicode__())

        # Result model
        self.result = Result(
            section=self.section,
            callrequest_id=1,
            response='apple'
        )
        self.result.save()
        self.assertEqual(
            self.result.__unicode__(), '[1] [1] call transfer = apple')

        # ResultAggregate model
        self.result_aggregate = ResultAggregate(
            survey=self.survey,
            section=self.section,
            count=1,
            response='apple'
        )
        self.result_aggregate.save()
        self.assertEqual(
            self.result_aggregate.__unicode__(), '[1] [1] call transfer = apple')

    def test_survey_forms(self):
        self.assertEqual(self.survey_template.name, "test_survey")
        #self.assertEqual(self.section_template.survey, self.survey_template)
        self.assertEqual(self.branching_template.section, self.section_template)
        self.assertEqual(self.result.section, self.section)

        form = PlayMessageSectionForm(self.user, instance=self.section_template)
        obj = form.save(commit=False)
        obj.question = "test question"
        obj.type = 1
        obj.survey = self.survey_template
        obj.save()

        form = MultipleChoiceSectionForm(self.user, instance=self.section_template)
        obj = form.save(commit=False)
        obj.type = 2
        obj.question = "test question"
        obj.key_0 = "apple"
        obj.survey = self.survey_template
        obj.save()

        form = RatingSectionForm(self.user,
                                 instance=self.section_template)
        obj = form.save(commit=False)
        obj.type = 3
        obj.question = "test question"
        obj.rating_laps = 5
        obj.survey_template = self.survey_template
        obj.save()

        form = CaptureDigitsSectionForm(self.user,
                                        instance=self.section_template)
        obj = form.save(commit=False)
        obj.type = 4
        obj.question = "test question"
        obj.number_digits = 2
        obj.min_number = 1
        obj.max_number = 100
        obj.survey = self.survey_template
        obj.save()

        form = RecordMessageSectionForm(self.user)
        obj = form.save(commit=False)
        obj.type = 5
        obj.question = "test question"
        obj.survey = self.survey_template
        obj.save()

        form = CallTransferSectionForm(self.user)
        obj = form.save(commit=False)
        obj.type = 6
        obj.question = "test question"
        obj.phonenumber = 1234567890
        obj.survey = self.survey_template
        obj.save()

        form = SMSSectionForm(self.user)
        obj = form.save(commit=False)
        obj.type = 10
        obj.question = "sms question"
        obj.sms_text = "this is test sms"
        obj.survey = self.survey_template
        obj.save()

        form = ScriptForm()
        obj = form.save(commit=False)
        obj.script = 'xyz'
        obj.survey = self.survey_template
        obj.save()

        form = SurveyDetailReportForm(self.user)

    def teardown(self):
        self.survey_template.delete()
        self.survey.delete()
        self.section_template.delete()
        self.section.delete()
        self.branching_template.delete()
        self.branching.delete()
        self.result.delete()
        self.result_aggregate.delete()
