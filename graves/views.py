from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.conf import settings
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from .models import Grave, PersonalNote, FavoriteGrave, EditProposal
from .forms import GraveForm, PersonalNoteForm, EditProposalForm
from notifications.utils import notify_user, notify_user_about_proposal_status

User = get_user_model()

def map_view(request):
    """
    Главная страница с интерактивной картой
    """
    # Получаем API ключ для Яндекс Карт
    yandex_maps_api_key = settings.YANDEX_MAPS_API_KEY
    
    # Центр карты по умолчанию
    cemetery_center = settings.DEFAULT_CEMETERY_CENTER
    
    # Если пользователь авторизован, получаем его избранные захоронения
    favorite_graves_ids = []
    if request.user.is_authenticated:
        favorite_graves_ids = list(FavoriteGrave.objects.filter(
            user=request.user
        ).values_list('grave_id', flat=True))
    
    context = {
        'yandex_maps_api_key': yandex_maps_api_key,
        'cemetery_center': cemetery_center,
        'favorite_graves_ids': favorite_graves_ids,
    }
    
    return render(request, 'graves/map.html', context)


def grave_detail_ajax(request, grave_id):
    """
    Представление для получения информации о захоронении через AJAX
    """
    grave = get_object_or_404(Grave, id=grave_id)
    
    # Получаем личную заметку пользователя, если он авторизован
    personal_note = None
    is_favorite = False
    
    if request.user.is_authenticated:
        try:
            personal_note = PersonalNote.objects.get(grave=grave, user=request.user)
        except PersonalNote.DoesNotExist:
            pass
        
        # Проверяем, добавлено ли захоронение в избранное
        is_favorite = FavoriteGrave.objects.filter(grave=grave, user=request.user).exists()
    
    context = {
        'grave': grave,
        'personal_note': personal_note,
        'is_favorite': is_favorite,
    }
    
    return render(request, 'graves/grave_detail.html', context)


def search_graves(request):
    """
    Поиск захоронений по ФИО и датам
    """
    query = request.GET.get('query', '')
    birth_date = request.GET.get('birth_date', '')
    death_date = request.GET.get('death_date', '')
    favorites_only = request.GET.get('favorites_only') == 'true'
    
    graves = Grave.objects.all()
    
    # Фильтрация по ФИО
    if query:
        graves = graves.filter(full_name__icontains=query)
    
    # Фильтрация по дате рождения
    if birth_date:
        graves = graves.filter(birth_date=birth_date)
    
    # Фильтрация по дате смерти
    if death_date:
        graves = graves.filter(death_date=death_date)
    
    # Фильтрация по избранному (только для авторизованных пользователей)
    if favorites_only and request.user.is_authenticated:
        favorite_graves_ids = FavoriteGrave.objects.filter(
            user=request.user
        ).values_list('grave_id', flat=True)
        graves = graves.filter(id__in=favorite_graves_ids)
    
    # Преобразуем результаты в формат JSON
    graves_data = []
    for grave in graves:
        graves_data.append({
            'id': grave.id,
            'full_name': grave.full_name,
            'birth_date': grave.birth_date.strftime('%d.%m.%Y') if grave.birth_date else None,
            'death_date': grave.death_date.strftime('%d.%m.%Y') if grave.death_date else None,
            'polygon': grave.polygon_coordinates,
        })
    
    return JsonResponse({'graves': graves_data})


@login_required
def toggle_favorite(request, grave_id):
    """
    Добавление/удаление захоронения из избранного
    """
    grave = get_object_or_404(Grave, id=grave_id)
    
    favorite, created = FavoriteGrave.objects.get_or_create(
        grave=grave,
        user=request.user
    )
    
    # Если запись существовала, удаляем её
    if not created:
        favorite.delete()
        is_favorite = False
        messages.success(request, 'Захоронение удалено из избранного')
    else:
        is_favorite = True
        messages.success(request, 'Захоронение добавлено в избранное')
    
    # Если запрос AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite})
    
    # Иначе редиректим на страницу с картой
    return redirect('map')


@login_required
def save_personal_note(request, grave_id):
    """
    Сохранение или удаление личной заметки к захоронению
    """
    grave = get_object_or_404(Grave, id=grave_id)
    
    if request.method == 'POST':
        note_text = request.POST.get('note_text', '').strip()
        
        # Если текст пустой, удаляем заметку
        if not note_text:
            # Проверяем существование и удаляем
            try:
                personal_note = PersonalNote.objects.get(grave=grave, user=request.user)
                personal_note.delete()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'deleted': True
                    })
                
                messages.success(request, 'Заметка удалена')
                
                # Проверяем, откуда был запрос
                referer = request.META.get('HTTP_REFERER', '')
                if 'my-notes' in referer:
                    return redirect('my_personal_notes')
                return redirect('map')
                
            except PersonalNote.DoesNotExist:
                pass
        else:
            # Создаем или обновляем заметку
            personal_note, created = PersonalNote.objects.update_or_create(
                grave=grave,
                user=request.user,
                defaults={'text': note_text}
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'created': created,
                    'note_text': personal_note.text
                })
            
            messages.success(request, 'Заметка сохранена')
            
            # Проверяем, откуда был запрос
            referer = request.META.get('HTTP_REFERER', '')
            if 'my-notes' in referer:
                return redirect('my_personal_notes')
            return redirect('map')
    
    return HttpResponseForbidden()


@login_required
def submit_edit_proposal(request, grave_id):
    """
    Отправка предложения по редактированию описания захоронения
    """
    print(f"Получен запрос на редактирование захоронения {grave_id}")
    grave = get_object_or_404(Grave, id=grave_id)
    
    if request.method == 'POST':
        # Проверяем, как приходят данные (через форму или напрямую в теле запроса)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            print(f"Получен AJAX запрос: {request.POST}")
            # Для AJAX запросов создаем данные формы
            form_data = {'proposed_description': request.POST.get('proposed_description', '')}
            form = EditProposalForm({'proposed_description': form_data['proposed_description']})
        else:
            form = EditProposalForm(request.POST)
        
        print(f"Форма создана, валидация: {form.is_valid()}")
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.grave = grave
            proposal.user = request.user
            proposal.save()
            print(f"Предложение сохранено: {proposal.id}")
            
            # Отправляем уведомление администраторам
            admin_users = User.objects.filter(role='admin', is_active=True)
            for admin in admin_users:
                notify_user(
                    user=admin,
                    notification_type='edit_proposal',
                    message=f'Новое предложение редактирования для захоронения {grave.full_name}',
                    related_id=proposal.id
                )
            
            messages.success(request, 'Ваше предложение отправлено на рассмотрение')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            return redirect('map')
        else:
            print(f"Ошибки формы: {form.errors}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    return HttpResponseForbidden()


@method_decorator(login_required, name='dispatch')
class FavoriteGravesListView(ListView):
    """
    Список избранных захоронений пользователя
    """
    model = FavoriteGrave
    template_name = 'graves/favorites_list.html'
    context_object_name = 'favorites'
    
    def get_queryset(self):
        return FavoriteGrave.objects.filter(user=self.request.user)


@method_decorator(login_required, name='dispatch')
class MyEditProposalsListView(ListView):
    """
    Список предложений редактирования пользователя
    """
    model = EditProposal
    template_name = 'graves/my_proposals.html'
    context_object_name = 'proposals'
    
    def get_queryset(self):
        return EditProposal.objects.filter(user=self.request.user).select_related('grave')


@method_decorator(login_required, name='dispatch')
class EditProposalDetailView(DetailView):
    """
    Подробная информация о предложении редактирования
    """
    model = EditProposal
    template_name = 'graves/edit_proposal_detail.html'
    context_object_name = 'proposal'
    
    def get_queryset(self):
        # Обычные пользователи могут просматривать только свои предложения
        if self.request.user.role != 'admin':
            return EditProposal.objects.filter(user=self.request.user).select_related('grave')
        # Администраторы могут просматривать все предложения
        return EditProposal.objects.all().select_related('grave')


@method_decorator(login_required, name='dispatch')
class MyPersonalNotesListView(ListView):
    """
    Список личных заметок пользователя
    """
    model = PersonalNote
    template_name = 'graves/my_personal_notes.html'
    context_object_name = 'notes'
    paginate_by = 10
    
    def get_queryset(self):
        return PersonalNote.objects.filter(user=self.request.user).select_related('grave')


@method_decorator(login_required, name='dispatch')
class AdminEditProposalsListView(ListView):
    """
    Список всех предложений редактирования для администраторов
    """
    model = EditProposal
    template_name = 'graves/admin_proposals_list.html'
    context_object_name = 'proposals'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь - администратор
        if request.user.role != 'admin':
            messages.error(request, 'У вас нет доступа к этой странице')
            return redirect('map')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        # Получаем базовый queryset
        queryset = EditProposal.objects.all().select_related('grave', 'user')
        
        # Применяем фильтры из параметров GET
        status_filter = self.request.GET.get('status')
        if status_filter and status_filter in ['pending', 'approved', 'rejected']:
            queryset = queryset.filter(status=status_filter)
            
        # Сортировка: сначала ожидающие, затем по дате создания (новые - первые)
        from django.db import models
        return queryset.order_by(
            # Первый уровень сортировки: pending в начало
            models.Case(
                models.When(status='pending', then=0),
                default=1,
                output_field=models.IntegerField()
            ),
            # Второй уровень: по дате создания (новые в начало)
            '-created_at'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем информацию о фильтрах
        status_filter = self.request.GET.get('status', '')
        context['status_filter'] = status_filter
        
        # Счетчики статусов
        context['pending_count'] = EditProposal.objects.filter(status='pending').count()
        context['approved_count'] = EditProposal.objects.filter(status='approved').count()
        context['rejected_count'] = EditProposal.objects.filter(status='rejected').count()
        
        return context
