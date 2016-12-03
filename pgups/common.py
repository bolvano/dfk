# -*- coding: utf-8 -*-

from django.forms.widgets import TextInput
from django import forms

class NumberInput(TextInput):
    input_type = 'number'

class SplitTimeWidget(forms.widgets.MultiWidget):

    def __init__(self, *args, **kwargs):
        widgets = (
            NumberInput(attrs={'min': '0', 'step': '1',
                               'class': 'form-control pull-left',
                               'placeholder': 'мин.'}),
            NumberInput(attrs={'min': '0', 'max': '59,99',
                               'step': '0.01', 'class': 'form-control pull-left',
                               'placeholder': 'сек.'}),
        )
        super(SplitTimeWidget, self).__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value:
            minutes,seconds = divmod(value,60)
            return [minutes, seconds]
        return [None, None]

    def format_output(self, rendered_widgets):
        return (rendered_widgets[0] + rendered_widgets[1])

    def value_from_datadict(self, data, files, name):
        #import ipdb; ipdb.set_trace()
        minutes = self.widgets[0].value_from_datadict(data, files, name + '_0')
        if not minutes:
            minutes_seconds = 0
        else:
            minutes_seconds = int(minutes)*60

        seconds = self.widgets[1].value_from_datadict(data, files, name + '_1')
        if not seconds:
            seconds = 0
        else:
            seconds = float(seconds)

        return round(minutes_seconds + seconds, 2)


# Получает IP пользователя
def get_client_ip(request):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip