
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    USER_ROLES = (
        ('ADMIN', 'Administrator'),
        ('MODERATOR', 'Moderator'),
        ('USER', 'User'),
        ('GUEST', 'Guest')
    )
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='USER')
    created_at = models.DateTimeField(auto_now_add=True)

    def create_modification_request(self, cemetery_object, request_type, description):
        return ObjectModificationRequest.objects.create(
            object=cemetery_object,
            request_type=request_type,
            description=description,
            updated_by=self
        )

    def search_objects(self, criteria):
        # Реализация поиска объектов по критериям
        return CemeteryObject.objects.filter(**criteria)

class Cemetery(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)  # Можно заменить на GeoDjango Point
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_all_objects(self):
        return self.cemeteryobject_set.all()

    def get_map(self):
        return self.map

class Coordinates(models.Model):
    x_points = models.JSONField()  # Хранение списка координат X
    y_points = models.JSONField()  # Хранение списка координат Y

    def add_point(self, x, y):
        self.x_points.append(x)
        self.y_points.append(y)
        self.save()

    def remove_point(self, index):
        self.x_points.pop(index)
        self.y_points.pop(index)
        self.save()

    def get_point(self, index):
        return (self.x_points[index], self.y_points[index])

    def get_all_points(self):
        return list(zip(self.x_points, self.y_points))

class Photo(models.Model):
    url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class CemeteryObject(models.Model):
    OBJECT_TYPES = (
        ('GRAVE', 'Grave'),
        ('MONUMENT', 'Monument'),
        ('MEMORIAL', 'Memorial'),
        ('CHAPEL', 'Chapel'),
        ('OTHER', 'Other')
    )

    OBJECT_STATUSES = (
        ('ACTIVE', 'Active'),
        ('ARCHIVED', 'Archived'),
        ('PENDING_REVIEW', 'Pending Review'),
        ('DELETED', 'Deleted')
    )

    cemetery = models.ForeignKey(Cemetery, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    coordinates = models.OneToOneField(Coordinates, on_delete=models.CASCADE)
    description = models.TextField()
    photos = models.ManyToManyField(Photo)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=OBJECT_STATUSES, default='ACTIVE')

    def update_info(self, info):
        for key, value in info.items():
            setattr(self, key, value)
        self.save()

    def add_photo(self, photo):
        self.photos.add(photo)

class ObjectModificationRequest(models.Model):
    REQUEST_TYPES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete')
    )

    REQUEST_STATUSES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    )

    object = models.ForeignKey(CemeteryObject, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    status = models.CharField(max_length=20, choices=REQUEST_STATUSES, default='PENDING')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def approve(self):
        self.status = 'APPROVED'
        self.save()

    def reject(self):
        self.status = 'REJECTED'
        self.save()

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