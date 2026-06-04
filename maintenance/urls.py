from django.urls import path

from . import views



urlpatterns = [

    path(
        'update-maintenance-status/<int:id>/',
        views.update_maintenance_status,
        name='update_maintenance_status'
    ),

]