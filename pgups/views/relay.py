# -*- coding: utf-8 -*-

import json
from pgups.models import Userrequest, Competition, Team, TeamRelay, Competitor, Tour, TourRelay, Age, Distance, \
    DistanceRelay, Style, Start, Cdsg
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
        # save new order
        pass
    else:
        pass
    data = {'relay': relay}
    return render(request, 'pgups/relay_teams.html', data)
