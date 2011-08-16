from django.contrib.auth.models import User
from django import forms
from django.forms.util import ErrorList
from django.forms import *
from django.contrib import *
from django.contrib.admin.widgets import *
from django.utils.translation import ugettext_lazy as _
from dialer_campaign.models import *
from dialer_campaign.function_def import *
from datetime import *


class SearchForm(forms.Form):
    """General Search Form with From & To date para."""
    from_date = CharField(label=_('From'), required=False, max_length=10,
    help_text=_("Date Format") + ": <em>YYYY-MM-DD</em>.")
    to_date = CharField(label=_('To'), required=False, max_length=10,
    help_text=_("Date Format") + ": <em>YYYY-MM-DD</em>.")


class FileImport(forms.Form):
    """General Form : CSV file upload"""
    csv_file = forms.FileField(label=_("Upload CSV File "), required=True,
                            error_messages={'required': 'Please upload File'},
                            help_text=_("Browse CSV file"))

    def clean_file(self):
        """Form Validation :  File extension Check"""
        filename = self.cleaned_data["csv_file"]
        file_exts = (".csv", )
        if not str(filename).split(".")[1].lower() in file_exts:
            raise forms.ValidationError(_(u'Document types accepted: %s' % \
            ' '.join(file_exts)))
        else:
            return filename


class Contact_fileImport(FileImport):
    """Admin Form : Import CSV file with phonebook"""
    phonebook = forms.ChoiceField(label=_("Phonebook"),
                                choices=field_list("phonebook"),
                                required=False,
                                help_text=_("Select Phonebook"))

    def __init__(self, user, *args, **kwargs):
        super(Contact_fileImport, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['phonebook', 'csv_file']
        # To get user's phonebook list
        if user: # and not user.is_superuser
            self.fields['phonebook'].choices = field_list(name="phonebook",
                                                          user=user)


class LoginForm(forms.Form):
    """Client Login Form"""
    user = forms.CharField(max_length=30, label=_('Username:'), required=True)
    password = forms.CharField(max_length=30, label=_('Password:'),
               required=True, widget=forms.PasswordInput())


class PhonebookForm(ModelForm):
    """Phonebook ModelForm"""

    class Meta:
        model = Phonebook
        fields = ['name', 'description']
        exclude = ('user',)
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }


class ContactForm(ModelForm):
    """Contact ModelForm"""

    class Meta:
        model = Contact
        fields = ['phonebook', 'contact', 'last_name', 'first_name', 'email',
                  'country', 'city', 'description', 'status',
                  'additional_vars']
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        # To get user's phonebook list
        if user:
            self.fields['phonebook'].choices = field_list(name="phonebook",
                                                          user=user)
            self.fields['country'].choices = field_list(name="country",
                                                        user=user)


class CampaignForm(ModelForm):
    """Campaign ModelForm"""
    campaign_code = forms.CharField(widget=forms.HiddenInput)
    ds_user = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = Campaign
        fields = ['campaign_code', 'name', 'description',
                  'callerid', 'status', 'aleg_gateway', 'voipapp',
                  'extra_data', 'phonebook',
                  'frequency', 'callmaxduration', 'maxretry',
                  'intervalretry', 'calltimeout',
                  'startingdate', 'expirationdate',
                  'daily_start_time', 'daily_stop_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday', 'ds_user',
                  ]
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)
        self.fields['campaign_code'].initial = get_unique_code(length=5)
        if user:
            self.fields['ds_user'].initial = user
            list_pb = []
            list_voipapp = []
            list_gw = []

            list_pb.append((0, '---'))
            pb_list = field_list("phonebook", user)
            for i in pb_list:
                list_pb.append((i[0], i[1]))
            self.fields['phonebook'].choices = list_pb

            list_voipapp.append((0, '---'))
            vp_list = field_list("voipapp", user)
            for i in vp_list:
                list_voipapp.append((i[0], i[1]))
            self.fields['voipapp'].choices = list_voipapp

            list_gw.append((0, '---'))
            gw_list = field_list("gateway", user)
            for i in gw_list:
                list_gw.append((i[0], i[1]))
            self.fields['aleg_gateway'].choices = list_gw

    def clean(self):
        cleaned_data = self.cleaned_data
        ds_user = cleaned_data.get("ds_user")
        frequency = cleaned_data.get('frequency')
        callmaxduration = cleaned_data.get('callmaxduration')
        maxretry = cleaned_data.get('maxretry')
        calltimeout = cleaned_data.get('calltimeout')

        dialer_set = user_dialer_setting(ds_user)
        if dialer_set:
            if frequency > dialer_set.max_frequency:
                msg = _('Maximum Frequency limit of %d exceeded.'\
                % dialer_set.max_frequency)
                self._errors['frequency'] = ErrorList([msg])
                del self.cleaned_data['frequency']

            if callmaxduration > dialer_set.callmaxduration:
                msg = _('Maximum Duration limit of %d exceeded.'\
                         % dialer_set.callmaxduration)
                self._errors['callmaxduration'] = ErrorList([msg])
                del self.cleaned_data['callmaxduration']

            if maxretry > dialer_set.maxretry:
                msg = _('Maximum Retries limit of %d exceeded.' \
                % dialer_set.maxretry)
                self._errors['maxretry'] = ErrorList([msg])
                del self.cleaned_data['maxretry']

            if calltimeout > dialer_set.max_calltimeout:
                msg = _('Maximum Timeout limit of %d exceeded.'\
                % dialer_set.max_calltimeout)
                self._errors['calltimeout'] = ErrorList([msg])
                del self.cleaned_data['calltimeout']

        return cleaned_data


class CampaignAdminForm(ModelForm):
    """Admin Campaign ModelForm"""
    class Meta:
        model = Campaign
        fields = ['campaign_code', 'name', 'description', 'user', 'status',
                  'callerid', 'startingdate', 'expirationdate',
                  'aleg_gateway', 'voipapp', 'extra_data', 'phonebook',
                  'frequency', 'callmaxduration', 'maxretry', 'intervalretry',
                  'calltimeout', 'daily_start_time', 'daily_stop_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday']

    def __init__(self,  *args, **kwargs):
        super(CampaignAdminForm, self).__init__(*args, **kwargs)
        self.fields['campaign_code'].widget.attrs['readonly'] = True
        self.fields['campaign_code'].initial = get_unique_code(length=5)


NAME_TYPE = (
    (1, _('Last Name')),
    (2, _('First Name')),
)

CHOICE_TYPE = (
    (1, _('Contains')),
    (2, _('Equals')),
    (3, _('Begins with')),
    (4, _('Ends with')),
)

SEARCH_TYPE = (
    (1, _('Last 30 days')),
    (2, _('Last 7 days')),
    (3, _('Yesterday')),
    (4, _('Last 24 hours')),
    (5, _('Last 12 hours')),
    (6, _('Last 6 hours')),
    (7, _('Last hour')),
)


class ContactSearchForm(forms.Form):
    """Search Form on Contact List"""

    contact_no = forms.CharField(label=_('Contact Number:'), required=False,
                           widget=forms.TextInput(attrs={'size': 15}))
    contact_no_type = forms.ChoiceField(label='', required=False, initial=1,
                      choices=CHOICE_TYPE, widget=forms.RadioSelect)
    name = forms.CharField(label=_('Contact Name:'), required=False,
                           widget=forms.TextInput(attrs={'size': 15}))
    phonebook = forms.ChoiceField(label=_('Phonebook:'), required=False)
    status = forms.TypedChoiceField(label=_('Status:'), required=False,
             choices=(('0', _('Inactive')), ('1', _('Active ')),
                      ('2', _('All'))),
             widget=forms.RadioSelect, initial='2')

    def __init__(self, user, *args, **kwargs):
        super(ContactSearchForm, self).__init__(*args, **kwargs)
         # To get user's phonebook list
        if user:
            list = []
            list.append((0, '---'))
            pb_list = field_list("phonebook", user)
            for i in pb_list:
                list.append((i[0], i[1]))
            self.fields['phonebook'].choices = list


class DashboardForm(forms.Form):
    """Dashboard Form"""
    campaign = forms.ChoiceField(label=_('Campaign'), required=False)
    search_type = forms.ChoiceField(label=_('Type'), required=False, initial=4,
                                    choices=SEARCH_TYPE)


    def __init__(self, user, *args, **kwargs):
        super(DashboardForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['campaign', 'search_type']
         # To get user's running campaign list
        if user:
            list = []
            #list.append((0, '---'))
            pb_list = field_list("campaign", user)
            for i in pb_list:
                list.append((i[0], i[1]))
            self.fields['campaign'].choices = list
