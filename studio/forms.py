from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': '1.00', 'step': '0.01'}),
        }