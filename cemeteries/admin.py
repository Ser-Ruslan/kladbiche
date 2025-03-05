from django.contrib import admin

from cemeteries.models import Cemetery, CemeteryObject, Coordinates, Photo
from maps.models import Boundaries, MapLayer, Map
from notifications.models import ObjectModificationRequest
#from users.models import User


# Register your models here.

admin.site.register(Cemetery)
admin.site.register(Coordinates)
admin.site.register(Photo)
admin.site.register(CemeteryObject)

admin.site.register(Boundaries)
admin.site.register(MapLayer)
admin.site.register(Map)

admin.site.register(ObjectModificationRequest)

#admin.site.register(User)