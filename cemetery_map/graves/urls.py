from django.urls import path
from . import views

urlpatterns = [
    path('map/', views.map_view, name='map'),
    path('grave/<int:grave_id>/', views.grave_detail_ajax, name='grave_detail_ajax'),
    path('search/', views.search_graves, name='search_graves'),
    path('grave/<int:grave_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('grave/<int:grave_id>/save-note/', views.save_personal_note, name='save_personal_note'),
    path('grave/<int:grave_id>/submit-edit/', views.submit_edit_proposal, name='submit_edit_proposal'),
    path('favorites/', views.FavoriteGravesListView.as_view(), name='favorites_list'),
]
