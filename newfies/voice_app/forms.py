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
from django.forms import ModelForm, Textarea
from voice_app.models import VoiceApp_template


class VoiceAppForm(ModelForm):
    """VoiceApp ModelForm"""

    class Meta:
        model = VoiceApp_template
        fields = ['name', 'description', 'type', 'data',
                  'tts_language', 'gateway']
        exclude = ('user', )
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        voiceapp_view = ''

        if 'voiceapp_view' in kwargs:
            voiceapp_view = kwargs.pop('voiceapp_view')
        super(VoiceAppForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        if instance and voiceapp_view:
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['description'].widget.attrs['readonly'] = True
            self.fields['data'].widget.attrs['readonly'] = True

            self.fields['type'].widget.attrs['disabled'] = 'disabled'
            self.fields['tts_language'].widget.attrs['disabled'] = 'disabled'
            self.fields['gateway'].widget.attrs['disabled'] = 'disabled'
