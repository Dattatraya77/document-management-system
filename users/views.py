from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, UserGroupForm, AddUserForm, UpdateUserForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from document_management_system.decorators import admin_only
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .utils import account_activation_token
from django.urls import reverse, reverse_lazy
from django.conf import settings
from .models import Profile
from django.db import connection
from django.utils.timezone import now, timedelta
from django.contrib.sessions.models import Session
from django.utils.encoding import force_str


def get_current_tenant(request):
    try:
        return {
            'client_name': request.tenant.name,
            'client_title': request.tenant.page_title,
        }
    except Exception as e:
        print(e)
        return {
            'client_name': '',
            'client_title': '',
        }


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            'type': 'login'
        }
        self.extra_context.update(get_current_tenant(request))
        return super(CustomLoginView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        tenant = self.request.tenant
        multiple_login_restriction = getattr(tenant, 'multiple_login_restriction', False)

        if multiple_login_restriction:

            # Check if this user is already in another active session
            user_id_str = str(user.id)
            sessions = Session.objects.filter(expire_date__gte=now())

            for session in sessions:
                try:
                    data = session.get_decoded()
                    session_user_id = str(data.get('_auth_user_id'))
                    # Block if same user is already in another session
                    if session_user_id == user_id_str:
                        messages.error(
                            self.request,
                            "This user is already logged in from another device or browser."
                        )
                        return self.form_invalid(form)
                except:
                    continue  # ignore bad sessions

        # Safe to log in
        login(self.request, user)

        # Now update session expiry to 2 hrs(7200) seconds if restriction is on
        if multiple_login_restriction:
            self.request.session.set_expiry(7200)  # Sets expiry in session data
            # Also manually update DB session expire_date for immediate visibility
            session_key = self.request.session.session_key
            Session.objects.filter(session_key=session_key).update(
                expire_date=now() + timedelta(seconds=7200)
            )

        return redirect(self.get_success_url())


class CustomLogoutView(LogoutView):
    template_name = 'users/logout.html'

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            'type': 'logout'
        }
        self.extra_context.update(get_current_tenant(request))

        return super(CustomLogoutView, self).get(request, *args, **kwargs)


def sendEmail(self, request, user, email):
    current_site = get_current_site(request)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    activation_link = reverse('activate', kwargs={
        'uidb64': uid,
        'token': token
    })

    activate_url = f"https://{current_site.domain}{activation_link}"

    email_subject = 'Activate your account'
    email_body = (
        f"Hi {user.username},\n\n"
        f"Please click the link below to activate your account:\n\n"
        f"{activate_url}\n\n"
        f"Thank you!"
    )

    email_message = EmailMessage(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )

    email_message.send(fail_silently=False)

    messages.success(
        self.request,
        'Account created successfully. Please check your email to activate your account.'
    )


class UserRegistrationView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')

    def get(self, request):
        if request.user.is_authenticated:
            messages.info(
                request,
                'You are already logged in. Please logout to register a new account.'
            )
            return redirect('login')

        return render(request, self.template_name, {'form': self.form_class()})

    def form_valid(self, form):
        email = form.cleaned_data.get('email')

        # Prevent duplicate email registration
        if User.objects.filter(email=email).exists():
            messages.error(self.request, 'This email is already registered.')
            return render(self.request, self.template_name, {'form': form})

        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=email,
            password=form.cleaned_data['password1']
        )

        user.is_active = False
        user.save()

        sendEmail(self, self.request, user, email)

        return redirect('login')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if user.is_active:
                messages.info(request, 'Your account is already activated.')
                return redirect('login')

            if not account_activation_token.check_token(user, token):
                messages.error(request, 'Activation link is invalid or expired.')
                return redirect('login')

            user.is_active = True
            user.save()

            # Optional: add default group
            # user.groups.add(Group.objects.get(name='COMMON'))

            messages.success(
                request,
                'Your account has been activated successfully. You can now log in.'
            )
            return redirect('login')

        except Exception:
            messages.error(request, 'Invalid activation link.')
            return redirect('login')


@login_required
def profile(request):
    profile_obj = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile_obj
        )

        if u_form.is_valid() and p_form.is_valid():
            # Save user + profile
            u_form.save()
            profile = p_form.save(commit=False)

            # ✅ Handle profile picture removal
            if request.POST.get('check_profile_picture_remove_or_not') == 'on':
                if profile.image and profile.image.name != 'default.jpg':
                    profile.image.delete(save=False)
                profile.image = 'default.jpg'

            profile.save()

            messages.success(request, 'Your account has been updated successfully!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile_obj)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'type': 'profile',
        'time_zone': profile_obj.client_tz,
    }

    return render(request, 'users/profile.html', context)


def login_admin(request):
    if request.method == 'POST':
        u = request.POST['username']
        p = request.POST['password']
        user = authenticate(username=u, password=p)
        try:
            if user:
                login(request, user)
                print(user)
                msg = "Welcome " + str(user) + "  to Document Management System !!!"
                messages.success(request, msg)
                return redirect('home')

            else:
                messages.error(request, "Invalid Username or Password. Please re-enter your user information.")
                return render(request,"users/login.html")
        except Exception as e:
            # print("Error:->", e)
            # msg = "Error : " + str(e)
            # messages.error(request, msg)
            messages.error(request, "Invalid Username or Password. Please re-enter your user information.")
            return redirect('login')

    return render(request, "users/login.html")


def Logout(request):
    logout(request)
    return redirect('login')


@login_required
@admin_only
def view_users(request):
    admin_group = Group.objects.get(name='DOC_ADMIN')
    common_group = get_object_or_404(Group, name='COMMON')
    if request.user.is_staff == True:
        users = User.objects.filter(is_active=True).order_by("id")
        total_users = User.objects.filter(is_active=True).count()
    else:
        users = User.objects.filter(Q(is_active=True, groups__in=request.user.groups.all()) |
                                    Q(groups__in=[common_group])).distinct()
        total_users = User.objects.filter(Q(is_active=True, groups__in=request.user.groups.all()) |
                                          Q(groups__in=[common_group])).distinct().count()

    context = {
        "users": users,
        'total_users': total_users,
        'client_name': connection.tenant.name,
    }

    return render(request, 'users/view_all_users.html', context)


class DeleteUser(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs["id"])
        username = user.username
        user.is_active = False
        user.is_staff = False
        user.is_superuser = False
        user.save()
        messages.success(request, f'User "{ username }" has been deleted Successfully. Thank You!!!')
        return redirect('view-all-users')


class CreateShowUserGroup(LoginRequiredMixin, View):

    def get(self, request):

        g_form = UserGroupForm()
        groups = Group.objects.all().order_by("-id")

        context = {
            'g_form': g_form,
            'groups': groups,
        }

        context.update(get_current_tenant(request))
        return render(request, 'users/create_show_user_group.html', context)

    def post(self, request):
        g_form = UserGroupForm(request.POST)
        if g_form.is_valid():
            group_name = g_form.data['name']
            g_form.save()
            messages.success(request, f'Group "{ group_name }" has been created successfully!')
            return redirect('create-show-user-group')
        else:
            groups = Group.objects.all().order_by("-id")

            context = {
                'g_form': g_form,
                'groups': groups,
            }

            context.update(get_current_tenant(request))
            return render(request, 'users/create_show_user_group.html', context)


class UpdateShowUserGroup(LoginRequiredMixin, View):

    def get(self, request, id):

        group = get_object_or_404(Group, id=id)
        g_form = UserGroupForm(instance=group)

        context = {
            'g_form': g_form,
            'client_name': connection.tenant.name,
        }

        context.update(get_current_tenant(request))
        return render(request, 'users/update_show_user_group.html', context)

    def post(self, request, id):

        group = get_object_or_404(Group, id=id)
        g_form = UserGroupForm(request.POST, instance=group)
        group_name = group.name
        
        if g_form.is_valid():
            g_form.save()
            messages.success(request, f'Group "{ group_name }" has been updated successfully!')
            return redirect('create-show-user-group')
        else:
            groups = Group.objects.all().order_by("-id")

            context = {
                'g_form': g_form,
                'groups': groups,
            }

            context.update(get_current_tenant(request))
            return render(request, 'users/update_show_user_group.html', context)


class DeleteShowUserGroup(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, id=kwargs["id"])
        group_name = group.name
        group.delete()
        messages.success(request, f'Group "{ group_name }" has been deleted successfully. Thank You!!!')
        return redirect('create-show-user-group')


class AddShowUser(LoginRequiredMixin, View):

    def get(self, request):

        user_form = AddUserForm()
        users = User.objects.filter(is_active=True).order_by("-id")
        users_groups_data = [{'user': item, 'group': ', '.join(map(str, item.groups.all()))} for item in users]

        context = {
            'user_form': user_form,
            'users_groups_data': users_groups_data,
        }

        context.update(get_current_tenant(request))

        return render(request, 'users/add_show_user.html', context)

    def post(self, request):

        user_form = AddUserForm(request.POST)
        group_ids = request.POST.getlist('groups')
        user_name = user_form.data['username']

        if user_form.is_valid():
            user = user_form.save()
            for id in group_ids:
                group = get_object_or_404(Group, id=id)
                group.user_set.add(user)


            messages.success(request, f'User "{ user_name }" has been created successfully!')
            return redirect('add-show-user')
        else:
            users = User.objects.filter(is_active=True).order_by("-id")
            users_groups_data = [{'user': item, 'group': ', '.join(map(str, item.groups.all()))} for item in users]

            context = {
                'user_form': user_form,
                'users_groups_data': users_groups_data,
            }

            context.update(get_current_tenant(request))

            return render(request, 'users/add_show_user.html', context)


class DeleteAddShowUser(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs["id"])
        username = user.username
        user.is_active = False
        user.is_staff = False
        user.is_superuser = False
        user.save()
        messages.success(request, f'User "{ username }" has been deleted successfully. Thank You!!!')
        return redirect('add-show-user')


class UpdateAddShowUser(LoginRequiredMixin, View):

    def get(self, request, id):

        user = get_object_or_404(User, id=id)
        user_form = UpdateUserForm(instance=user)

        context = {
            'user_form': user_form,
            'client_name': connection.tenant.name,
        }

        context.update(get_current_tenant(request))
        return render(request, 'users/update_add_show_user.html', context)

    def post(self, request, id):

        user = get_object_or_404(User, id=id)
        user_form = UpdateUserForm(request.POST, instance=user)
        group_ids = request.POST.getlist('groups')
        user_name = user_form.data['username']

        if user_form.is_valid():
            user1 = user_form.save()
            user.groups.clear()
            for id in group_ids:
                group = get_object_or_404(Group, id=id)
                group.user_set.add(user1)
            messages.success(request, f'User "{ user_name }" has been updated successfully!')
            return redirect('add-show-user')
        else:
            pass

            context = {
                'user_form': user_form,
                'client_name': connection.tenant.name,
            }

            context.update(get_current_tenant(request))
            return render(request, 'users/update_add_show_user.html', context)


class ChangeUserPassword(LoginRequiredMixin, View):

    def get(self, request, id):

        user = get_object_or_404(User, id=id)
        form = SetPasswordForm(user)

        context = {
            'form': form,
            'client_name': connection.tenant.name,
        }

        context.update(get_current_tenant(request))
        return render(request, 'users/change_user_password.html', context)

    def post(self, request, id):

        user = get_object_or_404(User, id=id)
        form = SetPasswordForm(user, request.POST)
        user_name = user.username

        if form.is_valid():
            form.save()
            messages.success(request, f'The password has been changed for the user "{ user_name }".')
            return redirect('add-show-user')
        else:
            pass

            context = {
                'form': form,
                'client_name': connection.tenant.name,
            }

            context.update(get_current_tenant(request))
            return render(request, 'users/change_user_password.html', context)


class ChangeUserPasswordProfile(LoginRequiredMixin, View):

    def get(self, request, id):

        try:
            user = get_object_or_404(User, id=id)
        except:
            messages.error(request, f'Oops! User not found. Please contact system administrator.')
            return redirect('profile')
        if user.id != request.user.id:
            messages.error(request, f'You are not authorised user to change password.')
            return redirect('profile')
        else:
            form = SetPasswordForm(user)

            context = {
                'form': form,
                'client_name': connection.tenant.name,
            }

            context.update(get_current_tenant(request))
            return render(request, 'users/change_user_password_profile.html', context)

    def post(self, request, id):

        user = get_object_or_404(User, id=id)
        form = SetPasswordForm(user, request.POST)
        user_name = user.username

        if form.is_valid():
            form.save()
            messages.success(request, f'The password has been changed for the user "{ user_name }".')
            return redirect('login')
        else:
            pass

            context = {
                'form': form,
                'client_name': connection.tenant.name,
            }

            context.update(get_current_tenant(request))
            return render(request, 'users/change_user_password_profile.html', context)


def count_active_users():
    """Count users who have a valid session (based on expire_date)."""
    sessions = Session.objects.filter(expire_date__gte=now())
    user_ids = set()

    for session in sessions:
        try:
            data = session.get_decoded()
            uid = data.get('_auth_user_id')
            if uid:
                user_ids.add(uid)
        except:
            continue  # skip invalid/broken sessions

    return len(user_ids)