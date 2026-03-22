from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('mypage/', views.mypage, name='mypage'),
    path('account/edit/', views.account_edit, name='account_edit'),
    path('password_change/done/', views.password_change_done_view, name='password_change_done'),
]