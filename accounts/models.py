"""
Accounts App Models

This module defines user authentication models for the Fleet Tracker system.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with role-based access control.
    
    Roles:
    - ADMIN: System administrator with full access
    - FLEET_MANAGER: Fleet manager with access to fleet operations
    - STAFF: Staff member with limited access
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
    
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user account is active'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'ADMIN'
    
    def is_fleet_manager(self):
        """Check if user is a fleet manager"""
        return self.role == 'FLEET_MANAGER'
    
    def is_staff_member(self):
        """Check if user is staff"""
        return self.role == 'STAFF'




    created_at = models.DateTimeField(
        auto_now_add=True
    )



    def __str__(self):
        return f"{self.asset_name} - {self.status}"