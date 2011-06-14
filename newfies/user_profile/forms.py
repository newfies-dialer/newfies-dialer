from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.admin.widgets import *
from django.utils.translation import ugettext_lazy as _
from user_profile.models import *
# place form definition here


class UserChangeDetailForm(ModelForm):
    """A form used to change the detail of a user in the Customer UI."""
    email = forms.CharField(label=_('Email address'), required=True)
    class Meta:
        model = User
        fields = ["last_name", "first_name", "email"]

    def __init__(self, user, *args, **kwargs):
        self.user = user        
        super(UserChangeDetailForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        """Saves the detail."""
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save()
        return self.user


class UserProfileForm(ModelForm):

    class Meta:
        model = UserProfile
