from django.shortcuts import render
from .forms import RequestForm
from .forms import PersonForm


def get_client_ip(request):				# Получает IP пользователя

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



def reg_request(request):                # Сохраняет данные из формы в БД
	
	if request.method == "POST":
		request_form = RequestForm(request.POST)
		person_form = PersonForm(request.POST)
		if person_form.is_valid() and request_form.is_valid():
			person = person_form.save()
			person.save()
			userrequest = request_form.save(commit=False)
			userrequest.ip = get_client_ip(request)
			userrequest.save()
			request_form = RequestForm() 
			person_form = PersonForm()
			return render(request, 'pgups/reg.html', {'request_form' : request_form, 'person_form' : person_form}) 
	else:
		request_form = RequestForm()
		person_form = PersonForm()
	return render(request, 'pgups/reg.html', {'request_form' : request_form, 'person_form' : person_form})