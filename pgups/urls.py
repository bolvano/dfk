# -*- coding: utf-8 -*-
from django.conf.urls import url
from pgups.views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^regrequest/(?P<userrequest_id>\d+)?/?$', reg_request, name='regrequest'),
    url(r'^competition/(?P<competition_id>\d+)/$', competition, name='competition'),
    url(r'^userrequest/(?P<userrequest_id>\d+)/$', userrequest, name='userrequest'),

    #url(r'^userrequest_edit/(?P<userrequest_id>\d+)/$', userrequest_edit, name='userrequest_edit'),

    url(r'^person/(?P<person_id>\d+)/$', person, name='person'),
    url(r'^results/starts/(?P<competition_id>\d+)/$', results_starts),
    url(r'^results/tours/(?P<competition_id>\d+)/$', results_tours),
    url(r'^results/teams/(?P<competition_id>\d+)/$', results_teams),
    url(r'^competition/starts/(?P<competition_id>\d+)/$', competition_starts, name='competition_starts'),
    url(r'^competition/relays/(?P<competition_id>\d+)/$', competition_relays, name='competition_relays'),
    url(r'^competition/start_result/(?P<start_id>\d+)/$', start_result, name='start_result'),
    url(r'^competition/start_result_view/(?P<start_id>\d+)/$', start_result_view),
    url(r'^tour/(?P<id>\d+)/$', tour),
    url(r'^competition/team/(?P<competition_id>\d+)/(?P<team_id>\d+)/$', competition_team),
    url(r'^relay_teams/(?P<relay_id>\d+)/$', relay_teams),

    url(r'^competition/relay_starts/(?P<competition_id>\d+)/$', relay_starts, name='relay_starts'),

    url(r'^competition/relay_start_result/(?P<start_id>\d+)/$', relay_start_result, name='relay_start_result'),
    url(r'^competition/relay_start_result_view/(?P<start_id>\d+)/$', relay_start_result_view),

    # ajax
    url(r'^get_competitions/(?P<userrequest_id>\d+)?/?$', get_competitions),
    url(r'^get_teams/$', get_teams),
    url(r'^get_ages_distances_styles/(?P<competition_id>\d+)?/?$', get_ages_distances_styles),
    url(r'^get_competition_starts/(?P<id>\d+)/$', get_competition_starts),
    url(r'^get_relay_teams/(?P<id>\d+)/$', get_relay_teams),

    # starts and tours
    url(r'^generate_starts/$', generate_starts),
    url(r'^generate_relay_starts/$', generate_relay_starts),

    # competition create
    url(r'^competition_create/(?P<competition_id>\d+)?/?$', create_competition, name="competitioncreate"),
    url(r'^competition_edit/(?P<competition_id>\d+)?/?$', create_competition, name="competitionedit"),

    # sortable starts
    url(r'^competition_starts_sort/(?P<competition_id>\d+)/$', competition_starts_sort,
        name="competition_starts_sort"),

    url(r'^login/$', login_user, name="login"),
    url(r'^logout/$', logout_user, name="logout"),

    url(r'^starts_print/(?P<competition_id>\d+)/$', starts_print, name="starts_print"),
    url(r'^cdsg_print/(?P<cdsg_id>\d+)/$', cdsg_print, name="cdsg_print"),
    url(r'^final_print/(?P<competition_id>\d+)/(?P<as_csv>(0|1))?/?$', final_print, name="final_print"),

    url(r'^relay_cdsg_print/(?P<cdsg_id>\d+)/$', relay_cdsg_print, name="relay_cdsg_print"),
]
