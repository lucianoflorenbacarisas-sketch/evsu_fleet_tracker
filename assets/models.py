from django.db import models
from accounts.models import User
from django.utils import timezone


class Asset(models.Model):

    image = models.ImageField(
        upload_to='assets/',
        null=True,
        blank=True
    )

    TYPE_CHOICES = (
        ('VEHICLE', 'Vehicle'),
        ('IT', 'IT Equipment'),
        ('OFFICE', 'Office Equipment'),
    )

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('MAINTENANCE', 'Maintenance'),
        ('INACTIVE', 'Inactive'),
    )

    name = models.CharField(
        max_length=255
    )

    asset_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    assigned_to = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name