from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.reg_request, name='regrequest'),
    url(r'^r$', views.reg_request2, name='regrequest2'),
    #url(r'^person_form$', views.person_form) # ajax
]