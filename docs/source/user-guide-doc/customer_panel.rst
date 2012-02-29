.. _customer-panel:

==============
Customer Panel
==============

User Interface :

http://localhost:8000/
This application provides a user interface for restricted management of
the User's Campaigns, Phonebooks and Subscribers. It also provides detailed
reporting of calls and message delivery.

.. contents::
    :local:
    :depth: 1

.. _customer-screenshot-features:

Screenshot with Features
========================

Index
~~~~~

Index page for the customer interface after successful login with user credentials 

.. image:: ../_static/images/customer_screenshot.png
    :width: 1000


.. _customer-phonebook-access:

Phonebook
~~~~~~~~~

The phonebook list will be displayed from the following URL. You can add a new
phonebook by clicking ``Add phonebook`` and add the name of a phonebook and its
description. Also from the phonebook list, click on the phonebook to update.

**URL**:

    * http://localhost:8000/dialer_campaign/phonebook/

.. image:: ../_static/images/customer/phonebook_list.png

To Add/Update a Phonebook for a logged in user

**URL**:

    * http://localhost:8000/dialer_campaign/phonebook/add/
    * http://localhost:8000/dialer_campaign/phonebook/1/

.. image:: ../_static/images/customer/update_phonebook.png

.. _customer-contact-access:

Contact
~~~~~~~

The contact list will be displayed from following the URL. You can add a new contact
by clicking ``Add contact`` & adding the contact details (i.e. phone number, name,
description about contact, contact status) under the logged in user's phonebook from
the phonebook list. On the contact list, click on the contact to update.


**URL**:

    * http://localhost:8000/dialer_campaign/contact/

.. image:: ../_static/images/customer/contact_list.png

To Add/Update a contact in a phonebook

**URL**:

    * http://localhost:8000/dialer_campaign/contact/add/
    * http://localhost:8000/dialer_campaign/contact/1/

.. image:: ../_static/images/customer/update_contact.png

To import bulk contacts into a phonebook, click on ``Import``.
where you can upload contacts via a CSV file under a logged in 
user's phonebook.

**URL**:

    * http://localhost:8000/dialer_campaign/contact/import/

.. image:: ../_static/images/customer/import_contact.png


.. _voice-app:

Voice Application
-----------------

A number of voice applications are provided with Newfies-Dialer. Click ``Add Voice App`` give the
voice application a name, select the type of  application from the dropdown, select the gateway
to use if the call is to be redirected, and provide the data to be used, e.g. in the case of “Speak”
this would be the words to convert to text to speech.

**URL**:

    * http://localhost:8000/voiceapp/

.. image:: ../_static/images/customer/voiceapp_list.png


To Add/Update a contact in a voice app

**URL**:

    * http://localhost:8000/voiceapp/add/
    * http://localhost:8000/voiceapp/1/

.. image:: ../_static/images/customer/update_voiceapp.png

A Number of voice applications currently supported are:-

**Dial**:
 
The dial command allows the call to be redirected another destination. In this case, Select the B-Leg
as the trunk to be used for the redirected call.
 
**Conference**:
 
Direct the contact into a conference which has previously been defined in Freeswitch. In the Data 
field, put the name or extension number.


**PlayAudio**:

PlayAudio plays a sound file that has previously been uploaded to the system.
 
The Audio is uploaded via the Audio Files menu on the top menu. Click add, then select the file on
your computer to be uploaded. The file will be renamed with a unique name. It can be played via the
web browser.
 
In the data field in the voice application, either put the full file path to the sound file. 
Typically this is /usr/share/newfies/usermedia/upload/audiofiles/audio-file-XXXX-12345678.mp3
 
However where there are multiple Freeswitch nodes and workers, the sound file can uploaded to 
Newfies-Dialer, and the Web URL placed in the Data field. Typically, this will be
  
	* http://domain.tld:8008/mediafiles/upload/audiofiles/-XXXX-12345678.mp3
	
This allows other Freeswitch nodes to download and play the audio file on demand without having to 
upload it to each node.
 
**Speak**:
  
This will call a contact, and then using the text to speech engine, which is Flite as standard, 
play the audio in the Data field.
  
**Survey**:
A survey and polling application which is described in more detail in a subsequent section.


.. _survey-app:

Survey
------

The survey application for Newfies-Dialer allows polls and surveys to be taken over the phone.

Each contact is called, and then played a sound file. After the sound file is heard, the user can
enter their answer through the phone keypad using keys 0 to 9.

Therefore before creating the survey, the first job is to upload the audio for the survey. One audio
file is required for each question.

**Uploading Audio Files**:

Select Audio Files from the top menu then click add.

Enter a name to describe the audio, then click chose file, select the file you require from your
computer, then click submit.

Note that only mp3, Wav and ogg formats are supported.

The audio file will then be uploaded and renamed so that it is unique.

**Create the Survey**:

**URL**:

    * http://localhost:8000/survey/
    * http://localhost:8000/survey/add/
    * http://localhost:8000/survey/1/

.. image:: ../_static/images/customer/survey_list.png

Select Modules from the top menu, then Survey. 

Click the add button, then give the survey a name and description, then click Submit.

A button will now appear to add a question.

In the question field, put in some text to describe the question - e.g "What is 1+1"; select the audio
file pertaining to the question which was uploaded in the previous step.

If no audio file is selected, then the system will automatically play the text in the question field 
using the text to speech engine.

Then click Add Response. A further two fields will appear named Key Digit and Key Value. In key Digit
put a number from 0 to 9 which should be pressed for this answer. In the example "What is 1+1", "2"
should be placed in the Key Digit Field" 

The Key Value field is used in the survey reports, and so in this case, you would put "Correct" as 
1+1=2. You may chose to add responses 0,1 and 3 to 9 as key digits, with key values of "Wrong" as 
these answers will then be summed up in the Survey Reports.

You can then go on to add another question, and its associated responses. On completion, click 
Update Survey.

To use the Survey in a campaign, simply create a campaign as normal, and select the Survey name in
the Application drop-down.
    
**Survey Results**    

When the survey is complete, the survey results can be inspected by clicking Reporting on the top 
and selecting Survey Results from the drop-down.

.. _customer-campaign-access:

Campaign
~~~~~~~~

The campaign list will be displayed from the following URL. You can add a new campaign for
the logged in user by clicking ``Add campaign``. When adding a campaign, it is important
to add the campaign's start and end dates with time & week-day exceptions. Select 
the gateway through which calls will be routed & phonebook(s) that are
linked with contacts from the campaign list, click on campaign to update.

**URL**:

    * http://localhost:8000/dialer_campaign/campaign/

.. image:: ../_static/images/customer/campaign_list.png

To Add/Update a Campaign for a logged in user

**URL**:

    * http://localhost:8000/dialer_campaign/campaign/add/
    * http://localhost:8000/dialer_campaign/campaign/1/

.. image:: ../_static/images/customer/update_campaign.png

.. image:: ../_static/images/customer/update_campaign_part2.png



.. _customer-dashboard-access:

Dashboard
~~~~~~~~~

Dashboard gives the information anbout campaign & its related call records

.. image:: ../_static/images/customer/customer_dashboard.png
