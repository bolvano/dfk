# -*- coding: utf-8 -*-

import json
from django.contrib import messages
from django.contrib.messages import get_messages

from pgups.models import Userrequest, Competition, Team, TeamRelay, Competitor, Tour, TourRelay, Age, Distance, \
    DistanceRelay, Style, Start, CdsgRelay, StartRelay
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.shortcuts import render, get_object_or_404

def attribute_lanes_relay(relay_team_set, num_of_lanes):
    num_of_lanes = int(num_of_lanes)
    return_set = {}
    if num_of_lanes == 5:
        lanes = [3,2,4,1,5]
    elif num_of_lanes == 6:
        lanes = [3,4,2,5,1,6]
    for relay_team in reversed(relay_team_set):
        return_set[lanes.pop(0)] = relay_team
    return return_set


def relay_teams(request, relay_id):
    relay = get_object_or_404(TourRelay, pk=relay_id)
    if request.method == "POST":

        #import ipdb; ipdb.set_trace()
        body_unicode = request.body.decode('utf-8')
        relay_teams_new = json.loads(body_unicode)
        relay_teams_old = TeamRelay.objects.filter(tour=relay)

        # delete missing
        for rt in relay_teams_old:
            if str(rt.id) not in [str(r['id']) for r in relay_teams_new if 'id' in r]:
                rt.delete()

        # add new
        for rt in relay_teams_new:
            if 'id' not in rt:
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
                                                       'competition': competition })


def competition_relays_sort(request, competition_id):

    if request.POST:

        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        competition = Competition.objects.get(pk=data['competition_id'])
        num_of_lanes = data['max_length']
        starts_list = data['relays']
        starts_list = starts_list[1:]

        cdsg = CdsgRelay(competition=competition, number=1)
        cdsg.name = 'Все заплывы'
        cdsg.save()

        i_starts = 1

        total_competitors = {}

        valid_start_ids = []
        for s in starts_list:

            competitors = s['teams']
            if len(competitors) == 0:
                continue

            if 'id' in s:
                start = StartRelay.objects.get(pk=s['id'])
                start.num = i_starts
                if 'name' in s:
                    start.name = s['name']
                else:
                    start.name = str(start.num)
                #start.name = distance.name + ' ' + style.name + ' ' + age.name + ' ' + gender
                start.cdsg = cdsg
                start.save()
            else:
                start = StartRelay()
                start.num = i_starts
                if 'name' in s:
                    start.name = s['name']
                else:
                    start.name = str(start.num)
                start.cdsg = cdsg
                start.save()

            valid_start_ids.append(start.id)

            competitor_set = []
            for c in competitors:
                cc = TeamRelay.objects.get(pk=c['id'])
                competitor_set.append(cc)
                if cc.tour.id in total_competitors:
                    total_competitors[cc.tour.id] += 1
                else:
                    total_competitors[cc.tour.id] = 1

            competitor_set = attribute_lanes_relay(competitor_set, num_of_lanes)

            for lane, competitor in competitor_set.items():
                competitor.lane = lane
                competitor.start = start
                competitor.save()

            i_starts += 1

        valid_cdsg_ids = [cdsg.id,]
        passed_starts = []
        finished_tours_ids = []
        passed_competitors = {}

        cdsgs = CdsgRelay.objects.filter(competition=competition)
        all_starts = StartRelay.objects.filter(cdsg__in=cdsgs)
        for start in all_starts:
            if start.id not in valid_start_ids:
                start.delete()

        for c in cdsgs:
            if c.id not in valid_cdsg_ids:
                c.delete()

        i_cdsg = 1

        for s in StartRelay.objects.filter(cdsg__in=cdsgs).order_by('num'):
            for c in TeamRelay.objects.filter(start=s):
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
                cdsg_new = CdsgRelay(competition=competition, number=i_cdsg)
                #cdsg_new.name = 'Группа заплывов №' + str(i_cdsg)
                cdsg_new.name = str(i_cdsg)
                cdsg_new.save()
                for ps in passed_starts:
                    ps.cdsg = cdsg_new
                    ps.save()
                    c = TeamRelay.objects.filter(start=ps).first()
                    cdsg_new.name = c.tour.distance.name +' '+ c.tour.style.name +' '+ c.tour.gender
                    cdsg_new.save()

                finished_tours_ids = []
                passed_starts = []
                i_cdsg += 1

        cdsg.delete()

        return HttpResponseRedirect('../../competition/relay_starts/'+competition_id+'/')

    return render(request, 'pgups/competition_relays_sort.html', { 'competition_id': competition_id, }, )
