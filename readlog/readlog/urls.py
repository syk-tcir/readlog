from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/password_change/',
         auth_views.PasswordChangeView.as_view(
             success_url='/accounts/password_change/done/'
         ),
         name='password_change'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('app.urls')),
]