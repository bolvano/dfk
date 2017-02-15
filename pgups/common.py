# -*- coding: utf-8 -*-

from django.forms.widgets import TextInput
from django import forms

class NumberInput(TextInput):
    input_type = 'number'

class SplitTimeWidget(forms.widgets.MultiWidget):

    def __init__(self, *args, **kwargs):
        widgets = (
            NumberInput(attrs={'min': '0', 'step': '1',
                               'class': 'col s5',
                               'placeholder': 'мин.'}),
            NumberInput(attrs={'min': '0', 'max': '59,99',
                               'class': 'col s5 offset-s2',
                               'step': '0.01',
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
        minutes = self.widgets[0].value_from_datadict(data, files, name + '_0')
        minutes_seconds = int(minutes) * 60 if minutes else 0
        seconds = self.widgets[1].value_from_datadict(data, files, name + '_1')
        seconds = float(seconds) if seconds else 0
        return round(minutes_seconds + seconds, 2)


# Получает IP пользователя
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
