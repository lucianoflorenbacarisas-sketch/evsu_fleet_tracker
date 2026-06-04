"""
Core App Views

Views for Fleet and Asset Tracking System including:
- Dashboard and reporting
- Vehicle management
- Asset management
- Maintenance tracking
- Fuel logging
- Driver management
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
    TemplateView, FormView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from core.models import (
    Vehicle, Driver, Asset, MaintenanceRecord, FuelLog,
    InspectionRecord, DriverAssignment
)


# ============================================================================
# PERMISSION CHECKS
# ============================================================================

def is_admin_or_manager(user):
    """Check if user is admin or fleet manager"""
    return user.is_authenticated and user.role in ['ADMIN', 'FLEET_MANAGER']


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.role == 'ADMIN'


class AdminOrManagerRequiredMixin(UserPassesTestMixin):
    """Mixin to check admin or manager role"""
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'FLEET_MANAGER']
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('dashboard')


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to check admin role"""
    def test_func(self):
        return self.request.user.role == 'ADMIN'
    
    def handle_no_permission(self):
        messages.error(self.request, 'Only administrators can access this page.')
        return redirect('dashboard')


# ============================================================================
# DASHBOARD & REPORTING
# ============================================================================

@login_required
def dashboard(request):
    """Main dashboard view with key metrics"""
    context = {
        'total_vehicles': Vehicle.objects.count(),
        'active_vehicles': Vehicle.objects.filter(status='ACTIVE').count(),
        'vehicles_in_maintenance': Vehicle.objects.filter(status='MAINTENANCE').count(),
        'total_drivers': Driver.objects.count(),
        'total_assets': Asset.objects.count(),
        'active_assets': Asset.objects.filter(status='ACTIVE').count(),
        'overdue_maintenance': MaintenanceRecord.objects.filter(
            status__in=['SCHEDULED', 'IN_PROGRESS'],
            scheduled_date__lt=timezone.now().date()
        ).count(),
        'upcoming_maintenance': MaintenanceRecord.objects.filter(
            status='SCHEDULED',
            scheduled_date__gte=timezone.now().date(),
            scheduled_date__lte=timezone.now().date() + timedelta(days=30)
        ).count(),
    }
    
    # Fuel consumption last 30 days
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    fuel_logs = FuelLog.objects.filter(refuel_date__gte=thirty_days_ago)
    context['fuel_cost_30_days'] = fuel_logs.aggregate(Sum('total_cost'))['total_cost__sum'] or Decimal('0.00')
    context['fuel_liters_30_days'] = fuel_logs.aggregate(Sum('quantity_liters'))['quantity_liters__sum'] or Decimal('0.00')
    
    # Recent maintenance
    context['recent_maintenance'] = MaintenanceRecord.objects.select_related(
        'vehicle', 'maintenance_type'
    ).order_by('-scheduled_date')[:5]
    
    # Vehicle utilization
    active_assignments = DriverAssignment.objects.filter(unassigned_date__isnull=True).count()
    context['vehicle_utilization'] = round(
        (active_assignments / max(Vehicle.objects.count(), 1)) * 100, 2
    ) if Vehicle.objects.count() > 0 else 0
    
    return render(request, 'core/dashboard.html', context)


class ReportView(LoginRequiredMixin, TemplateView):
    """Fleet operations report"""
    template_name = 'core/report_fleet.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Vehicle metrics
        vehicles = Vehicle.objects.all()
        context['vehicles_by_status'] = vehicles.values('status').annotate(count=Count('id'))
        context['vehicles_by_type'] = vehicles.values('vehicle_type__name').annotate(count=Count('id'))
        
        # Maintenance metrics
        maintenance = MaintenanceRecord.objects.all()
        context['maintenance_by_status'] = maintenance.values('status').annotate(count=Count('id'))
        context['total_maintenance_cost'] = maintenance.aggregate(Sum('cost'))['cost__sum'] or Decimal('0.00')
        
        # Asset metrics
        assets = Asset.objects.all()
        context['assets_by_status'] = assets.values('status').annotate(count=Count('id'))
        context['total_asset_value'] = assets.aggregate(Sum('current_value'))['current_value__sum'] or Decimal('0.00')
        
        # Fuel metrics
        fuel_logs = FuelLog.objects.all()
        context['total_fuel_cost'] = fuel_logs.aggregate(Sum('total_cost'))['total_cost__sum'] or Decimal('0.00')
        context['total_fuel_liters'] = fuel_logs.aggregate(Sum('quantity_liters'))['quantity_liters__sum'] or Decimal('0.00')
        
        return context


# ============================================================================
# VEHICLE MANAGEMENT
# ============================================================================

class VehicleListView(LoginRequiredMixin, ListView):
    """List all vehicles"""
    model = Vehicle
    template_name = 'core/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Vehicle.objects.select_related(
            'vehicle_type', 'fuel_type', 'assigned_driver'
        )
        
        # Filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        vehicle_type = self.request.GET.get('type')
        if vehicle_type:
            queryset = queryset.filter(vehicle_type_id=vehicle_type)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(registration_number__icontains=search) |
                Q(make__icontains=search) |
                Q(model__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Vehicle.STATUS_CHOICES
        context['vehicle_types'] = Vehicle.objects.values_list(
            'vehicle_type_id', 'vehicle_type__name'
        ).distinct()
        return context


class VehicleDetailView(LoginRequiredMixin, DetailView):
    """Vehicle detail view"""
    model = Vehicle
    template_name = 'core/vehicle_detail.html'
    context_object_name = 'vehicle'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.get_object()
        
        context['maintenance_records'] = vehicle.maintenance_records.all().order_by('-scheduled_date')[:10]
        context['fuel_logs'] = vehicle.fuel_logs.all().order_by('-refuel_date')[:10]
        context['inspections'] = vehicle.inspections.all().order_by('-inspection_date')[:5]
        context['driver_assignments'] = vehicle.driver_assignments.all().order_by('-assigned_date')[:5]
        context['avg_fuel_efficiency'] = self._calculate_avg_fuel_efficiency(vehicle)
        context['total_maintenance_cost'] = vehicle.maintenance_records.aggregate(
            Sum('cost')
        )['cost__sum'] or Decimal('0.00')
        
        return context
    
    def _calculate_avg_fuel_efficiency(self, vehicle):
        """Calculate average fuel efficiency for vehicle"""
        fuel_logs = vehicle.fuel_logs.all().order_by('refuel_date')
        efficiencies = []
        
        for log in fuel_logs:
            eff = log.fuel_efficiency()
            if eff:
                efficiencies.append(eff)
        
        return round(sum(efficiencies) / len(efficiencies), 2) if efficiencies else None


class VehicleCreateView(AdminOrManagerRequiredMixin, CreateView):
    """Create new vehicle"""
    model = Vehicle
    template_name = 'core/vehicle_form.html'
    fields = [
        'registration_number', 'vin', 'vehicle_type', 'make', 'model',
        'year', 'color', 'fuel_type', 'status', 'purchase_price',
        'purchase_date', 'current_value'
    ]
    success_url = reverse_lazy('vehicle_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Vehicle added successfully.')
        return super().form_valid(form)


class VehicleUpdateView(AdminOrManagerRequiredMixin, UpdateView):
    """Update vehicle information"""
    model = Vehicle
    template_name = 'core/vehicle_form.html'
    fields = [
        'registration_number', 'vin', 'vehicle_type', 'make', 'model',
        'year', 'color', 'fuel_type', 'status', 'current_odometer',
        'purchase_price', 'purchase_date', 'current_value', 'assigned_driver'
    ]
    success_url = reverse_lazy('vehicle_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Vehicle updated successfully.')
        return super().form_valid(form)


class VehicleDeleteView(AdminRequiredMixin, DeleteView):
    """Delete vehicle"""
    model = Vehicle
    template_name = 'core/vehicle_confirm_delete.html'
    success_url = reverse_lazy('vehicle_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Vehicle deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# ASSET MANAGEMENT
# ============================================================================

class AssetListView(LoginRequiredMixin, ListView):
    """List all assets"""
    model = Asset
    template_name = 'core/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Asset.objects.select_related('category', 'assigned_to')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(asset_code__icontains=search) |
                Q(name__icontains=search) |
                Q(location__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Asset.STATUS_CHOICES
        context['categories'] = Asset.objects.values_list(
            'category_id', 'category__name'
        ).distinct()
        context['total_value'] = Asset.objects.aggregate(
            Sum('current_value')
        )['current_value__sum'] or Decimal('0.00')
        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    """Asset detail view"""
    model = Asset
    template_name = 'core/asset_detail.html'
    context_object_name = 'asset'


class AssetCreateView(AdminOrManagerRequiredMixin, CreateView):
    """Create new asset"""
    model = Asset
    template_name = 'core/asset_form.html'
    fields = [
        'asset_code', 'name', 'category', 'description',
        'location', 'assigned_to', 'purchase_price',
        'purchase_date', 'current_value', 'status'
    ]
    success_url = reverse_lazy('asset_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Asset added successfully.')
        return super().form_valid(form)


class AssetUpdateView(AdminOrManagerRequiredMixin, UpdateView):
    """Update asset"""
    model = Asset
    template_name = 'core/asset_form.html'
    fields = [
        'asset_code', 'name', 'category', 'description',
        'location', 'assigned_to', 'purchase_price',
        'purchase_date', 'current_value', 'status'
    ]
    success_url = reverse_lazy('asset_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Asset updated successfully.')
        return super().form_valid(form)


class AssetDeleteView(AdminRequiredMixin, DeleteView):
    """Delete asset"""
    model = Asset
    template_name = 'core/asset_confirm_delete.html'
    success_url = reverse_lazy('asset_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Asset deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# MAINTENANCE MANAGEMENT
# ============================================================================

class MaintenanceListView(LoginRequiredMixin, ListView):
    """List maintenance records"""
    model = MaintenanceRecord
    template_name = 'core/maintenance_list.html'
    context_object_name = 'maintenance_records'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = MaintenanceRecord.objects.select_related(
            'vehicle', 'maintenance_type'
        )
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        vehicle = self.request.GET.get('vehicle')
        if vehicle:
            queryset = queryset.filter(vehicle_id=vehicle)
        
        return queryset.order_by('-scheduled_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = MaintenanceRecord.STATUS_CHOICES
        context['overdue'] = MaintenanceRecord.objects.filter(
            status__in=['SCHEDULED', 'IN_PROGRESS'],
            scheduled_date__lt=timezone.now().date()
        ).count()
        return context


class MaintenanceDetailView(LoginRequiredMixin, DetailView):
    """Maintenance record detail"""
    model = MaintenanceRecord
    template_name = 'core/maintenance_detail.html'
    context_object_name = 'record'


class MaintenanceCreateView(AdminOrManagerRequiredMixin, CreateView):
    """Create maintenance record"""
    model = MaintenanceRecord
    template_name = 'core/maintenance_form.html'
    fields = [
        'vehicle', 'maintenance_type', 'status', 'scheduled_date',
        'completed_date', 'description', 'cost', 'vendor', 'odometer_reading', 'notes'
    ]
    success_url = reverse_lazy('maintenance_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Maintenance record created.')
        return super().form_valid(form)


class MaintenanceUpdateView(AdminOrManagerRequiredMixin, UpdateView):
    """Update maintenance record"""
    model = MaintenanceRecord
    template_name = 'core/maintenance_form.html'
    fields = [
        'vehicle', 'maintenance_type', 'status', 'scheduled_date',
        'completed_date', 'description', 'cost', 'vendor', 'odometer_reading', 'notes'
    ]
    success_url = reverse_lazy('maintenance_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Maintenance record updated.')
        return super().form_valid(form)


# ============================================================================
# FUEL LOG MANAGEMENT
# ============================================================================

class FuelLogListView(LoginRequiredMixin, ListView):
    """List fuel logs"""
    model = FuelLog
    template_name = 'core/fuellog_list.html'
    context_object_name = 'fuel_logs'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FuelLog.objects.select_related(
            'vehicle', 'driver', 'fuel_type'
        )
        
        vehicle = self.request.GET.get('vehicle')
        if vehicle:
            queryset = queryset.filter(vehicle_id=vehicle)
        
        return queryset.order_by('-refuel_date')


class FuelLogDetailView(LoginRequiredMixin, DetailView):
    """Fuel log detail"""
    model = FuelLog
    template_name = 'core/fuellog_detail.html'
    context_object_name = 'log'


class FuelLogCreateView(AdminOrManagerRequiredMixin, CreateView):
    """Create fuel log"""
    model = FuelLog
    template_name = 'core/fuellog_form.html'
    fields = [
        'vehicle', 'driver', 'refuel_date', 'refuel_time',
        'fuel_type', 'quantity_liters', 'cost_per_liter',
        'total_cost', 'refuel_location', 'odometer_reading', 'notes'
    ]
    success_url = reverse_lazy('fuellog_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Fuel log created.')
        return super().form_valid(form)


# ============================================================================
# DRIVER MANAGEMENT
# ============================================================================

class DriverListView(LoginRequiredMixin, ListView):
    """List drivers"""
    model = Driver
    template_name = 'core/driver_list.html'
    context_object_name = 'drivers'
    paginate_by = 20
    
    def get_queryset(self):
        return Driver.objects.select_related('user').order_by('user__last_name')


class DriverDetailView(LoginRequiredMixin, DetailView):
    """Driver detail view"""
    model = Driver
    template_name = 'core/driver_detail.html'
    context_object_name = 'driver'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        driver = self.get_object()
        
        context['assignments'] = driver.assignments.all().order_by('-assigned_date')[:10]
        context['fuel_logs'] = driver.fuel_logs.all().order_by('-refuel_date')[:10]
        context['current_assignment'] = driver.assignments.filter(
            unassigned_date__isnull=True
        ).first()
        
        return context


# ============================================================================
# INSPECTION MANAGEMENT
# ============================================================================

class InspectionListView(LoginRequiredMixin, ListView):
    """List vehicle inspections"""
    model = InspectionRecord
    template_name = 'core/inspection_list.html'
    context_object_name = 'inspections'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = InspectionRecord.objects.select_related('vehicle')
        
        result = self.request.GET.get('result')
        if result:
            queryset = queryset.filter(result=result)
        
        return queryset.order_by('-inspection_date')


class InspectionDetailView(LoginRequiredMixin, DetailView):
    """Inspection detail"""
    model = InspectionRecord
    template_name = 'core/inspection_detail.html'
    context_object_name = 'inspection'


class InspectionCreateView(AdminOrManagerRequiredMixin, CreateView):
    """Create inspection record"""
    model = InspectionRecord
    template_name = 'core/inspection_form.html'
    fields = [
        'vehicle', 'inspection_date', 'result', 'odometer_reading',
        'fuel_level', 'tire_condition', 'brake_condition',
        'light_condition', 'fluid_levels', 'remarks', 'next_inspection_due'
    ]
    success_url = reverse_lazy('inspection_list')
    
    def form_valid(self, form):
        form.instance.inspected_by = self.request.user
        messages.success(self.request, 'Inspection record created.')
        return super().form_valid(form)
