from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.contrib import messages


def admin_only(view_func):
    user = User.objects.all()
    def wrap(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, f'You are authenticated as {request.user} user, but you are not authorized to access this page. Would you like to login to a different account?')
            return HttpResponseRedirect(reverse('login'))
    return wrap