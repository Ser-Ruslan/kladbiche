from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm as BasePasswordResetForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    """
    Форма для регистрации новых пользователей
    """
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'})
    )
    username = forms.CharField(
        label=_('Имя пользователя'),
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'})
    )
    password1 = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )
    password2 = forms.CharField(
        label=_('Подтверждение пароля'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'})
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Пользователь с таким email уже существует'))
        return email


class UserLoginForm(AuthenticationForm):
    """
    Форма для входа пользователей
    """
    username = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'})
    )
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )
    
    def clean_username(self):
        """
        Убеждаемся, что пользователь существует и активирован
        """
        email = self.cleaned_data.get('username')
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                raise forms.ValidationError(
                    _('Ваша учетная запись не активирована. Пожалуйста, проверьте вашу электронную почту для активации.')
                )
        except User.DoesNotExist:
            pass  # Пользователь не найден, стандартное сообщение об ошибке
        return email


class UserProfileForm(forms.ModelForm):
    """
    Форма для редактирования профиля пользователя
    """
    email = forms.EmailField(
        label=_('Email'),
        disabled=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label=_('Имя пользователя'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email', 'username')


class PasswordResetForm(BasePasswordResetForm):
    """
    Форма для сброса пароля
    """
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'})
    )
