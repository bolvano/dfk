# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django import forms
from django.forms import modelformset_factory
from pgups.models import Competition, Competitor, Tour, Start, Cdsg, StartRelay, CdsgRelay, TeamRelay, TourRelay

from pgups.common import SplitTimeWidget
from django.contrib import messages
from django.http import HttpResponseRedirect

from collections import OrderedDict


def results_starts(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    cdsgs = Cdsg.objects.filter(competition=competition)
    starts = Start.objects.filter(cdsg__in=cdsgs).order_by('num')

    return render(request, 'pgups/results_starts.html', {'competition':competition, 'starts':starts},)


def results_tours(request, competition_id):

    disqualification_dict = {1:'Неявка',
                             2:'Фальстарт',
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
    result_dict = {}

    tours = Tour.objects.filter(competition=competition, out=False)
    for tour in tours:
        competitors = Competitor.objects.filter(tour=tour,
                                                approved=True,
                                                main_distance=True,
                                                disqualification=0,
                                                time__gt=0).order_by('time')
        for competitor in competitors:
            if competitor.userrequest.team:
                result_dict.setdefault(competitor.userrequest.team.name, {'competitors':[],
                                                                          'relay_competitors': [],
                                                                          'total':0})
                result_dict[competitor.userrequest.team.name]['competitors'].append(competitor)
                result_dict[competitor.userrequest.team.name]['total'] += int(competitor.points or 0)

    relay_tours = TourRelay.objects.filter(competition=competition, out=False)
    for tour in relay_tours:
        competitors = TeamRelay.objects.filter(tour=tour,
                                                disqualification=0,
                                                time__gt=0).order_by('time')
        for competitor in competitors:
            if competitor.team:

                result_dict.setdefault(competitor.team.name, {'competitors':[],
                                                              'relay_competitors': [],
                                                              'total':0})
                result_dict[competitor.team.name]['relay_competitors'].append(competitor)
                result_dict[competitor.team.name]['total'] += int(competitor.points or 0)

    for k,v in result_dict.items():
        v['competitors'].sort(key=lambda c: (c.tour.style.name, c.tour.distance.meters, c.tour.age.min_age,
                                             c.tour.gender, c.person.last_name))

    result_dict = OrderedDict(sorted(result_dict.items(), key=lambda x: x[1]['total'], reverse=True))

    return render(request, 'pgups/results_teams.html', {'competition': competition,
                                                        'result_dict': result_dict},)


def relay_start_result(request, start_id):
    start = StartRelay.objects.get(pk=start_id)
    relay_teams = TeamRelay.objects.filter(start=start)
    competition = start.cdsg.competition
    cdsgs = CdsgRelay.objects.filter(competition=competition)

    # TODO: get relay competitors

    try:
        next_start = StartRelay.objects.get(cdsg__in=cdsgs, num=start.num+1)
        next_start_id = next_start.id
    except StartRelay.DoesNotExist:
        next_start_id = ''

    try:
        prev_start = StartRelay.objects.get(cdsg__in=cdsgs, num=start.num-1)
        prev_start_id = prev_start.id
    except StartRelay.DoesNotExist:
        prev_start_id = ''

    #import ipdb; ipdb.set_trace()

    ResultFormSet = modelformset_factory(TeamRelay,
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
            return HttpResponseRedirect('../../../competition/relay_start_result_view/'+start_id+'/')

    else:
        result_formset = ResultFormSet(queryset=relay_teams.order_by('lane'))

    return render(request, 'pgups/relay_start_result.html', {'result_formset' : result_formset,
                                                       'start_num': start.num,
                                                       'cdsg_name': start.cdsg.__str__(),
                                                       'next_start_id':next_start_id,
                                                       'prev_start_id':prev_start_id,
                                                       'competition_id':competition.id} )


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


def relay_start_result_view(request, start_id):
    start = StartRelay.objects.get(pk=start_id)

    competition = start.cdsg.competition
    cdsgs = CdsgRelay.objects.filter(competition=competition)

    last_in_cdsg = False
    cdsg = start.cdsg
    if start.num == StartRelay.objects.filter(cdsg=cdsg).order_by('-num')[0].num:
        last_in_cdsg = True

    try:
        next_start = StartRelay.objects.get(cdsg__in=cdsgs, num=start.num+1)
        next_start_id = next_start.id
    except StartRelay.DoesNotExist:
        next_start_id = ''

    try:
        prev_start = StartRelay.objects.get(cdsg__in=cdsgs, num=start.num-1)
        prev_start_id = prev_start.id
    except StartRelay.DoesNotExist:
        prev_start_id = ''

    relay_teams = TeamRelay.objects.filter(start=start).order_by('lane')
    return render(request, 'pgups/relay_start_result_view.html', {'relay_teams' : relay_teams,
                                                            'start_num': start.num,
                                                            'last_in_cdsg':last_in_cdsg,
                                                            'cdsg_id':start.cdsg.id,
                                                            'cdsg_name': start.cdsg.__str__(),
                                                            'start_id': start.id,
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
