# -*- coding: utf-8 -*- 
from django.shortcuts import render
from .forms import RequestForm, PersonForm, CompetitorForm
from django.contrib import messages
import datetime
from django.forms.models import inlineformset_factory
from django.forms import formset_factory
from django.forms import modelformset_factory
from .models import Userrequest, Person, Competition, Team, Competitor, Tour, Age, Distance, Style, Start, Order, Cdsg, Result
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
import json
import re
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet




def index(request):
    competitions = Competition.objects.all().order_by('date_start')
    return render(request, 'pgups/index.html', {'competitions': competitions},)

def competition(request, competition_id):
    teams = []
    competition = get_object_or_404(Competition, pk=competition_id)
    userrequests = Userrequest.objects.filter(competition=competition)
    teams = set([userrequest.team for userrequest in userrequests if userrequest.team is not None])
    return render(request, 'pgups/competition.html', {'competition': competition, 'teams':teams},)

def userrequest(request, userrequest_id):
    userrequest = get_object_or_404(Userrequest, pk=userrequest_id)
    return render(request, 'pgups/userrequest.html', {'userrequest': userrequest},)

def person(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    return render(request, 'pgups/person.html', {'person': person},)

def results_starts(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    cdsgs = Cdsg.objects.filter(competition=competition)
    starts = Start.objects.filter(cdsg__in=cdsgs).order_by('num')

    return render(request, 'pgups/results_starts.html', {'competition':competition, 'starts':starts},)

def results_tours(request, competition_id):

    results = []
    competition = get_object_or_404(Competition, pk=competition_id)
    tours = Tour.objects.filter(competition=competition)
    for tour in tours:
        competitors = []
        competitors_good = []
        competitors_bad = []

        for c in tour.competitor_set.all():
            competitors.append(c)

        competitors.sort(key=lambda c: c.result_set.all()[0].time)
        competitors_good = list(filter(lambda c: c.result_set.all()[0].time > 0, competitors))
        competitors_bad = list(filter(lambda c: c.result_set.all()[0].time == 0, competitors))

        results.append((tour,competitors_good,competitors_bad, competitors))

    return render(request, 'pgups/results_tours.html', {'results': results, 'tours':tours, 'competition': competition},)

def results_teams(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)
    tours = Tour.objects.filter(competition=competition)
    result = {}
    for tour in tours:
        competitors = []
        competitors_good = []
        competitors_bad = []
        for c in tour.competitor_set.all():
            competitors.append(c)
        competitors.sort(key=lambda c: c.result_set.all()[0].time)
        competitors_good = list(filter(lambda c: c.result_set.all()[0].time > 0, competitors))
        competitors_good = list(filter(lambda c: c.userrequest.team is not None, competitors))
        if len(competitors_good)>0:
            if competitors_good[0].userrequest.team.name in result:
                result[competitors_good[0].userrequest.team.name] += 30
            else:
                result[competitors_good[0].userrequest.team.name] = 30

            if len(competitors_good)>1:
                if competitors_good[1].userrequest.team.name in result:
                    result[competitors_good[1].userrequest.team.name] += 20
                else:
                    result[competitors_good[1].userrequest.team.name] = 20

                if len(competitors_good)>2:
                    if competitors_good[2].userrequest.team.name in result:
                        result[competitors_good[2].userrequest.team.name] += 10
                    else:
                        result[competitors_good[2].userrequest.team.name] = 10

    return render(request, 'pgups/results_teams.html', {'result': result, 'competition': competition},)


# Получает IP пользователя
def get_client_ip(request):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def attribute_lanes(competitor_set):
    return_set = {}
    lanes = [3,2,4,1,5]
    for competitor in reversed(competitor_set):
        return_set[lanes.pop(0)] = competitor

    return return_set

def competition_team(request, competition_id, team_id):
    result = {}
    competition = Competition.objects.get(pk=competition_id)
    team = Team.objects.get(pk=team_id)
    userrequests = Userrequest.objects.filter(competition=competition, team=team)
    competitors = Competitor.objects.filter(userrequest__in=userrequests)
    for competitor in competitors:
        if competitor.person.id in result:
            result[competitor.person.id].append(competitor)
        else:
            result[competitor.person.id] = [competitor,]
    result = [(Person.objects.get(pk=k),v) for k,v in result.items()]
    return render(request, 'pgups/competition_team.html', {'result': result, 'team':team, 'competition':competition},)

def start_result(request, start_id):

    start = Start.objects.get(pk=start_id)
    orders = Order.objects.filter(start=start)
    competition = start.cdsg.competition
    cdsgs = Cdsg.objects.filter(competition=competition)
    
    try:
        next_start = Start.objects.get(cdsg__in=cdsgs, num=start.num+1)
        next_start_id = next_start.id
    except Start.DoesNotExist:
        next_start_id = ''

    try:
        prev_start = Start.objects.get(cdsg__in=cdsgs, num=start.num-1)
        prev_start_id = prev_start.id
    except Start.DoesNotExist:
        prev_start_id = ''

    competitors = Competitor.objects.filter(order__in=orders)

    for competitor in competitors:
        result = Result.objects.filter(competitor=competitor)
        if not result:
            result = Result(competitor=competitor, time=0, result=0, points=0)
            result.save()

    #import ipdb; ipdb.set_trace()

    ResultFormSet = modelformset_factory(Result, fields=('time', 'competitor'), extra=0, widgets={'time': forms.NumberInput(), 'competitor': forms.HiddenInput()})

    if request.method == "POST":
        result_formset = ResultFormSet(request.POST)
        if(result_formset.is_valid()):
            saveres = result_formset.save()
            messages.success(request, 'Результат сохранён')
            return HttpResponseRedirect('../../../competition/start_result_view/'+start_id+'/')

    else:
        result_formset = ResultFormSet(queryset=Result.objects.filter(competitor__in=competitors).order_by('competitor__order__lane'))

    return render(request, 'pgups/start_result.html', {'result_formset' : result_formset, 'start_num': start.num, 'cdsg_name': start.cdsg.__str__(), 'next_start_id':next_start_id, 'prev_start_id':prev_start_id, 'competition_id':competition.id} )


def start_result_view(request, start_id):
    start = Start.objects.get(pk=start_id)

    competition = start.cdsg.competition
    cdsgs = Cdsg.objects.filter(competition=competition)

    try:
        next_start = Start.objects.get(cdsg__in=cdsgs, num=start.num+1)
        next_start_id = next_start.id
    except Start.DoesNotExist:
        next_start_id = ''

    try:
        prev_start = Start.objects.get(cdsg__in=cdsgs, num=start.num-1)
        prev_start_id = prev_start.id
    except Start.DoesNotExist:
        prev_start_id = ''

    orders = Order.objects.filter(start=start)
    competitors = Competitor.objects.filter(order__in=orders)   
    results = Result.objects.filter(competitor__in=competitors).order_by('competitor__order__lane')
    return render(request, 'pgups/start_result_view.html', {'results' : results, 'start_num': start.num, 'cdsg_name': start.cdsg.__str__(), 'start_id': start.id, 'next_start_id':next_start_id, 'prev_start_id':prev_start_id, 'competition_id':competition.id} )


def reg_request(request): 

    RequestCompetitorFormSet = inlineformset_factory(Person, Competitor, form=CompetitorForm, can_delete=True, extra=1)
    RequestPersonFormSet = inlineformset_factory(Userrequest, Person, form=PersonForm, can_delete=True, extra=1)

    if request.method == "POST":

        #import ipdb; ipdb.set_trace()

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


def generate_tours(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)
    distance50 = Distance.objects.get(meters=50)
    distance100 = Distance.objects.get(meters=100)
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


def competition_starts(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)

    cdsg_list = Cdsg.objects.filter(competition=competition)

    return render(request, 'pgups/competition_starts.html', {'cdsg_list': cdsg_list, 'competition_id':competition_id},)

def generate_starts(request):

    if request.method == "POST":

        competition_id = request.POST.get("competition_id", "")

        num_of_lanes = 5
        minimal = 3

        all_starts = []

        competition = Competition.objects.get(pk=competition_id)

        # delete old starts
        cdsgs = Cdsg.objects.filter(competition=competition)
        for cdsg in cdsgs:
            cdsg.delete()

        distances = Distance.objects.all().order_by('meters') #[50, 100]
        styles = [Style.objects.get(name='на спине'), Style.objects.get(name='вольный стиль'), Style.objects.get(name='брасс'), Style.objects.get(name='баттерфляй'), Style.objects.get(name='комплекс') ]
        genders = ['Ж','М']

        i_cdsg = 1
        i_starts = 1

        for distance in distances:
            for style in styles:
                for gender in genders:

                    starts = []

                    tours = Tour.objects.filter(competition=competition, distance=distance, style=style, gender=gender)
                    if tours:
                        #import ipdb; ipdb.set_trace()
                        competitors = Competitor.objects.filter(tour__in=tours).order_by('-prior_time')
                        if competitors:

                            #import ipdb; ipdb.set_trace()

                            cdsg = Cdsg(competition=competition, number=i_cdsg)
                            cdsg.name = distance.name + ' ' + style.name + ' ' + gender
                            cdsg.save()
                            i_cdsg += 1

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

                            starts2 = []


                            for competitor_set in starts:
                                start = Start()
                                start.num = i_starts
                                start.name = distance.name + ' ' + style.name + ' ' + gender
                                start.cdsg = cdsg
                                start.save()

                                #import ipdb; ipdb.set_trace()

                                competitor_set = attribute_lanes(competitor_set)
                                for lane, competitor in competitor_set.items():
                                    order = Order(lane=lane, competitor=competitor, start=start)
                                    order.save()

                                starts2.append(start)
                                i_starts += 1
                
    
    return HttpResponseRedirect('../../competition/starts/'+competition_id+'/')

def tour(request, id):

    res = []    

    tour = Tour.objects.get(pk=id)
    tour_name = tour.distance.name + ' ' + tour.style.name + ' ' + tour.age.name + ' ' + tour.gender
    competitors = Competitor.objects.filter(tour=tour)
    for competitor in competitors:
        try:
            result = Result.objects.get(competitor=competitor)
            tag1 = ''
            if competitor.main_distance:
                tag1 = '*'
            competitor_data = tag1 + competitor.person.last_name + ' ' + competitor.person.first_name + ' ('+competitor.userrequest.team.name+')'
            res.append((competitor_data,result.time))
        except:
            pass

    res = sorted(res, key=lambda x: x[1])
            
    return render(request, 'pgups/tour.html', {'res': res, 'tour_name': tour_name},)    


# ajax для селектора туров в заявке
def get_tours(request, age, gender, competition_id):
    now = datetime.datetime.now()
    age = now.year - int(age)
    age = Age.objects.get(min_age__lte=age, max_age__gte=age)
    competition = get_object_or_404(Competition, pk=competition_id)
    tours = Tour.objects.filter(age=age, gender=gender, competition=competition)
    tour_dict = {}
    for tour in tours:
        tour_dict[tour.id] = tour.__str__()
    return HttpResponse(json.dumps(tour_dict), content_type="application/json")



