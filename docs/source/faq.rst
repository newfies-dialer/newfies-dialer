.. _faq:

==========================
Frequently Asked Questions
==========================

.. contents::
    :local:
    :depth: 2

.. _faq-general:

General
=======


.. _faq-what-is-newfies-dialer:

What is Newfies-Dialer
----------------------

**Answer:**

Newfies-Dialer is a voice broadcast application designed and built to automate the delivery of interactive phone calls to contacts, clients and the general public.


.. _faq-why-should-use-newfies-dialer:

Why should I use Newfies-Dialer
-------------------------------

**Answer:**

Below are some examples of some of the uses that Newfies-Dialer can be put to. There are more details and examples at http://www.newfies-dialer.org/solutions/

* **Telecasting**:

    Broadcast marketing or informational messages to customers and clients.


* **Phone Polling, Surveys and Voting**:

    Ring large numbers of people and present IVR options for either polling their opinions, interactive surveys, or taking their vote and record the results.

* **Debt Control**:

    Customers can be automatically reminded at intervals that they owe money, and an IVR menu presented to talk to the finance department or passed to a credit card capture IVR to pay over the phone.

* **Appointment reminders**:

    Doctors, Dentists, and other organisations that make appointments for their clients can integrate Newfies-Dialer into their appointment systems to pass a message reminding them of an upcoming appointment.

* **Dissemination of Information by Phone**:

    Newfies-Dialer was originally designed to call large numbers of people and disseminate medical and health advice via the ubiquitous cellphone in 3rd world countries where often, literacy levels are low.

* **Mass Emergency Broadcasting**:

        Where there is a necessity to warn large numbers of people in a short space of time, such as weather warnings.


* **Subscription Reminders and Renewals**:

    Where a company sells an annual subscription for a product or service, Newfies-Dialer can be configured to dial the customer, remind them that the subscription is due, and optionally pass the call into a call centre or into a credit card payment IVR.



.. _faq-what-s-the-history-newfies-dialer:

What's the history behind Newfies-Dialer
----------------------------------------

**Answer:**

Newfies-Dialer is a bulk dialer application which was commissioned by a charity named Kubatana (http://www.kubatana.net) based in Zimbabwe, which sponsors the Freedomfone project (http://www.freedomfone.org/) dedicated to providing information via phone technology.

In less economically developed countries, Internet is often limited, but there is usually comprehensive mobile phone coverage. Freedomfone uses Newfies-Dialer to dial up people’s phones and offer health information on Cholera, Malaria and so many other avoidable health issues in the third world, which may be alleviated by education. Newfies-Dialer was so named after the Newfoundland Dog nicknamed Newfies and used by sea rescue services around the world.


.. _faq-change-ip-address:

How to change your IP address
-----------------------------

During the installation Newfies-Dialer Web interface are bind to the detected IP, if you change the IP or want to change the interface to which is bind you then need change the settings ALLOWED_HOSTS. Please find some documentation about this settings at https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts

The configuration file on your server is located at /usr/share/newfies-dialer/newfies_dialer/settings_local.py

After changes in settings_local.py you will need to restart supervisord:

    /etc/init.d/supervisor stop

Then to start it back:

    /etc/init.d/supervisor start


.. _faq-how-to-translate:

How to translate the frontend application
-----------------------------------------

First check if there is an existing translation directory in:
https://github.com/newfies-dialer/newfies-dialer/tree/develop/newfies/locale
Each language is represented by a 2 character ISO code (http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

If there is no existing directory for your language code, then you can download the English PO file and use it as a base: https://raw.githubusercontent.com/Star2Billing/newfies-dialer/develop/newfies/locale/en/LC_MESSAGES/django.po

If there is a file for the language you want to translate, you will need to download that PO file and completed the missing translations. For instance, there is a PO file for Japanese:
https://raw.githubusercontent.com/Star2Billing/newfies-dialer/develop/newfies/locale/ja/LC_MESSAGES/django.po

Working with an existing PO File: it's likely that you will see missing translations and/or translations that need to be reviewed, they are usually marked by `fuzzy`.
The translation has to be corrected before removing the `fuzzy` line.

Here an example:
#: appointment/models/events.py:32
#, fuzzy
msgid "created on"
msgstr "キャンペーンのアップデート"

If the translation is good, then just remove the line with "#, fuzzy"
If there is an error, correct it and remove the line with "#, fuzzy"

Once the PO is completed, please send it over to our team at newfies-dialer@star2billing.com, so that it can be included in the next release.


.. _faq-how-often-to-upgrade:

How often do I need to upgrade / How do I upgrade?
--------------------------------------------------

It is not necessary to upgrade to each and every release, and generally we would advise against it, unless we issue an advisory via mailing list to the contrary, e.g. major bug or security issue. Generally one can stay with a single version for a long time and decide to upgrade when there are new features or bug fixes that affect you.

The database has to be migrated with Django migration which is very well documented here: https://docs.djangoproject.

Newfies-Dialer has several components that will need to be reinstalled / upgraded: the code of the Django project, the dependencies in virtualenv, the lua code base for the IVR and the dependencies for Lua.

In some versions, OS packages need to be upgraded too, so it might be wise to keep an eye on what is needed.

The Newfies-Dialer team provide an upgrade service as described at http://www.newfies-dialer.org/ where we try to limit your downtime. Do note that it may not be possible to upgrade from very old instances of Newfies-Dialer due to major architecture changes.


.. _faq-text2speech:

Text2Speech
===========


.. _faq-how-does-tag-substitution-work:

How does the tag substitution work with the TTS engine
------------------------------------------------------

**Answer:**

This is the list of standard tags that will be automatically replaced:
    {last_name}
    {first_name}
    {email}
    {country}
    {city}
    {contact}  // This is the phone number

If you need more flexibility, you can use the "Additional Parameters (JSON)" field which allow you to add custom key-values that will be replaced.

For example, let's add this in "Additional Parameters (JSON)":
    {"company_name": "Canonical", "bonus" : "200", "currency" : "euro"}

When you create a survey with a node that plays TTS, you can easily replace the key-values in the text.
Text example:

    "We are calling you on behalf of {company_name}, you receive a bonus of {bonus} {currency}"


.. _faq-how-provide-tts-in-multiple-languages:

How does Newfies-Dialer provide TTS in multiple languages
---------------------------------------------------------

**Answer:**

By default the TTS engine used by newfies-Dialer is Flite (http://www.speech.cs.cmu.edu/flite/)
which only supports English. If you want to use another language you will need another TTS engine.

We have integrated Acapela: http://acapela-vaas.com/ and in order to use Acapela,
the only thing you have to do is to sign in and enable Acapela on Newfies-dialer.


.. _faq-how-enable-acapela:

How to enable Acapela on Newfies-Dialer
---------------------------------------

**Answer:**

First you will have to sign-up and register an account with Acapela : http://acapela-vaas.com/
Once you signed up you will receive a login, an application login and an application password, you will need those to configure Acapela on Newfies-Dialer.

Acapela needs to be configured in 2 places:

1. On the Web interface

Edit the file /usr/share/newfies-dialer/newfies_dialer/settings_local.py and find::

    #TEXT-TO-SPEECH
    #==============
    TTS_ENGINE = 'FLITE'  # FLITE, CEPSTRAL, ACAPELA

    ACCOUNT_LOGIN = 'EVAL_XXXX'
    APPLICATION_LOGIN = 'EVAL_XXXXXXX'
    APPLICATION_PASSWORD = 'XXXXXXXX'

    SERVICE_URL = 'http://vaas.acapela-group.com/Services/Synthesizer'
    QUALITY = '22k'  # 22k, 8k, 8ka, 8kmu
    ACAPELA_GENDER = 'W'
    ACAPELA_INTONATION = 'NORMAL'

    You will have to change the value of the settings : TTS_ENGINE, ACCOUNT_LOGIN, APPLICATION_LOGIN and APPLICATION_PASSWORD.


2. On the IVR application

Create a new file /usr/share/newfies-lua/libs/acapela_config.lua and add the following::

    TTS_ENGINE = 'acapela'

    ACCOUNT_LOGIN = 'EVAL_VAAS'
    APPLICATION_LOGIN = 'EVAL_XXXXXX'
    APPLICATION_PASSWORD = 'XXXXXX'

    SERVICE_URL = 'http://vaas.acapela-group.com/Services/Synthesizer'
    QUALITY = '22k'  -- 22k, 8k, 8ka, 8kmu
    ACAPELA_GENDER = 'M'
    ACAPELA_INTONATION = 'NORMAL'
    ACAPELA_LANG = 'EN'


    Change the value of the settings : ACCOUNT_LOGIN, APPLICATION_LOGIN, APPLICATION_PASSWORD and optionally, ACAPELA_LANG.


Finally restart the web UI:::

    /etc/init.d/supervisor stop
    and
    /etc/init.d/supervisor start



.. _faq-dialer-logic:

Dialer Logic
============

.. _faq-how-retry-works:

How does the dial retry logic works
-----------------------------------

**Answer:**

There are 2 systems available to retry calls:

Basic Retry:

    Basic retry checks to see if the call has been answered, even for a very
    short duration, this is regarded as a successful call. However if the call
    is not answered, busy or unreachable, it will be considered as a failed
    call, and will be retried as defined in the "Dialer Settings"  section in
    the campaign.


Completion Retry:

    This feature works with the survey editor. When a survey node is created, the
    "Survey Complete" checkbox can be ticked so that it is clear that the contact
    reached a certain point in the survey and did not abandon the call early.
    Usually, one of the last nodes in the survey is ticked as "Survey Complete".

    The Completion Retry interval and number of times to retry is set in the
    campaign under the "Dialer Completion Settings" section.
