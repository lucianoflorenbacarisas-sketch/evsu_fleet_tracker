from django import forms
from .models import MaintenanceRequest


class MaintenanceRequestForm(forms.ModelForm):

    class Meta:

        model = MaintenanceRequest

        fields = [
            'asset_name',
            'issue_description'
        ]

        widgets = {

            'asset_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Asset Name'
                }
            ),

            'issue_description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Describe the issue...'
                }
            )

        }
        
        asset_name = forms.CharField(
    required=True,
    widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter Asset Name'
        }
    )
)