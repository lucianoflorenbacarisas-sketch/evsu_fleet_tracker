"""
Core App Configuration

Main business logic app for Fleet and Asset Tracking System.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Fleet & Asset Management'
