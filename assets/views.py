from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import AssetForm
from .models import Asset

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.platypus.flowables import HRFlowable

from datetime import datetime


@login_required
def export_assets_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="assets_report_{datetime.now().timestamp()}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=28,
    )

    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph(
        "<font size='22'><b>EVSU Asset Management Report</b></font>",
        styles['Title'],
    )
    elements.append(title)
    elements.append(Spacer(1, 18))

    date_text = Paragraph(
        f"""
        <font size='11'>
        Generated on: {datetime.now().strftime('%B %d, %Y %I:%M %p')}
        </font>
        """,
        styles['Normal'],
    )
    elements.append(date_text)
    elements.append(Spacer(1, 12))

    line = HRFlowable(width='100%', thickness=1, color=colors.grey)
    elements.append(line)
    elements.append(Spacer(1, 24))

    assets = Asset.objects.all()
    data = [
        ['Asset Name', 'Asset Type', 'Assigned To', 'Status'],
    ]

    for asset in assets:
        data.append([
            asset.name,
            asset.asset_type,
            str(asset.assigned_to),
            asset.status,
        ])

    table = Table(data, colWidths=[150, 130, 140, 100])
    table.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
            ('TOPPADDING', (0, 0), (-1, 0), 14),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ])
    )

    elements.append(table)
    doc.build(elements)
    return response


@login_required
def edit_asset(request, id):
    asset = Asset.objects.get(id=id)

    if request.method == 'POST':
        form = AssetForm(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            form.save()
            return redirect('/assets/')
    else:
        form = AssetForm(instance=asset)

    context = {
        'form': form,
        'asset': asset,
    }

    return render(request, 'dashboard/edit_asset.html', context)
