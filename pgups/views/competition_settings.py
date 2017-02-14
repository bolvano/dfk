# -*- coding: utf-8 -*-
from pgups.models import Competition, Competitor, Tour, Age, Distance, Style, Start, Cdsg, DistanceRelay, TourRelay, \
    CdsgRelay, StartRelay, CompetitorRelay, TeamRelay
from django.http import HttpResponseRedirect
from django.shortcuts import render
import datetime
import json

def attribute_lanes(competitor_set, num_of_lanes):
    num_of_lanes = int(num_of_lanes)
    return_set = {}
    if num_of_lanes == 5:
        lanes = [3,2,4,1,5]
    elif num_of_lanes == 6:
        lanes = [3,4,2,5,1,6]
    for competitor in reversed(competitor_set):
        return_set[lanes.pop(0)] = competitor

    return return_set


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


def generate_relay_starts(request):
    if request.method == "POST":

        #import ipdb; ipdb.set_trace()
        competition_id = request.POST.get("competition_id", "")
        num_of_lanes = int(request.POST.get("lanes", 5))
        age_diff = bool(request.POST.get("ages", False))

        minimal = 3

        all_starts = []

        competition = Competition.objects.get(pk=competition_id)

        # delete old starts
        cdsgs = CdsgRelay.objects.filter(competition=competition)
        for cdsg in cdsgs:
            starts = StartRelay.objects.filter(cdsg=cdsg)
            for start in starts:
                team_relays = TeamRelay.objects.filter(start=start)
                competitors = CompetitorRelay.objects.filter(teamRelay__in=team_relays)
                for competitor in competitors:
                    competitor.start = None
                    competitor.result = None
                    competitor.points = 0
                    #competitor.disqualification = 0
                    #competitor.time = 0
                    competitor.save()
                for t in team_relays:
                    t.start = None
                    t.save()
            cdsg.delete()

        distances = DistanceRelay.objects.all().order_by('meters') #[50, 100]
        styles = [Style.objects.get(name='на спине'),
                  Style.objects.get(name='вольный стиль'),
                  Style.objects.get(name='брасс'),
                  Style.objects.get(name='баттерфляй'),
                  Style.objects.get(name='комплекс') ]
        genders = ['Ж', 'М', 'С']
        ages = Age.objects.all().order_by('min_age')

        i_cdsg = 1
        i_starts = 1

        for distance in distances:
            for style in styles:
                for gender in genders:
                    for age in ages:
                        starts = []
                        tours = TourRelay.objects.filter(competition=competition,
                                                    distance=distance,
                                                    style=style,
                                                    gender=gender,
                                                    age=age)
                        if tours:
                            relay_teams = TeamRelay.objects.filter(tour__in=tours)
                            if relay_teams:
                                #import ipdb; ipdb.set_trace()
                                cdsg = CdsgRelay(competition=competition, number=i_cdsg)
                                cdsg.name = 'Эстафеты ' + distance.name + ' ' + style.name + ' ' + age.name + ' ' + \
                                            gender
                                cdsg.save()
                                i_cdsg += 1
                                (full_starts, remainders) = divmod(len(relay_teams), num_of_lanes)

                                #import ipdb; ipdb.set_trace()

                                if remainders > 0: # есть остаток
                                    if full_starts > 0 and remainders < minimal:
                                        #есть полные и остаток меньше трёх, перегруппировка первых двух
                                        starts.append(relay_teams[:minimal])
                                        # первый старт - три участника
                                        if full_starts == 1:
                                            # был один полный старт: будет два неполных
                                            starts.append(relay_teams[minimal:])
                                        else:
                                            # было более одного полного: второй будет неполным, остальные полными
                                            begin = minimal
                                            end = begin + num_of_lanes - (minimal - remainders)

                                            starts.append(relay_teams[begin:end])

                                            begin = end
                                            for i in range(0, full_starts - 1):
                                                end = begin + num_of_lanes
                                                starts.append(relay_teams[begin:end])
                                                begin = end

                                    elif full_starts > 0 and remainders >= minimal:
                                        # есть полные старты и остаток три или больше
                                        starts.append(relay_teams[:remainders])
                                        begin = remainders
                                        for i in range(0, full_starts):
                                            end = begin + num_of_lanes
                                            starts.append(relay_teams[begin:end])
                                            begin = end

                                    else:
                                        starts.append(relay_teams[:])

                                elif full_starts: # нет остатков, просто раскидываем
                                    begin = 0
                                    for i in range(0, full_starts):
                                        end = begin + num_of_lanes
                                        starts.append(relay_teams[begin:end])
                                        begin = end

                                #import ipdb; ipdb.set_trace()
                                num_starts = len(starts)
                                starts2 = []

                                for relay_team_set in starts:
                                    start = StartRelay()
                                    start.num = i_starts
                                    start.name = 'Эстафета ' + distance.name + ' ' \
                                                 + style.name + ' ' \
                                                 + age.name + ' ' \
                                                 + gender
                                    start.cdsg = cdsg
                                    start.save()

                                    #import ipdb; ipdb.set_trace()

                                    relay_team_set = attribute_lanes_relay(relay_team_set, num_of_lanes)
                                    for lane, relay_team in relay_team_set.items():
                                        relay_team.lane = lane
                                        relay_team.start = start
                                        relay_team.save()

                                    starts2.append(start)
                                    i_starts += 1

        return HttpResponseRedirect('../../competition/relay_starts/' + competition_id + '/')


def generate_starts(request):

    if request.method == "POST":

        # import ipdb; ipdb.set_trace()
        competition_id = request.POST.get("competition_id", "")
        num_of_lanes = int(request.POST.get("lanes", 5))
        age_diff = bool(request.POST.get("ages", False))

        minimal = 3

        all_starts = []

        competition = Competition.objects.get(pk=competition_id)

        # delete old starts
        cdsgs = Cdsg.objects.filter(competition=competition)
        for cdsg in cdsgs:
            starts = Start.objects.filter(cdsg=cdsg)
            for start in starts:
                competitors = Competitor.objects.filter(start=start)
                for competitor in competitors:
                    competitor.start = None
                    competitor.lane = None
                    competitor.result = None
                    competitor.points = 0
                    #competitor.disqualification = 0
                    #competitor.time = 0
                    competitor.save()
            cdsg.delete()

        distances = Distance.objects.all().order_by('meters') #[50, 100]
        styles = [Style.objects.get(name='на спине'),
                  Style.objects.get(name='вольный стиль'),
                  Style.objects.get(name='брасс'),
                  Style.objects.get(name='баттерфляй'),
                  Style.objects.get(name='комплекс') ]
        genders = ['Ж','М']
        ages = Age.objects.all().order_by('min_age')

        i_cdsg = 1
        i_starts = 1

        for distance in distances:
            for style in styles:
                if age_diff:
                    for gender in genders:
                        for age in ages:
                            starts = []
                            tours = Tour.objects.filter(competition=competition,
                                                        distance=distance,
                                                        style=style,
                                                        gender=gender,
                                                        age=age)
                            if tours:
                                #import ipdb; ipdb.set_trace()
                                competitors_no_prior = Competitor.objects\
                                    .filter(tour__in=tours)\
                                    .filter(approved=True)\
                                    .filter(prior_time=0)
                                competitors_prior = Competitor.objects\
                                    .filter(tour__in=tours)\
                                    .filter(approved=True)\
                                    .filter(prior_time__gt=0).order_by('-prior_time')

                                competitors = list(competitors_no_prior) + list(competitors_prior)

                                if competitors:
                                    #import ipdb; ipdb.set_trace()
                                    cdsg = Cdsg(competition=competition, number=i_cdsg)
                                    cdsg.name = distance.name + ' ' + style.name + ' ' + age.name + ' ' + gender
                                    cdsg.save()
                                    i_cdsg += 1
                                    (full_starts, remainders) = divmod(len(competitors), num_of_lanes)

                                    #import ipdb; ipdb.set_trace()

                                    if remainders > 0: # есть остаток
                                        if full_starts > 0 and remainders < minimal:
                                            #есть полные и остаток меньше трёх, перегруппировка первых двух
                                            starts.append(competitors[:minimal])
                                            # первый старт - три участника
                                            if full_starts == 1:
                                                # был один полный старт: будет два неполных
                                                starts.append(competitors[minimal:])
                                            else:
                                                # было более одного полного: второй будет неполным, остальные полными
                                                begin = minimal
                                                end = begin + num_of_lanes - (minimal - remainders)

                                                starts.append(competitors[begin:end])

                                                begin = end
                                                for i in range(0, full_starts - 1):
                                                    end = begin + num_of_lanes
                                                    starts.append(competitors[begin:end])
                                                    begin = end

                                        elif full_starts > 0 and remainders >= minimal:
                                            # есть полные старты и остаток три или больше
                                            starts.append(competitors[:remainders])
                                            begin = remainders
                                            for i in range(0, full_starts):
                                                end = begin + num_of_lanes
                                                starts.append(competitors[begin:end])
                                                begin = end

                                        else:
                                            starts.append(competitors[:])

                                    elif full_starts: # нет остатков, просто раскидываем
                                        begin = 0
                                        for i in range(0, full_starts):
                                            end = begin + num_of_lanes
                                            starts.append(competitors[begin:end])
                                            begin = end

                                    num_starts = len(starts)

                                    starts2 = []


                                    for competitor_set in starts:
                                        start = Start()
                                        start.num = i_starts
                                        start.name = distance.name + ' ' \
                                                     + style.name + ' ' \
                                                     + age.name + ' ' \
                                                     + gender
                                        start.cdsg = cdsg
                                        start.save()

                                        #import ipdb; ipdb.set_trace()

                                        competitor_set = attribute_lanes(competitor_set, num_of_lanes)
                                        for lane, competitor in competitor_set.items():
                                            competitor.lane = lane
                                            competitor.start = start
                                            competitor.save()

                                        starts2.append(start)
                                        i_starts += 1
                else:
                    for gender in genders:
                        starts = []
                        tours = Tour.objects.filter(competition=competition,
                                                    distance=distance,
                                                    style=style,
                                                    gender=gender)
                        if tours:
                            #import ipdb; ipdb.set_trace()
                            competitors_no_prior = Competitor.objects\
                                .filter(tour__in=tours)\
                                .filter(approved=True)\
                                .filter(prior_time=0)
                            competitors_prior = Competitor.objects\
                                .filter(tour__in=tours)\
                                .filter(approved=True)\
                                .filter(prior_time__gt=0).order_by('-prior_time')
                            competitors = list(competitors_no_prior) + list(competitors_prior)
                            if competitors:
                                #import ipdb; ipdb.set_trace()
                                cdsg = Cdsg(competition=competition, number=i_cdsg)
                                cdsg.name = distance.name + ' ' + style.name + ' ' + gender
                                cdsg.save()
                                i_cdsg += 1
                                (full_starts, remainders) = divmod(len(competitors), int(num_of_lanes))
                                #import ipdb; ipdb.set_trace()

                                if remainders > 0: # есть остаток
                                    if full_starts > 0 and remainders < minimal:
                                        #есть полные и остаток меньше трёх, перегруппировка первых двух
                                        starts.append(competitors[:minimal])
                                        # первый старт - три участника
                                        if full_starts == 1:
                                            # был один полный старт: будет два неполных
                                            starts.append(competitors[minimal:])
                                        else:
                                            # было более одного полного: второй будет неполным, остальные полными
                                            begin = minimal
                                            end = begin + num_of_lanes - (minimal - remainders)

                                            starts.append(competitors[begin:end])

                                            begin = end
                                            for i in range(0, full_starts - 1):
                                                end = begin + num_of_lanes
                                                starts.append(competitors[begin:end])
                                                begin = end

                                    elif full_starts > 0 and remainders >= minimal:
                                        # есть полные старты и остаток три или больше
                                        starts.append(competitors[:remainders])
                                        begin = remainders
                                        for i in range(0, full_starts):
                                            end = begin + num_of_lanes
                                            starts.append(competitors[begin:end])
                                            begin = end

                                    else:
                                        starts.append(competitors[:])

                                elif full_starts: # нет остатков, просто раскидываем
                                    begin = 0
                                    for i in range(0, full_starts):
                                        end = begin + num_of_lanes
                                        starts.append(competitors[begin:end])
                                        begin = end

                                num_starts = len(starts)
                                starts2 = []

                                for competitor_set in starts:
                                    start = Start()
                                    start.num = i_starts
                                    start.name = distance.name + ' ' + style.name + ' ' + gender
                                    start.cdsg = cdsg
                                    start.save()

                                    #import ipdb; ipdb.set_trace()

                                    competitor_set = attribute_lanes(competitor_set, num_of_lanes)
                                    for lane, competitor in competitor_set.items():
                                        competitor.lane = lane
                                        competitor.start = start
                                        competitor.save()

                                    starts2.append(start)
                                    i_starts += 1

        return HttpResponseRedirect('../../competition/starts/'+competition_id+'/')

# форма создания соревнований
def create_competition(request, competition_id=None):
    if request.method == "POST":

        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        if data['type'] == '1':
            typ = 'взрослые'
        elif data['type'] == '0':
            typ = 'детские'
        else:
            typ = 'смешанные'

        #import ipdb; ipdb.set_trace()

        if 'id' in data:
            date_start = datetime.datetime.strptime(data['date_start'], "%Y-%m-%dT%H:%M:%S.%fZ")
            date_end = datetime.datetime.strptime(data['date_finish'], "%Y-%m-%dT%H:%M:%S.%fZ")
            new_competition = False
            competition = Competition.objects.get(pk=data['id'])
            competition.name = data['name']
            competition.typ = typ
            competition.date_start = date_start
            competition.date_end = date_end
            competition.finished = False

        else:
            date_start = datetime.datetime.strptime(data['date_start'], "%Y-%m-%dT%H:%M:%S.%fZ")+\
                         datetime.timedelta(days=1)
            date_end = datetime.datetime.strptime(data['date_finish'], "%Y-%m-%dT%H:%M:%S.%fZ")+\
                       datetime.timedelta(days=1)
            new_competition = True
            competition = Competition(name=data['name'],
                                      typ=typ,
                                      date_start=date_start,
                                      date_end=date_end,
                                      finished=False)
        competition.save()

        if new_competition:
            if 'tours' in data:
                for tour in data['tours']:
                    style = Style.objects.get(pk=tour['style'])
                    age = Age.objects.get(pk=tour['age'])
                    distance = Distance.objects.get(pk=tour['distance'])

                    new_tour_m = Tour(competition=competition, finished=False)
                    new_tour_m.gender = 'М'
                    new_tour_m.style = style
                    new_tour_m.distance = distance
                    new_tour_m.age = age
                    new_tour_m.save()

                    new_tour_f = Tour(competition=competition, finished=False)
                    new_tour_f.gender = 'Ж'
                    new_tour_f.style = style
                    new_tour_f.distance = distance
                    new_tour_f.age = age
                    new_tour_f.save()

            if 'toursRelay' in data:
                for tour in data['toursRelay']:
                    style = Style.objects.get(pk=tour['style'])
                    age = Age.objects.get(pk=tour['age'])
                    distance = DistanceRelay.objects.get(pk=tour['distance'])
                    if tour['gender'] == 'Смешанные':
                        gender = 'С'
                    elif tour['gender'] == 'М':
                        gender = 'М'
                    else:
                        gender = 'Ж'

                    new_tour_m = TourRelay(competition=competition, finished=False)
                    new_tour_m.gender = gender
                    new_tour_m.style = style
                    new_tour_m.distance = distance
                    new_tour_m.age = age
                    new_tour_m.save()

        else:
            got_out_of_order_tours = False
            existing_tours = Tour.objects.filter(competition=competition)
            if 'tours' in data:
                form_tours = data['tours']

                #deleting non-present in form
                for tour in existing_tours:
                    if tour.id not in [t['id'] for t in form_tours if 'id' in t]:
                        tour.delete()

                #adding new ones
                for tour in form_tours:
                    if 'new' in tour:
                        style = Style.objects.get(pk=tour['style'])
                        age = Age.objects.get(pk=tour['age'])
                        distance = Distance.objects.get(pk=tour['distance'])

                        new_tour = Tour(competition=competition, finished=False)
                        new_tour.gender = tour['gender']
                        new_tour.style = style
                        new_tour.distance = distance
                        new_tour.age = age

                        if 'out' in tour:
                            new_tour.out = True
                            got_out_of_order_tours = True

                        new_tour.save()
            else:
                for tour in existing_tours:
                    tour.delete()
            if got_out_of_order_tours:
                competition.typ = 'смешанные'
                competition.save()

            # Эстафеты
            got_out_of_order_relay = False
            existing_relays = TourRelay.objects.filter(competition=competition)
            if 'toursRelay' in data:
                form_tours = data['toursRelay']

                #deleting non-present in form
                for tour in existing_relays:
                    if tour.id not in [t['id'] for t in form_tours if 'id' in t]:
                        tour.delete()

                #adding new ones
                for tour in form_tours:
                    if 'new' in tour:
                        style = Style.objects.get(pk=tour['style'])
                        age = Age.objects.get(pk=tour['age'])
                        distance = DistanceRelay.objects.get(pk=tour['distance'])

                        new_tour = TourRelay(competition=competition, finished=False)

                        if tour['gender'] == 'Смешанные':
                            gender = 'С'
                        elif tour['gender'] == 'М':
                            gender = 'М'
                        else:
                            gender = 'Ж'

                        new_tour.gender = gender
                        new_tour.style = style
                        new_tour.distance = distance
                        new_tour.age = age

                        if 'out' in tour:
                            new_tour.out = True
                            got_out_of_order_relay = True

                        new_tour.save()
            else:
                for tour in existing_relays:
                    tour.delete()
            if got_out_of_order_relay:
                competition.typ = 'смешанные'
                competition.save()

    else:
        data = {}

    return render(request, 'pgups/competition_create.html', data, )


def competition_starts_sort(request, competition_id):
    if request.POST:

        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        competition = Competition.objects.get(pk=data['competition_id'])
        num_of_lanes = data['max_length']
        starts_list = data['starts_list']
        starts_list = starts_list[1:]

        cdsg = Cdsg(competition=competition, number=1)
        cdsg.name = 'Все заплывы'
        cdsg.save()

        i_starts = 1

        total_competitors = {}

        valid_start_ids = []
        for s in starts_list:

            competitors = s['competitors']
            if len(competitors) == 0:
                continue

            if 'id' in s:
                start = Start.objects.get(pk=s['id'])
                start.num = i_starts
                #start.name = distance.name + ' ' + style.name + ' ' + age.name + ' ' + gender
                start.cdsg = cdsg
                start.save()
            else:
                start = Start()
                start.num = i_starts
                start.name = str(start.num)
                start.cdsg = cdsg
                start.save()

            valid_start_ids.append(start.id)

            #import ipdb; ipdb.set_trace()

            name_dict = {'distance':set(), 'style':set(), 'age':set(), 'gender':set()}
            competitor_set = []
            for c in competitors:
                cc = Competitor.objects.get(pk=c['id'])
                competitor_set.append(cc)
                if cc.tour.id in total_competitors:
                    total_competitors[cc.tour.id] += 1
                else:
                    total_competitors[cc.tour.id] = 1

            for c in competitor_set:
                name_dict['distance'].add(c.tour.distance.name)
                name_dict['style'].add(c.tour.style.name)
                name_dict['age'].add(c.age.name)
                name_dict['gender'].add(c.tour.gender)

            start.name = ', '.join(name_dict['distance']) + ' ' \
                         + ', '.join(name_dict['style']) + ' ' \
                         + ', '.join(name_dict['age']) + ' '\
                         + ', '.join(name_dict['gender'])
            start.save()

            competitors_good = list(filter(lambda c: c.prior_time > 0, competitor_set))
            competitors_bad = list(filter(lambda c: c.prior_time == 0, competitor_set))

            competitors_good.sort(key=lambda c: c.prior_time, reverse=True)

            competitor_set = competitors_bad + competitors_good

            competitor_set = attribute_lanes(competitor_set, num_of_lanes)
            for lane, competitor in competitor_set.items():
                competitor.lane = lane
                competitor.start = start
                competitor.save()

            i_starts += 1

        valid_cdsg_ids = [cdsg.id,]
        passed_starts = []
        finished_tours_ids = []
        passed_competitors = {}

        cdsgs = Cdsg.objects.filter(competition=competition)
        all_starts = Start.objects.filter(cdsg__in=cdsgs)
        for start in all_starts:
            if start.id not in valid_start_ids:
                start.delete()

        for c in cdsgs:
            if c.id not in valid_cdsg_ids:
                c.delete()

        i_cdsg = 1

        for s in Start.objects.filter(cdsg__in=cdsgs).order_by('num'):
            for c in Competitor.objects.filter(start=s):
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
                cdsg_new = Cdsg(competition=competition, number=i_cdsg)
                #cdsg_new.name = 'Группа заплывов №' + str(i_cdsg)
                cdsg_new.name = str(i_cdsg)
                cdsg_new.save()
                for ps in passed_starts:
                    ps.cdsg = cdsg_new
                    ps.save()
                    c = Competitor.objects.filter(start=ps).first()
                    cdsg_new.name = c.tour.distance.name +' '+ c.tour.style.name +' '+ c.tour.gender
                    cdsg_new.save()

                finished_tours_ids = []
                passed_starts = []
                i_cdsg += 1

        #import ipdb; ipdb.set_trace()
        cdsg.delete()

        return HttpResponseRedirect('../../competition/starts/'+competition_id+'/')

    return render(request, 'pgups/competition_starts_sort.html', { 'competition_id': competition_id, }, )
