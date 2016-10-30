from django import template
import math

register = template.Library()

@register.filter(name='formatSeconds')
def formatSeconds(s):
    mins = math.floor(s / 60)
    secs = s - (mins * 60)
    if mins:
        return "%d:%05.2f" % (mins, secs)
    else:
        return "%05.2f" % secs
