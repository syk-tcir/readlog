from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'), 
    path('test/', views.api_test, name='api_test'),
    path('books/register/', views.register_book, name='register_book'),
    path('books/register/detail/', views.book_register_detail, name='book_register_detail'),
    path('books/check/', views.check_book_exists, name='check_book_exists'),
    path('books/check/', views.check_book_exists, name='check_book_exists'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:book_id>/delete/', views.book_delete, name='book_delete'),
    path('top/', views.top, name='top'),
]