from django import forms
from .models import DonationGoal, UserProfile

class DonationForm(forms.Form):
    DONATION_TYPE_CHOICES = [
        ('one_time', 'One-time Donation'),
        ('monthly', 'Monthly ($5 minimum)'),
        ('yearly', 'Yearly ($50 minimum)'),
    ]
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1.00,
        label="Donation Amount (USD)",
        widget=forms.NumberInput(attrs={
            'class': 'w-full p-3 rounded-lg bg-gray-600 text-white border border-gray-500 focus:border-blue-400 focus:ring-2 focus:ring-blue-400', 
            'placeholder': 'Enter amount'
        })
    )
    
    donor_name = forms.CharField(
        max_length=100,
        required=False,
        label="Your Name (Optional)",
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 rounded-lg bg-gray-600 text-white border border-gray-500 focus:border-blue-400 focus:ring-2 focus:ring-blue-400', 
            'placeholder': 'Enter your name (or leave blank for anonymous)'
        })
    )
    
    donor_email = forms.EmailField(
        required=False,
        label="Email (Optional - for thank you message and updates)",
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-3 rounded-lg bg-gray-600 text-white border border-gray-500 focus:border-blue-400 focus:ring-2 focus:ring-blue-400', 
            'placeholder': 'Enter your email'
        })
    )
    
    donation_type = forms.ChoiceField(
        choices=DONATION_TYPE_CHOICES,
        initial='one_time',
        label="Donation Type",
        widget=forms.RadioSelect(attrs={
            'class': 'text-blue-400'
        })
    )
    
    donation_goal = forms.ModelChoiceField(
        queryset=DonationGoal.objects.filter(status='active'),
        required=False,
        empty_label="General Support",
        label="Support a specific goal (Optional)",
        widget=forms.Select(attrs={
            'class': 'w-full p-3 rounded-lg bg-gray-600 text-white border border-gray-500 focus:border-blue-400 focus:ring-2 focus:ring-blue-400'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        donation_type = cleaned_data.get('donation_type')
        
        if donation_type == 'monthly' and amount and amount < 5:
            raise forms.ValidationError("Monthly donations must be at least $5.")
        
        if donation_type == 'yearly' and amount and amount < 50:
            raise forms.ValidationError("Yearly donations must be at least $50.")
        
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'favorite_game']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'accept': 'image/*'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'placeholder': 'Tell us about yourself and your gaming interests...',
                'rows': 4
            }),
            'favorite_game': forms.Select(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400'
            })
        }