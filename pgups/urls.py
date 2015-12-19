from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.reg_request, name='regrequest'),
    url(r'^tours/$', views.tours),
    url(r'^tour/(?P<tour_id>\d+)/$', views.tour_starts),
    url(r'^get_tours/(?P<age>\d+)/$', views.get_tours),
    #(r'^user/(?P<username>\w{0,50})/$', views.profile_page,),

    #url(r'^person_form$', views.person_form) # ajax
]