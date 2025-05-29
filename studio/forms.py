from django import forms

class DonationForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1.00,
        label="Donation Amount (USD)",
        widget=forms.NumberInput(attrs={'class': 'w-full p-2 rounded bg-gray-600 text-white', 'placeholder': 'Enter amount'})
    )
    donor_name = forms.CharField(
        max_length=100,
        required=False,
        label="Your Name (Optional)",
        widget=forms.TextInput(attrs={'class': 'w-full p-2 rounded bg-gray-600 text-white', 'placeholder': 'Enter your name (or leave blank for anonymous)'})
    )