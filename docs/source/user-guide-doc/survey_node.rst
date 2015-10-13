.. _survey-nodes:

============
Survey Nodes
============


.. contents::
    :local:
    :depth: 2


Most survey nodes have similar attributes that include:

 - Section Title, the title of the section and becomes the TTS (text To Speech)
 - Audio File, The sound file to be played for this node.
 - Retries, if no valid input, then the question can be asked again.
 - Timeout, the amount of time before it is considered that no input has been received.
 - Check Validity, whether the answer is deemed valid.
 - Audio Invalid Input, The audio to play when invalid input is received.
 - Survey Complete, check this field to mark the survey is complete for reporting & retry purposes.


.. _call-transfer:

Call Transfer
-------------

Used for "press one" campaigns and live lead generation. This node bridges the call to the number in the Phone Number field when the contact answers.

The field can have a telephone number or something like sofia/gateway/my.gateway/12345 which will direct the call via a specified gateway (my.gateway) to number 12345.

.. image:: ../_static/images/customer/node_call_transfer.png

In order to support screen-pops and deliver other data, there has been some data included in the SIP message

By default the following data is included in the SIP header on call transfer:
    P-CallRequest-ID is the Call request ID
    P-Contact-ID is is the Contact ID.

It is envisaged that these ID numbers can be used to do database look-ups on the Newfies-Dialer database.

Furthermore, there is a optional SIP header that can be added.

    P-Contact-Transfer-Ref:

This can be added against the Contact in the "Additional Parmeters (JSON)" field.
Simply add the "transfer_ref" keyword and string to send in the SIP message as follows:

    {"transfer_ref": "My-Unique-Ref-Number"}

In the SIP headers, you will see:

    P-CallRequest-ID: 3
    P-Contact-ID: 1
    P-Contact-Transfer-Ref: My-Unique-Ref-Number


.. _httpapi-request:

HTTP API Request
----------------

This node will make a HTTP API Request, in order to do this the UI will provide some
new features in the survey node:

    * API URL: to enter the url for the HTTP query

    * Branching based on matching results: this will allow to define match on the query results (HTTP content) and decide a branching

A list of HTTP variables will be passed out to identify the call request, e.g. contact, current variable, etc.

This is the current list of current variables passed:

    - campaign_id
    - subscriber_id
    - contact_id
    - callrequest_id
    - used_gateway_id
    - alarm_request_id
    - contact_last_name
    - contact_first_name
    - contact_email
    - contact_country
    - contact_city
    - caller_id_name
    - caller_id_number
    - destination_number
    - uuid
    - survey_id
    - current_node_id
    - record_filename


The API needs to return a valid Json with a field "api_result", eg::

    {
        "api_result": "5000"
    }

Use case, HTTP API could be used in scenarios, such validating that a call is authorized, or asking to your customer's PBX, how many agents are available.

.. image:: ../_static/images/customer/node_http_api.png


.. _capture-digits:

Capture Digits
--------------

Captures a series of digits, e.g. a telephone number or account number and stores it in the reporting. The number of digits and the minimum and maximum values can be set.

.. image:: ../_static/images/customer/node_capture_digits.png


.. _conference-node:

Conference
----------

Set up a conference with outbound calls. The default conference number in Freeswitch is 9888. The Freeswitch dialplan can be adjusted to add more conferences.

.. image:: ../_static/images/customer/node_conference.png


.. _dnc-list:

DNC
---

Do Not Call node, which will add the called contact to the DNC list configured in the campaign.

.. image:: ../_static/images/customer/node_dnc.png


.. _hangup-node:

Hangup
------

Hang up the call at the end of the survey.

.. image:: ../_static/images/customer/node_hangup.png


.. _multi-choice-node:

Multi-Choice
------------

Multi-Choice offering options 0 to 9. The value placed in the "Key X" fields appears in the survey reports.

Survey branching can be used to control the flow of the IVR depending on the key pressed.

.. image:: ../_static/images/customer/node_multi-choice.png


.. _play-message:

Play Message
------------

Play message is simply to play a message, either with TTS or pre-recorded audio.

.. image:: ../_static/images/customer/node_play_message.png


.. _rating-question:

Rating Question
---------------

Rating allows the entry of a digit or digits from 1 to X, where X is a number you select.


.. image:: ../_static/images/customer/node_rating_question.png


.. _record-message:

Record Message
--------------

.. image:: ../_static/images/customer/node_record_message.png

Record a message, the system stops recording after 3 seconds of silence, or by pressing the # key. The IVR flow will then continue.

Recordings can be listened to in the survey reports menu.


SMS Message
-----------

Play a message to the customer, either via TTS or audio file, then send an SMS message to the customer.

Note that when the campaign is created, an SMS gateway must be selected under the Dialer tab.

Reports on SMS messages can be be viewed under the Reporting section.


