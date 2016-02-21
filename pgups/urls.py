# -*- coding: utf-8 -*- 
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^regrequest$', views.reg_request, name='regrequest'),
    url(r'^competition/(?P<competition_id>\d+)/$', views.competition, name='competition'),
    url(r'^userrequest/(?P<userrequest_id>\d+)/$', views.userrequest, name='userrequest'),
    url(r'^person/(?P<person_id>\d+)/$', views.person, name='person'),
    url(r'^results/starts/(?P<competition_id>\d+)/$', views.results_starts),
    url(r'^results/tours/(?P<competition_id>\d+)/$', views.results_tours),
    #url(r'^teams/$', views.teams),
    #url(r'^distances/$', views.distances),
    url(r'^tours/$', views.tours, name='tours'),
    url(r'^tours2/$', views.tours2),
    url(r'^tour/(?P<id>\d+)/$', views.tour),
    url(r'^starts/$', views.starts),
    url(r'^start/(?P<id>\d+)/$', views.start),
    url(r'^distance/(?P<competition_id>\d+)/(?P<distance_id>\d+)/(?P<style_id>\d+)/(?P<gender_id>\w+)/$', views.distance),
    url(r'^distance_starts/(?P<competition_id>\d+)/(?P<distance_id>\d+)/(?P<style_id>\d+)/(?P<gender_id>\w+)/$', views.distance_starts),
    url(r'^get_tours/(?P<age>\d+)/(?P<gender>\w+)/$', views.get_tours),
    #url(r'^generate_tours/(?P<competition_id>\d+)/$', views.generate_tours),
    #url(r'^generate_starts/(?P<competition_id>\d+)/$', views.generate_starts),
    url(r'^all_starts/(?P<competition_id>\d+)/$', views.all_starts, name='all_starts'),
    url(r'^start_result/(?P<start_id>\d+)/$', views.start_result),
    url(r'^start_result_view/(?P<start_id>\d+)/$', views.start_result_view),
    
    
    #(r'^user/(?P<username>\w{0,50})/$', views.profile_page,),

    #url(r'^person_form$', views.person_form) # ajax
]