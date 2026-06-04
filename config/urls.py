from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import RedirectView

from assets import views



urlpatterns = [

    path(
        '',
        include('maintenance.urls')
    ),

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        '',
        RedirectView.as_view(
            url='/login/'
        )
    ),
    
    

    path(
        '',
        include('accounts.urls')
    ),

    path(
        'export-assets-pdf/',
        views.export_assets_pdf,
        name='export_assets_pdf'
    ),

]



urlpatterns += static(

    settings.MEDIA_URL,

    document_root=settings.MEDIA_ROOT

)