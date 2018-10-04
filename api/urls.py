from django.urls import path
from django.conf.urls import url
from django.urls import include
from api import views

urlpatterns = [
    path('about', views.about, name='about'),
    path('seq', views.seq, name='seq'),
    path('genomes', views.genomes, name='genomes'),
    path('genome', views.genome, name='genome'),
]
