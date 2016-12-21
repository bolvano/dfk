# -*- coding: utf-8 -*-

from django.shortcuts import render
from pgups.models import Competition, Competitor, Tour, Age, Start, Cdsg, CdsgRelay, TeamRelay, StartRelay, TourRelay

from collections import defaultdict


def relay_cdsg_print(request, cdsg_id):
    cdsg = CdsgRelay.objects.get(pk=cdsg_id)
    starts = StartRelay.objects.filter(cdsg=cdsg)
    relay_teams = TeamRelay.objects.filter(start__in=starts)

    prev_cdsgs = CdsgRelay.objects.filter(number__lt=cdsg.number)
    prev_starts = StartRelay.objects.filter(cdsg__in=prev_cdsgs)
    prev_relay_teams = TeamRelay.objects.filter(start__in=prev_starts)

    tour_dict = defaultdict(list)
    tours = []
    for c in relay_teams:
        if c.tour not in tours:
            tours.append(c.tour)

    for tour in tours:
        #places
        main_competitors = TeamRelay.objects.filter(tour=tour,
                                                disqualification=0,
                                                time__gt=0).order_by('time')
        main_competitors = list(main_competitors)
        for i in range(1, 4):
            if main_competitors:
                c = main_competitors.pop(0)
                c.result = i
                c.save()

        total = TeamRelay.objects.filter(tour=tour).count()
        passed = relay_teams.filter(tour=tour).count() + prev_relay_teams.filter(tour=tour).count()
        if total == passed:
            tour_competitors = TeamRelay.objects.filter(tour=tour)
            for competitor in tour_competitors:
                tour_dict[competitor.tour.id].append(competitor)

    tour_dict = dict(tour_dict)

    tour_dict = {k: sorted((c for c in v if c.disqualification == 0 and c.time > 0),
                           key=lambda k:k.time)+list(filter(lambda c: c.disqualification > 0 or c.time == 0, v))
                 for k, v in tour_dict.items()}
    tour_list = [(TourRelay.objects.get(pk=k), v) for k, v in tour_dict.items()]


    # tour_list.sort(key=lambda tup: tup[0].style)

    return render(request, 'pgups/relay_cdsg_print.html', {'cdsg': cdsg, 'tour_dict': tour_dict, 'tour_list':
        tour_list}, )


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
        #places
        main_competitors = Competitor.objects.filter(tour=tour,
                                                approved=True,
                                                main_distance=True,
                                                disqualification=0,
                                                time__gt=0).order_by('time')
        main_competitors = list(main_competitors)
        for i in range(1, 4):
            if main_competitors:
                c = main_competitors.pop(0)
                c.result = i
                c.save()

        total = Competitor.objects.filter(tour=tour, approved=True).count()
        passed = competitors.filter(tour=tour).count() + prev_competitors.filter(tour=tour).count()
        if total == passed:
            tour_competitors = Competitor.objects.filter(tour=tour, approved=True)
            for competitor in tour_competitors:
                tour_dict[competitor.tour.id].append(competitor)

    tour_dict = dict(tour_dict)

    tour_dict = {k: sorted((c for c in v if c.disqualification == 0 and c.time > 0),
                           key=lambda k:k.time)+list(filter(lambda c: c.disqualification > 0 or c.time == 0, v))
                 for k, v in tour_dict.items()}
    tour_list = [(Tour.objects.get(pk=k), v) for k, v in tour_dict.items()]
    # tour_list.sort(key=lambda tup: tup[0].style)
    return render(request, 'pgups/cdsg_print.html', { 'cdsg': cdsg, 'tour_dict':tour_dict, 'tour_list':tour_list}, )


def starts_print(request, competition_id):
    competition = Competition.objects.get(pk=competition_id)
    cdsg_list = Cdsg.objects.filter(competition=competition)
    return render(request, 'pgups/starts_print.html', {'cdsg_list': cdsg_list,
                                                             'competition_id':competition_id,
                                                             'competition': competition,
                                                            },)


def final_print(request, competition_id, as_csv=0):

    # индивидуальные заплывы

    cdsg_dict = defaultdict(list)

    styles = {'на спине': 1, 'вольный стиль': 2, 'брасс': 3, 'баттерфляй': 4, 'комплекс': 5}
    ages = Age.objects.all().order_by('min_age')
    ages = {key.name: index for index, key in enumerate(ages)}
    genders = {'Ж': 1, 'М': 2}

    competition = Competition.objects.get(pk=competition_id)
    cdsgs = Cdsg.objects.filter(competition=competition)
    starts = Start.objects.filter(cdsg__in=cdsgs)

    competitors = Competitor.objects.filter(start__in=starts)
    for competitor in competitors:
        cdsg_dict[competitor.start.cdsg.id].append(competitor)

    cdsg_dict = dict(cdsg_dict)

    # cdsg_dict = { cdsg_id1 : [competitor1, competitor2 , ...],  cdsg_id2 : [competitor3, competitor4 , ...], ... }

    tour_dict = defaultdict(list)

    for k,v in cdsg_dict.items():
        for competitor in v:
            tour_dict[competitor.tour.id].append(competitor)


    tour_dict = dict(tour_dict)

    # tour_dict = {tour_id1 : [competitor1, competitor2 , ...],  tour_id2 : [competitor3, competitor4 , ...], ... }

    tour_list = [(Tour.objects.get(pk=k), v) for k, v in tour_dict.items() if Tour.objects.get(pk=k).out == False]
    out_list = [(Tour.objects.get(pk=k), v) for k, v in tour_dict.items() if Tour.objects.get(pk=k).out == True]

    # tour_list = [(tour1, [competitor1, competitor2, ...]), (tour2, [competitor3, competitor4, ...]), ...}
    # out_list = [(tour3, [competitor, competitor2, ...]), (tour4, [competitor3, competitor4, ...]), ...}

    grouped_tour_dict = defaultdict(list)
    for t in tour_list:
        grouped_tour_dict[t[0].style.name + t[0].distance.name + t[0].gender].append((t[0], t[1]))

    grouped_tour_dict = dict(grouped_tour_dict)

    # grouped_tour_list = {'50 brass M': [(tour1, [comp1, comp2]), (tour2, [comp3, comp4])], '50 brass F': [(t,[c,c]),
    # ()]}

    grouped_tour_dict = {k: [(i[0], sorted((a for a in i[1] if a.disqualification == 0), key=lambda k: k.time)
                              + list(filter(lambda k: k.disqualification > 0, i[1]))) for i in v]
                         for k,v in grouped_tour_dict.items()}

    grouped_tour_list = [(k, v) for k, v in grouped_tour_dict.items()]

    # grouped_tour_list = [('50 brass M', [(tour1, [comp1, comp2]), (tour2, [comp3, comp4])]), ('50 brass F', [(t,[c,
    # c]), ()]}

    grouped_tour_list.sort(key=lambda t: genders[t[1][0][0].gender])
    grouped_tour_list.sort(key=lambda tup: ages[tup[1][0][0].age.name])
    grouped_tour_list.sort(key=lambda tup: styles[tup[1][0][0].style.name])

    # внеконкурсники:

    grouped_out_dict = defaultdict(list)
    for t in out_list:
        grouped_out_dict[t[0].style.name + t[0].distance.name + t[0].gender].append((t[0], t[1]))

    grouped_out_dict = dict(grouped_out_dict)

    # grouped_out_list = {'50 brass M': [(tour1, [comp1, comp2]), (tour2, [comp3, comp4])], '50 brass F': [(t,[c,c]),
    # ()]}

    grouped_out_dict = {k: [(i[0], sorted((a for a in i[1] if a.disqualification == 0 and a.time > 0), key=lambda k:
    k.time)
                              + list(filter(lambda k: k.disqualification > 0 or k.time == 0, i[1]))) for i in v]
                         for k,v in grouped_out_dict.items()}

    grouped_out_list = [(k, v) for k, v in grouped_out_dict.items()]

    # grouped_out_list = [('50 brass M', [(tour1, [comp1, comp2]), (tour2, [comp3, comp4])]), ('50 brass F', [(t,[c,
    # c]), ()]}

    grouped_out_list.sort(key=lambda t: genders[t[1][0][0].gender])
    grouped_out_list.sort(key=lambda tup: ages[tup[1][0][0].age.name])
    grouped_out_list.sort(key=lambda tup: styles[tup[1][0][0].style.name])

    res = (grouped_tour_list, grouped_out_list)

    #
    # эстафеты
    #

    relay_cdsg_dict = defaultdict(list)

    styles = {'на спине': 1, 'вольный стиль': 2, 'брасс': 3, 'баттерфляй': 4, 'комплекс': 5 }
    ages = Age.objects.all().order_by('min_age')
    ages = {key.name: index for index, key in enumerate(ages)}
    genders = {'Ж': 1, 'М': 2, 'С': 3}

    cdsgs = CdsgRelay.objects.filter(competition=competition)
    starts = StartRelay.objects.filter(cdsg__in=cdsgs)

    competitors = TeamRelay.objects.filter(start__in=starts)
    for competitor in competitors:
        relay_cdsg_dict[competitor.start.cdsg.id].append(competitor)

    relay_cdsg_dict = dict(relay_cdsg_dict)

    relay_tour_dict = defaultdict(list)

    for k,v in relay_cdsg_dict.items():
        for competitor in v:
            relay_tour_dict[competitor.tour.id].append(competitor)

    relay_tour_dict = dict(relay_tour_dict)

    relay_tour_list = [(TourRelay.objects.get(pk=k), v) for k, v in relay_tour_dict.items() if TourRelay.objects.get(pk=k).out ==
                       False]
    relay_out_list = [(TourRelay.objects.get(pk=k), v) for k, v in relay_tour_dict.items() if TourRelay.objects.get(pk=k).out == True]

    relay_grouped_tour_dict = defaultdict(list)
    for t in relay_tour_list:
        relay_grouped_tour_dict[t[0].style.name + t[0].distance.name + t[0].gender].append((t[0], t[1]))

    relay_grouped_tour_dict = dict(relay_grouped_tour_dict)

    relay_grouped_tour_dict = {k: [(i[0], sorted((a for a in i[1] if a.disqualification == 0), key=lambda k: k.time)
                              + list(filter(lambda k: k.disqualification > 0, i[1]))) for i in v]
                         for k,v in relay_grouped_tour_dict.items()}

    relay_grouped_tour_list = [(k, v) for k, v in relay_grouped_tour_dict.items()]
    relay_grouped_tour_list.sort(key=lambda t: genders[t[1][0][0].gender])
    relay_grouped_tour_list.sort(key=lambda tup: ages[tup[1][0][0].age.name])
    relay_grouped_tour_list.sort(key=lambda tup: styles[tup[1][0][0].style.name])


    # внеконкурсники:

    relay_grouped_out_dict = defaultdict(list)
    for t in relay_out_list:
        relay_grouped_out_dict[t[0].style.name + t[0].distance.name + t[0].gender].append((t[0], t[1]))

        relay_grouped_out_dict = dict(relay_grouped_out_dict)

    relay_grouped_out_dict = {k: [(i[0], sorted((a for a in i[1] if a.disqualification == 0 and a.time > 0),
                                               key=lambda k:
    k.time)
                              + list(filter(lambda k: k.disqualification > 0 or k.time == 0, i[1]))) for i in v]
                         for k,v in relay_grouped_out_dict.items()}

    relay_grouped_out_list = [(k, v) for k, v in relay_grouped_out_dict.items()]

    relay_grouped_out_list.sort(key=lambda t: genders[t[1][0][0].gender])
    relay_grouped_out_list.sort(key=lambda tup: ages[tup[1][0][0].age.name])
    relay_grouped_out_list.sort(key=lambda tup: styles[tup[1][0][0].style.name])

    res_relay = (relay_grouped_tour_list, relay_grouped_out_list)

    return render(request, 'pgups/final_print.html', {'competition': competition,
                                                      'res': res,
                                                      'res_relay': res_relay}, )