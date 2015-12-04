from django.shortcuts import render
from .forms import RequestForm, RequestCompetitorFormSet, RequestPersonFormSet
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Age, Person, Userrequest
import datetime


# Получает IP пользователя
def get_client_ip(request):				

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Сохраняет данные из формы в БД
def reg_request(request):                

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

			# Сохранение данных о человеке
			for person_form in request_person_formset:
				
				person = person_form.save(commit=False)
				person.userrequest = Userrequest.objects.get(pk = userrequest.pk)	
				person.save()

			for competitor_form in request_competitor_formset:

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
		
	# Отобразить пустую форму
	else:

		request_form = RequestForm()
		request_person_formset = RequestPersonFormSet()
		request_competitor_formset = RequestCompetitorFormSet()

	# Показать страницу с формой
	return render(request, 'pgups/reg.html', {'request_form' : request_form,
											  'request_person_formset' : request_person_formset,
											  'request_competitor_formset' : request_competitor_formset}, )
