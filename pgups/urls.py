# -*- coding: utf-8 -*- 
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.reg_request, name='regrequest'),
    url(r'^teams/$', views.teams),
    url(r'^distances/$', views.distances),
    url(r'^tours/$', views.tours),
    url(r'^tours2/$', views.tours2),
    url(r'^tour/(?P<id>\d+)/$', views.tour),
    url(r'^starts/$', views.starts),
    url(r'^start/(?P<id>\d+)/$', views.start),
    url(r'^distance/(?P<competition_id>\d+)/(?P<distance_id>\d+)/(?P<style_id>\d+)/(?P<gender_id>\w+)/$', views.distance),
    url(r'^distance_starts/(?P<competition_id>\d+)/(?P<distance_id>\d+)/(?P<style_id>\d+)/(?P<gender_id>\w+)/$', views.distance_starts),
    url(r'^get_tours/(?P<age>\d+)/(?P<gender>\w+)/$', views.get_tours),
    #url(r'^generate_tours/(?P<competition_id>\d+)/$', views.generate_tours),
    #url(r'^generate_starts/(?P<competition_id>\d+)/$', views.generate_starts),
    url(r'^all_starts/(?P<competition_id>\d+)/$', views.all_starts),
    url(r'^start_result/(?P<start_id>\d+)/$', views.start_result),
    url(r'^start_result_view/(?P<start_id>\d+)/$', views.start_result_view),
    
    
    #(r'^user/(?P<username>\w{0,50})/$', views.profile_page,),

    #url(r'^person_form$', views.person_form) # ajax
]