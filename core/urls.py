from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# REST API router
router = DefaultRouter()
router.register(r'cemeteries', views.CemeteryViewSet)
router.register(r'burials', views.BurialViewSet)
router.register(r'notes', views.UserNoteViewSet, basename='notes')
router.register(r'favorites', views.FavoriteBurialViewSet, basename='favorites')
router.register(r'burial-requests', views.BurialRequestViewSet, basename='burial-requests')

urlpatterns = [
    # Веб-интерфейс
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.user_profile, name='user_profile'),
    path('burials/<int:burial_id>/', views.burial_detail, name='burial_detail'),
    path('burials/<int:burial_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('burials/<int:burial_id>/note/', views.add_note, name='add_note'),
    path('burials/<int:burial_id>/note/delete/', views.delete_note, name='delete_note'),
    path('search/', views.search_burials, name='search_burials'),
    path('submit-burial/', views.submit_burial, name='submit_burial'),
    
    # Функции администратора
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('process-burial-request/<int:request_id>/', views.process_burial_request, name='process_burial_request'),
    path('add-burial/', views.add_burial, name='add_burial'),
    
    # REST API
    path('api/', include(router.urls)),
]
