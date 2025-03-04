from django.urls import path
from . import views

app_name = 'maps'

urlpatterns = [
    # Маршруты для координат
    path('coordinates/', views.CoordinatesListView.as_view(), name='coordinates_list'),
    path('coordinates/<int:pk>/', views.CoordinatesDetailView.as_view(), name='coordinates_detail'),
    path('coordinates/<int:pk>/add-point/', views.CoordinatesAddPointView.as_view(), name='coordinates_add_point'),
    path('coordinates/<int:pk>/remove-point/<int:point_index>/', views.CoordinatesRemovePointView.as_view(), name='coordinates_remove_point'),
    
    # Маршруты для карт кладбищ
    path('cemetery/<int:cemetery_id>/', views.CemeteryMapView.as_view(), name='cemetery_map'),
    path('cemetery/<int:cemetery_id>/objects/', views.CemeteryMapObjectsView.as_view(), name='cemetery_map_objects'),
    
    # Генерация карты и визуализация
    path('cemetery/<int:cemetery_id>/render/', views.RenderCemeteryMapView.as_view(), name='render_cemetery_map'),
    path('cemetery/<int:cemetery_id>/search/', views.SearchOnMapView.as_view(), name='search_on_map'),
]
