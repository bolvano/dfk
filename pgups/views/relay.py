# -*- coding: utf-8 -*-

import json
from pgups.models import Userrequest, Competition, Team, TeamRelay, Competitor, Tour, TourRelay, Age, Distance, \
    DistanceRelay, Style, Start, CdsgRelay
from django.http import HttpResponse

from django.shortcuts import render, get_object_or_404


def competition_relays(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    relay_list = TourRelay.objects.filter(competition=competition)
    if request.method == "POST":
        # save new order
        pass
    else:
        pass
    data = {'competition': competition, 'relay_list': relay_list}
    return render(request, 'pgups/competition_relays.html', data)


def relay_teams(request, relay_id):
    relay = get_object_or_404(TourRelay, pk=relay_id)

    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        '''{"competition_name": "\u0422\u0435\u0441\u0442\u043e\u0432\u044b\u0435 \u0441 \u044d\u0441\u0442\u0430\u0444\u0435\u0442\u043e\u0439",
        "competition_id": 5, "relay_id": 5,
         "relayTeams": [], "persons": [
         {"team_name": "\u0414\u0424\u041a \u041f\u0413\u0423\u041f\u0421", "gender": "\u041c", "age_id": 11, "id": 723, "name": "Qqqq Qqqqq (2000/\u041c)", "age": 16, "team_id": 1},
         {"team_name": "MEVIS", "gender": "\u0416", "age_id": 11, "id": 728, "name": "Dddddddddd Dddddddd (2000/\u0416)", "age": 16, "team_id": 2},
          {"team_name": "\u0414\u0424\u041a \u041f\u0413\u0423\u041f\u0421", "gender": "\u041c", "age_id": 11, "id": 724, "name": "Wwwwwww Wwwwwww (1999/\u041c)", "age": 17, "team_id": 1},
          {"team_name": "\u0414\u0424\u041a \u041f\u0413\u0423\u041f\u0421", "gender": "\u041c", "age_id": 11, "id": 725, "name": "Eeeeee Eeeeeee (2000/\u041c)", "age": 16, "team_id": 1},
        {"team_name": "MEVIS", "gender": "\u0416", "age_id": 11, "id": 726, "name": "Aaaaa Aaaaa (2000/\u0416)", "age": 16, "team_id": 2},
        {"team_name": "MEVIS", "gender": "\u041c", "age_id": 11, "id": 727, "name": "Sssssss Sssssss (2000/\u041c)", "age": 16, "team_id": 2}],
         "teams": [{"parent_id": 1, "name": "\u0414\u0424\u041a \u041f\u0413\u0423\u041f\u0421-I"},
         {"parent_id": 1, "name": "\u0414\u0424\u041a \u041f\u0413\u0423\u041f\u0421-II"},
         {"parent_id": 2, "name": "MEVIS-I"},
         {"parent_id": 2, "name": "MEVIS-II"}]}'''

        relay_teams_old = TeamRelay.objects.filter(tour=relay)
        relay_teams_new = data["relayTeams"]

        # delete missing
        for rt in relay_teams_old:
            if str(rt.id) not in [r['id'] for r in relay_teams_new if 'id' in r]:
                rt.delete()

        # add new
        for rt in relay_teams_new:
            team = Team.objects.get(pk=int(rt['parent_id']))
            new_rt = TeamRelay()
            new_rt.name = rt['name']
            new_rt.team = team
            new_rt.age = relay.age
            new_rt.tour = relay
            new_rt.time = 0
            new_rt.save()
        pass
    else:
        pass

    data = {'relay': relay}
    return render(request, 'pgups/relay_teams.html', data)


def relay_starts(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)
    cdsg_list = CdsgRelay.objects.filter(competition=competition)
    return render(request, 'pgups/relay_starts.html', {'cdsg_list': cdsg_list,
                                                             'competition_id':competition_id,
                                                             'competition': competition,
                                                            },)

