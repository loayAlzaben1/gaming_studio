from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from decimal import Decimal
import paypalrestsdk
import os
from dotenv import load_dotenv
from .models import (ContactMessage, Donation, Game, TeamMember, SponsorTier, 
                     DonationGoal, UserProfile, Achievement, UserAchievement, UserActivity,
                     UserFollow, GameReview, UserGameStats, GameSession, FeaturedAchievement)
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
    try:
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
            try:
                profile.award_achievement('early_supporter')
                profile.add_experience(50)
            except Exception as e:
                print(f"Achievement error: {e}")
    except Exception as e:
        print(f"Profile creation error: {e}")
        # Create a basic context for error cases
        return render(request, 'studio/dashboard_simple.html', {
            'user': request.user,
            'error': 'Profile system temporarily unavailable'
        })
    
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
    """Enhanced profile editing with gaming features."""
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                
                # Award achievements for profile completion
                try:
                    if profile.avatar and profile.bio and profile.custom_title:
                        profile.award_achievement('social_butterfly')
                    
                    # Create activity record
                    UserActivity.objects.create(
                        user=request.user,
                        activity_type='profile_update',
                        description='Updated gaming profile with new information',
                        experience_gained=25
                    )
                    
                    # Add experience for profile update
                    profile.add_experience(25)
                    
                    # Update profile views counter when profile is updated
                    profile.profile_views += 1
                    profile.save()
                    
                except Exception as e:
                    print(f"Achievement/Activity error: {e}")
                
                messages.success(request, '🎮 Your gaming profile has been updated successfully! (+25 XP)')
                return redirect('dashboard')
        else:
            form = UserProfileForm(instance=profile)
        
        # Get user achievements for showcase selection
        user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement').order_by('-earned_date')
        
        context = {
            'form': form,
            'profile': profile,
            'user_achievements': user_achievements[:10],  # Show recent 10 for selection
        }
        
        return render(request, 'studio/profile_edit_enhanced.html', context)
    
    except Exception as e:
        print(f"Profile edit error: {e}")
        messages.error(request, 'Profile editing is temporarily unavailable. Please try again later.')
        return redirect('dashboard')

@login_required 
def profile_view(request, username=None):
    """Enhanced user profile view with gaming stats and social features."""
    try:
        if username:
            profile_user = get_object_or_404(User, username=username)
            profile = get_object_or_404(UserProfile, user=profile_user)
            
            # Check if profile is public or if it's the user's own profile
            if not profile.is_profile_public and request.user != profile_user:
                messages.error(request, "This profile is private.")
                return redirect('dashboard')
            
            # Increment profile views (only if it's not the owner viewing)
            if request.user != profile_user:
                profile.profile_views += 1
                profile.save()
        else:
            profile_user = request.user
            profile, created = UserProfile.objects.get_or_create(user=profile_user)
        
        # Get user achievements
        user_achievements = UserAchievement.objects.filter(user=profile_user).select_related('achievement').order_by('-earned_date')
        showcased_achievements = user_achievements.filter(is_showcased=True)[:3]
        achievements_count = user_achievements.count()
        
        # Get recent activities
        recent_activities = UserActivity.objects.filter(user=profile_user)[:10]
        
        # Calculate level progress
        next_level_xp = profile.account_level * 100
        current_level_xp = (profile.account_level - 1) * 100
        xp_to_next_level = next_level_xp - profile.experience_points
        next_level_progress = profile.get_next_level_progress()
        
        # Get social stats
        followers_count = UserFollow.objects.filter(following=profile_user).count()
        following_count = UserFollow.objects.filter(follower=profile_user).count()
        
        # Get gaming stats
        game_stats = UserGameStats.objects.filter(user=profile_user).select_related('game').order_by('-total_playtime_hours')[:5]
        total_playtime = sum(stat.total_playtime_hours for stat in game_stats)
        
        context = {
            'profile_user': profile_user,
            'profile': profile,
            'user_achievements': user_achievements[:12],
            'showcased_achievements': showcased_achievements,
            'achievements_count': achievements_count,
            'total_achievements': Achievement.objects.count(),
            'recent_activities': recent_activities,
            'next_level_progress': next_level_progress,
            'next_level_xp': next_level_xp,
            'xp_to_next_level': max(0, xp_to_next_level),
            'followers_count': followers_count,
            'following_count': following_count,
            'game_stats': game_stats,
            'total_playtime': total_playtime,
        }
        
        return render(request, 'studio/profile_enhanced.html', context)
    
    except Exception as e:
        print(f"Profile view error: {e}")
        messages.error(request, 'Profile viewing is temporarily unavailable.')
        return redirect('dashboard')

@login_required
def follow_user(request, username):
    """Follow/unfollow a user."""
    if request.method == 'POST':
        try:
            user_to_follow = get_object_or_404(User, username=username)
            
            if user_to_follow == request.user:
                return JsonResponse({'error': 'Cannot follow yourself'})
            
            follow_relationship, created = UserFollow.objects.get_or_create(
                follower=request.user,
                following=user_to_follow
            )
            
            if not created:
                # Unfollow
                follow_relationship.delete()
                is_following = False
                action = 'unfollowed'
            else:
                # Follow
                is_following = True
                action = 'followed'
                
                # Create activity
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='social',
                    description=f'Started following {user_to_follow.username}',
                    experience_gained=5
                )
                
                # Add experience for social interaction
                profile = UserProfile.objects.get(user=request.user)
                profile.add_experience(5)
            
            return JsonResponse({
                'success': True,
                'is_following': is_following,
                'action': action,
                'followers_count': UserFollow.objects.filter(following=user_to_follow).count()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Invalid request method'})

@login_required
def my_donations(request):
    """Display user's donation history."""
    try:
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
    
    except Exception as e:
        print(f"My donations error: {e}")
        # Return simple donation history without profile dependencies
        try:
            user_donations = Donation.objects.filter(donor_email=request.user.email).order_by('-donated_at')
            total_donated = user_donations.aggregate(total=Sum('amount'))['total'] or 0
            
            context = {
                'donations': user_donations,
                'total_donated': total_donated,
                'donation_count': user_donations.count(),
                'error': 'Profile system temporarily unavailable'
            }
            
            return render(request, 'studio/my_donations.html', context)
        except Exception:
            messages.error(request, 'Donation history is temporarily unavailable. Please try again later.')
            return redirect('dashboard')

@login_required
def settings(request):
    """Enhanced user settings page with gaming profile integration."""
    try:
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Get user's achievements count for display
        achievements_count = UserAchievement.objects.filter(user=request.user).count()
        
        # Calculate total donated
        total_donated = Donation.objects.filter(donor_email=request.user.email).aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00')
        
        context = {
            'profile': profile,
            'achievements_count': achievements_count,
            'total_donated': total_donated,
        }
        
        return render(request, 'studio/settings.html', context)
    
    except Exception as e:
        print(f"Settings page error: {e}")
        # Fallback context without profile dependencies
        context = {
            'error': 'Profile system temporarily unavailable'
        }
        return render(request, 'studio/settings.html', context)