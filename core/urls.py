"""
Core App URL Configuration

Maps all core app views to their respective URLs.
"""

from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    # Dashboard & Reporting
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/fleet/', views.ReportView.as_view(), name='report_fleet'),
    
    # Vehicle Management
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle_list'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle_detail'),
    path('vehicles/create/', views.VehicleCreateView.as_view(), name='vehicle_create'),
    path('vehicles/<int:pk>/update/', views.VehicleUpdateView.as_view(), name='vehicle_update'),
    path('vehicles/<int:pk>/delete/', views.VehicleDeleteView.as_view(), name='vehicle_delete'),
    
    # Asset Management
    path('assets/', views.AssetListView.as_view(), name='asset_list'),
    path('assets/<int:pk>/', views.AssetDetailView.as_view(), name='asset_detail'),
    path('assets/create/', views.AssetCreateView.as_view(), name='asset_create'),
    path('assets/<int:pk>/update/', views.AssetUpdateView.as_view(), name='asset_update'),
    path('assets/<int:pk>/delete/', views.AssetDeleteView.as_view(), name='asset_delete'),
    
    # Maintenance Management
    path('maintenance/', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('maintenance/<int:pk>/', views.MaintenanceDetailView.as_view(), name='maintenance_detail'),
    path('maintenance/create/', views.MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('maintenance/<int:pk>/update/', views.MaintenanceUpdateView.as_view(), name='maintenance_update'),
    
    # Fuel Log Management
    path('fuel-logs/', views.FuelLogListView.as_view(), name='fuellog_list'),
    path('fuel-logs/<int:pk>/', views.FuelLogDetailView.as_view(), name='fuellog_detail'),
    path('fuel-logs/create/', views.FuelLogCreateView.as_view(), name='fuellog_create'),
    
    # Driver Management
    path('drivers/', views.DriverListView.as_view(), name='driver_list'),
    path('drivers/<int:pk>/', views.DriverDetailView.as_view(), name='driver_detail'),
    
    # Inspection Management
    path('inspections/', views.InspectionListView.as_view(), name='inspection_list'),
    path('inspections/<int:pk>/', views.InspectionDetailView.as_view(), name='inspection_detail'),
    path('inspections/create/', views.InspectionCreateView.as_view(), name='inspection_create'),
]
