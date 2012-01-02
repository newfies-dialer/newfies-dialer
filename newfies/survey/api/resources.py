try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from django.contrib.auth.models import User

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import Authentication, BasicAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie import http
from tastypie import fields

from survey.models import SurveyApp, SurveyQuestion, SurveyResponse


class UserResource(ModelResource):
    class Meta:
        allowed_methods = ['get']
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'last_login', 'id']
        filtering = {
            'username': 'exact',
        }
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour


class SurveyAppValidation(Validation):
    """SurveyApp Validation Class"""
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        return errors


class SurveyAppResource(ModelResource):
    """
    **Attributes**:

        * ``name`` -
        * ``description`` -
        * ``user_id`` - User ID


    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "surveyname", "description": ""}' http://localhost:8000/api/v1/survey/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/survey/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/survey/?format=json

        Response::

            {
               "meta":{
                  "limit":20,
                  "next":null,
                  "offset":0,
                  "previous":null,
                  "total_count":1
               },
               "objects":[
                  {
                     "created_date":"2011-04-08T07:55:05",
                     "description":"This is default phone book",
                     "id":"1",
                     "name":"survey name",
                     "resource_uri":"/api/v1/survey/1/",
                     "updated_date":"2011-04-08T07:55:05",
                     "user":{
                        "first_name":"",
                        "id":"1",
                        "last_login":"2011-10-11T01:03:42",
                        "last_name":"",
                        "resource_uri":"/api/v1/user/1/",
                        "username":"areski"
                     }
                  }
               ]
            }


    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"name": "survey name", "description": ""}' http://localhost:8000/api/v1/survey/%survey_id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey/%survey_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    """
    user = fields.ForeignKey(UserResource, 'user', full=True)
    class Meta:
        queryset = SurveyApp.objects.all()
        resource_name = 'survey'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = SurveyAppValidation() 
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour


class SurveyQuestionValidation(Validation):
    """
    SurveyQuestion Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        surveyapp_id = bundle.data.get('surveyapp')
        if surveyapp_id:
            try:
                surveyapp_id = SurveyApp.objects.get(id=surveyapp_id).id
                bundle.data['surveyapp'] = '/api/v1/survey/%s/' % surveyapp_id
            except:
                errors['survey'] = ["The Survey app ID doesn't exist!"]

        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        return errors


class SurveyQuestionResource(ModelResource):
    """
    **Attributes**:

        * ``question`` -
        * ``tags`` -
        * ``user`` - User ID
        * ``surveyapp`` - surveyapp ID
        * ``audio_message``
        * ``message_type``


    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"question": "survey que", "tags": "", "user": "1", "surveyapp": "1", "message_type": "1"}' http://localhost:8000/api/v1/survey_question/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/survey_question/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/survey_question/?format=json

        Response::

        {
            "meta":{
              "limit":20,
              "next":null,
              "offset":0,
              "previous":null,
              "total_count":2
            },
            "objects":[
              {
                 "created_date":"2011-12-15T13:10:49",
                 "id":"1",
                 "message_type":1,
                 "order":1,
                 "question":"Test Servey Qus",
                 "resource_uri":"/api/v1/survey_question/1/",
                 "surveyapp":{
                    "created_date":"2011-12-15T09:55:25",
                    "description":"",
                    "id":"5",
                    "name":"new test",
                    "order":2,
                    "resource_uri":"/api/v1/survey/5/",
                    "updated_date":"2011-12-15T09:55:25",
                    "user":{
                       "first_name":"",
                       "id":"1",
                       "last_login":"2011-12-14T07:26:00",
                       "last_name":"",
                       "resource_uri":"/api/v1/user/1/",
                       "username":"areski"
                    }
                 },
                 "tags":"",
                 "updated_date":"2011-12-15T13:10:49",
                 "user":{
                    "first_name":"",
                    "id":"1",
                    "last_login":"2011-12-14T07:26:00",
                    "last_name":"",
                    "resource_uri":"/api/v1/user/1/",
                    "username":"areski"
                 }
              },
            ]
        }


    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"question": "survey que", "tags": "", "user": "1", "surveyapp": "1", "message_type": "1"}' http://localhost:8000/api/v1/survey_question/%survey_question_id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey_question/%survey_question_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey_question/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    """
    user = fields.ForeignKey(UserResource, 'user', full=True)
    surveyapp = fields.ForeignKey(SurveyAppResource, 'surveyapp', full=True)
    class Meta:
        queryset = SurveyQuestion.objects.all()
        resource_name = 'survey_question'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = SurveyQuestionValidation()
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour


class SurveyResponseValidation(Validation):
    """
    SurveyResponse Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        key = bundle.data.get('key')
        if key:
            dup_count = SurveyResponse.objects.filter(key=str(key)).count()
            if request.method == 'POST':
                if dup_count >= 1:
                    errors['duplicate_key'] = ["Key is already exist!"]
            if request.method == 'PUT':
                if dup_count > 1:
                    errors['duplicate_key'] = ["Key is already exist!"]

        surveyquestion_id = bundle.data.get('surveyquestion')
        if surveyquestion_id:
            try:
                surveyquestion_id = SurveyQuestion.objects.get(id=surveyquestion_id).id
                bundle.data['surveyquestion'] = '/api/v1/survey_question/%s/' % surveyquestion_id
            except:
                errors['surveyquestion'] = ["The Survey question ID doesn't exist!"]

        return errors


class SurveyResponseResource(ModelResource):
    """
    **Attributes**:

        * ``key`` -
        * ``key value`` -
        * ``surveyquestion`` - survey question ID


    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"key": "Apple", "keyvalue": "1", "surveyquestion": "1"}' http://localhost:8000/api/v1/survey_response/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/v1/survey_response/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/survey_response/?format=json

        Response::

            {
               "meta":{
                  "limit":20,
                  "next":null,
                  "offset":0,
                  "previous":null,
                  "total_count":1
               },
               "objects":[
                  {
                     "created_date":"2011-12-15T14:54:50",
                     "id":"3",
                     "key":"YES",
                     "keyvalue":"1",
                     "resource_uri":"/api/v1/survey_response/3/",
                     "surveyquestion":{
                        "created_date":"2011-12-15T13:10:49",
                        "id":"17",
                        "message_type":1,
                        "order":1,
                        "question":"Servey Qus",
                        "resource_uri":"/api/v1/survey_question/17/",
                        "surveyapp":{
                           "created_date":"2011-12-15T09:55:25",
                           "description":"",
                           "id":"5",
                           "name":"new test",
                           "order":2,
                           "resource_uri":"/api/v1/survey/5/",
                           "updated_date":"2011-12-15T14:45:46",
                           "user":{
                              "first_name":"",
                              "id":"1",
                              "last_login":"2011-12-14T07:26:00",
                              "last_name":"",
                              "resource_uri":"/api/v1/user/1/",
                              "username":"areski"
                           }
                        },
                        "tags":"",
                        "updated_date":"2011-12-15T13:10:49",
                        "user":{
                           "first_name":"",
                           "id":"1",
                           "last_login":"2011-12-14T07:26:00",
                           "last_name":"",
                           "resource_uri":"/api/v1/user/1/",
                           "username":"areski"
                        }
                     },
                     "updated_date":"2011-12-15T14:54:50"
                  }
               ]
            }


    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"key": "Apple", "keyvalue": "1", "surveyquestion": "1"}' http://localhost:8000/api/v1/survey_response/%survey_response_id%/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey_response/%survey_response_id%/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/survey_response/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    """
    surveyquestion = fields.ForeignKey(SurveyQuestionResource, 'surveyquestion', full=True)
    class Meta:
        queryset = SurveyResponse.objects.all()
        resource_name = 'survey_response'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = SurveyResponseValidation()
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour
