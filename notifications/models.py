from django.db import models
from users.models import User
from cemeteries.models import CemeteryObject

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