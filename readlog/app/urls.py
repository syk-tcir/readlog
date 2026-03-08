from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'), 
    path('test/', views.api_test, name='api_test'),
]