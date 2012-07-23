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

from django import forms
from django.forms import ModelForm
from audiofield.forms import CustomerAudioFileForm


class SurveyCustomerAudioFileForm(CustomerAudioFileForm):

    def __init__(self, *args, **kwargs):
        super(SurveyCustomerAudioFileForm, self).__init__(*args, **kwargs)
        self.fields['audio_file'].widget.attrs['class'] = "input-file"
