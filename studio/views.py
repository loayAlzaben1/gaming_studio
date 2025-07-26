from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import paypalrestsdk
import os
from dotenv import load_dotenv
from .models import (ContactMessage, Donation, Game, TeamMember, SponsorTier, 
                     DonationGoal, UserProfile, Achievement, UserAchievement, UserActivity)
from .forms import DonationForm, UserProfileForm

# Load environment variables
load_dotenv()

# Initialize PayPal SDK with error handling
paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
paypal_client_secret = os.getenv("PAYPAL_CLIENT_SECRET")

print(f"PayPal Client ID: {paypal_client_id}")
print(f"PayPal Client Secret: {paypal_client_secret}")

if not paypal_client_id or not paypal_client_secret:
    raise ValueError("PayPal Client ID or Secret not found in environment variables.")

try:
    paypalrestsdk.configure({
        "mode": "live",
        "client_id": paypal_client_id,
        "client_secret": paypal_client_secret
    })
except Exception as e:
    print(f"PayPal configuration error: {e}")

    raise
def news(request):
    return render(request, 'studio/news.html', {})

def home(request):
    featured_games = Game.objects.filter(is_featured=True).prefetch_related('devlog_video_entries')
    return render(request, 'studio/home.html', {'featured_games': featured_games})

def games(request):
    games = Game.objects.all().prefetch_related('photos', 'videos', 'devlog_video_entries')
    return render(request, 'studio/games.html', {'games': games})

def donate(request):
    """Handle donation via PayPal with advanced features."""
    # Get sponsor tiers for display
    sponsor_tiers = SponsorTier.objects.all().order_by('min_amount')
    
    # Get active donation goals
    active_goals = DonationGoal.objects.filter(status='active').order_by('-start_date')
    
    # Calculate overall progress
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    general_goal = Decimal('1000.00')
    general_progress = min((total_donations / general_goal) * 100, 100)
    
    # Get recent donations with sponsor tiers
    donations = Donation.objects.select_related('sponsor_tier').order_by('-donated_at')[:10]

    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            donor_name = form.cleaned_data['donor_name'] or "Anonymous"
            donor_email = form.cleaned_data['donor_email']
            donation_type = form.cleaned_data['donation_type']
            donation_goal = form.cleaned_data['donation_goal']
            
            # Store form data in session
            request.session['donation_data'] = {
                'donor_name': donor_name,
                'donor_email': donor_email,
                'donation_type': donation_type,
                'donation_goal_id': donation_goal.id if donation_goal else None,
            }
            
            try:
                # Create payment description
                description = f"{'Recurring' if donation_type != 'one_time' else 'One-time'} donation of ${amount:.2f} to Gaming Studio by {donor_name}"
                if donation_goal:
                    description += f" for {donation_goal.title}"
                
                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {"payment_method": "paypal"},
                    "transactions": [{
                        "amount": {"total": f"{amount:.2f}", "currency": "USD"},
                        "description": description
                    }],
                    "redirect_urls": {
                        "return_url": request.build_absolute_uri("/donate/success/"),
                        "cancel_url": request.build_absolute_uri("/cancel/")
                    }
                })
                
                if payment.create():
                    for link in payment.links:
                        if link.method == "REDIRECT":
                            return HttpResponseRedirect(link.href)
                else:
                    print(f"Payment creation failed: {payment.error}")
                    return render(request, 'studio/donate.html', {
                        'form': form, 
                        'error': f"Payment creation failed: {payment.error}", 
                        'total_donations': total_donations, 
                        'general_progress': general_progress, 
                        'donations': donations,
                        'sponsor_tiers': sponsor_tiers,
                        'active_goals': active_goals,
                    })
            except Exception as e:
                print(f"Error during payment creation: {e}")
                messages.error(request, f"Payment failed: {e}")
                return render(request, 'studio/donate.html', {
                    'form': form, 
                    'total_donations': total_donations, 
                    'general_progress': general_progress, 
                    'donations': donations,
                    'sponsor_tiers': sponsor_tiers,
                    'active_goals': active_goals,
                })
        else:
            return render(request, 'studio/donate.html', {
                'form': form, 
                'total_donations': total_donations, 
                'general_progress': general_progress, 
                'donations': donations,
                'sponsor_tiers': sponsor_tiers,
                'active_goals': active_goals,
            })
    else:
        form = DonationForm()
    
    return render(request, 'studio/donate.html', {
        'form': form, 
        'total_donations': total_donations, 
        'general_progress': general_progress, 
        'donations': donations,
        'sponsor_tiers': sponsor_tiers,
        'active_goals': active_goals,
    })

def donate_success(request):
    """Handle successful donation and save to database with advanced features."""
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    if not payment_id or not payer_id:
        return HttpResponse("Missing paymentId or PayerID in the request.")

    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            amount = float(payment.transactions[0].amount.total)
            
            # Get donation data from session
            donation_data = request.session.get('donation_data', {})
            donor_name = donation_data.get('donor_name', 'Anonymous')
            donor_email = donation_data.get('donor_email')
            donation_type = donation_data.get('donation_type', 'one_time')
            donation_goal_id = donation_data.get('donation_goal_id')
            
            # Get donation goal if specified
            donation_goal = None
            if donation_goal_id:
                try:
                    donation_goal = DonationGoal.objects.get(id=donation_goal_id)
                except DonationGoal.DoesNotExist:
                    pass
            
            # Calculate next payment date for recurring donations
            next_payment_date = None
            is_recurring = donation_type != 'one_time'
            if is_recurring:
                if donation_type == 'monthly':
                    next_payment_date = datetime.now() + timedelta(days=30)
                elif donation_type == 'yearly':
                    next_payment_date = datetime.now() + timedelta(days=365)
            
            # Create donation record
            donation = Donation(
                amount=amount,
                donor_name=donor_name,
                donor_email=donor_email,
                donation_type=donation_type,
                is_recurring=is_recurring,
                next_payment_date=next_payment_date,
                donation_goal=donation_goal,
                donated_at=payment.create_time
            )
            donation.save()  # This will automatically set sponsor tier and send thank you email
            
            # Track user activity and award achievements if user is logged in
            if request.user.is_authenticated:
                # Get or create user profile
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                
                # Create activity record
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='donation',
                    description=f'Made a ${amount:.2f} donation',
                    experience_gained=int(amount * 5)  # 5 XP per dollar donated
                )
                
                # Add experience points
                profile.add_experience(int(amount * 5))
                
                # Update profile stats
                profile.total_donations_count += 1
                profile.total_donated += Decimal(amount)
                profile.update_tier()
                profile.save()
                
                # Award achievements
                if profile.total_donations_count == 1:
                    profile.award_achievement('first_donation')
                
                if profile.total_donations_count >= 5:
                    profile.award_achievement('loyal_supporter')
                
                if profile.total_donated >= 100:
                    profile.award_achievement('big_spender')
                
                if is_recurring:
                    profile.award_achievement('monthly_donor')
            
            # Clear session data
            if 'donation_data' in request.session:
                del request.session['donation_data']
            
            # Success message with tier info
            tier_message = ""
            if donation.sponsor_tier:
                tier_message = f" You are now a {donation.sponsor_tier.get_name_display()}!"
            
            recurring_message = ""
            if is_recurring:
                recurring_message = f" Your {donation_type} donation will automatically renew."
            
            messages.success(request, f"Thank you, {donor_name}, for your generous donation of ${amount:.2f}!{tier_message}{recurring_message}")
            return render(request, 'studio/success.html', {'donation': donation})
        else:
            print(f"Payment execution failed: {payment.error}")
            return HttpResponse(f"Payment execution failed: {payment.error}")
    except Exception as e:
        print(f"Error during payment execution: {e}")
        return HttpResponse(f"An unexpected error occurred: {e}")

def team(request):
    team_members = TeamMember.objects.all()
    return render(request, 'studio/team.html', {'team_members': team_members})

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            send_mail(
                'New Contact Message',
                f"From: {name} ({email})\n\n{message}",
                email,
                ['your-email@example.com'],  # Replace with your email
                fail_silently=False,
            )
            messages.success(request, "Thank you! Your message has been sent.")
        else:
            messages.error(request, "All fields are required.")
        return redirect('contact')
    return render(request, 'studio/contact.html')
    

def community(request):
    """Render the community page."""
    return render(request, 'studio/community.html')

def cancel(request):
    """Handle cancelled donation."""
    messages.info(request, "Donation was cancelled.")
    return render(request, 'studio/cancel.html')

def newsletter_subscribe(request):
    """Handle newsletter subscriptions."""
    if request.method == "POST":
        email = request.POST.get('email')
        messages.success(request, "Thank you for subscribing to our newsletter!")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def dashboard(request):
    """Enhanced user dashboard with gaming stats, achievements, and donation history."""
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Update login streak
    today = date.today()
    if profile.last_login_date:
        if profile.last_login_date == today - timedelta(days=1):
            profile.login_streak += 1
        elif profile.last_login_date != today:
            profile.login_streak = 1
    else:
        profile.login_streak = 1
    
    profile.last_login_date = today
    profile.save()
    
    # Award achievements for first login
    if created:
        profile.award_achievement('early_supporter')
        profile.add_experience(50)
    
    # Calculate total donated and update profile
    total_donated = Donation.objects.filter(donor_email=request.user.email).aggregate(
        total=Sum('amount'))['total'] or Decimal('0.00')
    
    donation_count = Donation.objects.filter(donor_email=request.user.email).count()
    
    if total_donated != profile.total_donated:
        profile.total_donated = total_donated
        profile.total_donations_count = donation_count
        profile.update_tier()
        
        # Award donation achievements
        if total_donated > 0 and not profile.user.achievements.filter(achievement__type='first_donation').exists():
            profile.award_achievement('first_donation')
        
        if donation_count >= 5:
            profile.award_achievement('loyal_supporter')
        
        if total_donated >= 100:
            profile.award_achievement('big_spender')
        
        if profile.current_tier and profile.current_tier.name == 'monthly':
            profile.award_achievement('monthly_donor')
        
        profile.save()
    
    # Get user's achievements
    user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement').order_by('-earned_date')
    showcased_achievements = user_achievements.filter(is_showcased=True)[:3]
    recent_achievements = user_achievements[:6]
    
    # Get recent donations
    recent_donations = Donation.objects.filter(donor_email=request.user.email).order_by('-donated_at')[:5]
    
    # Get recent activities
    recent_activities = UserActivity.objects.filter(user=request.user)[:10]
    
    # Calculate stats
    total_experience = profile.experience_points
    current_level = profile.account_level
    next_level_progress = profile.get_next_level_progress()
    
    # Gaming stats
    gaming_stats = {
        'total_donated': total_donated,
        'donations_count': donation_count,
        'account_level': current_level,
        'experience_points': total_experience,
        'login_streak': profile.login_streak,
        'achievements_count': user_achievements.count(),
        'profile_views': profile.profile_views,
        'join_date': profile.join_date,
    }
    
    context = {
        'profile': profile,
        'total_donated': total_donated,
        'recent_donations': recent_donations,
        'user_achievements': recent_achievements,
        'showcased_achievements': showcased_achievements,
        'recent_activities': recent_activities,
        'gaming_stats': gaming_stats,
        'next_level_progress': next_level_progress,
        'total_achievements': Achievement.objects.count(),
    }
    
    return render(request, 'studio/dashboard.html', context)

@login_required
def profile_edit(request):
    """Allow users to edit their gaming profile."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            
            # Award achievements for profile completion
            if profile.avatar and profile.bio:
                profile.award_achievement('social_butterfly')
            
            # Create activity record
            UserActivity.objects.create(
                user=request.user,
                activity_type='profile_update',
                description='Updated gaming profile',
                experience_gained=25
            )
            
            # Add experience for profile update
            profile.add_experience(25)
            
            messages.success(request, 'Your gaming profile has been updated successfully!')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'studio/profile_edit.html', context)

@login_required
def my_donations(request):
    """Display user's donation history."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get all donations for this user
    user_donations = Donation.objects.filter(donor_email=request.user.email).order_by('-donated_at')
    
    # Calculate total donated
    total_donated = user_donations.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'profile': profile,
        'donations': user_donations,
        'total_donated': total_donated,
        'donation_count': user_donations.count(),
    }
    
    return render(request, 'studio/my_donations.html', context)