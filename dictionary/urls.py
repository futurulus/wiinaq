from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^entry/(?P<chunk_id>[0-9]+)/$', views.entry, name='entry'),
    url(r'^search/$', views.search, name='search'),
]
