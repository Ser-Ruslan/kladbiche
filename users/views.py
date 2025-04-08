import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DetailView, View

from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, PasswordResetForm
from .models import User, ActivationToken
from .utils import generate_activation_token

User = get_user_model()

class CustomLoginView(LoginView):
    """
    Представление для авторизации пользователей
    """
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """
        Если форма валидна, обновляем дату последней активности
        """
        user = form.get_user()
        user.last_activity = timezone.now()
        user.save()
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """
    Представление для выхода пользователей
    """
    template_name = 'users/logout.html'
    next_page = reverse_lazy('login')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Обработка как GET, так и POST запросов
        """
        # Если запрос GET, показываем страницу подтверждения
        if request.method == 'GET':
            return render(request, self.template_name)
        
        # Если запрос POST, выходим из системы
        return super().dispatch(request, *args, **kwargs)


class UserRegistrationView(CreateView):
    """
    Представление для регистрации новых пользователей
    """
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """
        Если форма валидна, создаем неактивного пользователя и отправляем письмо активации
        """
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Создание токена активации
        token = generate_activation_token()
        expires_at = timezone.now() + timedelta(days=3)
        activation_token = ActivationToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

        # Отправка письма с ссылкой активации
        activation_url = self.request.build_absolute_uri(
            reverse_lazy('activate', kwargs={'token': token})
        )
        send_mail(
            'Активация аккаунта на сервисе "Интерактивная карта кладбища"',
            f'Для активации аккаунта перейдите по ссылке: {activation_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        messages.success(self.request, 'Регистрация успешна! Проверьте email для активации аккаунта.')
        return redirect('login')


class ActivateAccountView(View):
    """
    Представление для активации аккаунта по токену
    """
    def get(self, request, token):
        activation_token = get_object_or_404(ActivationToken, token=token)
        
        if not activation_token.is_valid():
            messages.error(request, 'Срок действия ссылки истек.')
            return redirect('login')
        
        user = activation_token.user
        user.is_active = True
        user.save()
        
        # Удаляем использованный токен
        activation_token.delete()
        
        messages.success(request, 'Аккаунт успешно активирован! Теперь вы можете войти.')
        return redirect('login')


@method_decorator(login_required, name='dispatch')
class UserProfileView(UpdateView):
    """
    Представление для просмотра и редактирования профиля пользователя
    """
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    """
    Представление для сброса пароля
    """
    form_class = PasswordResetForm
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Инструкции по сбросу пароля отправлены на ваш email.')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Представление для подтверждения сброса пароля
    """
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Пароль успешно изменен!')
        return super().form_valid(form)
