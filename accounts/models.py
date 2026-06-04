"""
Accounts App Models

This module defines user authentication models for the Fleet Tracker system.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with role-based access control.
    """

    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('FLEET_MANAGER', 'Fleet Manager'),
        ('STAFF', 'Staff'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='STAFF',
        help_text='User role for access control'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        help_text='Timestamp when the user account was created'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
