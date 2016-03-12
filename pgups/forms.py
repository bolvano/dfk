# -*- coding: utf-8 -*- 

from django import forms
from .models import Userrequest, Person, Competition, Team, Competitor, Tour, Result


# Форма заявки
class RequestForm(forms.ModelForm):

    form_name = "request_form"

    competition = forms.ModelChoiceField(   Competition.objects.filter(finished=False),
                                            empty_label='Выберите соревнование из списка:', 
                                            label='Соревнования:',
                                            error_messages={'required': 'Это обязательное поле'},
                                            widget=forms.Select(attrs={'class': 'form-control',
                                                                       'required': 'required',
                                                                       'ng-model': 'competition', 
                                                                       }),
                                            )

    team = forms.ModelChoiceField(          Team.objects.all(), 
                                            empty_label='Выберите команду:', 
                                            label='Команда (необязательно):',
                                            required=False,
                                            widget=forms.Select(attrs={'class': 'form-control'}),
                                            )

    representative = forms.CharField(       widget=forms.TextInput (attrs={'class': 'form-control', 
                                                                           'required': 'required',
                                                                           'ng-minlength': 2,
                                                                           'ng-model': 'representative',
                                                                          }
                                                                   ),
                                            label='Заявитель/Представитель команды:',
                                            )

    phone = forms.CharField(                widget=forms.TextInput (attrs={'class': 'form-control', 
                                                                           'required': 'required',
                                                                           'ng-model': 'phone',
                                                                          }
                                                                   ),
                                            label='Телефон:',
                                            )

    email = forms.CharField(                widget=forms.EmailInput (attrs={'class': 'form-control', 
                                                                            'required': 'required',
                                                                            'ng-model': 'email',
                                                                           }
                                                                   ),
                                            label='Электронная почта:',
                                            )

    competitorMap = forms.CharField(widget=forms.HiddenInput())

    class Meta:

        model = Userrequest
        exclude = ['ip', 'date']

        error_messages={
        'email': {'required': 'Это обязательное поле'},
        'phone': {'required': 'Это обязательное поле'},
        'representative': {'required': 'Это обязательное поле'},
        }


# Форма с данными о человеке 
class PersonForm(forms.ModelForm):

    class Meta:

        model = Person
        exclude = ['reg_date', 'userrequest']
        labels = {

            'first_name': (' Имя:'),
            'last_name': (' Фамилия:'),
            'birth_year': (' Год рождения:'),
            'gender': (' Пол:'),

        }


# Форма с данными об участнике
class CompetitorForm(forms.ModelForm):

    tour = forms.ModelChoiceField(          Tour.objects.all(),
                                            empty_label='Выберите дистанцию',
                                            label='Тур',
                                            error_messages={'required': 'Это обязательное поле'}
                                            )

    prior_time = forms.FloatField(
                                            required=True, 
                                            label='Время', 
                                            widget=forms.TextInput(attrs={'size': '6'}), 
                                            error_messages={'required': 'Это обязательное поле'}
                                            )

    class Meta:

        model = Competitor
        exclude = ['approved', 'person', 'userrequest', 'age', 'main_distance']
        labels = {
            #'tour' : ('Тур'),
            #'prior_time' : ('Время'),
            #'main_distance' : ('Основная дистанция:')
        }
