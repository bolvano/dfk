from django import template
import math
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='formatSeconds')
def formatSeconds(s):
    mins = math.floor(s / 60)
    secs = s - (mins * 60)
    if mins:
        return "%d:%05.2f" % (mins, secs)
    else:
        return "%05.2f" % secs


@register.filter(name='has_group')
def has_group(user, group_name):
    group =  Group.objects.get(name=group_name)
    return group in user.groups.all()
