from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from graves.models import Grave, PersonalNote, FavoriteGrave, EditProposal
from notifications.models import Notification
from notifications.utils import notify_user, notify_user_about_proposal_status
from .serializers import (
    UserSerializer, GraveSerializer, PersonalNoteSerializer,
    FavoriteGraveSerializer, EditProposalSerializer, NotificationSerializer
)

User = get_user_model()

class IsAdminUser(permissions.BasePermission):
    """
    Разрешение только для администраторов
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешение для владельца объекта или администратора
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        
        # Проверка для различных типов объектов
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class GraveViewSet(viewsets.ModelViewSet):
    """
    API для работы с захоронениями
    """
    queryset = Grave.objects.all()
    serializer_class = GraveSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name']
    
    def get_permissions(self):
        """
        Права доступа:
        - Чтение доступно всем
        - Создание/изменение/удаление только для администраторов
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Расширенный поиск захоронений по параметрам
        """
        query = request.query_params.get('query', '')
        birth_date = request.query_params.get('birth_date', '')
        death_date = request.query_params.get('death_date', '')
        favorites_only = request.query_params.get('favorites_only') == 'true'
        
        graves = self.get_queryset()
        
        # Фильтрация по ФИО
        if query:
            graves = graves.filter(full_name__icontains=query)
        
        # Фильтрация по датам
        if birth_date:
            graves = graves.filter(birth_date=birth_date)
        if death_date:
            graves = graves.filter(death_date=death_date)
        
        # Фильтрация по избранным
        if favorites_only and request.user.is_authenticated:
            favorite_ids = FavoriteGrave.objects.filter(
                user=request.user
            ).values_list('grave_id', flat=True)
            graves = graves.filter(id__in=favorite_ids)
        
        serializer = self.get_serializer(graves, many=True)
        return Response(serializer.data)


class PersonalNoteViewSet(viewsets.ModelViewSet):
    """
    API для работы с личными заметками
    """
    serializer_class = PersonalNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Возвращает только заметки текущего пользователя
        """
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'admin':
                return PersonalNote.objects.all()
            return PersonalNote.objects.filter(user=user)
        return PersonalNote.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteGraveViewSet(viewsets.ModelViewSet):
    """
    API для работы с избранными захоронениями
    """
    serializer_class = FavoriteGraveSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает только избранные захоронения текущего пользователя
        """
        return FavoriteGrave.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        """
        Удаление захоронения из избранного
        """
        grave = get_object_or_404(Grave, pk=pk)
        FavoriteGrave.objects.filter(user=request.user, grave=grave).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EditProposalViewSet(viewsets.ModelViewSet):
    """
    API для работы с предложениями редактирования
    """
    serializer_class = EditProposalSerializer
    
    def get_permissions(self):
        """
        Права доступа:
        - Чтение/модерация предложений только для администраторов
        - Создание для аутентифицированных пользователей
        - Счетчик предложений доступен только администраторам
        """
        if self.action in ['list', 'retrieve', 'moderate', 'pending_count']:
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """
        Возвращает все предложения для администраторов или только своих для обычных пользователей
        """
        user = self.request.user
        if user.role == 'admin':
            return EditProposal.objects.all()
        return EditProposal.objects.filter(user=user)
    
    def perform_create(self, serializer):
        proposal = serializer.save(user=self.request.user)
        
        # Отправляем уведомление всем администраторам
        admins = User.objects.filter(role='admin', is_active=True)
        for admin in admins:
            notify_user(
                user=admin,
                notification_type='edit_proposal',
                message=f'Новое предложение по редактированию от {self.request.user.username} для захоронения {proposal.grave.full_name}',
                related_id=proposal.id
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def moderate(self, request, pk=None):
        """
        Модерация предложения редактирования (одобрение/отклонение)
        """
        proposal = self.get_object()
        action = request.data.get('action')
        rejection_reason = request.data.get('rejection_reason', '')
        
        if action not in ['approve', 'reject']:
            return Response({'error': 'Необходимо указать действие (approve/reject)'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'approve':
            # Обновляем описание захоронения
            grave = proposal.grave
            grave.description = proposal.proposed_description
            grave.save()
            
            proposal.status = 'approved'
            proposal.save()
            
            # Отправляем уведомление пользователю
            notify_user_about_proposal_status(proposal, approved=True)
            
            return Response({'status': 'Предложение одобрено'})
        
        elif action == 'reject':
            proposal.status = 'rejected'
            proposal.rejection_reason = rejection_reason
            proposal.save()
            
            # Отправляем уведомление пользователю
            notify_user_about_proposal_status(proposal, approved=False)
            
            return Response({'status': 'Предложение отклонено'})
            
    @action(detail=False, methods=['get'])
    def pending_count(self, request):
        """
        Получить количество предложений, ожидающих модерации
        """
        count = EditProposal.objects.filter(status='pending').count()
        return Response({'count': count})


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для работы с уведомлениями
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает только уведомления текущего пользователя
        """
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Отметить уведомление как прочитанное
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Уведомление отмечено как прочитанное'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Отметить все уведомления как прочитанные
        """
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'Все уведомления отмечены как прочитанные'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Получить количество непрочитанных уведомлений
        """
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'count': count})
