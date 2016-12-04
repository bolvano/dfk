# -*- coding: utf-8 -*-

import json
from pgups.models import Userrequest, Competition, Team, TeamRelay, Competitor, Tour, TourRelay, Age, Distance, \
    DistanceRelay, Style, Start, Cdsg
from django.http import HttpResponse


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
        data['toursRelay'] = []

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
        toursRelay = TourRelay.objects.filter(competition=competition)

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

        ages = list(Age.objects.all().order_by('min_age'))
        competition_ages = list(Age.objects.distinct().filter(tour__in=tours))
        data['fetchedData']['ages'] = []
        for age in ages:
            obj = {'name':age.name,'id': age.id, 'kids': age.kids, 'min_age': age.min_age, 'max_age':  age.max_age}
            data['fetchedData']['ages'].append(obj)


        # Эстафеты
        distances = list(DistanceRelay.objects.all())
        data['fetchedData']['distancesRelay'] = []
        for distance in distances:
            obj = {'name':distance.name,'id': distance.id}
            data['fetchedData']['distancesRelay'].append(obj)

        styles = list(Style.objects.all())
        data['fetchedData']['stylesRelay'] = []
        for style in styles:
            obj = {'name':style.name,'id': style.id}
            data['fetchedData']['stylesRelay'].append(obj)

        ages = list(Age.objects.all().order_by('min_age'))
        data['fetchedData']['agesRelay'] = []
        for age in ages:
            obj = {'name':age.name,'id': age.id, 'kids': age.kids, 'min_age': age.min_age, 'max_age':  age.max_age}
            data['fetchedData']['agesRelay'].append(obj)

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

        for tour in toursRelay:
            num_of_teams = len(TeamRelay.objects.filter(tour=tour))
            data['tours'].append({'id': tour.id,
                                  'age': tour.age.id,
                                  'name': tour.__str__(),
                                  'distance': tour.distance.id,
                                  'style': tour.style.id,
                                  'gender': tour.gender,
                                  'min_age': tour.age.min_age,
                                  'max_age': tour.age.max_age,
                                  'num_of_teams': num_of_teams
            })

        return HttpResponse(json.dumps({'ages': data['fetchedData']['ages'],
                                        'styles': data['fetchedData']['styles'],
                                        'distances': data['fetchedData']['distances'],
                                        'tours': data['tours'],
                                        'agesRelay': data['fetchedData']['agesRelay'],
                                        'stylesRelay': data['fetchedData']['stylesRelay'],
                                        'distancesRelay': data['fetchedData']['distancesRelay'],
                                        'toursRelay': data['toursRelay'],
                                        'id': data['data']['id'],
                                        'name': data['data']['name'],
                                        'type': data['data']['type'],
                                        'date_start': data['data']['date_start'],
                                        'date_finish': data['data']['date_finish'],
                                        }), content_type="application/json")

    age_list = []
    ages = Age.objects.all().order_by('min_age')
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

    age_list_relay = []
    ages = Age.objects.all().order_by('min_age')
    for a in ages:
        age = {'id': a.id, 'name': a.name, 'kids': a.kids}
        age_list_relay.append(age)
    distance_list_relay = []
    distances = DistanceRelay.objects.all()
    for d in distances:
        distance = {'id': d.id, 'name': d.name}
        distance_list_relay.append(distance)
    style_list_relay = []
    styles = Style.objects.all()
    for s in styles:
        style = {'id': s.id, 'name': s.name}
        style_list_relay.append(style)

    return HttpResponse(json.dumps({'ages':age_list,
                                    'distances':distance_list,
                                    'styles':style_list,
                                    'agesRelay': age_list_relay,
                                    'distancesRelay': distance_list_relay,
                                    'stylesRelay': style_list_relay,
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
