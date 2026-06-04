from django.db import models
from accounts.models import User
from assets.models import Asset


class MaintenanceRequest(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )

    asset_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    issue_description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.asset.name} - {self.status}"


class AuditTrail(models.Model):

    user = models.CharField(
        max_length=255
    )

    action = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user