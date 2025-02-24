from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Инициализация SQLAlchemy
db = SQLAlchemy()

# Перечисления (Enums) для типов, статусов и ролей
class ObjectStatus(Enum):
    PENDING = 'pending'
    ACTIVE = 'active'
    REVIEW = 'review'
    DELETED = 'deleted'

class LayerType(Enum):
    BASE = 'base'
    GRAVES = 'graves'
    MONUMENTS = 'monuments'
    INFRASTRUCTURE = 'infrastructure'
    PATHS = 'paths'
    VEGETATION = 'vegetation'
    CUSTOM = 'custom'

class VisibilityType(Enum):
    PRIVATE = 'private'
    PUBLIC = 'public'
    SHARED = 'shared'

class NotificationStatus(Enum):
    PENDING = 'pending'
    SENT = 'sent'
    READ = 'read'
    CANCELLED = 'cancelled'

class Priority(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'

class NotificationType(Enum):
    REMINDER = 'reminder'
    SYSTEM_MESSAGE = 'system_message'
    MAINTENANCE_ALERT = 'maintenance_alert'
    USER_MENTION = 'user_mention'
    SCHEDULE_UPDATE = 'schedule_update'
    TASK_ASSIGNMENT = 'task_assignment'

class UserRole(Enum):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    GUEST = 'guest'

class RequestType(Enum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'

class RequestStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class ObjectType(Enum):
    GRAVE = 'grave'
    MONUMENT = 'monument'
    MEMORIAL = 'memorial'
    CHAPEL = 'chapel'
    OTHER = 'other'

class AttachmentType(Enum):
    PHOTO = 'photo'
    DOCUMENT = 'document'
    AUDIO = 'audio'
    VIDEO = 'video'

# Модели (Models) для Flask-SQLAlchemy
class Cemetery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(200))
    country = db.Column(db.String(50))
    scale = db.Column(db.Float)
    lastUpdated = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(ObjectStatus, values_callable=lambda x: [item.value for item in x]))
    maps = db.relationship('Map', backref='cemetery', lazy=True)

    def __init__(self, name, location, scale):
        self.name = name
        self.location = location
        self.scale = scale

    def getMap(self):
        return self.maps[0] if self.maps else None

    def updateStatus(self, status):
        self.status = status.value  # Используем .value для получения строки из Enum

class Map(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cemetery_id = db.Column(db.Integer, db.ForeignKey('cemetery.id'), nullable=False)
    scale = db.Column(db.Float)
    lastUpdated = db.Column(db.DateTime, default=datetime.utcnow)
    layers = db.relationship('MapLayer', backref='map', lazy=True)

    def __init__(self, cemetery_id, scale):
        self.cemetery_id = cemetery_id
        self.scale = scale

    def addLayer(self, layer):
        self.layers.append(layer)

    def setScale(self, scale):
        self.scale = scale

class MapLayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer, db.ForeignKey('map.id'), nullable=False)
    layerType = db.Column(db.Enum(LayerType, values_callable=lambda x: [item.value for item in x]))
    opacity = db.Column(db.Float)
    objects = db.relationship('CemeteryObject', backref='layer', lazy=True)

    def __init__(self, map_id, layerType, opacity):
        self.map_id = map_id
        self.layerType = layerType.value  # Используем .value для получения строки
        self.opacity = opacity

    def setOpacityValue(self, opacity):
        self.opacity = opacity

class CemeteryObject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    layer_id = db.Column(db.Integer, db.ForeignKey('map_layer.id'))
    objectType = db.Column(db.Enum(ObjectType, values_callable=lambda x: [item.value for item in x]))
    description = db.Column(db.Text)
    x = db.Column(db.Float)  # Встраиваем координаты напрямую
    y = db.Column(db.Float)
    z = db.Column(db.Float, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(ObjectStatus, values_callable=lambda x: [item.value for item in x]), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))

    def __init__(self, layer_id, objectType, description, x, y, z=None, status='pending'):
        self.layer_id = layer_id
        self.objectType = objectType.value  # Используем .value для получения строки
        self.description = description
        self.x = x
        self.y = y
        self.z = z
        self.status = status

    def updateStatus(self, status):
        self.status = status.value  # Используем .value для получения строки из Enum

    def addPhoto(self, photo):
        self.photo_id = photo.id

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    uploadedAt = db.Column(db.DateTime, default=datetime.utcnow)
    uploadedBy_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, url, uploadedBy_id):
        self.url = url
        self.uploadedBy_id = uploadedBy_id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.Enum(UserRole, values_callable=lambda x: [item.value for item in x]))
    notifications = db.relationship('Notification', backref='user', lazy=True)
    objectModificationRequests = db.relationship('ObjectModificationRequest', backref='user', lazy=True)

    def __init__(self, name, email, role):
        self.name = name
        self.email = email
        self.role = role.value  # Используем .value для получения строки

    def createNotification(self, content, priority, notificationType, visibilityType):
        notification = Notification(
            user_id=self.id,
            notificationType=notificationType.value,  # Используем .value
            content=content,
            status='pending',  # Значение по умолчанию
            priority=priority.value,  # Используем .value
            visibilityType=visibilityType.value  # Используем .value
        )
        db.session.add(notification)
        return notification

    def searchObjects(self, criteria):
        return CemeteryObject.query.filter_by(**criteria).all()

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notificationType = db.Column(db.Enum(NotificationType, values_callable=lambda x: [item.value for item in x]))
    content = db.Column(db.String(100))
    status = db.Column(db.Enum(NotificationStatus, values_callable=lambda x: [item.value for item in x]))
    priority = db.Column(db.Enum(Priority, values_callable=lambda x: [item.value for item in x]))
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    visibilityType = db.Column(db.Enum(VisibilityType, values_callable=lambda x: [item.value for item in x]))
    attachments = db.relationship('Attachment', backref='notification', lazy=True)

    def __init__(self, user_id, notificationType, content, status, priority, visibilityType):
        self.user_id = user_id
        self.notificationType = notificationType.value  # Используем .value для получения строки
        self.content = content
        self.status = status.value  # Используем .value
        self.priority = priority.value  # Используем .value
        self.visibilityType = visibilityType.value  # Используем .value

    def send(self):
        self.status = NotificationStatus.SENT.value  # Используем .value

    def cancel(self):
        self.status = NotificationStatus.CANCELLED.value  # Используем .value

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.Integer, db.ForeignKey('notification.id'), nullable=False)
    uri = db.Column(db.String(200))
    attachmentType = db.Column(db.Enum(AttachmentType, values_callable=lambda x: [item.value for item in x]))
    description = db.Column(db.String(100))

    def __init__(self, notification_id, uri, attachmentType, description):
        self.notification_id = notification_id
        self.uri = uri
        self.attachmentType = attachmentType.value  # Используем .value для получения строки
        self.description = description

class Coordinates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float, nullable=True)
    withinBounds = db.Column(db.Boolean, default=False)

    def __init__(self, x, y, z=None):
        self.x = x
        self.y = y
        self.z = z

class Boundaries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    northEast = db.Column(db.String(100))
    southWest = db.Column(db.String(100))
    intersectsOther = db.Column(db.Boolean, default=False)

    def __init__(self, northEast, southWest):
        self.northEast = northEast
        self.southWest = southWest

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(200))
    country = db.Column(db.String(50))

    def __init__(self, latitude, longitude, address, country):
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.country = country

class ObjectModificationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cemeteryObject_id = db.Column(db.Integer, db.ForeignKey('cemetery_object.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requestType = db.Column(db.Enum(RequestType, values_callable=lambda x: [item.value for item in x]))
    description = db.Column(db.String(100))
    status = db.Column(db.Enum(RequestStatus, values_callable=lambda x: [item.value for item in x]))
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, cemeteryObject_id, user_id, requestType, description, status='pending'):
        self.cemeteryObject_id = cemeteryObject_id
        self.user_id = user_id
        self.requestType = requestType.value  # Используем .value
        self.description = description
        self.status = status

    def approve(self):
        self.status = RequestStatus.APPROVED.value  # Используем .value

    def reject(self):
        self.status = RequestStatus.REJECTED.value  # Используем .value
