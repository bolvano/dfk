# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, render_to_response,redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.forms import modelformset_factory

import datetime
import json

from .models import Userrequest, Person, Competition, Team, Competitor, Tour, Age, Distance, Style, Start, Cdsg

from django.forms.widgets import TextInput

from django.contrib.auth import authenticate, login, logout

from collections import defaultdict

from django.db.models import Count


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
        #import ipdb; ipdb.set_trace()
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

        return round(minutes_seconds + seconds, 2)


def index(request):
    competitions = Competition.objects.all().order_by('date_start')
    return render(request, 'pgups/index.html', {'competitions': competitions},)

def competition(request, competition_id):

    competition = get_object_or_404(Competition, pk=competition_id)
    userrequests = Userrequest.objects.filter(competition=competition)
    teams = set([userrequest.team for userrequest in userrequests if userrequest.team is not None])

    if request.method == "POST":
        #import ipdb; ipdb.set_trace()

        points = {1:30, 2:25, 3:20, 4:15, 5:10}

        close = request.POST.get("close", '0')
        if close == '1':
            competition.finished=True
            tours = Tour.objects.filter(competition=competition)
            for tour in tours:
                competitors = Competitor.objects.filter(tour=tour,
                                                        approved=True,
                                                        main_distance=True,
                                                        disqualification=0,
                                                        time__gt=0).order_by('time')
                competitors = list(competitors)
                for i in range(1,6):
                    if competitors:
                        c = competitors.pop(0)
                        if i in points:
                            c.points = points[i]
                        if i <= 3:
                            c.result = i
                        c.save()

                    else:
                        break
        else:
            competition.finished=False
            tours = Tour.objects.filter(competition=competition)
            for tour in tours:
                competitors = Competitor.objects.filter(tour=tour)
                for c in competitors:
                    c.result = 0
                    c.points = 0
                    c.save()
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

    disqualification_dict = {1:'Неявка',
                             2: 'Фальстарт',
                             3:'Нарушение правил поворота',
                             4:'Нарушение правил прохождения дистанции'}

    results = []
    competition = get_object_or_404(Competition, pk=competition_id)
    tours = Tour.objects.filter(competition=competition)
    for tour in tours:
        competitors = []

        for c in tour.competitor_set.all():
            if c.approved:
                competitors.append(c)

        competitors.sort(key=lambda c: c.time)
        competitors_good = list(filter(lambda c: c.disqualification == 0, competitors))
        competitors_bad = list(filter(lambda c: c.disqualification > 0, competitors))

        competitors_bad = [(c,disqualification_dict[c.disqualification]) for c in  competitors_bad]

        results.append((tour,competitors_good,competitors_bad, competitors))

    return render(request, 'pgups/results_tours.html', {'results': results,
                                                        'tours':tours,
                                                        'competition': competition
                                                        },)

def results_teams(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)
    tours = Tour.objects.filter(competition=competition)
    result = {}
    result_list = []
    for tour in tours:
        competitors = Competitor.objects.filter(tour=tour,
                                                approved=True,
                                                main_distance=True,
                                                disqualification=0,
                                                time__gt=0).order_by('time')
        for competitor in competitors:
            if competitor.userrequest.team:
                if competitor.userrequest.team.name in result:
                    result[competitor.userrequest.team.name] += competitor.points
                else:
                    result[competitor.userrequest.team.name] = competitor.points

    for k,v in result.items():
        result_list.append((k,v))

    result_list.sort(key=lambda c: c[1], reverse=True)

    return render(request, 'pgups/results_teams.html', {'result_list': result_list, 'competition': competition},)


# Получает IP пользователя
def get_client_ip(request):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def attribute_lanes(competitor_set, num_of_lanes):
    num_of_lanes = int(num_of_lanes)
    return_set = {}
    if num_of_lanes == 5:
        lanes = [3,2,4,1,5]
    elif num_of_lanes == 6:
        lanes = [3,4,2,5,1,6]
    for competitor in reversed(competitor_set):
        return_set[lanes.pop(0)] = competitor

    return return_set

def competition_team(request, competition_id, team_id):
    persons = []
    competition = Competition.objects.get(pk=competition_id)
    if team_id == '0':
        team = ''
        userrequests = Userrequest.objects.filter(competition=competition, team=None)
    else:
        team = Team.objects.get(pk=team_id)
        userrequests = Userrequest.objects.filter(competition=competition, team=team)
    competitors = Competitor.objects.filter(userrequest__in=userrequests)
    for c in competitors:
        if c.person not in persons:
            persons.append(c.person)
    CompetitorFormSet = modelformset_factory(Competitor,
                                             fields=('approved',),
                                             extra=0,
                                             widgets={'approved': forms.CheckboxInput()})
    if request.method == "POST":
        competitor_formset = CompetitorFormSet(request.POST)
        if(competitor_formset.is_valid()):
            competitor_formset.save()
            messages.success(request, 'Изменения сохранены')
            return HttpResponseRedirect('/competition/team/'+competition_id+'/'+team_id+'/')
    else:
        competitor_formset = CompetitorFormSet(queryset=competitors.order_by('person__last_name'))

    if persons:
        persons.sort(key=lambda c: c.last_name)
    return render(request, 'pgups/competition_team.html', {'competitor_formset': competitor_formset,
                                                           'team':team,
                                                           'competition':competition,
                                                           'persons': persons},)

def userrequest(request, userrequest_id):
    persons = []
    userrequest = get_object_or_404(Userrequest, pk=userrequest_id)
    competitors = userrequest.competitor_set.all()
    for c in competitors:
        if c.person not in persons:
            persons.append(c.person)
    CompetitorFormSet = modelformset_factory(Competitor,
                                             fields=('approved',),
                                             extra=0,
                                             widgets={'approved': forms.CheckboxInput(),})

    if request.method == "POST":
        competitor_formset = CompetitorFormSet(request.POST)
        if(competitor_formset.is_valid()):
            competitor_formset.save()
            messages.success(request, 'Изменения сохранены')
            return HttpResponseRedirect('/userrequest/'+userrequest_id+'/')
    else:
        competitor_formset = CompetitorFormSet(queryset=competitors.order_by('person__last_name'))

    if persons:
        persons.sort(key=lambda c: c.last_name)

    return render(request, 'pgups/userrequest.html', {'userrequest': userrequest,
                                                      'competitor_formset': competitor_formset,
                                                      'persons':persons},)

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

    ResultFormSet = modelformset_factory(Competitor,
                                         fields=('time', 'disqualification'),
                                         extra=0,
                                         widgets={'time': SplitTimeWidget(),
                                                  'disqualification':
                                                      forms.widgets.Select(
                                                          attrs=None,
                                                          choices=([0,''],
                                                                   [1,'Неявка'],
                                                                   [2,'Фальстарт'],
                                                                   [3,'Нарушение правил поворота'],
                                                                   [4,'Нарушение правил прохождения дистанции']
                                                                    )
                                                      )
                                                  }
                                         )

    if request.method == "POST":
        result_formset = ResultFormSet(request.POST)
        #import ipdb; ipdb.set_trace()
        if(result_formset.is_valid()):
            result_formset.save()
            messages.success(request, 'Результат сохранён')
            return HttpResponseRedirect('../../../competition/start_result_view/'+start_id+'/')

    else:
        result_formset = ResultFormSet(queryset=competitors.order_by('lane'))

    return render(request, 'pgups/start_result.html', {'result_formset' : result_formset,
                                                       'start_num': start.num,
                                                       'cdsg_name': start.cdsg.__str__(),
                                                       'next_start_id':next_start_id,
                                                       'prev_start_id':prev_start_id,
                                                       'competition_id':competition.id} )


def start_result_view(request, start_id):
    start = Start.objects.get(pk=start_id)

    competition = start.cdsg.competition
    cdsgs = Cdsg.objects.filter(competition=competition)

    last_in_cdsg = False
    cdsg = start.cdsg
    if start.num == Start.objects.filter(cdsg=cdsg).order_by('-num')[0].num:
        last_in_cdsg = True

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
    return render(request, 'pgups/start_result_view.html', {'competitors' : competitors,
                                                            'start_num': start.num,
                                                            'last_in_cdsg':last_in_cdsg,
                                                            'cdsg_id':start.cdsg.id,
                                                            'cdsg_name': start.cdsg.__str__(),
                                                            'start_id': start.id,
                                                            'next_start_id':next_start_id,
                                                            'prev_start_id':prev_start_id,
                                                            'competition_id':competition.id} )


def reg_request(request, userrequest_id=None):
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

        if 'userrequest_id' in data:
            userrequest = Userrequest.objects.get(pk=data['userrequest_id'])
            userrequest.team = team
            userrequest.representative = representative
            userrequest.phone = phone
            userrequest.email = email
        else:
            userrequest = Userrequest(competition=competition,
                                      team=team,
                                      representative=representative,
                                      phone=phone,
                                      email=email,
                                      ip=ip)
        userrequest.save()

        actual_person_ids = []

        for person in data['persons']:
            first_name = person['first_name']
            last_name = person['last_name']
            birth_year = person['birth_year']
            gender = person['gender']

            if 'id' in person:
                new_person = Person.objects.get(pk=person['id'])
            else:
                new_person = Person()
                new_person.userrequest = userrequest

            new_person.first_name = first_name.lower()
            new_person.last_name = last_name.lower()
            new_person.birth_year = birth_year
            new_person.gender = gender

            new_person.save()


            actual_person_ids.append(new_person.id)
            actual_competitor_ids = []

            main_distance = True
            for competitor in person['competitors']:
                tour = Tour.objects.get(pk=competitor['tour']['id'])
                age = Age.objects.get(pk=competitor['tour']['age_id'])
                if 'prior_time' in competitor and competitor['prior_time']:
                    prior_time=float(competitor['prior_time'])
                else:
                    prior_time = 0
                if 'prior_time_minutes' in competitor and competitor['prior_time_minutes']:
                    prior_time += int(competitor['prior_time_minutes'])*60

                if 'id' in competitor:
                    new_competitor = Competitor.objects.get(pk=competitor['id'])
                else:
                    new_competitor = Competitor()

                new_competitor.person=new_person
                new_competitor.userrequest=userrequest
                new_competitor.tour=tour
                new_competitor.age=age
                new_competitor.prior_time=prior_time
                new_competitor.main_distance=main_distance
                new_competitor.time=0
                new_competitor.save()

                actual_competitor_ids.append(new_competitor.id)

                main_distance = False
            for c in Competitor.objects.filter(person=new_person, userrequest=userrequest):
                if c.id not in actual_competitor_ids:
                    c.delete()
        for p in Person.objects.filter(userrequest=userrequest):
            if p.id not in actual_person_ids:
                p.delete()
    else:
        pass

    data = {}

    return render(request, 'pgups/reg.html', data)


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

        #import ipdb; ipdb.set_trace()
        competition_id = request.POST.get("competition_id", "")
        num_of_lanes = int(request.POST.get("lanes", 5))
        age_diff = bool(request.POST.get("ages", False))

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
                    #competitor.disqualification = 0
                    #competitor.time = 0
                    competitor.save()
            cdsg.delete()

        distances = Distance.objects.all().order_by('meters') #[50, 100]
        styles = [Style.objects.get(name='на спине'),
                  Style.objects.get(name='вольный стиль'),
                  Style.objects.get(name='брасс'),
                  Style.objects.get(name='баттерфляй'),
                  Style.objects.get(name='комплекс') ]
        genders = ['Ж','М']
        ages = Age.objects.all().order_by('min_age')

        i_cdsg = 1
        i_starts = 1

        for distance in distances:
            for style in styles:
                if age_diff:
                    for age in ages:
                        for gender in genders:

                            starts = []
                            tours = Tour.objects.filter(competition=competition,
                                                        distance=distance,
                                                        style=style,
                                                        gender=gender,
                                                        age=age)
                            if tours:
                                #import ipdb; ipdb.set_trace()
                                competitors_no_prior = Competitor.objects\
                                    .filter(tour__in=tours)\
                                    .filter(approved=True)\
                                    .filter(prior_time=0)
                                competitors_prior = Competitor.objects\
                                    .filter(tour__in=tours)\
                                    .filter(approved=True)\
                                    .filter(prior_time__gt=0).order_by('-prior_time')

                                competitors = list(competitors_no_prior) + list(competitors_prior)

                                if competitors:
                                    #import ipdb; ipdb.set_trace()
                                    cdsg = Cdsg(competition=competition, number=i_cdsg)
                                    cdsg.name = distance.name + ' ' + style.name + ' ' + age.name + ' ' + gender
                                    cdsg.save()
                                    i_cdsg += 1
                                    (full_starts, remainders) = divmod(len(competitors), num_of_lanes)

                                    #import ipdb; ipdb.set_trace()

                                    if remainders > 0: # есть остаток
                                        if full_starts > 0 and remainders < minimal:
                                            #есть полные и остаток меньше трёх, перегруппировка первых двух
                                            starts.append(competitors[:minimal])
                                            # первый старт - три участника
                                            if full_starts == 1:
                                                # был один полный старт: будет два неполных
                                                starts.append(competitors[minimal:])
                                            else:
                                                # было более одного полного: второй будет неполным, остальные полными
                                                begin = minimal
                                                end = begin + num_of_lanes - (minimal - remainders)

                                                starts.append(competitors[begin:end])

                                                begin = end
                                                for i in range(0, full_starts - 1):
                                                    end = begin + num_of_lanes
                                                    starts.append(competitors[begin:end])
                                                    begin = end

                                        elif full_starts > 0 and remainders >= minimal:
                                            # есть полные старты и остаток три или больше
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
                                        start.name = distance.name + ' ' \
                                                     + style.name + ' ' \
                                                     + age.name + ' ' \
                                                     + gender
                                        start.cdsg = cdsg
                                        start.save()

                                        #import ipdb; ipdb.set_trace()

                                        competitor_set = attribute_lanes(competitor_set, num_of_lanes)
                                        for lane, competitor in competitor_set.items():
                                            competitor.lane = lane
                                            competitor.start = start
                                            competitor.save()

                                        starts2.append(start)
                                        i_starts += 1
                else:
                    for gender in genders:
                        starts = []
                        tours = Tour.objects.filter(competition=competition,
                                                    distance=distance,
                                                    style=style,
                                                    gender=gender)
                        if tours:
                            #import ipdb; ipdb.set_trace()
                            competitors_no_prior = Competitor.objects\
                                .filter(tour__in=tours)\
                                .filter(approved=True)\
                                .filter(prior_time=0)
                            competitors_prior = Competitor.objects\
                                .filter(tour__in=tours)\
                                .filter(approved=True)\
                                .filter(prior_time__gt=0).order_by('-prior_time')
                            competitors = list(competitors_no_prior) + list(competitors_prior)
                            if competitors:
                                #import ipdb; ipdb.set_trace()
                                cdsg = Cdsg(competition=competition, number=i_cdsg)
                                cdsg.name = distance.name + ' ' + style.name + ' ' + gender
                                cdsg.save()
                                i_cdsg += 1
                                (full_starts, remainders) = divmod(len(competitors), int(num_of_lanes))
                                #import ipdb; ipdb.set_trace()

                                if remainders > 0: # есть остаток
                                    if full_starts > 0 and remainders < minimal:
                                        #есть полные и остаток меньше трёх, перегруппировка первых двух
                                        starts.append(competitors[:minimal])
                                        # первый старт - три участника
                                        if full_starts == 1:
                                            # был один полный старт: будет два неполных
                                            starts.append(competitors[minimal:])
                                        else:
                                            # было более одного полного: второй будет неполным, остальные полными
                                            begin = minimal
                                            end = begin + num_of_lanes - (minimal - remainders)

                                            starts.append(competitors[begin:end])

                                            begin = end
                                            for i in range(0, full_starts - 1):
                                                end = begin + num_of_lanes
                                                starts.append(competitors[begin:end])
                                                begin = end

                                    elif full_starts > 0 and remainders >= minimal:
                                        # есть полные старты и остаток три или больше
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

                                    competitor_set = attribute_lanes(competitor_set, num_of_lanes)
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

    competition_id = tour.competition.id
    competition_name = tour.competition.name

    tour_name = tour.distance.name + ' ' + tour.style.name + ' ' + tour.age.name + ' ' + tour.gender
    competitors = Competitor.objects.filter(tour=tour, approved=True)
    for competitor in competitors:
        try:
            tag1 = ''
            if competitor.main_distance:
                tag1 = '*'
            competitor_data = tag1 + competitor.person.last_name.title() + ' ' \
                              + competitor.person.first_name.title() \
                              + ' ('+competitor.userrequest.team.name+')'
            m, s = divmod(competitor.prior_time, 60)
            formatted_prior =  "%d:%0.2f" % (m, s)
            res.append((competitor_data, formatted_prior))
        except:
            pass

    res = sorted(res, key=lambda x: x[1])

    return render(request, 'pgups/tour.html', {'competition_id':competition_id,
                                               'competition_name':competition_name,
                                               'res': res,
                                               'tour_name': tour_name},)


# ajax-контроллер
def get_competitions(request, userrequest_id=None):
    competition_list = []
    competitions = Competition.objects.filter(finished=False)
    for c in competitions:
        tours = []
        competition = {'name': c.name, 'id': c.id, 'type':c.typ}
        tour_objects = Tour.objects.filter(competition=c)
        for t in tour_objects:
            tours.append({'id':t.id,
                          'age_id':t.age.id,
                          'min_age': t.age.min_age,
                          'max_age': t.age.max_age,
                          'gender':t.gender,
                          'name':t.__str__(),
                          'out':t.out})
        competition['tours'] = tours
        competition_list.append(competition)
        source_data = {}

    if userrequest_id:
        userrequest = Userrequest.objects.get(pk=userrequest_id)
        source_data['userrequest_id'] = userrequest.id
        source_data['competition_id'] = userrequest.competition.id
        if userrequest.team:
            source_data['team_id'] = userrequest.team.id
        source_data['representative'] = userrequest.representative
        source_data['phone'] = userrequest.phone
        source_data['email'] = userrequest.email
        source_data['ip'] = userrequest.ip
        source_data['date'] = str(userrequest.date)

        source_data['persons'] = []
        competitors = Competitor.objects.filter(userrequest=userrequest)
        persons = []
        for competitor in competitors:
            if competitor.person not in persons:
                persons.append(competitor.person)
        person_i = 0
        for person in persons:
            person_obj = {"personId": "person-"+str(person_i),
                          "id": person.id,
                          "last_name" :person.last_name,
                          "first_name" :person.first_name,
                          "birth_year" :person.birth_year,
                          "gender": person.gender }
            person_i += 1
            person_obj["competitors"] = []
            competitor_i = 0

            for competitor in Competitor.objects.filter(person=person,
                                                        userrequest=userrequest).order_by('-main_distance'):

                prior_time = competitor.prior_time
                prior_time_minutes = 0
                if prior_time >= 60:
                    prior_time_minutes, prior_time = divmod(prior_time, 60)
                    prior_time = round(prior_time, 2)

                competitor_obj = {"competitorId": "competitor-"+str(competitor_i),
                                  "id": competitor.id,
                                  "tour": {"id": competitor.tour.id,
                                           "name": competitor.tour.__str__(),
                                           "age_id": competitor.tour.age.id,
                                           "out": competitor.tour.out}}
                if prior_time:
                    competitor_obj['prior_time'] = prior_time

                if prior_time_minutes:
                    competitor_obj['prior_time_minutes'] = prior_time_minutes

                competitor_i += 1

                person_obj["competitors"].append(competitor_obj)
            source_data['persons'].append(person_obj)

    return HttpResponse(json.dumps({"competition_list": competition_list,
                                    "source_data": source_data}),
                        content_type="application/json")

def get_teams(request):
    team_list = []
    teams = Team.objects.all()
    for t in teams:
        team = {'id':t.id, 'name':t.name}
        team_list.append(team)
    return HttpResponse(json.dumps(team_list), content_type="application/json")

def get_ages_distances_styles(request, competition_id=None):
    if competition_id:
        competition = Competition.objects.get(pk=competition_id)
        data = {}
        data['data'] = {}
        data['fetchedData'] = {}
        data['tours'] = []

        data['data']['id'] = competition_id
        data['data']['name'] = competition.name

        if competition.typ.lower() == 'взрослые':
            data['data']['type'] = '1'
        elif competition.typ.lower() == 'детские':
            data['data']['type'] = '0'
        else:
            data['data']['type'] = '2'

        data['data']['date_start'] = competition.date_start.isoformat()
        data['data']['date_finish'] = competition.date_end.isoformat()

        tours = Tour.objects.filter(competition=competition)

        distances = list(Distance.objects.all())
        competition_distances = list(Distance.objects.distinct().filter(tour__in=tours))
        data['fetchedData']['distances'] = []
        for distance in distances:
            obj = {'name':distance.name,'id': distance.id}
            data['fetchedData']['distances'].append(obj)

        styles = list(Style.objects.all())
        competition_styles = list(Style.objects.distinct().filter(tour__in=tours))
        data['fetchedData']['styles'] = []
        for style in styles:
            obj = {'name':style.name,'id': style.id}
            data['fetchedData']['styles'].append(obj)

        ages = list(Age.objects.all())
        competition_ages = list(Age.objects.distinct().filter(tour__in=tours))
        data['fetchedData']['ages'] = []
        for age in ages:
            obj = {'name':age.name,'id': age.id, 'kids': age.kids, 'min_age': age.min_age, 'max_age':  age.max_age}
            data['fetchedData']['ages'].append(obj)

        for tour in tours:
            num_of_competitors = len(Competitor.objects.filter(tour=tour))
            data['tours'].append({'id': tour.id,
                                  'age': tour.age.id,
                                  'name': tour.__str__(),
                                  'distance': tour.distance.id,
                                  'style': tour.style.id,
                                  'gender': tour.gender,
                                  'min_age': tour.age.min_age,
                                  'max_age': tour.age.max_age,
                                  'num_of_competitors': num_of_competitors
            })

        return HttpResponse(json.dumps({'ages': data['fetchedData']['ages'],
                                        'styles': data['fetchedData']['styles'],
                                        'distances': data['fetchedData']['distances'],
                                        'tours': data['tours'],
                                        'name': data['data']['name'],
                                        'type': data['data']['type'],
                                        'date_start': data['data']['date_start'],
                                        'date_finish': data['data']['date_finish'],
                                        }), content_type="application/json")

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
    return HttpResponse(json.dumps({'ages':age_list,
                                    'distances':distance_list,
                                    'styles':style_list
                                    }), content_type="application/json")


def get_competition_starts(request, id):
    starts_list = []
    competition = Competition.objects.get(pk=id)
    userrequests = Userrequest.objects.filter(competition=competition)
    no_start_competitors = Competitor.objects.filter(userrequest__in=userrequests, approved=True, start__isnull=True)
    to_buffer = []
    for c in no_start_competitors:
        if c.userrequest.team:
            team = c.userrequest.team.name
        else:
            team = 'Инд.'
        to_buffer.append({'id':c.id,
                         'last_name':c.person.last_name,
                         'first_name':c.person.first_name,
                         'team':team,
                         'age':c.age.name,
                         'prior_time':c.prior_time,
                         'main_distance': c.main_distance,
                         'person_id': c.person.id,
                         'style': c.tour.style.name,
                         'distance': c.tour.distance.name,
                         'gender': c.tour.gender
                         })
    buffer = {'role': 'buffer', 'competitors': to_buffer}
    starts_list.append(buffer)

    cdsg_list = Cdsg.objects.filter(competition=competition)
    for cdsg in cdsg_list:
        starts = Start.objects.filter(cdsg=cdsg)
        for start in starts:
            start_obj = {'id':start.id, 'competitors':[]}
            competitors = Competitor.objects.filter(start=start)
            for competitor in competitors:
                if competitor.userrequest.team:
                    team = competitor.userrequest.team.name
                else:
                    team = 'Инд.'
                start_obj['competitors'].append({'id':competitor.id,
                                                 'last_name':competitor.person.last_name,
                                                 'first_name':competitor.person.first_name,
                                                 'team':team,
                                                 'age':competitor.age.name,
                                                 'prior_time':competitor.prior_time,
                                                 'main_distance': competitor.main_distance,
                                                 'person_id': competitor.person.id,
                                                 'style': competitor.tour.style.name,
                                                 'distance': competitor.tour.distance.name,
                                                 'gender': competitor.tour.gender
                                                 })
            starts_list.append(start_obj)
    return HttpResponse(json.dumps({'competition_id':competition.id,
                                    'competition_name':competition.name,
                                    'starts_list':starts_list
                                    }), content_type="application/json")

# форма создания соревнований
def create_competition(request, competition_id=None):
    if request.method == "POST":

        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        if data['type'] == '1':
            typ = 'взрослые'
        elif data['type'] == '0':
            typ = 'детские'
        else:
            typ = 'смешанные'

        import ipdb; ipdb.set_trace()

        if 'id' in data:
            date_start = datetime.datetime.strptime(data['date_start'], "%Y-%m-%dT%H:%M:%S.%fZ")
            date_end = datetime.datetime.strptime(data['date_finish'], "%Y-%m-%dT%H:%M:%S.%fZ")
            new_competition = False
            competition = Competition.objects.get(pk=data['id'])
            competition.name = data['name']
            competition.typ = typ
            competition.date_start = date_start
            competition.date_end = date_end
            competition.finished = False

        else:
            date_start = datetime.datetime.strptime(data['date_start'], "%Y-%m-%dT%H:%M:%S.%fZ")+\
                         datetime.timedelta(days=1)
            date_end = datetime.datetime.strptime(data['date_finish'], "%Y-%m-%dT%H:%M:%S.%fZ")+\
                       datetime.timedelta(days=1)
            new_competition = True
            competition = Competition(name=data['name'],
                                      typ=typ,
                                      date_start=date_start,
                                      date_end=date_end,
                                      finished=False)
        competition.save()

        if new_competition:
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
        else:
            got_out_of_order_tours = False
            existing_tours = Tour.objects.filter(competition=competition)
            if 'tours' in data:
                form_tours = data['tours']

                #deleteng non-present in form
                for tour in existing_tours:
                    if tour.id not in [t['id'] for t in form_tours if 'id' in t]:
                        tour.delete()

                #adding new ones
                for tour in form_tours:
                    if 'new' in tour:
                        style = Style.objects.get(pk=tour['style'])
                        age = Age.objects.get(pk=tour['age'])
                        distance = Distance.objects.get(pk=tour['distance'])

                        new_tour = Tour(competition=competition, finished=False)
                        new_tour.gender = tour['gender']
                        new_tour.style = style
                        new_tour.distance = distance
                        new_tour.age = age

                        if 'out' in tour:
                            new_tour.out = True
                            got_out_of_order_tours = True

                        new_tour.save()
            else:
                for tour in existing_tours:
                    tour.delete()
            if got_out_of_order_tours:
                competition.typ = 'смешанные'
                competition.save()
    else:
        data = {}

    return render(request, 'pgups/competition_create.html', data, )


def competition_starts_sort(request, competition_id):
    if request.POST:

        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        competition = Competition.objects.get(pk=data['competition_id'])
        num_of_lanes = data['max_length']
        starts_list = data['starts_list']
        starts_list = starts_list[1:]

        cdsg = Cdsg(competition=competition, number=1)
        cdsg.name = 'Все заплывы'
        cdsg.save()

        i_starts = 1

        total_competitors = {}

        valid_start_ids = []
        for s in starts_list:

            competitors = s['competitors']
            if len(competitors) == 0:
                continue

            if 'id' in s:
                start = Start.objects.get(pk=s['id'])
                start.num = i_starts
                #start.name = distance.name + ' ' + style.name + ' ' + age.name + ' ' + gender
                start.cdsg = cdsg
                start.save()
            else:
                start = Start()
                start.num = i_starts
                start.name = str(start.num)
                start.cdsg = cdsg
                start.save()

            valid_start_ids.append(start.id)

            #import ipdb; ipdb.set_trace()

            name_dict = {'distance':set(), 'style':set(), 'age':set(), 'gender':set()}
            competitor_set = []
            for c in competitors:
                cc = Competitor.objects.get(pk=c['id'])
                competitor_set.append(cc)
                if cc.tour.id in total_competitors:
                    total_competitors[cc.tour.id] += 1
                else:
                    total_competitors[cc.tour.id] = 1

            for c in competitor_set:
                name_dict['distance'].add(c.tour.distance.name)
                name_dict['style'].add(c.tour.style.name)
                name_dict['age'].add(c.age.name)
                name_dict['gender'].add(c.tour.gender)

            start.name = ', '.join(name_dict['distance']) + ' ' \
                         + ', '.join(name_dict['style']) + ' ' \
                         + ', '.join(name_dict['age']) + ' '\
                         +', '.join(name_dict['gender'])
            start.save()

            competitors_good = list(filter(lambda c: c.prior_time > 0, competitor_set))
            competitors_bad = list(filter(lambda c: c.prior_time == 0, competitor_set))

            competitors_good.sort(key=lambda c: c.prior_time, reverse=True)

            competitor_set = competitors_bad + competitors_good

            competitor_set = attribute_lanes(competitor_set, num_of_lanes)
            for lane, competitor in competitor_set.items():
                competitor.lane = lane
                competitor.start = start
                competitor.save()

            i_starts += 1

        valid_cdsg_ids = [cdsg.id,]
        passed_starts = []
        finished_tours_ids = []
        passed_competitors = {}

        cdsgs = Cdsg.objects.filter(competition=competition)
        all_starts = Start.objects.filter(cdsg__in=cdsgs)
        for start in all_starts:
            if start.id not in valid_start_ids:
                start.delete()

        for c in cdsgs:
            if c.id not in valid_cdsg_ids:
                c.delete()

        i_cdsg = 1

        for s in Start.objects.filter(cdsg__in=cdsgs).order_by('num'):
            for c in Competitor.objects.filter(start=s):
                if c.tour.id in passed_competitors:
                    passed_competitors[c.tour.id] += 1
                else:
                    passed_competitors[c.tour.id] = 1
            for k,v in passed_competitors.items():
                if v == total_competitors[k]:
                    finished_tours_ids.append(k)
                    passed_competitors[k] = 0

            passed_starts.append(s)

            if len(finished_tours_ids):
                cdsg_new = Cdsg(competition=competition, number=i_cdsg)
                cdsg_new.name = 'Группа заплывов №' + str(i_cdsg)
                cdsg_new.save()
                for ps in passed_starts:
                    ps.cdsg = cdsg_new
                    ps.save()
                finished_tours_ids = []
                passed_starts = []
                i_cdsg += 1

        #import ipdb; ipdb.set_trace()
        cdsg.delete()

        return HttpResponseRedirect('../../competition/starts/'+competition_id+'/')

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

def cdsg_print(request, cdsg_id):

    cdsg = Cdsg.objects.get(pk=cdsg_id)
    starts = Start.objects.filter(cdsg=cdsg)
    competitors = Competitor.objects.filter(start__in=starts, approved=True)
    #все участники стартов cdsg filter(approved=True)

    prev_cdsgs = Cdsg.objects.filter(number__lt=cdsg.number)
    prev_starts = Start.objects.filter(cdsg__in=prev_cdsgs)
    prev_competitors = Competitor.objects.filter(start__in=prev_starts, approved=True)

    tour_dict = defaultdict(list)

    tours = []
    for c in competitors:
        if c.tour not in tours:
            tours.append(c.tour)

    for tour in tours:
        total = Competitor.objects.filter(tour=tour, approved=True).count()
        passed = competitors.filter(tour=tour).count() + prev_competitors.filter(tour=tour).count()
        if total == passed:
            tour_competitors = Competitor.objects.filter(tour=tour, approved=True)
            for competitor in tour_competitors:
                tour_dict[competitor.tour.id].append(competitor)

    tour_dict = dict(tour_dict)

    tour_dict = {k: sorted((c for c in v if c.disqualification==0 and c.time>0),
                           key=lambda k:k.time)+list(filter(lambda c: c.disqualification > 0 or c.time == 0, v))
                 for k, v in tour_dict.items()}
    tour_list = [(Tour.objects.get(pk=k), v) for k, v in tour_dict.items()]
    #tour_list.sort(key=lambda tup: tup[0].style)
    return render(request, 'pgups/cdsg_print.html', { 'cdsg': cdsg, 'tour_dict':tour_dict, 'tour_list':tour_list}, )

def starts_print(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)
    cdsg_list = Cdsg.objects.filter(competition=competition)
    return render(request, 'pgups/starts_print.html', {'cdsg_list': cdsg_list,
                                                             'competition_id':competition_id,
                                                             'competition': competition,
                                                            },)

def final_print(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)

    cdsgs = Cdsg.objects.filter(competition=competition)

    starts = Start.objects.filter(cdsg__in=cdsgs)

    tour_dict = defaultdict(list)
    competitors = Competitor.objects.filter(start__in=starts)
    for competitor in competitors:
        tour_dict[competitor.tour.id].append(competitor)

    tour_dict = dict(tour_dict)

    tour_dict = {k: sorted((c for c in v if c.disqualification==0),
                           key=lambda k:k.time)+list(filter(lambda c: c.disqualification > 0, v))
                 for k, v in tour_dict.items()}
    tour_list = [(Tour.objects.get(pk=k), v) for k, v in tour_dict.items()]

    styles = {'на спине': 1, 'вольный стиль': 2, 'брасс': 3, 'баттерфляй': 4, 'комплекс': 5 }
    ages = Age.objects.all().order_by('min_age')
    ages = {key.name: index for index, key in enumerate(ages)}
    genders = {'Ж':1,'М':2}

    tour_list.sort(key=lambda tup: genders[tup[0].gender])
    tour_list.sort(key=lambda tup: ages[tup[0].age.name])
    tour_list.sort(key=lambda tup: styles[tup[0].style.name])

    return render(request, 'pgups/final_print.html', { 'competition': competition,
                                                       'tour_dict':tour_dict,
                                                       'tour_list':tour_list}, )

