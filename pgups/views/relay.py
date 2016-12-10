# -*- coding: utf-8 -*-

import json
from pgups.models import Userrequest, Competition, Team, TeamRelay, Competitor, Tour, TourRelay, Age, Distance, \
    DistanceRelay, Style, Start, Cdsg
from django.http import HttpResponse

from django.shortcuts import render, get_object_or_404


def competition_relays(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    if request.method == "POST":
        # save new order
        pass
    else:
        pass
    data = {'competition': competition}
    return render(request, 'pgups/competition_relays.html', data)
