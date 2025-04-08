"""
URL Configuration for cemetery_map project
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/graves/map/')),
    path('users/', include('users.urls')),
    path('graves/', include('graves.urls')),
    path('notifications/', include('notifications.urls')),
    path('api/', include('api.urls')),
]
