from django.urls import path
from . import views

app_name = 'cemeteries'

urlpatterns = [
    # Маршруты для кладбищ
    path('', views.CemeteryListView.as_view(), name='cemetery_list'),
    path('create/', views.CemeteryCreateView.as_view(), name='cemetery_create'),
    path('<int:pk>/', views.CemeteryDetailView.as_view(), name='cemetery_detail'),
    path('<int:pk>/update/', views.CemeteryUpdateView.as_view(), name='cemetery_update'),
    path('<int:pk>/delete/', views.CemeteryDeleteView.as_view(), name='cemetery_delete'),
    
    # Маршруты для объектов на кладбищах
    path('<int:cemetery_id>/objects/', views.CemeteryObjectListView.as_view(), name='cemetery_object_list'),
    path('<int:cemetery_id>/objects/create/', views.CemeteryObjectCreateView.as_view(), name='cemetery_object_create'),
    path('objects/<int:pk>/', views.CemeteryObjectDetailView.as_view(), name='cemetery_object_detail'),
    path('objects/<int:pk>/update/', views.CemeteryObjectUpdateView.as_view(), name='cemetery_object_update'),
    path('objects/<int:pk>/status/', views.CemeteryObjectStatusUpdateView.as_view(), name='cemetery_object_status'),
    
    # Маршруты для фотографий
    path('photos/upload/', views.PhotoUploadView.as_view(), name='photo_upload'),
    path('objects/<int:object_id>/photos/', views.ObjectPhotoListView.as_view(), name='object_photo_list'),
    path('objects/<int:object_id>/photos/add/', views.AddPhotoToObjectView.as_view(), name='add_photo_to_object'),
]