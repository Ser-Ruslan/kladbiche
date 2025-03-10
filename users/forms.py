from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=True, label='Имя', max_length=150)
    last_name = forms.CharField(required=True, label='Фамилия', max_length=150)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
