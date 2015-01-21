
__author__ = 'Alex'

from django.conf.urls import patterns
from django.conf.urls import url
from rango import views
urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^about/', views.about, name='about'))
