from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('<int:notification_id>/mark-read/', views.mark_notification_as_read, name='mark_notification_read'),
    path('mark-all-read/', views.mark_all_notifications_as_read, name='mark_all_notifications_read'),
    path('unread-count/', views.get_unread_notifications_count, name='unread_notifications_count'),
]
