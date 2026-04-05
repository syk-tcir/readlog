from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('mypage/', views.mypage, name='mypage'),
    path('account/edit/', views.account_edit, name='account_edit'),
    path('password_change/done/', views.password_change_done_view, name='password_change_done'),
    path('password_reset/', views.custom_password_reset, name='password_reset'),
    path('password_reset/done/', views.custom_password_reset_done, name='custom_password_reset_done'),
    path('reset/<uidb64>/<token>/', views.custom_password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.custom_password_reset_complete, name='password_reset_complete'),
]