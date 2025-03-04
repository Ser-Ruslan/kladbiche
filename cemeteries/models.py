from django.db import models
from users.models import User


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