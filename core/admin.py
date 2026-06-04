"""
Core App Admin Configuration

Registers all core models in the Django admin interface with custom configurations.
"""

from django.contrib import admin
from django.utils.html import format_html
from core.models import (
    VehicleType, FuelType, MaintenanceType, AssetCategory,
    Vehicle, Driver, DriverAssignment, Asset,
    MaintenanceRecord, InspectionRecord, FuelLog, AuditLog
)


# ============================================================================
# LOOKUP MODELS - INLINE ONLY
# ============================================================================

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(FuelType)
class FuelTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(MaintenanceType)
class MaintenanceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


# ============================================================================
# VEHICLE MANAGEMENT
# ============================================================================

class DriverAssignmentInline(admin.TabularInline):
    """Inline driver assignments for vehicle detail view"""
    model = DriverAssignment
    extra = 0
    readonly_fields = ['assigned_date', 'is_active']
    
    def is_active(self, obj):
        return "✓ Active" if obj.is_active() else "✗ Inactive"
    is_active.short_description = "Status"


class FuelLogInline(admin.TabularInline):
    """Inline fuel logs for vehicle detail view"""
    model = FuelLog
    extra = 0
    readonly_fields = ['refuel_date', 'total_cost']
    fields = ['refuel_date', 'quantity_liters', 'cost_per_liter', 'total_cost']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = [
        'registration_number', 'colored_status', 'make_model',
        'year', 'assigned_driver_name', 'current_odometer'
    ]
    list_filter = ['status', 'vehicle_type', 'fuel_type', 'year']
    search_fields = ['registration_number', 'vin', 'make', 'model']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('registration_number', 'vin', 'vehicle_type', 'make', 'model', 'year', 'color')
        }),
        ('Operational Details', {
            'fields': ('fuel_type', 'status', 'current_odometer')
        }),
        ('Financial Information', {
            'fields': ('purchase_price', 'purchase_date', 'current_value')
        }),
        ('Assignment', {
            'fields': ('assigned_driver',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [DriverAssignmentInline, FuelLogInline]
    
    def make_model(self, obj):
        return f"{obj.make} {obj.model}"
    make_model.short_description = "Make & Model"
    
    def colored_status(self, obj):
        colors = {
            'ACTIVE': '#28a745',
            'MAINTENANCE': '#ffc107',
            'INACTIVE': '#6c757d',
            'DECOMMISSIONED': '#dc3545',
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    colored_status.short_description = "Status"
    
    def assigned_driver_name(self, obj):
        return obj.assigned_driver.user.get_full_name() if obj.assigned_driver else "-"
    assigned_driver_name.short_description = "Assigned Driver"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# DRIVER MANAGEMENT
# ============================================================================

class DriverAssignmentInlineForDriver(admin.TabularInline):
    """Inline assignments for driver detail view"""
    model = DriverAssignment
    extra = 0
    readonly_fields = ['vehicle', 'assigned_date', 'unassigned_date']


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'license_number', 'license_status_colored',
        'is_license_valid_display', 'total_distance_driven'
    ]
    list_filter = ['license_status', 'user__date_joined']
    search_fields = ['user__first_name', 'user__last_name', 'license_number']
    readonly_fields = ['total_distance_driven', 'violations', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('License Information', {
            'fields': ('license_number', 'license_expiry_date', 'license_status')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact', 'emergency_contact_number')
        }),
        ('Tracking', {
            'fields': ('total_distance_driven', 'violations')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [DriverAssignmentInlineForDriver]
    
    def full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    full_name.short_description = "Name"
    
    def license_status_colored(self, obj):
        colors = {
            'VALID': '#28a745',
            'EXPIRED': '#dc3545',
            'SUSPENDED': '#ffc107',
            'REVOKED': '#dc3545',
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.license_status, '#6c757d'),
            obj.get_license_status_display()
        )
    license_status_colored.short_description = "License Status"
    
    def is_license_valid_display(self, obj):
        return "✓ Valid" if obj.is_license_valid() else "✗ Invalid"
    is_license_valid_display.short_description = "License Valid"


@admin.register(DriverAssignment)
class DriverAssignmentAdmin(admin.ModelAdmin):
    list_display = ['driver', 'vehicle', 'assigned_date', 'active_status']
    list_filter = ['assigned_date', 'unassigned_date']
    search_fields = ['driver__user__first_name', 'vehicle__registration_number']
    readonly_fields = ['assigned_date']
    
    def active_status(self, obj):
        if obj.is_active():
            return format_html('<span style="color: #28a745;">✓ Active</span>')
        return format_html('<span style="color: #dc3545;">✗ Inactive</span>')
    active_status.short_description = "Status"


# ============================================================================
# ASSET MANAGEMENT
# ============================================================================

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        'asset_code', 'name', 'category', 'colored_status',
        'assigned_to_name', 'depreciation_display'
    ]
    list_filter = ['status', 'category', 'purchase_date']
    search_fields = ['asset_code', 'name', 'location']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Asset Information', {
            'fields': ('asset_code', 'name', 'category', 'description')
        }),
        ('Location & Assignment', {
            'fields': ('location', 'assigned_to')
        }),
        ('Financial Information', {
            'fields': ('purchase_price', 'purchase_date', 'current_value')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def colored_status(self, obj):
        colors = {
            'ACTIVE': '#28a745',
            'MAINTENANCE': '#ffc107',
            'RETIRED': '#6c757d',
            'LOST': '#dc3545',
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    colored_status.short_description = "Status"
    
    def assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else "-"
    assigned_to_name.short_description = "Assigned To"
    
    def depreciation_display(self, obj):
        depreciation = obj.depreciation_percentage()
        return f"{depreciation:.1f}%"
    depreciation_display.short_description = "Depreciation"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# MAINTENANCE & INSPECTIONS
# ============================================================================

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'vehicle', 'maintenance_type', 'colored_status',
        'scheduled_date', 'cost', 'vendor'
    ]
    list_filter = ['status', 'maintenance_type', 'scheduled_date']
    search_fields = ['vehicle__registration_number', 'vendor']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Maintenance Information', {
            'fields': ('vehicle', 'maintenance_type', 'description')
        }),
        ('Schedule & Status', {
            'fields': ('status', 'scheduled_date', 'completed_date')
        }),
        ('Details', {
            'fields': ('cost', 'vendor', 'odometer_reading', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def colored_status(self, obj):
        colors = {
            'SCHEDULED': '#17a2b8',
            'IN_PROGRESS': '#ffc107',
            'COMPLETED': '#28a745',
            'CANCELLED': '#6c757d',
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    colored_status.short_description = "Status"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(InspectionRecord)
class InspectionRecordAdmin(admin.ModelAdmin):
    list_display = [
        'vehicle', 'inspection_date', 'result_colored',
        'odometer_reading', 'next_inspection_due'
    ]
    list_filter = ['result', 'inspection_date']
    search_fields = ['vehicle__registration_number']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Inspection Information', {
            'fields': ('vehicle', 'inspection_date', 'inspected_by', 'result')
        }),
        ('Vehicle Condition', {
            'fields': ('odometer_reading', 'fuel_level', 'tire_condition',
                      'brake_condition', 'light_condition', 'fluid_levels')
        }),
        ('Follow-up', {
            'fields': ('remarks', 'next_inspection_due')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def result_colored(self, obj):
        colors = {
            'PASS': '#28a745',
            'FAIL': '#dc3545',
            'CONDITIONAL': '#ffc107',
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.result, '#6c757d'),
            obj.get_result_display()
        )
    result_colored.short_description = "Result"


# ============================================================================
# FUEL MANAGEMENT
# ============================================================================

@admin.register(FuelLog)
class FuelLogAdmin(admin.ModelAdmin):
    list_display = [
        'vehicle', 'refuel_date', 'quantity_liters',
        'cost_per_liter', 'total_cost', 'efficiency'
    ]
    list_filter = ['fuel_type', 'refuel_date', 'vehicle']
    search_fields = ['vehicle__registration_number', 'refuel_location']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Vehicle & Driver', {
            'fields': ('vehicle', 'driver')
        }),
        ('Fuel Details', {
            'fields': ('refuel_date', 'refuel_time', 'fuel_type',
                      'quantity_liters', 'cost_per_liter', 'total_cost')
        }),
        ('Location', {
            'fields': ('refuel_location', 'odometer_reading')
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def efficiency(self, obj):
        eff = obj.fuel_efficiency()
        return f"{eff:.2f} km/L" if eff else "N/A"
    efficiency.short_description = "Efficiency"


# ============================================================================
# AUDIT & COMPLIANCE
# ============================================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'user_name', 'action', 'object_name',
        'content_type', 'created_at'
    ]
    list_filter = ['action', 'created_at', 'content_type']
    search_fields = ['user__username', 'object_name']
    readonly_fields = ['user', 'action', 'object_id', 'object_name',
                       'content_type', 'changes', 'ip_address', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def user_name(self, obj):
        return obj.user.get_full_name() if obj.user else "System"
    user_name.short_description = "User"
