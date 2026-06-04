from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.db.models import Sum
from django.core.paginator import Paginator
from django.contrib.humanize.templatetags.humanize import intcomma

from .decorators import role_required

from assets.models import Asset
from assets.forms import AssetForm

from maintenance.models import MaintenanceRequest, AuditTrail
from maintenance.forms import MaintenanceRequestForm

# PDF IMPORTS

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.platypus.flowables import HRFlowable

from datetime import datetime


# LOGIN VIEW

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('redirect_dashboard')

    return render(
        request,
        'registration/login.html'
    )


# LOGOUT VIEW

def logout_view(request):

    logout(request)

    return redirect('login')


# REDIRECT DASHBOARD

@login_required
def redirect_dashboard(request):

    if request.user.role == 'MANAGER':
        return redirect('manager_dashboard')

    elif request.user.role == 'STAFF':
        return redirect('staff_dashboard')

    elif request.user.role == 'DRIVER':
        return redirect('driver_dashboard')

    elif request.user.role == 'AUDITOR':
        return redirect('auditor_dashboard')

    return redirect('login')

# MANAGER DASHBOARD

@login_required
def manager_dashboard(request):
    
    total_asset_value = Asset.objects.aggregate(
     total=Sum('price')
    )['total'] or 0
    
    

    total_assets = Asset.objects.count()

    active_count = Asset.objects.filter(
        status='ACTIVE'
    ).count()

    maintenance_count = Asset.objects.filter(
        status='MAINTENANCE'
    ).count()

    inactive_count = Asset.objects.filter(
        status='INACTIVE'
    ).count()

    active_vehicles = Asset.objects.filter(
        asset_type='VEHICLE',
        status='ACTIVE'
    ).count()

    pending_maintenance = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).count()

    approved_requests = MaintenanceRequest.objects.filter(
        status='APPROVED'
    ).count()

    completed_requests = MaintenanceRequest.objects.filter(
        status='COMPLETED'
    ).count()

    rejected_requests = MaintenanceRequest.objects.filter(
        status='REJECTED'
    ).count()

    recent_notifications = MaintenanceRequest.objects.order_by(
        '-created_at'
    )[:5]

    recent_assets = Asset.objects.order_by(
        '-created_at'
    )[:5]

    recent_requests = MaintenanceRequest.objects.order_by(
        '-created_at'
    )[:5]

    pending_count = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).count()

    context = {
        
        'total_asset_value': total_asset_value,

        'total_assets': total_assets,

        'active_count': active_count,

        'maintenance_count': maintenance_count,

        'inactive_count': inactive_count,

        'active_vehicles': active_vehicles,

        'pending_maintenance': pending_maintenance,

        'approved_requests': approved_requests,

        'completed_requests': completed_requests,

        'rejected_requests': rejected_requests,

        'recent_notifications': recent_notifications,

        'recent_assets': recent_assets,

        'recent_requests': recent_requests,

        'pending_count': pending_count,

    }

    return render(
        request,
        'dashboard/manager_dashboard.html',
        context
    )


# STAFF DASHBOARD

@login_required
@role_required(['STAFF'])
def staff_dashboard(request):

    pending_count = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).count()

    context = {

        'pending_count': pending_count,

    }

    return render(
        request,
        'dashboard/staff_dashboard.html',
        context
    )


# AUDITOR DASHBOARD

@login_required
@role_required(['AUDITOR'])
def auditor_dashboard(request):

    total_assets = Asset.objects.count()

    total_requests = MaintenanceRequest.objects.count()

    approved_requests = MaintenanceRequest.objects.filter(
        status='APPROVED'
    ).count()

    completed_requests = MaintenanceRequest.objects.filter(
        status='COMPLETED'
    ).count()

    pending_count = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).count()

    requests = MaintenanceRequest.objects.all().order_by(
        '-created_at'
    )[:5]

    context = {

        'total_assets': total_assets,

        'total_requests': total_requests,

        'approved_requests': approved_requests,

        'completed_requests': completed_requests,

        'pending_count': pending_count,

        'requests': requests,

    }

    return render(
        request,
        'dashboard/auditor_dashboard.html',
        context
    )


# DRIVER DASHBOARD

@login_required
@role_required(['DRIVER'])
def driver_dashboard(request):

    total_requests = MaintenanceRequest.objects.filter(
        requested_by=request.user
    ).count()

    pending_requests = MaintenanceRequest.objects.filter(
        requested_by=request.user,
        status='PENDING'
    ).count()

    completed_requests = MaintenanceRequest.objects.filter(
        requested_by=request.user,
        status='COMPLETED'
    ).count()

    pending_count = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).count()

    context = {

        'my_requests': total_requests,

        'pending_requests': pending_requests,

        'completed_requests': completed_requests,

        'pending_count': pending_count,

    }

    return render(
        request,
        'dashboard/driver_dashboard.html',
        context
    )


# ASSETS PAGE

@login_required
def assets_page(request):

    assets_list = Asset.objects.all().order_by(
        '-created_at'
    )

    paginator = Paginator(
        assets_list,
        10
    )

    page_number = request.GET.get(
        'page'
    )

    assets = paginator.get_page(
        page_number
    )

    context = {

        'assets': assets

    }

    return render(

        request,

        'dashboard/assets.html',

        context

    )


# ADD ASSET

@login_required
@role_required(['MANAGER'])
def add_asset(request):

    if request.method == 'POST':

        form = AssetForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            asset = form.save()

            AuditTrail.objects.create(

                user=request.user.username,

                action=f"Added new asset: {asset.name}"

            )

            return redirect('assets')

    else:

        form = AssetForm()

    pending_count = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).count()

    context = {

        'form': form,

        'pending_count': pending_count,

    }

    return render(
        request,
        'dashboard/add_asset.html',
        context
    )


# EDIT ASSET

@login_required
@role_required(['MANAGER'])
def edit_asset(request, id):

    asset = get_object_or_404(
        Asset,
        id=id
    )

    if request.method == 'POST':

        form = AssetForm(
            request.POST,
            request.FILES,
            instance=asset
        )

        if form.is_valid():

            updated_asset = form.save()

            AuditTrail.objects.create(

                user=request.user.username,

                action=f"Updated asset: {updated_asset.name}"

            )

            return redirect('assets')

    else:

        form = AssetForm(
            instance=asset
        )

    pending_count = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).count()

    context = {

        'form': form,

        'pending_count': pending_count,

    }

    return render(
        request,
        'dashboard/edit_asset.html',
        context
    )


# DELETE ASSET

@login_required
@role_required(['MANAGER'])
def delete_asset(request, id):

    asset = get_object_or_404(
        Asset,
        id=id
    )

    asset_name = asset.name

    asset.delete()

    AuditTrail.objects.create(

        user=request.user.username,

        action=f"Deleted asset: {asset_name}"

    )

    return redirect('assets')


# MAINTENANCE PAGE

@login_required
def maintenance_page(request):

    requests = MaintenanceRequest.objects.all().order_by(
        '-created_at'
    )

    pending_count = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).count()

    context = {

        'requests': requests,

        'pending_count': pending_count,

    }

    return render(
        request,
        'dashboard/maintenance.html',
        context
    )


# CREATE MAINTENANCE

@login_required
def create_maintenance(request):

    if request.method == 'POST':

        form = MaintenanceRequestForm(
            request.POST
        )

        if form.is_valid():

            maintenance = form.save(
                commit=False
            )

            maintenance.requested_by = request.user

            # Temporary asset para hindi mag-error
            maintenance.asset = Asset.objects.first()

            maintenance.save()

            AuditTrail.objects.create(

                user=request.user.username,

                action=f"Requested maintenance for {maintenance.asset_name} - {maintenance.status}"

            )

            return redirect('maintenance')

    else:

        form = MaintenanceRequestForm()

    pending_count = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).count()

    context = {

        'form': form,

        'pending_count': pending_count,

    }

    return render(
        request,
        'dashboard/create_maintenance.html',
        context
    )
        
# APPROVE REQUEST

@login_required
@role_required(['MANAGER'])
def approve_request(request, id):

    maintenance = get_object_or_404(
        MaintenanceRequest,
        id=id
    )

    maintenance.status = 'APPROVED'

    maintenance.save()

    AuditTrail.objects.create(

        user=request.user.username,

        action=f"Approved maintenance request for {maintenance.asset.name} - APPROVED"

    )

    return redirect('maintenance')


# REJECT REQUEST

@login_required
@role_required(['MANAGER'])
def reject_request(request, id):

    maintenance = get_object_or_404(
        MaintenanceRequest,
        id=id
    )

    maintenance.status = 'REJECTED'

    maintenance.save()

    AuditTrail.objects.create(

        user=request.user.username,

        action=f"Rejected maintenance request for {maintenance.asset.name} - REJECTED"

    )

    return redirect('maintenance')


# COMPLETE REQUEST

@login_required
@role_required(['MANAGER'])
def complete_request(request, id):

    maintenance = get_object_or_404(
        MaintenanceRequest,
        id=id
    )

    maintenance.status = 'COMPLETED'

    maintenance.save()

    AuditTrail.objects.create(

        user=request.user.username,

        action=f"Completed maintenance request for {maintenance.asset.name} - COMPLETED"

    )

    return redirect('maintenance')


# ACTIVITY LOGS

@login_required
@role_required(['MANAGER', 'AUDITOR'])
def activity_logs(request):

    logs = AuditTrail.objects.all().order_by(
        '-created_at'
    )

    pending_count = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).count()

    context = {

        'logs': logs,

        'pending_count': pending_count,

    }

    return render(
        request,
        'dashboard/activity_logs.html',
        context
    )


# EXPORT PDF

@login_required
def export_assets_pdf(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = f'attachment; filename="assets_report_{datetime.now().timestamp()}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=28
    )

    elements = []

    styles = getSampleStyleSheet()

    title = Paragraph(
        "<font size='22'><b>EVSU Asset Management Report</b></font>",
        styles['Title']
    )

    elements.append(title)

    elements.append(Spacer(1, 18))

    date_text = Paragraph(

        f"""
        <font size='11'>
        Generated on:
        {datetime.now().strftime('%B %d, %Y %I:%M %p')}
        </font>
        """,

        styles['Normal']
    )

    elements.append(date_text)

    elements.append(Spacer(1, 12))

    line = HRFlowable(
        width="100%",
        thickness=1,
        color=colors.grey
    )

    elements.append(line)

    elements.append(Spacer(1, 24))

    assets = Asset.objects.all()

    data = [

        [
            'Asset Name',
            'Asset Type',
            'Assigned To',
            'Status'
        ]

    ]

    for asset in assets:

        data.append([

            asset.name,

            asset.asset_type,

            str(asset.assigned_to),

            asset.status

        ])

    table = Table(
        data,
        colWidths=[150, 130, 140, 100]
    )

    table.setStyle(

        TableStyle([

            (
                'BACKGROUND',
                (0, 0),
                (-1, 0),
                colors.HexColor('#1e293b')
            ),

            (
                'TEXTCOLOR',
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                'FONTNAME',
                (0, 0),
                (-1, 0),
                'Helvetica-Bold'
            ),

            (
                'FONTSIZE',
                (0, 0),
                (-1, 0),
                12
            ),

            (
                'BOTTOMPADDING',
                (0, 0),
                (-1, 0),
                14
            ),

            (
                'TOPPADDING',
                (0, 0),
                (-1, 0),
                14
            ),

            (
                'BACKGROUND',
                (0, 1),
                (-1, -1),
                colors.whitesmoke
            ),

            (
                'GRID',
                (0, 0),
                (-1, -1),
                1,
                colors.grey
            ),

            (
                'FONTNAME',
                (0, 1),
                (-1, -1),
                'Helvetica'
            ),

            (
                'FONTSIZE',
                (0, 1),
                (-1, -1),
                11
            ),

            (
                'BOTTOMPADDING',
                (0, 1),
                (-1, -1),
                10
            ),

            (
                'TOPPADDING',
                (0, 1),
                (-1, -1),
                10
            ),

            (
                'ALIGN',
                (0, 0),
                (-1, -1),
                'CENTER'
            ),

        ])

    )

    elements.append(table)

    doc.build(elements)

    return response

@login_required
def staff_dashboard(request):

    if request.user.role != 'STAFF':
        return HttpResponse("ACCESS DENIED")

    total_assets = Asset.objects.count()

    pending_requests = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).count()

    approved_requests = MaintenanceRequest.objects.filter(
        status='APPROVED'
    ).count()

    context = {

        'total_assets': total_assets,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,

    }

    return render(
        request,
        'dashboard/staff_dashboard.html',
        context
    )