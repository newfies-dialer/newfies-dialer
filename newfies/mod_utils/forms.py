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
from django import forms
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from mod_utils.helper import Export_choice


class HorizRadioRenderer(forms.RadioSelect.renderer):
    """This overrides widget method to put radio buttons horizontally
    instead of vertically.
    """
    def render(self):
        """Outputs radios"""
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class Exportfile(forms.Form):
    """
    Abstract Form : export file in various format e.g. XLS, CSV, JSON
    """
    export_to = forms.TypedChoiceField(label=_('export to').capitalize(), required=True,
                                       choices=list(Export_choice),
                                       widget=forms.RadioSelect(renderer=HorizRadioRenderer))


class SaveUserModelForm(ModelForm):
    """SaveUserModelForm ModelForm"""

    def save(self, *args, **kwargs):
        """save that retrieve the user"""
        self.user = kwargs.pop('user', None)
        kwargs['commit'] = False
        obj = super(SaveUserModelForm, self).save(*args, **kwargs)
        if self.user:
            obj.user = self.user
        obj.save()
