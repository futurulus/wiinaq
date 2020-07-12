from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('w/<str:word>/', views.entry, name='entry'),
    path('search/', views.search, name='search'),
    path('random/', views.random_entry, name='random'),
    path('build/', views.build, name='build'),
    path('credits/', views.credits, name='credits'),
]
