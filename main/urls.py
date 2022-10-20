from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('new_cattle', views.new_cattle, name='new_cattle')
]
