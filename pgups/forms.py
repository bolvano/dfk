from django import forms
from .models import Userrequest
from .models import Person


class RequestForm(forms.ModelForm):

    class Meta:

        model = Userrequest
        exclude = ['ip', 'date']
        labels = {
            'competition': ('Соревнования:'),
            'team': ('Спортивное общество (команда):'),
            'representative': ('Представитель команды:'),
            'phone': ('Телефон:'),
            'email': ('Электронная почта:'),
        }


class PersonForm(forms.ModelForm):

    class Meta:

        model = Person
        exclude = ['regdate']
        labels = {
            'first_name': ('Имя:'),
            'last_name': ('Фамилия:'),
            'birth_year': ('Год рождения:'),
            'gender': ('Пол:'),
        }