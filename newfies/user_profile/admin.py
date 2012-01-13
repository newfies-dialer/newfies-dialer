from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from user_profile.models import *

class UserProfileInline(admin.StackedInline):
    model = UserProfile


class StaffAdmin(UserAdmin):
    inlines = [UserProfileInline]

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active', 'is_superuser', 'last_login')

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        qs = qs.filter(Q(is_staff=True) | Q(is_superuser=True))
        return qs


class CustomerAdmin(StaffAdmin):

    fieldsets = (
        ('', {
            'fields': ('username', 'password', ),
        }),
        (_('Personal info'), {
            #'classes': ('collapse',),
            'fields': ('first_name', 'last_name', 'email', )
        }),
        (_('Permission'), {
            'fields': ('is_active', )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', )
        }),
    )

    inlines = [
        UserProfileInline,
    ]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active', 'is_superuser', 'last_login')

    def queryset(self, request):
        qs = super(UserAdmin, self).queryset(request)
        qs = qs.exclude(Q(is_staff=True) | Q(is_superuser=True))
        return qs

admin.site.unregister(User)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Customer, CustomerAdmin)
