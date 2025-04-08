from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from .models import Notification

@method_decorator(login_required, name='dispatch')
class NotificationListView(ListView):
    """
    Список уведомлений пользователя
    """
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 10
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@login_required
def mark_notification_as_read(request, notification_id):
    """
    Пометить уведомление как прочитанное
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notification_list')


@login_required
def mark_all_notifications_as_read(request):
    """
    Пометить все уведомления пользователя как прочитанные
    """
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notification_list')


@login_required
def get_unread_notifications_count(request):
    """
    Получить количество непрочитанных уведомлений для отображения в меню
    """
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})
