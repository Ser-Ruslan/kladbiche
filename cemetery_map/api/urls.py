from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register(r'graves', views.GraveViewSet, basename='grave')
router.register(r'personal-notes', views.PersonalNoteViewSet, basename='personal-note')
router.register(r'favorites', views.FavoriteGraveViewSet, basename='favorite')
router.register(r'edit-proposals', views.EditProposalViewSet, basename='edit-proposal')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    
    # JWT токены для аутентификации
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
