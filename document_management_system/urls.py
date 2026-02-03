"""document_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf.urls.static import static
from users import views as user_views
from users.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.UserRegistrationView.as_view(), name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             extra_context={
                 'type': 'password_reset',
             }
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('', include('create_document.urls')),
    path('view_users/', user_views.view_users, name='view-all-users'),
    path('activate/<uidb64>/<token>', user_views.VerificationView.as_view(), name='activate'),
    path('deleteUser/<int:id>/', user_views.DeleteUser.as_view(), name='deleteUser'),
    path('create-show-user-group/', user_views.CreateShowUserGroup.as_view(), name='create-show-user-group'),
    path('update-show-user-group/<int:id>/', user_views.UpdateShowUserGroup.as_view(), name='update-show-user-group'),
    path('delete-show-user-group/<int:id>/', user_views.DeleteShowUserGroup.as_view(), name='delete-show-user-group'),
    path('add-show-user/', user_views.AddShowUser.as_view(), name='add-show-user'),
    path('delete-add-show-user/<int:id>/', user_views.DeleteAddShowUser.as_view(), name='delete-add-show-user'),
    path('update-add-show-user/<int:id>/', user_views.UpdateAddShowUser.as_view(), name='update-add-show-user'),
    path('change-user-password/<int:id>/', user_views.ChangeUserPassword.as_view(), name='change-user-password'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)