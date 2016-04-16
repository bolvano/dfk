# -*- coding: utf-8 -*- 
from django.shortcuts import render, get_object_or_404, render_to_response,redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.forms import modelformset_factory

import datetime
import json
import re

from .models import Userrequest, Person, Competition, Team, Competitor, Tour, Age, Distance, Style, Start, Cdsg

from django.forms.widgets import TextInput

#from django.http import *
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

class NumberInput(TextInput):
    input_type = 'number'

class SplitTimeWidget(forms.widgets.MultiWidget):

    def __init__(self, *args, **kwargs):
        widgets = (
            NumberInput(attrs={'min': '0', 'step': '1',
                               'class': 'form-control pull-left',
                               'placeholder': 'мин.'}),
            NumberInput(attrs={'min': '0', 'max': '59,99',
                               'step': '0.01', 'class': 'form-control pull-left',
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
        if not minutes:
            minutes_seconds = 0
        else:
            minutes_seconds = int(minutes)*60

        seconds = self.widgets[1].value_from_datadict(data, files, name + '_1')
        if not seconds:
            seconds = 0
        else:
            seconds = float(seconds)

        return minutes_seconds + seconds


def index(request):
    competitions = Competition.objects.all().order_by('date_start')
    return render(request, 'pgups/index.html', {'competitions': competitions},)

def competition(request, competition_id):

    competition = get_object_or_404(Competition, pk=competition_id)
    userrequests = Userrequest.objects.filter(competition=competition)
    teams = set([userrequest.team for userrequest in userrequests if userrequest.team is not None])

    if request.method == "POST":
        #import ipdb; ipdb.set_trace()
        close = request.POST.get("close", '0')
        if close == '1':
            competition.finished=True
        else:
            competition.finished=False
        competition.save()

    return render(request, 'pgups/competition.html', {'competition': competition, 'teams':teams},)

def person(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    return render(request, 'pgups/person.html', {'person': person},)

def results_starts(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    cdsgs = Cdsg.objects.filter(competition=competition)
    starts = Start.objects.filter(cdsg__in=cdsgs).order_by('num')

    return render(request, 'pgups/results_starts.html', {'competition':competition, 'starts':starts},)

def results_tours(request, competition_id):

    disqualification_dict = {1:'Неявка', 2: 'Фальстарт', 3:'Нарушение правил'}

    results = []
    competition = get_object_or_404(Competition, pk=competition_id)
    tours = Tour.objects.filter(competition=competition)
    for tour in tours:
        competitors = []

        for c in tour.competitor_set.all():
            competitors.append(c)

        competitors.sort(key=lambda c: c.time)
        competitors_good = list(filter(lambda c: c.disqualification == 0, competitors))
        competitors_bad = list(filter(lambda c: c.disqualification > 0, competitors))

        competitors_bad = [(c,disqualification_dict[c.disqualification]) for c in  competitors_bad]

        results.append((tour,competitors_good,competitors_bad, competitors))

    return render(request, 'pgups/results_tours.html', {'results': results, 'tours':tours, 'competition': competition},)

def results_teams(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)
    tours = Tour.objects.filter(competition=competition)
    result = {}
    for tour in tours:
        competitors = []
        for c in tour.competitor_set.all():
            competitors.append(c)
        competitors.sort(key=lambda c: c.time)
        competitors_good = list(filter(lambda c: c.time > 0, competitors))
        competitors_good = list(filter(lambda c: c.userrequest.team is not None, competitors_good))
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

def userrequest(request, userrequest_id):
    userrequest = get_object_or_404(Userrequest, pk=userrequest_id)
    competitors = userrequest.competitor_set.all()
    CompetitorFormSet = modelformset_factory(Competitor, fields=('approved',), extra=0, widgets={'approved': forms.CheckboxInput()})

    if request.method == "POST":
        competitor_formset = CompetitorFormSet(request.POST)
        if(competitor_formset.is_valid()):
            competitor_formset.save()
            messages.success(request, 'Изменения сохранены')
            return HttpResponseRedirect('/userrequest/'+userrequest_id+'/')
    else:
        competitor_formset = CompetitorFormSet(queryset=competitors.order_by('person__last_name'))

    return render(request, 'pgups/userrequest.html', {'userrequest': userrequest, 'competitor_formset': competitor_formset},)

def start_result(request, start_id):

    start = Start.objects.get(pk=start_id)
    competitors = Competitor.objects.filter(start=start)
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

    #import ipdb; ipdb.set_trace()

    ResultFormSet = modelformset_factory(Competitor, fields=('time', 'disqualification'), extra=0, widgets={'time': SplitTimeWidget(), 'disqualification':forms.widgets.Select(attrs=None, choices=([0,''],[1,'Неявка'],[2,'Фальстарт'], [3,'Нарушение']))})

    if request.method == "POST":
        result_formset = ResultFormSet(request.POST)
        #import ipdb; ipdb.set_trace()
        if(result_formset.is_valid()):
            result_formset.save()
            messages.success(request, 'Результат сохранён')
            return HttpResponseRedirect('../../../competition/start_result_view/'+start_id+'/')

    else:
        result_formset = ResultFormSet(queryset=competitors.order_by('lane'))

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

    competitors = Competitor.objects.filter(start=start).order_by('lane')
    return render(request, 'pgups/start_result_view.html', {'competitors' : competitors, 'start_num': start.num, 'cdsg_name': start.cdsg.__str__(), 'start_id': start.id, 'next_start_id':next_start_id, 'prev_start_id':prev_start_id, 'competition_id':competition.id} )


def reg_request(request):
    if request.method == "POST":

        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        competition = Competition.objects.get(pk=data['competition']['id'])
        representative = data['representative']
        phone = data['phone']
        email = data['email']
        ip = get_client_ip(request)

        #import ipdb; ipdb.set_trace()

        if 'team' in data and data['team']!=None:
            team = Team.objects.get(pk=data['team']['id'])
        else:
            team = None

        userrequest = Userrequest(competition=competition, team=team, representative=representative, phone=phone, email=email, ip=ip)
        userrequest.save()

        for person in data['persons']:
            first_name = person['first_name']
            last_name = person['last_name']
            birth_year = person['birth_year']
            gender = person['gender']
            new_person = Person(first_name=first_name.lower(), last_name=last_name.lower(), birth_year=birth_year, gender=gender, userrequest=userrequest)
            new_person.save()
            main_distance = True
            for competitor in person['competitors']:
                tour = Tour.objects.get(pk=competitor['tour']['id'])
                age = Age.objects.get(pk=competitor['tour']['age_id'])
                if 'prior_time' in competitor:
                    prior_time=float(competitor['prior_time'])
                else:
                    prior_time = 0
                if 'prior_time_minutes' in competitor and competitor['prior_time_minutes']:
                    prior_time += int(competitor['prior_time_minutes'])*60
                new_competitor = Competitor(person=new_person, userrequest=userrequest, tour=tour, age=age, prior_time=prior_time, main_distance=main_distance)
                new_competitor.save()
                main_distance = False
    else:
        pass
    return render(request, 'pgups/reg.html', {}, )


def generate_tours(request, competition_id, kids):
    competition = Competition.objects.get(pk=competition_id)
    distance50 = Distance.objects.get(meters=50)
    distance100 = Distance.objects.get(meters=100)
    styles = Style.objects.all()
    if kids:
        ages = Age.objects.filter(kids=True)
    else:
        ages = Age.objects.filter(kids=False)


    for age in ages:
        for style in styles:
            for gender in ['М','Ж']:
                tour = Tour(competition=competition, style=style, age=age, gender=gender, finished=False, )
                if style.name != 'Комплекс':
                    tour.distance = distance50
                else:
                    tour.distance = distance100
                tour.save()

    return HttpResponse(json.dumps({}), content_type="application/json")


def competition_starts(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)

    cdsg_list = Cdsg.objects.filter(competition=competition)

    return render(request, 'pgups/competition_starts.html', {'cdsg_list': cdsg_list,
                                                             'competition_id':competition_id,
                                                             'competition': competition, 
                                                            },)

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
            starts = Start.objects.filter(cdsg=cdsg)
            for start in starts:
                competitors = Competitor.objects.filter(start=start)
                for competitor in competitors:
                    competitor.start = None
                    competitor.lane = None
                    competitor.result = None
                    competitor.points = 0
                    competitor.disqualification = 0
                    competitor.time = 0
                    competitor.save()
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
                        competitors_no_prior = Competitor.objects.filter(tour__in=tours).filter(approved=True).filter(prior_time=0)
                        competitors_prior = Competitor.objects.filter(tour__in=tours).filter(approved=True).filter(prior_time__gt=0).order_by('-prior_time')
                        competitors = list(competitors_no_prior) + list(competitors_prior)

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
                                    competitor.lane = lane
                                    competitor.start = start
                                    competitor.save()

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
            tag1 = ''
            if competitor.main_distance:
                tag1 = '*'
            competitor_data = tag1 + competitor.person.last_name.title() + ' ' + competitor.person.first_name.title() + ' ('+competitor.userrequest.team.name+')'
            m, s = divmod(competitor.prior_time, 60)
            formatted_prior =  "%d:%0.2f" % (m, s)
            res.append((competitor_data, formatted_prior))
        except:
            pass

    res = sorted(res, key=lambda x: x[1])
            
    return render(request, 'pgups/tour.html', {'res': res, 'tour_name': tour_name},)    


# ajax-контроллер
def get_competitions(request):
    competition_list = []
    competitions = Competition.objects.filter(finished=False)
    for c in competitions:
        tours = []
        competition = {'name': c.name, 'id': c.id, 'type':c.typ}
        tour_objects = Tour.objects.filter(competition=c)
        for t in tour_objects:
            tours.append({'id':t.id, 'age_id':t.age.id, 'min_age': t.age.min_age, 'max_age': t.age.max_age, 'gender':t.gender, 'name':t.__str__()})
        competition['tours'] = tours
        competition_list.append(competition)
    return HttpResponse(json.dumps(competition_list), content_type="application/json")

def get_teams(request):
    team_list = []
    teams = Team.objects.all()
    for t in teams:
        team = {'id':t.id, 'name':t.name}
        team_list.append(team)
    return HttpResponse(json.dumps(team_list), content_type="application/json")

def get_ages_distances_styles(request):
    age_list = []
    ages = Age.objects.all()
    for a in ages:
        age = {'id': a.id, 'name': a.name, 'kids': a.kids}
        age_list.append(age)
    distance_list = []
    distances = Distance.objects.all()
    for d in distances:
        distance = {'id': d.id, 'name': d.name}
        distance_list.append(distance)
    style_list = []
    styles = Style.objects.all()
    for s in styles:
        style = {'id': s.id, 'name': s.name}
        style_list.append(style)
    return HttpResponse(json.dumps({'ages':age_list, 'distances':distance_list, 'styles':style_list}), content_type="application/json")

def get_competition_starts(request, id):
    cdsg_starts_list = []
    competition = Competition.objects.get(pk=id)
    cdsg_list = Cdsg.objects.filter(competition=competition)
    for cdsg in cdsg_list:
        cdsg_obj = {'id':cdsg.id, 'name':cdsg.name, 'starts':[]}
        starts = Start.objects.filter(cdsg=cdsg)
        for start in starts:
            start_obj = {'id':start.id, 'num': start.num, 'competitors':[]}
            competitors = Competitor.objects.filter(start=start)
            for competitor in competitors:
                start_obj['competitors'].append({'id':competitor.id, 'lane': competitor.lane,'last_name':competitor.person.last_name, 'first_name':competitor.person.first_name, 'team':competitor.userrequest.team.name, 'age':competitor.age.name, 'prior_time':competitor.prior_time})
            cdsg_obj['starts'].append(start_obj)
        cdsg_starts_list.append(cdsg_obj)
    return HttpResponse(json.dumps({'competition_id':competition.id, 'competition_name':competition.name,'cdsg_starts_list':cdsg_starts_list}), content_type="application/json")

# форма создания соревнований
def create_competition(request):
    if request.method == "POST":

        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        date_start = datetime.datetime.strptime(data['date_start'], "%Y-%m-%dT%H:%M:%S.%fZ")+datetime.timedelta(days=1)
        date_end = datetime.datetime.strptime(data['date_finish'], "%Y-%m-%dT%H:%M:%S.%fZ")+datetime.timedelta(days=1)

        typ = 'Взрослые' if data['type'] == '1' else 'Детские'


        competition = Competition(name=data['name'], typ=typ, date_start=date_start, date_end=date_end, finished=False)
        competition.save()

        if 'tours' in data:
            for tour in data['tours']:

                style = Style.objects.get(pk=tour['style'])
                age = Age.objects.get(pk=tour['age'])
                distance = Distance.objects.get(pk=tour['distance'])

                new_tour_m = Tour(competition=competition, finished=False)
                new_tour_m.gender = 'М'
                new_tour_m.style = style
                new_tour_m.distance = distance
                new_tour_m.age = age
                new_tour_m.save()

                new_tour_f = Tour(competition=competition, finished=False)
                new_tour_f.gender = 'Ж'
                new_tour_f.style = style
                new_tour_f.distance = distance
                new_tour_f.age = age
                new_tour_f.save()

    return render(request, 'pgups/competition_create.html', {}, )


def competition_starts_sort(request, competition_id):
    return render(request, 'pgups/competition_starts_sort.html', { 'competition_id': competition_id, }, )

def login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
    return render(request, 'pgups/login.html')

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')
