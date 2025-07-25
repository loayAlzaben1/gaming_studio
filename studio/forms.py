from django import forms
from .models import DonationGoal, UserProfile, GameReview

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
            'class': 'w-full p-3 pl-8 rounded-lg bg-gray-600 text-white border border-gray-500 focus:border-blue-400 focus:ring-2 focus:ring-blue-400 transition-colors', 
            'placeholder': '25.00'
        })
    )
    
    donor_name = forms.CharField(
        max_length=100,
        required=False,
        label="Your Name (Optional)",
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 rounded-lg bg-gray-600 text-white border border-gray-500 focus:border-blue-400 focus:ring-2 focus:ring-blue-400 transition-colors', 
            'placeholder': 'Anonymous Gamer'
        })
    )
    
    donor_email = forms.EmailField(
        required=False,
        label="Email (Optional - for thank you & updates)",
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-3 rounded-lg bg-gray-600 text-white border border-gray-500 focus:border-blue-400 focus:ring-2 focus:ring-blue-400 transition-colors', 
            'placeholder': 'your@email.com'
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
        empty_label="💝 General Support",
        label="Support a specific goal (Optional)",
        widget=forms.Select(attrs={
            'class': 'w-full p-3 rounded-lg bg-gray-600 text-white border border-gray-500 focus:border-blue-400 focus:ring-2 focus:ring-blue-400 transition-colors'
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
        fields = [
            'avatar', 'profile_banner', 'bio', 'custom_title',
            'favorite_game', 'gaming_style', 'preferred_platforms', 
            'favorite_genres', 'gaming_hours_weekly', 'theme_preference',
            'is_profile_public'
        ]
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'accept': 'image/*'
            }),
            'profile_banner': forms.FileInput(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'accept': 'image/*'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'placeholder': 'Tell us about yourself and your gaming interests...',
                'rows': 4,
                'maxlength': '500'
            }),
            'custom_title': forms.TextInput(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'placeholder': 'e.g., Master Strategist, Indie Game Explorer, Community Legend',
                'maxlength': '100'
            }),
            'favorite_game': forms.Select(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400'
            }),
            'gaming_style': forms.Select(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400'
            }),
            'preferred_platforms': forms.TextInput(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'placeholder': 'PC, PlayStation, Xbox, Nintendo Switch, Mobile',
                'maxlength': '200'
            }),
            'favorite_genres': forms.TextInput(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'placeholder': 'RPG, Action, Strategy, Indie, Horror, Racing',
                'maxlength': '200'
            }),
            'gaming_hours_weekly': forms.NumberInput(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'placeholder': '20',
                'min': '0',
                'max': '168'
            }),
            'theme_preference': forms.Select(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400'
            }),
            'is_profile_public': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text for form fields
        self.fields['preferred_platforms'].help_text = "Enter your preferred gaming platforms separated by commas"
        self.fields['favorite_genres'].help_text = "Enter your favorite game genres separated by commas"
        self.fields['gaming_hours_weekly'].help_text = "How many hours do you typically game per week?"
        self.fields['custom_title'].help_text = "A custom title that will be displayed on your profile"
        self.fields['is_profile_public'].help_text = "Allow other users to view your gaming profile"

# Enhanced Achievement Management Form
class AchievementShowcaseForm(forms.Form):
    """Form for users to select which achievements to showcase"""
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_achievements = user.achievements.select_related('achievement').order_by('-earned_date')
        
        for user_achievement in user_achievements:
            field_name = f'achievement_{user_achievement.achievement.id}'
            self.fields[field_name] = forms.BooleanField(
                required=False,
                label=user_achievement.achievement.name,
                initial=user_achievement.is_showcased,
                widget=forms.CheckboxInput(attrs={
                    'class': 'w-5 h-5 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2'
                })
            )

# Game Review Form
class GameReviewForm(forms.ModelForm):
    class Meta:
        model = GameReview
        fields = ['rating', 'title', 'content', 'is_recommended', 'playtime_hours']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={
                    'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400'
                }
            ),
            'title': forms.TextInput(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'placeholder': 'Enter a title for your review...',
                'maxlength': '200'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'placeholder': 'Share your thoughts about this game...',
                'rows': 6
            }),
            'is_recommended': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-green-600 bg-gray-700 border-gray-600 rounded focus:ring-green-500 focus:ring-2'
            }),
            'playtime_hours': forms.NumberInput(attrs={
                'class': 'w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:border-blue-400 focus:ring-2 focus:ring-blue-400',
                'placeholder': '0.0',
                'step': '0.1',
                'min': '0'
            })
        }