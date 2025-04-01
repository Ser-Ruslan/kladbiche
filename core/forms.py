from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Burial, UserNote, BurialRequest


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, 
                            label='Email',
                            help_text='Обязательное поле.')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class UserNoteForm(forms.ModelForm):
    class Meta:
        model = UserNote
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        labels = {
            'text': 'Ваша заметка',
        }


class BurialSearchForm(forms.Form):
    query = forms.CharField(required=False, label='Поиск по ФИО', 
                          widget=forms.TextInput(attrs={'placeholder': 'Введите ФИО'}))
    birth_date_from = forms.DateField(required=False, label='Дата рождения с', 
                                    widget=forms.DateInput(attrs={'type': 'date'}))
    birth_date_to = forms.DateField(required=False, label='Дата рождения по', 
                                  widget=forms.DateInput(attrs={'type': 'date'}))
    death_date_from = forms.DateField(required=False, label='Дата смерти с', 
                                    widget=forms.DateInput(attrs={'type': 'date'}))
    death_date_to = forms.DateField(required=False, label='Дата смерти по', 
                                  widget=forms.DateInput(attrs={'type': 'date'}))
    favorites_only = forms.BooleanField(required=False, label='Только избранные')


class BurialRequestForm(forms.ModelForm):
    class Meta:
        model = BurialRequest
        fields = ('full_name', 'birth_date', 'death_date', 'description')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'death_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class BurialAdminForm(forms.ModelForm):
    class Meta:
        model = Burial
        fields = ('full_name', 'birth_date', 'death_date', 'admin_description')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'death_date': forms.DateInput(attrs={'type': 'date'}),
            'admin_description': forms.Textarea(attrs={'rows': 4}),
        }


class BurialRequestAdminForm(forms.Form):
    ACTIONS = (
        ('approve', 'Одобрить'),
        ('reject', 'Отклонить'),
    )
    
    action = forms.ChoiceField(choices=ACTIONS, label='Действие')
    rejection_reason = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Причина отклонения'
    )
