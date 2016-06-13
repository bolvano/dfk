# -*- coding: utf-8 -*- 
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^regrequest/(?P<userrequest_id>\d+)?/?$', views.reg_request, name='regrequest'),
    url(r'^competition/(?P<competition_id>\d+)/$', views.competition, name='competition'),
    url(r'^userrequest/(?P<userrequest_id>\d+)/$', views.userrequest, name='userrequest'),

    #url(r'^userrequest_edit/(?P<userrequest_id>\d+)/$', views.userrequest_edit, name='userrequest_edit'),

    url(r'^person/(?P<person_id>\d+)/$', views.person, name='person'),
    url(r'^results/starts/(?P<competition_id>\d+)/$', views.results_starts),
    url(r'^results/tours/(?P<competition_id>\d+)/$', views.results_tours),
    url(r'^results/teams/(?P<competition_id>\d+)/$', views.results_teams),
    url(r'^competition/starts/(?P<competition_id>\d+)/$', views.competition_starts, name='competition_starts'),
    url(r'^competition/start_result/(?P<start_id>\d+)/$', views.start_result, name='start_result'),
    url(r'^competition/start_result_view/(?P<start_id>\d+)/$', views.start_result_view),
    url(r'^tour/(?P<id>\d+)/$', views.tour),
    url(r'^competition/team/(?P<competition_id>\d+)/(?P<team_id>\d+)/$', views.competition_team),

    # ajax
    url(r'^get_competitions/(?P<userrequest_id>\d+)?/?$', views.get_competitions),
    url(r'^get_teams/$', views.get_teams),
    url(r'^get_ages_distances_styles/(?P<competition_id>\d+)?/?$', views.get_ages_distances_styles),
    url(r'^get_competition_starts/(?P<id>\d+)/$', views.get_competition_starts),

    # starts and tours
    url(r'^generate_tours/(?P<competition_id>\d+)/(?P<kids>(0|1))/$', views.generate_tours),
    url(r'^generate_starts/$', views.generate_starts),

    # competition create
    url(r'^competition_create/(?P<competition_id>\d+)?/?$', views.create_competition, name="competitioncreate"),
    url(r'^competition_edit/(?P<competition_id>\d+)?/?$', views.create_competition, name="competitionedit"),

    # sortable starts
    url(r'^competition_starts_sort/(?P<competition_id>\d+)/$', views.competition_starts_sort,
        name="competition_starts_sort"),

    url(r'^login/$', views.login_user, name="login"),
    url(r'^logout/$', views.logout_user, name="logout"),

    url(r'^starts_print/(?P<competition_id>\d+)/$', views.starts_print, name="starts_print"),
    url(r'^cdsg_print/(?P<cdsg_id>\d+)/$', views.cdsg_print, name="cdsg_print"),
    url(r'^final_print/(?P<competition_id>\d+)/$', views.final_print, name="final_print"),


]
