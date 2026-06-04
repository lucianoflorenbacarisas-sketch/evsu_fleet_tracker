from django.urls import path
from . import views

urlpatterns = [

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    path(
        'redirect-dashboard/',
        views.redirect_dashboard,
        name='redirect_dashboard'
    ),

    path(
        'manager-dashboard/',
        views.manager_dashboard,
        name='manager_dashboard'
    ),

    path(
        'staff-dashboard/',
        views.staff_dashboard,
        name='staff_dashboard'
    ),

    path(
        'auditor-dashboard/',
        views.auditor_dashboard,
        name='auditor_dashboard'
    ),

    path(
        'driver-dashboard/',
        views.driver_dashboard,
        name='driver_dashboard'
    ),

    path(
        'maintenance/',
        views.maintenance_page,
        name='maintenance'
    ),

    # ASSETS

    path(
        'assets/',
        views.assets_page,
        name='assets'
    ),

    path(
        'add-asset/',
        views.add_asset,
        name='add_asset'
    ),

    path(
        'edit-asset/<int:id>/',
        views.edit_asset,
        name='edit_asset'
    ),

    path(
        'delete-asset/<int:id>/',
        views.delete_asset,
        name='delete_asset'
    ),

    # MAINTENANCE

    path(
        'create-maintenance/',
        views.create_maintenance,
        name='create_maintenance'
    ),

    path(
        'approve-request/<int:id>/',
        views.approve_request,
        name='approve_request'
    ),

    path(
        'reject-request/<int:id>/',
        views.reject_request,
        name='reject_request'
    ),

    path(
        'complete-request/<int:id>/',
        views.complete_request,
        name='complete_request'
    ),

    # ACTIVITY LOGS

    path(
        'activity-logs/',
        views.activity_logs,
        name='activity_logs'
    ),

    # PDF EXPORT

    path(
        'export-assets-pdf/',
        views.export_assets_pdf,
        name='export_assets_pdf'
    ),

]