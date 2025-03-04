from django.db import models
from .cemeteries import Cemetery, CemeteryObject, Coordinates

class Boundaries(models.Model):
    north_east = models.OneToOneField(Coordinates, on_delete=models.CASCADE, related_name='north_east_boundary')
    south_west = models.OneToOneField(Coordinates, on_delete=models.CASCADE, related_name='south_west_boundary')

    def contains(self, point):
        # Реализация проверки, находится ли точка внутри границ
        pass

    def intersects(self, other):
        # Реализация проверки пересечения с другими границами
        pass

class Map(models.Model):
    cemetery = models.OneToOneField(Cemetery, on_delete=models.CASCADE)
    scale = models.FloatField()
    boundaries = models.OneToOneField(Boundaries, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    def get_objects_in_bounds(self, bounds):
        # Реализация получения объектов в заданных границах
        pass

    def get_scale(self):
        return self.scale

    def set_scale(self, scale):
        self.scale = scale
        self.save()

class MapLayer(models.Model):
    LAYER_TYPES = (
        ('BASE', 'Base'),
        ('GRAVES', 'Graves'),
        ('MONUMENTS', 'Monuments'),
        ('INFRASTRUCTURE', 'Infrastructure'),
        ('PATHS', 'Paths'),
        ('VEGETATION', 'Vegetation'),
        ('CUSTOM', 'Custom')
    )

    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name='layers')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=LAYER_TYPES)
    visible = models.BooleanField(default=True)
    opacity = models.FloatField(default=1.0)
    objects = models.ManyToManyField(CemeteryObject)

    def toggle(self):
        self.visible = not self.visible
        self.save()

    def set_opacity(self, value):
        self.opacity = value
        self.save()