from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [

    # Регистрация и авторизация
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Управление пользователями
    path('', views.UserListView.as_view(), name='user_list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    
    # Административные функции для пользователей с ролью ADMIN или MODERATOR
    path('<int:pk>/change-role/', views.ChangeUserRoleView.as_view(), name='change_role'),
    
    # Поиск объектов пользователем
    path('search/', views.UserSearchObjectsView.as_view(), name='search_objects'),
    
    # Запросы на модификацию объектов
    path('modification-requests/', views.ModificationRequestListView.as_view(), name='modification_requests'),
    path('modification-requests/create/', views.CreateModificationRequestView.as_view(), name='create_modification_request'),
]