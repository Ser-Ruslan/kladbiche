from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import ListView, DetailView, UpdateView, View, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from cemeteries.models import Cemetery
from users.models import User
from notifications.models import ObjectModificationRequest


# ===== Проверка роли =====
class RoleRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки ролей пользователя. Используется для проверки доступа к административным функциям.
    """
    required_roles = []

    def test_func(self):
        return self.request.user.role in self.required_roles

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас недостаточно прав для выполнения этого действия.")


# ===== Список пользователей =====
class UserListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    required_roles = ['ADMIN', 'MODERATOR']

    def get_queryset(self):
        """
        Показываем список пользователей только для Администраторов и Модераторов.
        """
        return User.objects.all()


# ===== Детали пользователя =====
class UserDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'
    required_roles = ['ADMIN', 'MODERATOR']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modification_requests'] = ObjectModificationRequest.objects.filter(user=self.object)
        return context


# ===== Обновление данных пользователя =====
class UserUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = User
    template_name = 'users/user_form.html'
    fields = ['first_name', 'last_name', 'email']  # Поля для редактирования
    success_url = reverse_lazy('users:user_list')
    required_roles = ['ADMIN', 'MODERATOR']


# ===== Изменение роли пользователя =====
class ChangeUserRoleView(LoginRequiredMixin, RoleRequiredMixin, View):
    required_roles = ['ADMIN']

    def post(self, request, pk, *args, **kwargs):
        """
        Метод POST для изменения роли пользователя.
        """
        user = get_object_or_404(User, pk=pk)
        if 'role' in request.POST:
            new_role = request.POST['role']
            if new_role in dict(User.USER_ROLES):  # Проверяем, что новая роль допустима
                user.role = new_role
                user.save()
                return JsonResponse({'status': 'success', 'message': f'Роль пользователя изменена на {new_role}'})
        return JsonResponse({'status': 'error', 'message': 'Неверная роль'}, status=400)


# ===== Поиск объектов пользователем =====
class UserSearchObjectsView(LoginRequiredMixin, View):
    """
    Функция для поиска объектов (могил, кладбищ, и др.), доступная всем пользователям.
    """
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if query:
            # Поиск проходит по `Cemetery` или другим связанным моделям (как пример)
            cemeteries = Cemetery.objects.filter(name__icontains=query).values('id', 'name')
            return JsonResponse({'results': list(cemeteries)})
        return JsonResponse({'results': []})


# ===== Управление запросами на модификацию =====
class ModificationRequestListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """
    Список всех запросов на модификацию (для Администраторов и Модераторов).
    """
    model = ObjectModificationRequest
    template_name = 'users/modification_request_list.html'
    context_object_name = 'requests'
    required_roles = ['ADMIN', 'MODERATOR']


class CreateModificationRequestView(LoginRequiredMixin, CreateView):
    """
    Создание нового запроса на модификацию.
    """
    model = ObjectModificationRequest
    fields = ['object_type', 'object_id', 'description']
    template_name = 'users/modification_request_form.html'
    success_url = reverse_lazy('users:modification_requests')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Устанавливаем текущего пользователя как автора
        return super().form_valid(form)