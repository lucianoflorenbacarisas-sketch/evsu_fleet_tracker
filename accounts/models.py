from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):

    ROLE_CHOICES = (

        ('STAFF', 'Staff'),

        ('AUDITOR', 'Auditor'),

        ('MANAGER', 'Manager'),

        ('DRIVER', 'Driver'),

    )



    role = models.CharField(

        max_length=20,

        choices=ROLE_CHOICES,

        default='STAFF'

    )




class Asset(models.Model):

    STATUS_CHOICES = (

        ('ACTIVE', 'Active'),

        ('MAINTENANCE', 'Maintenance'),

    )



    TYPE_CHOICES = (

        ('IT', 'IT Equipment'),

        ('OFFICE', 'Office Equipment'),

        ('VEHICLE', 'Vehicle'),

        ('FURNITURE', 'Furniture'),

    )



    name = models.CharField(
        max_length=200
    )



    asset_type = models.CharField(

        max_length=20,

        choices=TYPE_CHOICES

    )



    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default='ACTIVE'

    )



    assigned_to = models.CharField(

        max_length=200,

        blank=True,

        null=True

    )



    created_at = models.DateTimeField(
        auto_now_add=True
    )



    def __str__(self):
        return f"{self.asset_name} - {self.status}"