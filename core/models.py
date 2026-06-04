"""
Core App Models

Contains all business logic models for Fleet and Asset Tracking System including:
- Vehicle Management
- Asset Management
- Driver Assignment
- Maintenance Records
- Fuel Logs
- Inspections and Documents
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import User


# ============================================================================
# ENUMERATIONS & LOOKUP MODELS
# ============================================================================

class VehicleType(models.Model):
    """Vehicle category/type (e.g., Sedan, Van, Truck)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Vehicle Type'
        verbose_name_plural = 'Vehicle Types'
    
    def __str__(self):
        return self.name


class FuelType(models.Model):
    """Fuel type (e.g., Gasoline, Diesel, Electric)"""
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = 'Fuel Type'
        verbose_name_plural = 'Fuel Types'
    
    def __str__(self):
        return self.name


class MaintenanceType(models.Model):
    """Maintenance category (e.g., Oil Change, Tire Rotation)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Maintenance Type'
        verbose_name_plural = 'Maintenance Types'
    
    def __str__(self):
        return self.name


class AssetCategory(models.Model):
    """Asset category (e.g., IT Equipment, Office Equipment)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Asset Category'
        verbose_name_plural = 'Asset Categories'
    
    def __str__(self):
        return self.name


# ============================================================================
# VEHICLE MANAGEMENT
# ============================================================================

class Vehicle(models.Model):
    """Fleet vehicle tracking model"""
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('INACTIVE', 'Inactive'),
        ('DECOMMISSIONED', 'Decommissioned'),
    )
    
    # Basic Information
    registration_number = models.CharField(
        max_length=20,
        unique=True,
        help_text='Vehicle registration/plate number'
    )
    vin = models.CharField(
        max_length=50,
        unique=True,
        help_text='Vehicle Identification Number'
    )
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.PROTECT)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    color = models.CharField(max_length=50, blank=True)
    
    # Operational Details
    fuel_type = models.ForeignKey(FuelType, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    current_odometer = models.IntegerField(
        default=0,
        help_text='Current mileage in kilometers'
    )
    
    # Financial Details
    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    purchase_date = models.DateField()
    current_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True
    )
    
    # Assignment
    assigned_driver = models.ForeignKey(
        'Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_vehicles'
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_vehicles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
        ordering = ['registration_number']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assigned_driver']),
        ]
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.registration_number})"
    
    def is_assigned(self):
        """Check if vehicle has an assigned driver"""
        return self.assigned_driver is not None


# ============================================================================
# DRIVER MANAGEMENT
# ============================================================================

class Driver(models.Model):
    """Driver information and license tracking"""
    
    LICENSE_STATUS_CHOICES = (
        ('VALID', 'Valid'),
        ('EXPIRED', 'Expired'),
        ('SUSPENDED', 'Suspended'),
        ('REVOKED', 'Revoked'),
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='driver_profile'
    )
    license_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Driver license number'
    )
    license_expiry_date = models.DateField()
    license_status = models.CharField(
        max_length=20,
        choices=LICENSE_STATUS_CHOICES,
        default='VALID'
    )
    emergency_contact = models.CharField(max_length=100)
    emergency_contact_number = models.CharField(max_length=20)
    
    # Tracking
    total_distance_driven = models.IntegerField(default=0, help_text='Total km driven')
    violations = models.IntegerField(default=0, help_text='Traffic violations count')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} (License: {self.license_number})"
    
    def is_license_valid(self):
        """Check if driver license is valid"""
        return (
            self.license_status == 'VALID' and 
            self.license_expiry_date >= timezone.now().date()
        )


class DriverAssignment(models.Model):
    """Track driver assignments to vehicles over time"""
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='assignments')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='driver_assignments')
    assigned_date = models.DateTimeField(auto_now_add=True)
    unassigned_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Driver Assignment'
        verbose_name_plural = 'Driver Assignments'
        ordering = ['-assigned_date']
        indexes = [
            models.Index(fields=['driver', 'assigned_date']),
        ]
    
    def __str__(self):
        return f"{self.driver} -> {self.vehicle}"
    
    def is_active(self):
        """Check if assignment is currently active"""
        return self.unassigned_date is None


# ============================================================================
# ASSET MANAGEMENT
# ============================================================================

class Asset(models.Model):
    """Track non-vehicle assets"""
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('RETIRED', 'Retired'),
        ('LOST', 'Lost'),
    )
    
    asset_code = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique asset identifier'
    )
    name = models.CharField(max_length=200)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    
    # Location & Assignment
    location = models.CharField(
        max_length=200,
        help_text='Current asset location'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_assets'
    )
    
    # Financial Tracking
    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    purchase_date = models.DateField()
    current_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.asset_code} - {self.name}"
    
    def depreciation_percentage(self):
        """Calculate asset depreciation as percentage"""
        if not self.current_value or self.purchase_price == 0:
            return 0
        return ((self.purchase_price - self.current_value) / self.purchase_price) * 100


# ============================================================================
# MAINTENANCE & INSPECTIONS
# ============================================================================

class MaintenanceRecord(models.Model):
    """Vehicle maintenance history"""
    
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='maintenance_records'
    )
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.PROTECT)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SCHEDULED'
    )
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    
    description = models.TextField()
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    vendor = models.CharField(max_length=200, blank=True)
    
    odometer_reading = models.IntegerField(
        help_text='Odometer reading when maintenance was performed'
    )
    
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_maintenance'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Maintenance Record'
        verbose_name_plural = 'Maintenance Records'
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['vehicle', 'status']),
        ]
    
    def __str__(self):
        return f"{self.vehicle} - {self.maintenance_type} ({self.scheduled_date})"
    
    def is_overdue(self):
        """Check if maintenance is overdue"""
        if self.status in ['COMPLETED', 'CANCELLED']:
            return False
        return self.scheduled_date < timezone.now().date()


class InspectionRecord(models.Model):
    """Vehicle safety and compliance inspections"""
    
    RESULT_CHOICES = (
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('CONDITIONAL', 'Conditional Pass'),
    )
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='inspections'
    )
    inspection_date = models.DateField()
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    
    odometer_reading = models.IntegerField()
    fuel_level = models.CharField(max_length=50, blank=True)
    
    # Inspection Details
    tire_condition = models.CharField(max_length=100)
    brake_condition = models.CharField(max_length=100)
    light_condition = models.CharField(max_length=100)
    fluid_levels = models.CharField(max_length=100)
    
    remarks = models.TextField(blank=True)
    next_inspection_due = models.DateField(null=True, blank=True)
    
    inspected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inspections_conducted'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Inspection Record'
        verbose_name_plural = 'Inspection Records'
        ordering = ['-inspection_date']
    
    def __str__(self):
        return f"{self.vehicle} - {self.inspection_date} ({self.result})"


# ============================================================================
# FUEL MANAGEMENT
# ============================================================================

class FuelLog(models.Model):
    """Track vehicle fuel consumption"""
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='fuel_logs'
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fuel_logs'
    )
    
    refuel_date = models.DateField()
    refuel_time = models.TimeField(null=True, blank=True)
    
    # Fuel Details
    fuel_type = models.ForeignKey(FuelType, on_delete=models.PROTECT)
    quantity_liters = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Fuel quantity in liters'
    )
    cost_per_liter = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Location
    refuel_location = models.CharField(max_length=200)
    odometer_reading = models.IntegerField(
        help_text='Odometer reading at time of refueling'
    )
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Fuel Log'
        verbose_name_plural = 'Fuel Logs'
        ordering = ['-refuel_date']
        indexes = [
            models.Index(fields=['vehicle', 'refuel_date']),
        ]
    
    def __str__(self):
        return f"{self.vehicle} - {self.refuel_date}"
    
    def fuel_efficiency(self):
        """Calculate fuel efficiency (km/liter) from previous log"""
        prev_log = FuelLog.objects.filter(
            vehicle=self.vehicle,
            refuel_date__lt=self.refuel_date
        ).order_by('-refuel_date').first()
        
        if not prev_log:
            return None
        
        distance = self.odometer_reading - prev_log.odometer_reading
        if distance <= 0 or self.quantity_liters == 0:
            return None
        
        return distance / float(self.quantity_liters)


# ============================================================================
# AUDIT & COMPLIANCE
# ============================================================================

class AuditLog(models.Model):
    """Track system changes for compliance and audit purposes"""
    
    ACTION_CHOICES = (
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('ASSIGN', 'Assigned'),
        ('VIEW', 'Viewed'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    content_type = models.CharField(max_length=100, help_text='Model name being accessed')
    object_id = models.IntegerField()
    object_name = models.CharField(max_length=255)
    
    changes = models.JSONField(
        null=True,
        blank=True,
        help_text='JSON of field changes'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.object_name}"
