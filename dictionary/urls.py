from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^w/(?P<word>.+)/$', views.entry, name='entry'),
    url(r'^search/$', views.search, name='search'),
    url(r'^random/$', views.random_entry, name='random'),
    url(r'^build/$', views.build, name='build'),
    url(r'^credits/', views.credits, name='credits'),
]
