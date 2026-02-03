from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.contrib.auth.models import Group


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("The email address you have entered is already registered.")
        return super(UserRegisterForm, self).clean(*args, **kwargs)


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image', 'client_tz']


class UserGroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class' : 'form-control'}),
        }


class AddUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'groups']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control border-primary'}),
            'email': forms.TextInput(attrs={'class': 'form-control border-primary'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control border-primary'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control border-primary'}),
            'groups' : forms.SelectMultiple(attrs={'class': 'form-control multiple-select border-primary'})
        }


class UpdateUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'groups']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control border-primary'}),
            'email': forms.TextInput(attrs={'class': 'form-control border-primary'}),
            'groups' : forms.SelectMultiple(attrs={'class': 'form-control multiple-select border-primary'})
        }

