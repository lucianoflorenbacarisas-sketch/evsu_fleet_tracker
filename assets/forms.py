from django import forms

from .models import Asset


class AssetForm(forms.ModelForm):

    class Meta:

        model = Asset

        fields = [
            
            'name',
            'asset_type',
            'status',
            'assigned_to',
            'price'
        ]

