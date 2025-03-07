from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.views.generic.edit import FormView
from django.forms.models import model_to_dict
from .models import Cemetery, CemeteryObject, Photo, Coordinates
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'index.html')  # Це путь к корневому шаблону приложухи, в виду особенностий - просто имя файла

# Модели кладбища
class CemeteryListView(ListView):
    model = Cemetery
    template_name = 'cemeteries/cemetery_list.html'
    context_object_name = 'cemeteries'

class CemeteryDetailView(DetailView):
    model = Cemetery
    template_name = 'cemeteries/cemetery_detail.html'
    context_object_name = 'cemetery'

class CemeteryCreateView(LoginRequiredMixin, CreateView):
    model = Cemetery
    fields = ['name', 'location', 'description']
    template_name = 'cemeteries/cemetery_form.html'
    success_url = reverse_lazy('cemeteries:cemetery_list')

    def form_valid(self, form):
        return super().form_valid(form)

class CemeteryUpdateView(LoginRequiredMixin, UpdateView):
    model = Cemetery
    fields = ['name', 'location', 'description']
    template_name = 'cemeteries/cemetery_form.html'

    def get_success_url(self):
        return reverse_lazy('cemeteries:cemetery_detail', kwargs={'pk': self.object.pk})

class CemeteryDeleteView(LoginRequiredMixin, DeleteView):
    model = Cemetery
    template_name = 'cemeteries/cemetery_confirm_delete.html'
    success_url = reverse_lazy('cemeteries:cemetery_list')

# Объекты на кладбищах
class CemeteryObjectListView(ListView):
    template_name = 'cemeteries/cemetery_object_list.html'
    context_object_name = 'objects'

    def get_queryset(self):
        cemetery_id = self.kwargs.get('cemetery_id')
        return CemeteryObject.objects.filter(cemetery_id=cemetery_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cemetery'] = get_object_or_404(Cemetery, pk=self.kwargs['cemetery_id'])
        return context

class CemeteryObjectDetailView(DetailView):
    model = CemeteryObject
    template_name = 'cemeteries/cemetery_object_detail.html'
    context_object_name = 'cemetery_object'

class CemeteryObjectCreateView(LoginRequiredMixin, CreateView):
    model = CemeteryObject
    fields = ['type', 'coordinates', 'description', 'status']
    template_name = 'cemeteries/cemetery_object_form.html'

    def form_valid(self, form):
        cemetery_id = self.kwargs.get('cemetery_id')
        form.instance.cemetery = get_object_or_404(Cemetery, pk=cemetery_id)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cemeteries:cemetery_object_list', kwargs={'cemetery_id': self.kwargs['cemetery_id']})

class CemeteryObjectUpdateView(LoginRequiredMixin, UpdateView):
    model = CemeteryObject
    fields = ['type', 'coordinates', 'description', 'status']
    template_name = 'cemeteries/cemetery_object_form.html'

    def get_success_url(self):
        return reverse_lazy('cemetery_object_detail', kwargs={'pk': self.object.pk})

class CemeteryObjectStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        cemetery_object = get_object_or_404(CemeteryObject, pk=pk)

        if not request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to update status.")

        new_status = request.POST.get('status')
        if new_status in dict(CemeteryObject.OBJECT_STATUSES):
            cemetery_object.status = new_status
            cemetery_object.save()
            return JsonResponse({'status': 'success', 'new_status': cemetery_object.status})
        return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)

# Фотографии
class PhotoUploadView(LoginRequiredMixin, CreateView):
    model = Photo
    fields = ['url']
    template_name = 'cemeteries/photo_upload_form.html'

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cemeteries:photo_upload')

class ObjectPhotoListView(ListView):
    template_name = 'cemeteries/object_photo_list.html'
    context_object_name = 'photos'

    def get_queryset(self):
        object_id = self.kwargs.get('object_id')
        cemetery_object = get_object_or_404(CemeteryObject, pk=object_id)
        return cemetery_object.photos.all()

class AddPhotoToObjectView(LoginRequiredMixin, View):
    def post(self, request, object_id):
        cemetery_object = get_object_or_404(CemeteryObject, pk=object_id)

        photo_id = request.POST.get('photo_id')
        photo = get_object_or_404(Photo, pk=photo_id)

        cemetery_object.photos.add(photo)
        return JsonResponse({'status': 'success'})