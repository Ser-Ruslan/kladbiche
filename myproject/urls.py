from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from cemeteries.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/cemeteries/', include('cemeteries.urls')),
    path('api/maps/', include('maps.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    path('', index, name='index'), #Домашняя страничка, да
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    