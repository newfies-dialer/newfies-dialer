from django import template
from django.conf import settings

register = template.Library()


def icon(icon_name):
    return 'class="icon" style="text-decoration:none;background-image:url(' \
           + settings.STATIC_URL + 'newfies/icons/' + icon_name + '.png);"'
register.simple_tag(icon)


def listicon(icon_name):
    return 'style="text-decoration:none;list-style-image:url(' \
           + settings.STATIC_URL + 'newfies/icons/' + icon_name + '.png);"'
register.simple_tag(listicon)
