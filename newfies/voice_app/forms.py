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
from voice_app.models import VoiceApp


class VoiceAppForm(ModelForm):
    """VoiceApp ModelForm"""

    class Meta:
        model = VoiceApp
        fields = ['name', 'description', 'type', 'data', 'tts_language', 'gateway']
        exclude = ('user', )
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }
