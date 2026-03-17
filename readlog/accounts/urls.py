from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('mypage/', views.mypage, name='mypage'),
    path('account/edit/', views.account_edit, name='account_edit'),
]