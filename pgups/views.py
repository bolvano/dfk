from django.shortcuts import render
from .forms import RequestForm, PersonForm, CompetitorForm
from django.contrib import messages
import datetime
from django.forms.models import inlineformset_factory
from .models import Userrequest, Person, Competition, Team, Competitor, Tour, Age, Distance, Style
from django.http import HttpResponseRedirect, HttpResponse

import json
import re


# Получает IP пользователя
def get_client_ip(request):				

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def reg_request(request): 

	RequestCompetitorFormSet = inlineformset_factory(Person, Competitor, form=CompetitorForm, can_delete=True, extra=1)
	RequestPersonFormSet = inlineformset_factory(Userrequest, Person, form=PersonForm, can_delete=True, extra=1)

	if request.method == "POST":	

		request_form = RequestForm(request.POST)

		competitorMap = json.loads(request.POST['competitorMap'])

		request_person_formset = RequestPersonFormSet(request.POST)
		request_competitor_formset = RequestCompetitorFormSet(request.POST)

		#import ipdb; ipdb.set_trace()

		if (request_form.is_valid() and request_competitor_formset.is_valid() and request_person_formset.is_valid()):

			# Сохранение данных о заявителе
			userrequest = request_form.save(commit=False)
			userrequest.ip = get_client_ip(request)
			userrequest.save()

			# Сохранение данных о человеке
			for person_form in request_person_formset:

				if person_form.cleaned_data.get('DELETE'):
					continue
				
				person = person_form.save(commit=False)
				person.userrequest = Userrequest.objects.get(pk = userrequest.pk)	
				person.save()

				person_form_id = int(re.search(r'\d+', person_form.prefix).group())
				main_distance = True;

				for competitor_form in request_competitor_formset:

					competitor_form_id = int(re.search(r'\d+', competitor_form.prefix).group())

					if str(competitor_form_id) in competitorMap and competitorMap[str(competitor_form_id)]==str(person_form_id):

						competitor = competitor_form.save(commit=False)
						competitor.person = Person.objects.get(pk = person.pk)
						competitor.userrequest = Userrequest.objects.get(pk = userrequest.pk)	
						now = datetime.datetime.now()
						age = now.year - int(person.birth_year)	
						competitor.age = Age.objects.get(min_age__lte=age, max_age__gte=age)
						competitor.main_distance = main_distance
						main_distance = False
						competitor.save()

			# Success message
			messages.success(request, 'Заявка сохранена.')

			# Редирект на страницу с пустой формой
			return HttpResponseRedirect('')
		
	else:

		request_form = RequestForm()
		request_person_formset = RequestPersonFormSet()
		request_competitor_formset = RequestCompetitorFormSet()

	return render(request, 'pgups/reg.html', {'request_form' : request_form,
		'request_person_formset': request_person_formset,
		'request_competitor_formset': request_competitor_formset}, )


def generate_tours(request):
	competition = Competition.objects.get(pk=2)
	distance50 = Distance.objects.get(pk=2)
	distance100 = Distance.objects.get(pk=1)
	styles = Style.objects.all()
	ages = Age.objects.all()

	for age in ages:
		for style in styles:
			for gender in ['М','Ж']:
				tour = Tour(competition=competition, style=style, age=age, gender=gender, finished=False, )
				if style.id != 6:
					tour.distance = distance50
				else:
					tour.distance = distance100
				tour.save()

	return HttpResponse(json.dumps({}), content_type="application/json")	


def distances(request):
	distances = {}

	tours = Tour.objects.all()

	for tour in tours:
		competitors = tour.competitor_set

		if competitors.count():
			distances['distance/'+str(tour.competition.id)+'/'+str(tour.distance.id)+'/'+str(tour.style.id)+'/'+tour.gender+'/'] = tour.distance.name+' '+tour.style.name+' '+tour.gender

	return render(request, 'pgups/distances.html', {'distances': distances},)


def distance(request, competition_id, distance_id, style_id, gender_id):

	num_of_lanes = 5
	minimal = 3

	starts = []

	competition = Competition.objects.get(pk=competition_id)
	distance = Distance.objects.get(pk=distance_id)
	style = Style.objects.get(pk=style_id)

	tours = Tour.objects.filter(competition=competition, distance=distance, style=style, gender=gender_id)
	competitors = Competitor.objects.filter(tour__in=tours).order_by('-prior_time')
	(full_starts, remainders) = divmod(len(competitors), num_of_lanes)

	#import ipdb; ipdb.set_trace()

	if remainders > 0: # есть остаток
		if full_starts > 0 and remainders < minimal: #есть полные и остаток меньше трёх, перегруппировка первых двух
			starts.append(competitors[:minimal]) # первый старт - три участника
			if full_starts == 1: # был один полный старт: будет два неполных
				starts.append(competitors[minimal:])
			else: # было более одного полного: второй будет неполным, остальные полными
				begin = minimal
				end = begin + num_of_lanes - (minimal - remainders)

				starts.append(competitors[begin:end])

				begin = end
				for i in range(0, full_starts - 1):
					end = begin + num_of_lanes
					starts.append(competitors[begin:end])
					begin = end

		elif full_starts > 0 and remainders >= minimal: # есть полные старты и остаток три или больше
			starts.append(competitors[:remainders])
			begin = remainders
			for i in range(0, full_starts):
				end = begin + num_of_lanes
				starts.append(competitors[begin:end])
				begin = end

		else:
			starts.append(competitors[:])

	elif full_starts: # нет остатков, просто раскидываем
		begin = 0
		for i in range(0, full_starts):
			end = begin + num_of_lanes
			starts.append(competitors[begin:end])
			begin = end

	num_starts = len(starts)
	title = 'Заплывы ' + distance.name + ' ' + style.name + ' ' + gender_id

	return render(request, 'pgups/distance.html', {
												'title': title,
												'competitors': competitors, 
												'full_starts': full_starts,
												'remainders': remainders,
												'num_starts': num_starts,
												'starts': starts}, )	


def get_tours(request, age, gender):
	now = datetime.datetime.now()
	age = now.year - int(age)
	age = Age.objects.get(min_age__lte=age, max_age__gte=age)
	tours = Tour.objects.filter(age=age, gender=gender)
	tour_dict = {}
	for tour in tours:
		tour_dict[tour.id] = tour.__str__()
	return HttpResponse(json.dumps(tour_dict), content_type="application/json")	
