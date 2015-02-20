#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from audiofield.forms import CustomerAudioFileForm
from mod_utils.forms import SaveUserModelForm, common_submit_buttons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div
# from django import forms
# from django.forms import ModelForm
# from audiofield.widgets import CustomerAudioFileWidget
# from audiofield.models import AudioFile


# class CustomerAudioFileForm(ModelForm):
#     """
#     The following form aims to be used on frontend to power
#     simple upload of audio files without convertion
#     """
#     audio_file = forms.FileField(widget=CustomerAudioFileWidget)

#     class Meta:
#         model = AudioFile
#         fields = ['name', 'audio_file', 'user']


class DialerAudioFileForm(CustomerAudioFileForm, SaveUserModelForm):

    def __init__(self, *args, **kwargs):
        super(DialerAudioFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Div(Fieldset('', 'name', 'audio_file', css_class='col-md-4')),
        )

        if self.instance.id:
            common_submit_buttons(self.helper.layout, 'update')
        else:
            common_submit_buttons(self.helper.layout)
