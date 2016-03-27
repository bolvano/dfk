# -*- coding: utf-8 -*- 
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^regrequest/$', views.reg_request, name='regrequest'),
    url(r'^competition/(?P<competition_id>\d+)/$', views.competition, name='competition'),
    url(r'^userrequest/(?P<userrequest_id>\d+)/$', views.userrequest, name='userrequest'),
    url(r'^person/(?P<person_id>\d+)/$', views.person, name='person'),
    url(r'^results/starts/(?P<competition_id>\d+)/$', views.results_starts),
    url(r'^results/tours/(?P<competition_id>\d+)/$', views.results_tours),
    url(r'^results/teams/(?P<competition_id>\d+)/$', views.results_teams),
    url(r'^competition/starts/(?P<competition_id>\d+)/$', views.competition_starts, name='competition_starts'),
    url(r'^competition/start_result/(?P<start_id>\d+)/$', views.start_result),
    url(r'^competition/start_result_view/(?P<start_id>\d+)/$', views.start_result_view),
    url(r'^tour/(?P<id>\d+)/$', views.tour),
    url(r'^competition/team/(?P<competition_id>\d+)/(?P<team_id>\d+)/$', views.competition_team),

    # ajax
    url(r'^get_competitions/$', views.get_competitions),
    url(r'^get_teams/$', views.get_teams),
    url(r'^get_ages_distances_styles/$', views.get_ages_distances_styles),

    # starts and tours
    url(r'^generate_tours/(?P<competition_id>\d+)/(?P<kids>(0|1))/$', views.generate_tours),
    url(r'^generate_starts/$', views.generate_starts),

    # competition create
    url(r'^competition_create/$', views.create_competition),
]