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

from api.serializers import User

from .models import Grave, PersonalNote, FavoriteGrave, EditProposal
from .forms import GraveForm, PersonalNoteForm, EditProposalForm
from notifications.utils import create_notification

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
    Сохранение личной заметки к захоронению
    """
    grave = get_object_or_404(Grave, id=grave_id)
    
    if request.method == 'POST':
        note_text = request.POST.get('note_text', '')
        
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
        return redirect('map')
    
    return HttpResponseForbidden()


@login_required
def submit_edit_proposal(request, grave_id):
    """
    Отправка предложения по редактированию описания захоронения
    """
    grave = get_object_or_404(Grave, id=grave_id)
    
    if request.method == 'POST':
        form = EditProposalForm(request.POST)
        
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.grave = grave
            proposal.user = request.user
            proposal.save()
            
            # Отправляем уведомление администраторам
            admin_users = User.objects.filter(role='admin', is_active=True)
            for admin in admin_users:
                create_notification(
                    user=admin,
                    message=f'Новое предложение редактирования для захоронения {grave.full_name}',
                    notification_type='edit_proposal',
                    related_id=proposal.id
                )
            
            messages.success(request, 'Ваше предложение отправлено на рассмотрение')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            return redirect('map')
        else:
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
