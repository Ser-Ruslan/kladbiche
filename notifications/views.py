from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from .models import ObjectModificationRequest
from django.contrib import messages

# Вьюха для отображения списка уведомлений
class NotificationListView(LoginRequiredMixin, ListView):
    model = ObjectModificationRequest
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return ObjectModificationRequest.objects.filter(updated_by=self.request.user).order_by('-created_at')

# Вьюха для отображения деталей конкретного уведомления
class NotificationDetailView(LoginRequiredMixin, DetailView):
    model = ObjectModificationRequest
    template_name = 'notifications/notification_detail.html'
    context_object_name = 'notification'

# Вьюха для отметки уведомления как прочитанного
class MarkNotificationAsReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(ObjectModificationRequest, pk=pk, updated_by=request.user)
        notification.status = 'READ'   # Добавьте соответствующий статус в модель, если нужно
        notification.save()
        messages.success(request, 'Уведомление помечено как прочитанное.')
        return redirect('notifications:notification_list')

# Вьюха для массового помечания всех уведомлений как прочитанных
class MarkAllNotificationsAsReadView(LoginRequiredMixin, View):
    def post(self, request):
        notifications = ObjectModificationRequest.objects.filter(updated_by=request.user)
        notifications.update(status='READ')  # Аналогично, требуется статус в модели
        messages.success(request, 'Все уведомления помечены как прочитанные.')
        return redirect('notifications:notification_list')



# Вьюха для уведомлений о модификациях объектов
class ObjectModificationNotificationsView(LoginRequiredMixin, ListView):
    model = ObjectModificationRequest
    template_name = 'notifications/object_modifications.html'
    context_object_name = 'modification_requests'

    def get_queryset(self):
        return ObjectModificationRequest.objects.filter(status='PENDING').order_by('-created_at')

# Вьюха для уведомлений модераторов
class ModerationNotificationsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = ObjectModificationRequest
    template_name = 'notifications/moderation_notifications.html'
    context_object_name = 'moderation_notifications'

    def test_func(self):
        # Ограничение доступа только для пользователей с правами модератора
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_queryset(self):
        return ObjectModificationRequest.objects.filter(status='PENDING').order_by('-created_at')