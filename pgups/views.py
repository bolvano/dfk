from django.shortcuts import render
from .forms import RequestForm, PersonForm, CompetitorForm
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Age, Person, Userrequest


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
		person_form = PersonForm(request.POST)
		competitor_form = CompetitorForm(request.POST)

		if person_form.is_valid() and request_form.is_valid() and competitor_form.is_valid():	

			# Сохранение данных о человеке
			person = person_form.save()
			person.save()

			# Сохранение данных о заявителе
			userrequest = request_form.save(commit=False)
			userrequest.ip = get_client_ip(request)
			userrequest.save()

			# Создание и сохранение нового участника
			competitor = competitor_form.save(commit=False)
			competitor.person = Person.objects.get(pk = person.pk)
			competitor.userrequest = Userrequest.objects.get(pk = userrequest.pk)		
			competitor.save()

			# Очистить формы
			#request_form = RequestForm() 
			#person_form = PersonForm()
			#competitor_form = CompetitorForm()

			# Success message
			messages.success(request, 'Заявка сохранена.')

			# Редирект на страницу с пустой формой
			return HttpResponseRedirect('')
		
	# Отобразить пустую форму
	else:

		request_form = RequestForm()
		person_form = PersonForm()
		competitor_form = CompetitorForm()

	# Показать страницу с формой
	return render(request, 'pgups/reg.html', {'request_form' : request_form, 'person_form' : person_form, 'competitor_form' : competitor_form}, )