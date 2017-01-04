# -*- coding: utf-8 -*-

import json
from pgups.models import Userrequest, Competition, Team, TeamRelay, Competitor, Tour, TourRelay, Age, Distance, \
    DistanceRelay, Style, Start, CdsgRelay
from django.http import HttpResponse

from django.shortcuts import render, get_object_or_404


def relay_teams(request, relay_id):

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


    relay = get_object_or_404(TourRelay, pk=relay_id)
    if request.method == "POST":
        # save new order
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

