from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Уведомления для пользователей
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('<int:pk>/mark-as-read/', views.MarkNotificationAsReadView.as_view(), name='mark_as_read'),
    path('mark-all-as-read/', views.MarkAllNotificationsAsReadView.as_view(), name='mark_all_as_read'),
    
    # Управление подписками на уведомления
    path('subscriptions/', views.NotificationSubscriptionListView.as_view(), name='subscription_list'),
    path('subscriptions/create/', views.NotificationSubscriptionCreateView.as_view(), name='subscription_create'),
    path('subscriptions/<int:pk>/delete/', views.NotificationSubscriptionDeleteView.as_view(), name='subscription_delete'),
    
    # Уведомления о модификациях объектов
    path('object-modifications/', views.ObjectModificationNotificationsView.as_view(), name='object_modifications'),
    
    # Уведомления для модераторов и администраторов
    path('moderation/', views.ModerationNotificationsView.as_view(), name='moderation_notifications'),
]