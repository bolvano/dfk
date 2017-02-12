# -*- coding: utf-8 -*-

import json
from django.contrib import messages
from django.contrib.messages import get_messages

from pgups.models import Userrequest, Competition, Team, TeamRelay, Competitor, Tour, TourRelay, Age, Distance, \
    DistanceRelay, Style, Start, CdsgRelay
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.shortcuts import render, get_object_or_404



def relay_teams(request, relay_id):
    relay = get_object_or_404(TourRelay, pk=relay_id)
    if request.method == "POST":

        #import ipdb; ipdb.set_trace()
        body_unicode = request.body.decode('utf-8')
        relay_teams_new = json.loads(body_unicode)
        relay_teams_old = TeamRelay.objects.filter(tour=relay)

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

    data = {'relay': relay}
    return render(request, 'pgups/relay_teams.html', data)


def relay_starts(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)
    cdsg_list = CdsgRelay.objects.filter(competition=competition)
    return render(request, 'pgups/relay_starts.html', {'cdsg_list': cdsg_list,
                                                             'competition_id':competition_id,
                                                             'competition': competition,
                                                            },)


def competition_relays_sort(request, competition_id):
    return render(request, 'pgups/competition_relays_sort.html', { 'competition_id': competition_id, }, )
