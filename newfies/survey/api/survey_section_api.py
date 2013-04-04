# -*- coding: utf-8 -*-

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

from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie import fields
from api.audiofile_api import AudioFileResource
from survey.api.survey_api import SurveyResource
from survey.models import Survey_template, Section_template
from survey.constants import SECTION_TYPE
from audiofield.models import AudioFile
import logging

logger = logging.getLogger('newfies.filelog')


class SectionValidation(Validation):
    """
    Section Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        survey_id = bundle.data.get('survey')
        if survey_id and survey_id != '':
            try:
                Survey_template.objects.get(id=survey_id).id
                bundle.data['survey'] = survey_id
            except:
                errors['survey'] = "The Survey ID doesn't exist!"
        else:
            errors['survey'] = "Enter survey id"

        if not bundle.data.get('question'):
            errors['question'] = "Please add question field"

        return errors


class SectionResource(ModelResource):
    """
    **Attributes**:

        * ``type`` - section type
        * ``question`` - question
        * ``script`` - text that will be used in TTS
        * ``audiofile`` - audio file to be use instead of TTS
        * ``invalid_audiofile`` - audio to play when input is invalid
        * ``retries`` - amount of time to retry to get a valid input
        * ``timeout`` - time to wait for user input
        * ``key_0`` - on multi choice section, text for result on key 0
        * ``key_1`` - on multi choice section, text for result on key 1
        * ``key_2`` - on multi choice section, text for result on key 2
        * ``key_3`` - on multi choice section, text for result on key 3
        * ``key_4`` - on multi choice section, text for result on key 4
        * ``key_5`` - on multi choice section, text for result on key 5
        * ``key_6`` - on multi choice section, text for result on key 6
        * ``key_7`` - on multi choice section, text for result on key 7
        * ``key_8`` - on multi choice section, text for result on key 8
        * ``key_9`` - on multi choice section, text for result on key 9
        * ``rating_laps`` - From 1 to X, value to accept rating input
        * ``validate_number`` - check if we want to valid the input on Enter Number section
        * ``number_digits`` - Number of digits to wait for on Enter Number section
        * ``min_number`` - if validate_number the minimum number accepted
        * ``max_number`` - if validate_number the maximum number accepted
        * ``phonenumber`` - phonenumber to dialout
        * ``conference`` - conference pin
        * ``queue`` - queue
        * ``completed`` - reaching this section will mark the subscriber as completed

    **Validation**:

        * SectionValidation()

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"type": 1, "question": "survey que", "survey": 1}' http://localhost:8000/api/v1/section/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/section/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/section/?format=json

        Response::

            {
               "meta":{
                  "limit":20,
                  "next":null,
                  "offset":0,
                  "previous":null,
                  "total_count":4
               },
               "objects":[
                  {
                     "created_date":"2012-09-13T08:06:05.344297",
                     "phonenumber":null,
                     "conference":null,
                     "id":"15",
                     "key_0":null,
                     "key_1":null,
                     "key_2":null,
                     "key_3":null,
                     "key_4":null,
                     "key_5":null,
                     "key_6":null,
                     "key_7":null,
                     "key_8":null,
                     "key_9":null,
                     "max_number":100,
                     "min_number":1,
                     "number_digits":null,
                     "order":1,
                     "script":"this is test question hello",
                     "question":"this is test question",
                     "rating_laps":null,
                     "resource_uri":"/api/v1/section/15/",
                     "retries":0,
                     "survey":{
                        "created_date":"2012-09-13T08:05:51.458779",
                        "description":"",
                        "id":"2",
                        "name":"sample survey",
                        "order":1,
                        "resource_uri":"/api/v1/survey/2/",
                        "updated_date":"2012-09-14T07:56:30.304371",
                        "user":{
                           "first_name":"",
                           "id":"1",
                           "last_login":"2012-09-11T09:14:16.986223",
                           "last_name":"",
                           "resource_uri":"/api/v1/user/1/",
                           "username":"areski"
                        }
                     },
                     "timeout":null,
                     "type":1,
                     "updated_date":"2012-09-13T08:06:14.565249",
                     "use_audiofile":false,
                     "validate_number":true
                  }
               ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"question": "survey que", "type": "1", "survey": 1}' http://localhost:8000/api/v1/section/%section_id%/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us


    **Delete**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/section/%section_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/section/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    survey = fields.ForeignKey(SurveyResource, 'survey')
    audiofile = fields.ForeignKey(AudioFileResource, 'audiofile',
        null=True, blank=True)

    class Meta:
        queryset = Section_template.objects.all()
        resource_name = 'section'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = SectionValidation()
        # default 1000 calls / hour
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600)

    def full_hydrate(self, bundle, request=None):
        bundle.obj.survey = Survey_template.objects.get(pk=bundle.data.get('survey'))

        if bundle.data.get('audiofile'):
            bundle.obj.audiofile = AudioFile.objects.get(pk=bundle.data.get('audiofile'))

        if bundle.data.get('type'):
            bundle.obj.type = bundle.data.get('type')
        if bundle.data.get('question'):
            bundle.obj.question = bundle.data.get('question')
        if bundle.data.get('script'):
            bundle.obj.script = bundle.data.get('script')
        if bundle.data.get('timeout'):
            bundle.obj.timeout = bundle.data.get('timeout')
        if bundle.data.get('retries'):
            bundle.obj.retries = bundle.data.get('retries')

        if bundle.data.get('key_0'):
            bundle.obj.key_0 = bundle.data.get('key_0')
        if bundle.data.get('key_1'):
            bundle.obj.key_1 = bundle.data.get('key_1')
        if bundle.data.get('key_2'):
            bundle.obj.key_2 = bundle.data.get('key_2')
        if bundle.data.get('key_3'):
            bundle.obj.key_3 = bundle.data.get('key_3')
        if bundle.data.get('key_4'):
            bundle.obj.key_4 = bundle.data.get('key_4')
        if bundle.data.get('key_5'):
            bundle.obj.key_5 = bundle.data.get('key_5')
        if bundle.data.get('key_6'):
            bundle.obj.key_6 = bundle.data.get('key_6')
        if bundle.data.get('key_7'):
            bundle.obj.key_7 = bundle.data.get('key_7')
        if bundle.data.get('key_8'):
            bundle.obj.key_8 = bundle.data.get('key_8')
        if bundle.data.get('key_9'):
            bundle.obj.key_9 = bundle.data.get('key_9')


        if bundle.data.get('rating_laps'):
            bundle.obj.rating_laps = bundle.data.get('rating_laps')
        if bundle.data.get('validate_number'):
            bundle.obj.validate_number = bundle.data.get('validate_number')
        if bundle.data.get('number_digits'):
            bundle.obj.number_digits = bundle.data.get('number_digits')

        if bundle.data.get('min_number'):
            bundle.obj.min_number = bundle.data.get('min_number')
        if bundle.data.get('max_number'):
            bundle.obj.max_number = bundle.data.get('max_number')

        if bundle.data.get('phonenumber'):
            bundle.obj.phonenumber = bundle.data.get('phonenumber')
        if bundle.data.get('conference'):
            bundle.obj.conference = bundle.data.get('conference')
        if bundle.data.get('queue'):
          bundle.obj.queue = bundle.data.get('queue')

        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        logger.debug('Section API get called')

        self.is_valid(bundle)
        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        bundle = self.full_hydrate(bundle)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        bundle.obj.save()

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        logger.debug('Section API : Result ok 200')
        return bundle

