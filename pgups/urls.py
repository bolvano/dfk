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
    url(r'^generate_starts/$', views.generate_starts),
    url(r'^competition/start_result/(?P<start_id>\d+)/$', views.start_result),
    url(r'^competition/start_result_view/(?P<start_id>\d+)/$', views.start_result_view),
    url(r'^tour/(?P<id>\d+)/$', views.tour),
    url(r'^competition/team/(?P<competition_id>\d+)/(?P<team_id>\d+)/$', views.competition_team),



    url(r'^get_tours/(?P<age>\d+)/(?P<gender>\w+)/(?P<competition_id>\d+)/$', views.get_tours),
    url(r'^generate_tours/(?P<competition_id>\d+)/$', views.generate_tours),
    #url(r'^generate_starts/(?P<competition_id>\d+)/$', views.generate_starts),
    #(r'^user/(?P<username>\w{0,50})/$', views.profile_page,),
    #url(r'^person_form$', views.person_form) # ajax
]