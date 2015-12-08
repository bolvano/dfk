from django import forms
from .models import Userrequest, Person, Competition, Team, Competitor, Tour


class RequestForm2(forms.ModelForm):

    competition = forms.ModelChoiceField(   Competition.objects.all(),
                                            empty_label='Выберите соревнование из списка:', 
                                            label='Соревнования:'
                                            )

    team = forms.ModelChoiceField(          Team.objects.all(), 
                                            empty_label='Выберите команду:', 
                                            label='Спортивное общество (команда):'
                                            )
    class Meta:

        model = Userrequest
        exclude = ['ip', 'date']
        labels = {
            'representative': ('Представитель команды (ФИО):'),
            'phone': ('Телефон:'),
            'email': ('Электронная почта:'),
        }


# Форма заявки
class RequestForm(forms.ModelForm):

    competition = forms.ModelChoiceField(   Competition.objects.all(),
                                            empty_label='Выберите соревнование из списка:', 
                                            label='Соревнования:'
                                            )

    team = forms.ModelChoiceField(          Team.objects.all(), 
                                            empty_label='Выберите команду:', 
                                            label='Спортивное общество (команда):'
                                            )
    class Meta:

        model = Userrequest
        exclude = ['ip', 'date']
        labels = {

            'representative': ('Представитель команды (ФИО):'),
            'phone': ('Телефон:'),
            'email': ('Электронная почта:'),

        }
        

# Форма с данными о человеке 
class PersonForm(forms.ModelForm):

    class Meta:

        model = Person
        exclude = ['reg_date']
        labels = {

            'first_name': (' Имя'),
            'last_name': (' Фамилия'),
            'birth_year': (' Год рождения'),
            'gender': (' Пол'),

        }


# Форма с данными об участнике
class CompetitorForm(forms.ModelForm):

    tour = forms.ModelChoiceField(Tour.objects.all(), empty_label='Выберите тур:', label=' Тур: ')
    prior_time = forms.FloatField(required=False, label=' Предварительное время: ', widget=forms.TextInput())

    class Meta:

        model = Competitor
        exclude = ['approved', 'person', 'userrequest', 'age']
        labels = {

            'main_distance' : ('Основная дистанция:')

        }
