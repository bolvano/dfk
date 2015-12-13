from django.shortcuts import render
from .forms import RequestForm, PersonForm, CompetitorForm
from django.contrib import messages
import datetime
from django.forms.models import inlineformset_factory
from .models import Userrequest, Person, Competition, Team, Competitor, Tour, Age
from django.http import HttpResponseRedirect
import json


# Получает IP пользователя
def get_client_ip(request):				

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#def person_form(request):
#	return render(request,PersonForm())


def reg_request2(request): 

	RequestCompetitorFormSet = inlineformset_factory(Person, Competitor, form=CompetitorForm, can_delete=True, extra=1)
	RequestPersonFormSet = inlineformset_factory(Userrequest, Person, form=PersonForm, can_delete=True, extra=1)

	if request.method == "POST":	

		import ipdb; ipdb.set_trace()

		request_form = RequestForm(request.POST)

		competitorMap = json.loads(request.POST['competitorMap'])

		request_person_formset = RequestPersonFormSet(request.POST)
		request_competitor_formset = RequestCompetitorFormSet(request.POST)

		if (request_form.is_valid() and request_competitor_formset.is_valid() and request_person_formset.is_valid()):

			# Сохранение данных о заявителе
			userrequest = request_form.save(commit=False)
			userrequest.ip = get_client_ip(request)
			userrequest.save()

			# Сохранение данных о человеке
			for person_form in request_person_formset:
				
				person = person_form.save(commit=False)
				person.userrequest = Userrequest.objects.get(pk = userrequest.pk)	
				person.save()

				for competitor_form in request_competitor_formset:

					#import ipdb; ipdb.set_trace()

					if 'tour' in competitor_form.data:

						competitor = competitor_form.save(commit=False)
						competitor.person = Person.objects.get(pk = person.pk)
						competitor.userrequest = Userrequest.objects.get(pk = userrequest.pk)	
						now = datetime.datetime.now()
						age = now.year - int(person.birth_year)	
						competitor.age = Age.objects.get(min_age__lte=age, max_age__gte=age)
						competitor.save()

			# Success message
			messages.success(request, 'Заявка сохранена.')

			# Редирект на страницу с пустой формой
			return HttpResponseRedirect('')
		
	else:

		request_form = RequestForm()
		request_person_formset = RequestPersonFormSet()
		request_competitor_formset = RequestCompetitorFormSet()

	return render(request, 'pgups/reg2.html', {'request_form' : request_form,
		'request_person_formset': request_person_formset,
		'request_competitor_formset': request_competitor_formset}, )

# Сохраняет данные из формы в БД
def reg_request(request):                

	# Формсеты
	extra_persons = 1
	person_competitor_coef = 2
	extra_competitors = extra_persons*person_competitor_coef

	RequestCompetitorFormSet = inlineformset_factory(Person, Competitor, form=CompetitorForm, extra=extra_competitors, can_delete=False)
	RequestPersonFormSet = inlineformset_factory(Userrequest, Person, form=PersonForm, extra=extra_persons, can_delete=False)


	# Если форма отправлена, сохранить данные
	if request.method == "POST":

		request_form = RequestForm(request.POST)

		request_person_formset = RequestPersonFormSet(request.POST)
		request_competitor_formset = RequestCompetitorFormSet(request.POST)

		if (request_form.is_valid() and request_competitor_formset.is_valid() and request_person_formset.is_valid()):

			# Сохранение данных о заявителе
			userrequest = request_form.save(commit=False)
			userrequest.ip = get_client_ip(request)
			userrequest.save()

			c = 2 # Количество участников на человека
			offset = 0 # Смещение

			# Сохранение данных о человеке
			for person_form in request_person_formset:
				
				person = person_form.save(commit=False)
				person.userrequest = Userrequest.objects.get(pk = userrequest.pk)	
				person.save()

				for competitor_form in request_competitor_formset[offset : offset + c]:

					#import ipdb; ipdb.set_trace()

					if 'tour' in competitor_form.data:

						competitor = competitor_form.save(commit=False)
						competitor.person = Person.objects.get(pk = person.pk)
						competitor.userrequest = Userrequest.objects.get(pk = userrequest.pk)	
						now = datetime.datetime.now()
						age = now.year - int(person.birth_year)	
						competitor.age = Age.objects.get(min_age__lte=age, max_age__gte=age)
						competitor.save()

				offset += c

			# Success message
			messages.success(request, 'Заявка сохранена.')

			# Редирект на страницу с пустой формой
			return HttpResponseRedirect('')
		
	# Отобразить пустую форму
	else:

		request_form = RequestForm()
		request_person_formset = RequestPersonFormSet()
		request_competitor_formset = RequestCompetitorFormSet()

	# Показать страницу с формой
	return render(request, 'pgups/reg.html', {'request_form' : request_form,
											  'request_person_formset' : request_person_formset,
											  'request_competitor_formset' : request_competitor_formset}, )