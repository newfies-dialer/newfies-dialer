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

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import IntegrityError
from optparse import make_option
from dialer_campaign.models import Campaign, Subscriber
from dialer_campaign.constants import SUBSCRIBER_STATUS
from dialer_contact.models import Contact, Phonebook
from dialer_cdr.models import Callrequest
from dialer_cdr.constants import CALLREQUEST_TYPE
from callcenter.models import CallAgent
from callcenter.constants import AGENT_CALLSTATE_TYPE
from agent.models import Agent, AgentProfile
from random import choice, randint
from uuid import uuid1
import time
from datetime import datetime, timedelta
from django.utils.timezone import utc
from faker import Factory


def create_callrequest(phonenumber, campaign, subscriber):
    # Create callrequest
    admin_user = User.objects.filter(is_superuser=True)[0]

    #content_type_id is survey
    try:
        content_type_id = ContentType.objects.get(model='survey').id
    except:
        content_type_id = 1

    delta_days = randint(0, 10)
    delta_minutes = randint(-720, 720)
    created_date = datetime.utcnow().replace(tzinfo=utc) \
        - timedelta(minutes=delta_minutes) \
        - timedelta(days=delta_days)

    new_callrequest = Callrequest.objects.create(
        request_uuid=uuid1(),
        user=admin_user,
        phone_number=phonenumber,
        campaign=campaign,
        aleg_gateway=campaign.aleg_gateway,
        status=choice("12345678"),
        call_type=CALLREQUEST_TYPE.ALLOW_RETRY,
        content_type_id=content_type_id,
        call_time=created_date,
        created_date=created_date,
        object_id=campaign.object_id,
        subscriber=subscriber)

    return new_callrequest


def create_contact_subscriber(campaign, phonebook_id, agent_id):
    """Create new contact and subscriber"""
    length = 10
    chars = "1234567890"
    phonenumber = '' . join([choice(chars) for i in range(length)])
    print "phonenumber => %s" % phonenumber

    faker = Factory.create()
    faker.name()

    try:
        new_contact = Contact.objects.create(
            contact=phonenumber,
            phonebook_id=phonebook_id,
            first_name=faker.firstName(),
            last_name=faker.lastName(),
            email=faker.email(),
            address=faker.address(),
            city=faker.city(),
            state=faker.state(),
            country=faker.countryCode(),
            description=faker.text())
    except IntegrityError:
        print "Duplicate contact!"
        return False

    try:
        print "created contact=>%s (%d)" % (str(new_contact), new_contact.id)

        #When contact is created a subscriber is created automatically

        #Get Subscriber
        subscriber = Subscriber.objects.get(contact=new_contact, campaign_id=campaign.id)
        #Simulate the process of them being called and moved to the queue of the agent

        subscriber.status = SUBSCRIBER_STATUS.SENT
        subscriber.save()

    except IntegrityError:
        print "Cannot find subscriber!"
        return False

    try:
        # Create Callrequest

        new_callrequest = create_callrequest(phonenumber, campaign, subscriber)
        #print "new_callrequest: " + str(new_callrequest)

        # when a subscriber is routed to an agent
        # an instance is created in the CallAgent table

        #The agent name to test the simulator1 is 'agent'
        #Other scenario will implement several agent

        call_agent = CallAgent.objects.create(
            callrequest=new_callrequest,
            agent=AgentProfile.objects.get(user_id=agent_id),
            callstate=AGENT_CALLSTATE_TYPE.agent_offering,
        )

        print "new_call_agent: " + str(call_agent)

    except IntegrityError:
        print "Duplicate callrequest!"
        raise
        return False

    data = {
        'new_callrequest_id': new_callrequest.id,
        'call_agent_id': call_agent.id,
    }
    return data


class Command(BaseCommand):
    args = 'scenario'
    help = "Simulator\n" \
           "---------------------------\n" \
           "python manage.py simulator --scenario=1"

    option_list = BaseCommand.option_list + (
        make_option('--scenario',
                    default=1,
                    dest='scenario',
                    help="number representing the scenario that will be triggered (value: 1, 2 or 3)"),
    )

    def handle(self, *args, **options):
        """Note that subscriber created with callrequest"""

        campaign = Campaign.objects.all()[0]
        if campaign.phonebook.all().count() > 0:
            phonebook_id = campaign.phonebook.all()[0].id
        else:
            phonebook_id = Phonebook.objects.all()[0].id

        scenario = 1  # default
        try:
            scenario = int(options.get('scenario'))
        except ValueError:
            scenario = 1

        # delete previous contacts & subscriber
        #Contact.objects.filter(phonebook_id=phonebook_id).delete()
        #Subscriber.objects.filter(campaign=campaign).delete()
        #delay_list = [20, 10, 20]
        agent_id = Agent.objects.get(username='agent').id
        #print "agent => %s" % str(agent)

        if scenario == 1:
            # Implement scenario 1
            scenario_1(campaign, phonebook_id, agent_id)
        elif scenario == 2:
            # Implement scenario 2
            scenario_2(campaign, phonebook_id, agent_id)
        else:
            print("No scenario...")


def scenario_1(campaign, phonebook_id, agent_id):
    # Implementation scenario 1
    # Delete previous CallAgent data which are belong to agent_id
    #CallAgent.objects.filter(agent__user_id=agent_id).delete()
    CallAgent.objects.all().delete()

    time2wrapup = 3
    time2sleep = 15

    data = create_contact_subscriber(campaign, phonebook_id, agent_id)
    print Callrequest.objects.get(pk=data['new_callrequest_id'])

    time.sleep(time2wrapup)

    call_agent = CallAgent.objects.get(pk=data['call_agent_id'])
    call_agent.callstate = AGENT_CALLSTATE_TYPE.bridge_agent_start
    call_agent.save()

    print "delay : %s sec" % str(time2sleep)
    time.sleep(time2sleep)
    # When a subscriber finish the call with the agent
    # callrequest is removed from CallAgent
    call_agent.delete()

    data = create_contact_subscriber(campaign, phonebook_id, agent_id)
    print Callrequest.objects.get(pk=data['new_callrequest_id'])

    time.sleep(time2wrapup)

    call_agent = CallAgent.objects.get(pk=data['call_agent_id'])
    call_agent.callstate = AGENT_CALLSTATE_TYPE.bridge_agent_start
    call_agent.save()

    print "delay : %s sec" % str(time2sleep)
    time.sleep(time2sleep)
    # When a subscriber finish the call with the agent
    # callrequest is removed from CallAgent
    call_agent.delete()


def scenario_2(campaign, phonebook_id, agent_id):
    # Implementation scenario 2
    # Delete previous CallAgent data which are belong to agent_id
    #CallAgent.objects.filter(agent__user_id=agent_id).delete()
    CallAgent.objects.all().delete()

    time2wrapup = 5
    time2sleep = 15

    # Step 1 (for the first 20 seconds : 0-20 secs)
    # - Create contact (5 secs: agent_offering, then during 15 secs bridge_agent_start)
    data = create_contact_subscriber(campaign, phonebook_id, agent_id)
    print Callrequest.objects.get(pk=data['new_callrequest_id'])
    time.sleep(time2wrapup)

    call_agent = CallAgent.objects.get(pk=data['call_agent_id'])
    call_agent.callstate = AGENT_CALLSTATE_TYPE.bridge_agent_start
    call_agent.save()

    print "delay : %s sec" % str(time2sleep)
    time.sleep(time2sleep)
    call_agent.delete()

    # Step 2 (for the first 20 seconds : 0-20 secs)
    # - Create contact (5 secs: agent_offering) but no bridge_agent_start
    data = create_contact_subscriber(campaign, phonebook_id, agent_id)
    print Callrequest.objects.get(pk=data['new_callrequest_id'])
    time.sleep(time2wrapup)

    call_agent = CallAgent.objects.get(pk=data['call_agent_id'])
    #print "delay : %s sec" % str(time2sleep)
    #time.sleep(time2sleep)
    call_agent.delete()

    # Step 3 (for the first 20 seconds : 0-20 secs)
    # - Create contact (5 secs: agent_offering, then during 15 secs bridge_agent_start)
    data = create_contact_subscriber(campaign, phonebook_id, agent_id)
    print Callrequest.objects.get(pk=data['new_callrequest_id'])
    time.sleep(time2wrapup)

    call_agent = CallAgent.objects.get(pk=data['call_agent_id'])
    call_agent.callstate = AGENT_CALLSTATE_TYPE.bridge_agent_start
    call_agent.save()

    print "delay : %s sec" % str(time2sleep)
    time.sleep(time2sleep)
    call_agent.delete()

    # Step 4 (for the first 20 seconds : 0-20 secs)
    # - Create contact (5 secs: agent_offering, then during 1 secs bridge_agent_start)
    data = create_contact_subscriber(campaign, phonebook_id, agent_id)
    print Callrequest.objects.get(pk=data['new_callrequest_id'])
    time.sleep(time2wrapup)

    call_agent = CallAgent.objects.get(pk=data['call_agent_id'])
    call_agent.callstate = AGENT_CALLSTATE_TYPE.bridge_agent_start
    call_agent.save()

    print "delay : %s sec" % str(1)
    time.sleep(1)
    call_agent.delete()

    # Step 5 (for the first 20 seconds : 0-20 secs)
    # - Create contact (5 secs: agent_offering, then during 15 secs bridge_agent_start)
    data = create_contact_subscriber(campaign, phonebook_id, agent_id)
    print Callrequest.objects.get(pk=data['new_callrequest_id'])
    time.sleep(time2wrapup)

    call_agent = CallAgent.objects.get(pk=data['call_agent_id'])
    call_agent.callstate = AGENT_CALLSTATE_TYPE.bridge_agent_start
    call_agent.save()

    print "delay : %s sec" % str(time2sleep)
    time.sleep(time2sleep)
    call_agent.delete()
