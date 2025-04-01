from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login
from django.urls import reverse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import logout

from .models import Cemetery, Burial, UserNote, FavoriteBurial, BurialRequest
from .serializers import (
    CemeterySerializer, BurialSerializer, UserNoteSerializer, 
    FavoriteBurialSerializer, BurialRequestSerializer, BurialRequestAdminSerializer,
    BurialListSerializer, BurialDetailSerializer
)
from .forms import (
    SignUpForm, UserNoteForm, BurialSearchForm, BurialRequestForm,
    BurialAdminForm, BurialRequestAdminForm
)
from .permissions import IsAdminUser, IsOwnerOrAdmin


def index(request):
    """Главная страница с картой"""
    cemeteries = Cemetery.objects.all()
    if not cemeteries.exists():
        # Создаем Читинское центральное кладбище по умолчанию
        cemetery = Cemetery.objects.create(
            name="Читинское центральное кладбище",
            latitude=settings.DEFAULT_CEMETERY_LATITUDE,
            longitude=settings.DEFAULT_CEMETERY_LONGITUDE,
            description="Центральное кладбище города Читы"
        )
    
    # Получаем выбранное кладбище или используем первое
    selected_cemetery_id = request.GET.get('cemetery_id')
    if selected_cemetery_id:
        cemetery = get_object_or_404(Cemetery, id=selected_cemetery_id)
    else:
        cemetery = cemeteries.first()
    
    search_form = BurialSearchForm()
    
    context = {
        'cemetery': cemetery,
        'cemeteries': cemeteries,
        'yandex_maps_api_key': settings.YANDEX_MAPS_API_KEY,
        'search_form': search_form,
    }
    return render(request, 'map.html', context)

def logout_view(request):
    logout(request)
    return redirect('index')


def signup(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def user_profile(request):
    """Профиль пользователя"""
    user = request.user
    favorites = FavoriteBurial.objects.filter(user=user).select_related('burial')
    pending_requests = BurialRequest.objects.filter(user=user, status='pending')
    processed_requests = BurialRequest.objects.filter(user=user).exclude(status='pending')
    
    context = {
        'user': user,
        'favorites': favorites,
        'pending_requests': pending_requests,
        'processed_requests': processed_requests,
    }
    return render(request, 'user_profile.html', context)


@login_required
def toggle_favorite(request, burial_id):
    """Добавление/удаление захоронения из избранного"""
    burial = get_object_or_404(Burial, id=burial_id)
    favorite, created = FavoriteBurial.objects.get_or_create(
        user=request.user,
        burial=burial
    )
    
    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True
    
    return JsonResponse({'success': True, 'is_favorite': is_favorite})


@login_required
def add_note(request, burial_id):
    """Добавление/обновление заметки к захоронению"""
    burial = get_object_or_404(Burial, id=burial_id)
    
    if request.method == 'POST':
        form = UserNoteForm(request.POST)
        if form.is_valid():
            note, created = UserNote.objects.update_or_create(
                user=request.user,
                burial=burial,
                defaults={'text': form.cleaned_data['text']}
            )
            return JsonResponse({'success': True, 'text': note.text})
    
    return JsonResponse({'success': False}, status=400)


@login_required
def delete_note(request, burial_id):
    """Удаление заметки к захоронению"""
    burial = get_object_or_404(Burial, id=burial_id)
    
    try:
        note = UserNote.objects.get(user=request.user, burial=burial)
        note.delete()
        return JsonResponse({'success': True})
    except UserNote.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Заметка не найдена'}, status=404)


def burial_detail(request, burial_id):
    """Подробная информация о захоронении"""
    burial = get_object_or_404(Burial, id=burial_id)
    
    user_note = None
    is_favorite = False
    
    if request.user.is_authenticated:
        try:
            user_note = UserNote.objects.get(user=request.user, burial=burial)
        except UserNote.DoesNotExist:
            pass
        
        is_favorite = FavoriteBurial.objects.filter(user=request.user, burial=burial).exists()
    
    note_form = UserNoteForm(instance=user_note)
    
    context = {
        'burial': burial,
        'user_note': user_note,
        'is_favorite': is_favorite,
        'note_form': note_form,
    }
    
    return render(request, 'burial_detail.html', context)


def search_burials(request):
    """Поиск захоронений"""
    form = BurialSearchForm(request.GET)
    results = []
    
    if form.is_valid():
        query = form.cleaned_data.get('query', '')
        birth_date_from = form.cleaned_data.get('birth_date_from')
        birth_date_to = form.cleaned_data.get('birth_date_to')
        death_date_from = form.cleaned_data.get('death_date_from')
        death_date_to = form.cleaned_data.get('death_date_to')
        favorites_only = form.cleaned_data.get('favorites_only', False)
        
        filters = Q()
        
        if query:
            filters &= Q(full_name__icontains=query)
        
        if birth_date_from:
            filters &= Q(birth_date__gte=birth_date_from)
        
        if birth_date_to:
            filters &= Q(birth_date__lte=birth_date_to)
        
        if death_date_from:
            filters &= Q(death_date__gte=death_date_from)
        
        if death_date_to:
            filters &= Q(death_date__lte=death_date_to)
        
        queryset = Burial.objects.filter(filters)
        
        if favorites_only and request.user.is_authenticated:
            favorite_burials = FavoriteBurial.objects.filter(user=request.user).values_list('burial_id', flat=True)
            queryset = queryset.filter(id__in=favorite_burials)
        
        results = queryset
    
    context = {
        'form': form,
        'results': results,
        'query': request.GET.get('query', ''),
    }
    
    return render(request, 'search_results.html', context)


@login_required
def submit_burial(request):
    """Отправка запроса на добавление захоронения"""
    if request.method == 'POST':
        form = BurialRequestForm(request.POST)
        if form.is_valid():
            # Получаем координаты из формы (передаются через скрытые поля)
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            if not latitude or not longitude:
                return JsonResponse({
                    'success': False,
                    'error': 'Координаты не указаны. Пожалуйста, отметьте место на карте.'
                }, status=400)
            
            cemetery_id = request.POST.get('cemetery_id')
            if cemetery_id:
                cemetery = get_object_or_404(Cemetery, id=cemetery_id)
            else:
                cemetery = Cemetery.objects.first()
            
            burial_request = form.save(commit=False)
            burial_request.user = request.user
            burial_request.cemetery = cemetery
            burial_request.latitude = float(latitude)
            burial_request.longitude = float(longitude)
            burial_request.save()
            
            return JsonResponse({'success': True, 'request_id': burial_request.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Метод не разрешен'}, status=405)


@staff_member_required
def admin_panel(request):
    """Панель администратора"""
    pending_requests = BurialRequest.objects.filter(status='pending').order_by('-created_at')
    
    context = {
        'pending_requests': pending_requests,
    }
    
    return render(request, 'admin_panel.html', context)


@staff_member_required
def process_burial_request(request, request_id):
    """Обработка запроса на добавление захоронения администратором"""
    burial_request = get_object_or_404(BurialRequest, id=request_id)
    
    if burial_request.status != 'pending':
        return JsonResponse({'success': False, 'error': 'Этот запрос уже обработан'}, status=400)
    
    if request.method == 'POST':
        form = BurialRequestAdminForm(request.POST)
        
        if form.is_valid():
            action = form.cleaned_data['action']
            
            if action == 'approve':
                # Создаем новое захоронение
                burial = Burial.objects.create(
                    cemetery=burial_request.cemetery,
                    full_name=burial_request.full_name,
                    birth_date=burial_request.birth_date,
                    death_date=burial_request.death_date,
                    latitude=burial_request.latitude,
                    longitude=burial_request.longitude,
                    admin_description=burial_request.description  # Используем описание пользователя как базовое
                )
                
                # Обновляем запрос
                burial_request.status = 'approved'
                burial_request.approved_burial = burial
                burial_request.save()
                
                # Отправляем уведомление пользователю
                send_mail(
                    'Ваш запрос на добавление захоронения одобрен',
                    f'Здравствуйте, {burial_request.user.username}!\n\nВаш запрос на добавление захоронения {burial_request.full_name} был одобрен администратором. '
                    f'Теперь это захоронение доступно на карте кладбища.\n\nС уважением, администрация сайта.',
                    settings.DEFAULT_FROM_EMAIL,
                    [burial_request.user.email],
                    fail_silently=True,
                )
                
                return JsonResponse({'success': True, 'status': 'approved'})
                
            elif action == 'reject':
                rejection_reason = form.cleaned_data.get('rejection_reason', '')
                
                # Обновляем запрос
                burial_request.status = 'rejected'
                burial_request.rejection_reason = rejection_reason
                burial_request.save()
                
                # Отправляем уведомление пользователю
                send_mail(
                    'Ваш запрос на добавление захоронения отклонен',
                    f'Здравствуйте, {burial_request.user.username}!\n\nК сожалению, Ваш запрос на добавление захоронения {burial_request.full_name} был отклонен администратором.\n\n'
                    f'Причина: {rejection_reason or "Причина не указана"}\n\nС уважением, администрация сайта.',
                    settings.DEFAULT_FROM_EMAIL,
                    [burial_request.user.email],
                    fail_silently=True,
                )
                
                return JsonResponse({'success': True, 'status': 'rejected'})
    
    return JsonResponse({'success': False, 'error': 'Некорректный запрос'}, status=400)


@staff_member_required
def add_burial(request):
    """Добавление нового захоронения администратором"""
    if request.method == 'POST':
        form = BurialAdminForm(request.POST)
        if form.is_valid():
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            if not latitude or not longitude:
                return JsonResponse({
                    'success': False,
                    'error': 'Координаты не указаны. Пожалуйста, отметьте место на карте.'
                }, status=400)
            
            cemetery_id = request.POST.get('cemetery_id')
            if cemetery_id:
                cemetery = get_object_or_404(Cemetery, id=cemetery_id)
            else:
                cemetery = Cemetery.objects.first()
            
            burial = form.save(commit=False)
            burial.cemetery = cemetery
            burial.latitude = float(latitude)
            burial.longitude = float(longitude)
            burial.save()
            
            return JsonResponse({'success': True, 'burial_id': burial.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Метод не разрешен'}, status=405)


# API VIEWS

class CemeteryViewSet(viewsets.ModelViewSet):
    """API для работы с кладбищами"""
    queryset = Cemetery.objects.all()
    serializer_class = CemeterySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()


class BurialViewSet(viewsets.ModelViewSet):
    """API для работы с захоронениями"""
    queryset = Burial.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BurialListSerializer
        elif self.action == 'retrieve':
            return BurialDetailSerializer
        return BurialSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по кладбищу
        cemetery_id = self.request.query_params.get('cemetery_id')
        if cemetery_id:
            queryset = queryset.filter(cemetery_id=cemetery_id)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', '')
        birth_date_from = request.query_params.get('birth_date_from')
        birth_date_to = request.query_params.get('birth_date_to')
        death_date_from = request.query_params.get('death_date_from')
        death_date_to = request.query_params.get('death_date_to')
        favorites_only = request.query_params.get('favorites_only') == 'true'
        cemetery_id = request.query_params.get('cemetery_id')
        
        filters = Q()
        
        if query:
            filters &= Q(full_name__icontains=query)
        
        if birth_date_from:
            filters &= Q(birth_date__gte=birth_date_from)
        
        if birth_date_to:
            filters &= Q(birth_date__lte=birth_date_to)
        
        if death_date_from:
            filters &= Q(death_date__gte=death_date_from)
        
        if death_date_to:
            filters &= Q(death_date__lte=death_date_to)
        
        if cemetery_id:
            filters &= Q(cemetery_id=cemetery_id)
        
        queryset = self.get_queryset().filter(filters)
        
        if favorites_only and request.user.is_authenticated:
            favorite_burials = FavoriteBurial.objects.filter(user=request.user).values_list('burial_id', flat=True)
            queryset = queryset.filter(id__in=favorite_burials)
        
        serializer = BurialListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class UserNoteViewSet(viewsets.ModelViewSet):
    """API для работы с заметками пользователей"""
    serializer_class = UserNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return UserNote.objects.all()
        return UserNote.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteBurialViewSet(viewsets.ModelViewSet):
    """API для работы с избранными захоронениями"""
    serializer_class = FavoriteBurialSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return FavoriteBurial.objects.all()
        return FavoriteBurial.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        burial_id = request.data.get('burial_id')
        if not burial_id:
            return Response({'error': 'burial_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            burial = Burial.objects.get(id=burial_id)
        except Burial.DoesNotExist:
            return Response({'error': 'Burial not found'}, status=status.HTTP_404_NOT_FOUND)
        
        favorite, created = FavoriteBurial.objects.get_or_create(
            user=request.user,
            burial=burial
        )
        
        if not created:
            favorite.delete()
            return Response({'is_favorite': False})
        
        return Response({'is_favorite': True})


class BurialRequestViewSet(viewsets.ModelViewSet):
    """API для работы с запросами на добавление захоронений"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.user.is_staff:
            return BurialRequestAdminSerializer
        return BurialRequestSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return BurialRequest.objects.all()
        return BurialRequest.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        burial_request = self.get_object()
        
        if burial_request.status != 'pending':
            return Response({'error': 'This request has already been processed'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Создаем новое захоронение
        burial = Burial.objects.create(
            cemetery=burial_request.cemetery,
            full_name=burial_request.full_name,
            birth_date=burial_request.birth_date,
            death_date=burial_request.death_date,
            latitude=burial_request.latitude,
            longitude=burial_request.longitude,
            admin_description=burial_request.description
        )
        
        # Обновляем запрос
        burial_request.status = 'approved'
        burial_request.approved_burial = burial
        burial_request.save()
        
        # Отправляем уведомление пользователю
        send_mail(
            'Ваш запрос на добавление захоронения одобрен',
            f'Здравствуйте, {burial_request.user.username}!\n\nВаш запрос на добавление захоронения {burial_request.full_name} был одобрен администратором. '
            f'Теперь это захоронение доступно на карте кладбища.\n\nС уважением, администрация сайта.',
            settings.DEFAULT_FROM_EMAIL,
            [burial_request.user.email],
            fail_silently=True,
        )
        
        return Response({'status': 'approved', 'burial_id': burial.id})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        burial_request = self.get_object()
        
        if burial_request.status != 'pending':
            return Response({'error': 'This request has already been processed'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        rejection_reason = request.data.get('rejection_reason', '')
        
        # Обновляем запрос
        burial_request.status = 'rejected'
        burial_request.rejection_reason = rejection_reason
        burial_request.save()
        
        # Отправляем уведомление пользователю
        send_mail(
            'Ваш запрос на добавление захоронения отклонен',
            f'Здравствуйте, {burial_request.user.username}!\n\nК сожалению, Ваш запрос на добавление захоронения {burial_request.full_name} был отклонен администратором.\n\n'
            f'Причина: {rejection_reason or "Причина не указана"}\n\nС уважением, администрация сайта.',
            settings.DEFAULT_FROM_EMAIL,
            [burial_request.user.email],
            fail_silently=True,
        )
        
        return Response({'status': 'rejected'})
