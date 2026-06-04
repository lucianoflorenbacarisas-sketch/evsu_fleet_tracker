from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from maintenance.models import MaintenanceRequest

@login_required
def update_maintenance_status(request, id):

    maintenance = MaintenanceRequest.objects.get(id=id)

    if request.method == 'POST':

        new_status = request.POST.get('status')

        maintenance.status = new_status

        maintenance.save()

    return redirect('/maintenance/')