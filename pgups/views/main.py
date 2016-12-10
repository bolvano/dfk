# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, render_to_response,redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.forms import modelformset_factory

from django.contrib.auth import authenticate, login, logout

from pgups.models import Userrequest, Person, Competition, Team, Competitor, Tour, Age, Cdsg


import json

from pgups.common import get_client_ip


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


def competition_starts(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)

    cdsg_list = Cdsg.objects.filter(competition=competition)

    return render(request, 'pgups/competition_starts.html', {'cdsg_list': cdsg_list,
                                                             'competition_id':competition_id,
                                                             'competition': competition,
                                                            },)


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
            if m:
                formatted_prior =  "%d:%0.2f" % (m, s)
            else:
                formatted_prior = "%0.2f" % s
            res.append((competitor_data, formatted_prior))
        except:
            pass

    res = sorted(res, key=lambda x: x[1])

    return render(request, 'pgups/tour.html', {'competition_id':competition_id,
                                               'competition_name':competition_name,
                                               'res': res,
                                               'tour_name': tour_name},)


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

