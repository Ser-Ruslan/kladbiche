from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from cemeteries.models import Cemetery, CemeteryObject, Coordinates
from .models import Map, MapLayer, Boundaries
from django.contrib.auth.mixins import LoginRequiredMixin
import json


# ===== COORDINATES =====
class CoordinatesListView(ListView):
    model = Coordinates
    template_name = 'maps/coordinates_list.html'
    context_object_name = 'coordinates'


class CoordinatesDetailView(DetailView):
    model = Coordinates
    template_name = 'maps/coordinates_detail.html'
    context_object_name = 'coordinate'


class CoordinatesAddPointView(View):
    """Добавление координаты (точки)"""
    def post(self, request, pk):
        data = json.loads(request.body)
        lat = data.get('latitude')
        lon = data.get('longitude')
        if not lat or not lon:
            return JsonResponse({"error": "Latitude and longitude are required"}, status=400)

        coordinate = get_object_or_404(Coordinates, pk=pk)
        # Предполагается, что у Coordinates должна быть структура для хранения дополнительных точек
        coordinate.points.append({'latitude': lat, 'longitude': lon})
        coordinate.save()
        return JsonResponse({"message": "Coordinate added successfully"})


class CoordinatesRemovePointView(View):
    """Удаление точки координат"""
    def delete(self, request, pk, point_index):
        coordinate = get_object_or_404(Coordinates, pk=pk)
        try:
            coordinate.points.pop(point_index)
            coordinate.save()
            return JsonResponse({"message": "Point removed successfully"})
        except IndexError:
            return JsonResponse({"error": "Invalid point index"}, status=400)


# ===== CEMETERY MAP =====
class CemeteryMapView(DetailView):
    """Визуализация карты кладбища"""
    model = Cemetery
    template_name = 'maps/cemetery_map.html'
    context_object_name = 'cemetery'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cemetery = self.object
        try:
            cemetery_map = cemetery.map
            context['map'] = cemetery_map
            context['layers'] = cemetery_map.layers.all()
        except Map.DoesNotExist:
            context['map'] = None
            context['layers'] = []
        return context


class CemeteryMapObjectsView(View):
    """Получение объектов в заданных границах"""
    def get(self, request, cemetery_id):
        cemetery = get_object_or_404(Cemetery, pk=cemetery_id)
        try:
            cemetery_map = cemetery.map
            boundaries = cemetery_map.boundaries
        except Map.DoesNotExist:
            return JsonResponse({"error": "No map found for this cemetery"}, status=404)

        objects_in_bounds = cemetery_map.get_objects_in_bounds(boundaries)
        return JsonResponse({"objects": [obj.id for obj in objects_in_bounds]})


class RenderCemeteryMapView(View):
    """Генерация JSON данных для карты"""
    def get(self, request, cemetery_id):
        cemetery = get_object_or_404(Cemetery, pk=cemetery_id)
        try:
            cemetery_map = cemetery.map
            boundaries = cemetery_map.boundaries
        except Map.DoesNotExist:
            return JsonResponse({"error": "No map found for this cemetery"}, status=404)

        data = {
            "cemetery": cemetery.id,
            "boundaries": {
                "north_east": {
                    "latitude": boundaries.north_east.latitude,
                    "longitude": boundaries.north_east.longitude,
                },
                "south_west": {
                    "latitude": boundaries.south_west.latitude,
                    "longitude": boundaries.south_west.longitude,
                },
            },
            "layers": [
                {
                    "id": layer.id,
                    "name": layer.name,
                    "type": layer.type,
                    "visible": layer.visible,
                    "opacity": layer.opacity,
                }
                for layer in cemetery_map.layers.all()
            ],
        }
        return JsonResponse(data)


class SearchOnMapView(View):
    """Поиск объектов на карте"""
    def get(self, request, cemetery_id):
        query = request.GET.get('query')
        if not query:
            return JsonResponse({"error": "Search query is required"}, status=400)

        cemetery = get_object_or_404(Cemetery, pk=cemetery_id)
        try:
            cemetery_map = cemetery.map
        except Map.DoesNotExist:
            return JsonResponse({"error": "No map found for this cemetery"}, status=404)

        # Пример простого поиска по имени объектов
        matching_objects = cemetery_map.layers.filter(objects__name__icontains=query).distinct()
        results = [
            {
                "id": obj.id,
                "name": obj.name,
                "layer": obj.layer.name,
            }
            for obj in matching_objects
        ]
        return JsonResponse({"results": results})


# ===== MAPLAYER =====
class MapLayerToggleView(View):
    """Скрыть/показать слой"""
    def post(self, request, layer_id):
        layer = get_object_or_404(MapLayer, pk=layer_id)
        layer.toggle()
        return JsonResponse({"message": "Layer visibility toggled"})


class MapLayerSetOpacityView(View):
    """Изменение прозрачности слоя"""
    def post(self, request, layer_id):
        layer = get_object_or_404(MapLayer, pk=layer_id)
        data = json.loads(request.body)
        opacity = data.get('opacity')
        if not 0 <= opacity <= 1:
            return JsonResponse({"error": "Opacity must be a value between 0 and 1"}, status=400)

        layer.set_opacity(opacity)
        return JsonResponse({"message": "Opacity updated successfully"})