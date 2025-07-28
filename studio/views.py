from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
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
                     UserFollow, UserGameStats, GameSession, FeaturedAchievement,
                     GameWishlist, GameCollection, GameAnalytics, CommunityGameReview, 
                     ReviewHelpful, GameForum, ForumTopic, ForumPost, Comment, CommentLike,
                     UserGeneratedContent, UGCLike, AdvancedGameRating)
from .forms import (DonationForm, UserProfileForm, CommunityGameReviewForm, ForumTopicForm,
                   ForumPostForm, CommentForm, UGCForm, AdvancedGameRatingForm)

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
    try:
        featured_games = Game.objects.filter(is_featured=True).prefetch_related('devlog_video_entries')
    except Exception as e:
        # Handle case where tables don't exist yet
        print(f"Database error in home view: {e}")
        featured_games = []
    return render(request, 'studio/home.html', {'featured_games': featured_games})

def games(request):
    """Enhanced games showcase with filtering, search, and pagination."""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    try:
        # Get all games with related data
        games_list = Game.objects.all().prefetch_related('photos', 'videos', 'devlog_video_entries')
        
        # Search functionality
        search_query = request.GET.get('search', '').strip()
        if search_query:
            games_list = games_list.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(platform__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        # Filter by genre
        genre_filter = request.GET.get('genre', '').strip()
        if genre_filter:
            games_list = games_list.filter(genre=genre_filter)
            
    except Exception as e:
        # Handle case where tables don't exist yet
        print(f"Database error in games view: {e}")
        games_list = []
        search_query = ''
        genre_filter = ''
    
    # Filter by platform
    platform_filter = request.GET.get('platform', '').strip()
    if platform_filter:
        games_list = games_list.filter(platform=platform_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        games_list = games_list.filter(status=status_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['-created_at', 'created_at', '-average_rating', '-play_count', 'title', '-title']
    if sort_by in valid_sorts:
        games_list = games_list.order_by(sort_by)
    else:
        games_list = games_list.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(games_list, 12)  # Show 12 games per page
    page_number = request.GET.get('page')
    games = paginator.get_page(page_number)
    
    # Get featured games separately
    featured_games = Game.objects.filter(is_featured=True).order_by('-featured_order', '-created_at')[:6]
    
    # Get filter choices for template
    genre_choices = Game.GENRE_CHOICES
    platform_choices = Game.PLATFORM_CHOICES
    status_choices = Game.STATUS_CHOICES
    
    context = {
        'games': games,
        'featured_games': featured_games,
        'genre_choices': genre_choices,
        'platform_choices': platform_choices,
        'status_choices': status_choices,
        'search_query': search_query,
        'current_filters': {
            'genre': genre_filter,
            'platform': platform_filter,
            'status': status_filter,
            'sort': sort_by,
        }
    }
    
    return render(request, 'studio/games.html', context)

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

# Enhanced Game Management Views
def game_detail(request, pk):
    """Detailed view for individual game with analytics tracking."""
    game = get_object_or_404(Game, pk=pk)
    
    # Track game view (simple analytics)
    game.play_count += 1
    game.save(update_fields=['play_count'])
    
    # Get related games (same genre or platform)
    related_games = Game.objects.filter(
        Q(genre=game.genre) | Q(platform=game.platform)
    ).exclude(pk=game.pk)[:4]
    
    # Get user's wishlist status if authenticated
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = GameWishlist.objects.filter(
            user=request.user, game=game
        ).exists()
    
    # Get reviews for this game
    reviews = CommunityGameReview.objects.filter(game=game).select_related('user', 'user__profile').order_by('-created_at')[:10]
    
    # Get ratings for this game
    ratings = AdvancedGameRating.objects.filter(game=game).select_related('user', 'user__profile').order_by('-created_at')[:10]
    
    # Calculate average ratings
    ratings_summary = None
    if ratings.exists():
        from django.db.models import Avg
        avg_data = AdvancedGameRating.objects.filter(game=game).aggregate(
            overall=Avg('overall_rating'),
            gameplay=Avg('gameplay'),
            graphics=Avg('graphics'),
            sound=Avg('sound'),
            story=Avg('story'),
            innovation=Avg('innovation'),
            replayability=Avg('replayability')
        )
        ratings_summary = {
            'overall': round(avg_data['overall'] or 0, 1),
            'gameplay': round(avg_data['gameplay'] or 0, 1),
            'graphics': round(avg_data['graphics'] or 0, 1),
            'sound': round(avg_data['sound'] or 0, 1),
            'story': round(avg_data['story'] or 0, 1),
            'innovation': round(avg_data['innovation'] or 0, 1),
            'replayability': round(avg_data['replayability'] or 0, 1),
            'count': ratings.count()
        }
    
    # Get UGC content for this game
    ugc_content = UserGeneratedContent.objects.filter(game=game, is_approved=True).select_related('user', 'user__profile').order_by('-created_at')[:10]
    
    # Add like information for authenticated users
    if request.user.is_authenticated:
        # Get user's likes for these content items
        user_likes = set(UGCLike.objects.filter(
            user=request.user,
            content__in=ugc_content
        ).values_list('content_id', flat=True))
        
        # Add is_liked attribute to each content
        for content in ugc_content:
            content.is_liked = content.id in user_likes
    else:
        # For anonymous users, set is_liked to False
        for content in ugc_content:
            content.is_liked = False
    
    # Get user's own UGC content (even if not approved)
    user_ugc_content = []
    if request.user.is_authenticated:
        user_ugc_content = UserGeneratedContent.objects.filter(game=game, user=request.user).select_related('user', 'user__profile').order_by('-created_at')[:5]
    
    # Check if user can review (separate query to avoid slice issue)
    user_can_review = request.user.is_authenticated and not CommunityGameReview.objects.filter(game=game, user=request.user).exists()
    
    context = {
        'game': game,
        'related_games': related_games,
        'in_wishlist': in_wishlist,
        'reviews': reviews,
        'ratings': ratings,
        'ratings_summary': ratings_summary,
        'ugc_content': ugc_content,
        'user_ugc_content': user_ugc_content,
        'user_can_review': user_can_review,
    }
    
    return render(request, 'studio/game_detail.html', context)

@login_required
def toggle_wishlist(request, pk):
    """Toggle game in user's wishlist via AJAX."""
    if request.method == 'POST':
        game = get_object_or_404(Game, pk=pk)
        wishlist_item, created = GameWishlist.objects.get_or_create(
            user=request.user,
            game=game,
            defaults={'priority': 2}
        )
        
        if not created:
            wishlist_item.delete()
            in_wishlist = False
            # Decrement wishlist count
            game.wishlist_count = max(0, game.wishlist_count - 1)
        else:
            in_wishlist = True
            # Increment wishlist count
            game.wishlist_count += 1
        
        game.save(update_fields=['wishlist_count'])
        
        return JsonResponse({
            'in_wishlist': in_wishlist,
            'wishlist_count': game.wishlist_count
        })
    
    return JsonResponse({'error': 'Invalid request method'})

@login_required
def user_wishlist(request):
    """Display user's wishlist."""
    wishlist_items = GameWishlist.objects.filter(user=request.user).select_related('game').order_by('-priority', '-added_at')
    
    # Group by priority
    high_priority = wishlist_items.filter(priority=4)
    medium_priority = wishlist_items.filter(priority__in=[2, 3])
    low_priority = wishlist_items.filter(priority=1)
    
    context = {
        'wishlist_items': wishlist_items,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
    }
    
    return render(request, 'studio/wishlist.html', context)

@login_required
def game_collection_list(request):
    """Display user's game collections."""
    collections = GameCollection.objects.filter(user=request.user).prefetch_related('games').order_by('-updated_at')
    
    # Get collection stats
    total_games = sum(collection.games.count() for collection in collections)
    
    context = {
        'collections': collections,
        'total_games': total_games,
    }
    
    return render(request, 'studio/collections.html', context)

@login_required
def create_game_collection(request):
    """Create a new game collection."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        collection_type = request.POST.get('collection_type', 'custom')
        is_public = request.POST.get('is_public') == 'on'
        
        if name:
            collection = GameCollection.objects.create(
                user=request.user,
                name=name,
                description=description,
                collection_type=collection_type,
                is_public=is_public
            )
            messages.success(request, f'Collection "{collection.name}" created successfully!')
            return redirect('game_collection_list')
        else:
            messages.error(request, 'Collection name is required.')
    
    return redirect('game_collection_list')

# Game Analytics Views (for future admin dashboard)
def game_analytics_summary(request):
    """Basic analytics summary for games."""
    if not request.user.is_staff:
        return redirect('home')
    
    from django.db.models import Avg, Count
    
    # Game statistics
    total_games = Game.objects.count()
    featured_games_count = Game.objects.filter(is_featured=True).count()
    avg_rating = Game.objects.aggregate(avg=Avg('average_rating'))['avg'] or 0
    
    # Popular games
    popular_games = Game.objects.order_by('-play_count')[:10]
    
    # Recent games
    recent_games = Game.objects.order_by('-created_at')[:10]
    
    context = {
        'total_games': total_games,
        'featured_games_count': featured_games_count,
        'avg_rating': round(avg_rating, 2),
        'popular_games': popular_games,
        'recent_games': recent_games,
    }
    
    return render(request, 'studio/admin/game_analytics.html', context)

# Community Features Views

@login_required
def write_review(request, game_id):
    """Write or edit a game review with detailed ratings"""
    game = get_object_or_404(Game, id=game_id)
    existing_review = CommunityGameReview.objects.filter(user=request.user, game=game).first()
    
    if request.method == 'POST':
        form = CommunityGameReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.game = game
            review.save()
            
            # Update game's average rating
            game.update_average_rating()
            
            # Award achievement and experience
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            if not existing_review:  # Only for new reviews
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='review',
                    description=f'Reviewed {game.title}',
                    experience_gained=50
                )
                profile.add_experience(50)
                profile.award_achievement('game_critic')
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('game_detail', pk=game.id)
        else:
            # Debug: Show form errors
            messages.error(request, f'Form errors: {form.errors}')
    else:
        form = CommunityGameReviewForm(instance=existing_review)
    
    return render(request, 'studio/write_review.html', {
        'form': form,
        'game': game,
        'existing_review': existing_review
    })

def game_forum(request, game_id):
    """Game-specific forum with discussion topics"""
    game = get_object_or_404(Game, id=game_id)
    forum, created = GameForum.objects.get_or_create(
        game=game,
        defaults={'name': f'{game.title} Forum', 'description': f'Discussion forum for {game.title}'}
    )
    
    # Get filter parameters
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'recent')
    
    # Base queryset for topics
    topics_queryset = forum.topics.select_related('author').prefetch_related('posts')
    
    # Apply category filter
    if category_filter:
        topics_queryset = topics_queryset.filter(topic_type=category_filter)
    
    # Apply sorting
    if sort_by == 'recent':
        topics = topics_queryset.order_by('-is_pinned', '-updated_at')
    elif sort_by == 'popular':
        topics = topics_queryset.order_by('-is_pinned', '-view_count')
    elif sort_by == 'replies':
        from django.db.models import Count
        topics = topics_queryset.annotate(reply_count=Count('posts')).order_by('-is_pinned', '-reply_count')
    else:
        topics = topics_queryset.order_by('-is_pinned', '-created_at')
    
    # Limit to recent 20 topics for main view
    topics = topics[:20]
    
    # Get user's topics if authenticated
    user_topics = []
    if request.user.is_authenticated:
        user_topics = forum.topics.filter(author=request.user).order_by('-created_at')[:5]
    
    # Get topic categories for filtering
    topic_categories = [
        ('discussion', 'General Discussion', 'fas fa-chat', 'blue'),
        ('help', 'Help & Support', 'fas fa-question-circle', 'green'),
        ('bug', 'Bug Reports', 'fas fa-bug', 'red'),
        ('feature', 'Feature Requests', 'fas fa-lightbulb', 'yellow'),
        ('guide', 'Guides & Tips', 'fas fa-book', 'purple'),
        ('showcase', 'Player Showcase', 'fas fa-trophy', 'orange'),
    ]
    
    # Calculate forum stats
    total_posts = sum(topic.posts.count() for topic in forum.topics.all())
    active_users = forum.topics.values('author').distinct().count()
    
    return render(request, 'studio/game_forum.html', {
        'game': game,
        'forum': forum,
        'topics': topics,
        'user_topics': user_topics,
        'topic_categories': topic_categories,
        'category_filter': category_filter,
        'sort_by': sort_by,
        'total_posts': total_posts,
        'active_users': active_users,
    })

@login_required
def create_topic(request, forum_id):
    """Create a new forum topic"""
    forum = get_object_or_404(GameForum, id=forum_id)
    
    if request.method == 'POST':
        form = ForumTopicForm(request.POST)
        if form.is_valid():
            try:
                topic = form.save(commit=False)
                topic.forum = forum
                topic.author = request.user
                topic.save()
                
                # Award experience for community participation
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='forum',
                    description=f'Started discussion: {topic.title}',
                    experience_gained=25
                )
                profile.add_experience(25)
                profile.award_achievement('discussion_starter')
                
                messages.success(request, 'Discussion topic created successfully!')
                return redirect('forum_topic', topic_id=topic.id)
            except Exception as e:
                messages.error(request, f'Error creating topic: {e}')
        else:
            # Show form errors for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ForumTopicForm()

    return render(request, 'studio/create_topic.html', {
        'form': form,
        'forum': forum,
        'game': forum.game,
        'recent_topics': forum.topics.all()[:5]
    })

def forum_topic(request, topic_id):
    """View forum topic with replies"""
    topic = get_object_or_404(ForumTopic, id=topic_id)
    posts = topic.posts.all()
    
    # Increment view count
    topic.view_count += 1
    topic.save(update_fields=['view_count'])
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()
            topic.updated_at = timezone.now()
            topic.save(update_fields=['updated_at'])
            
            # Award experience for participation
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.add_experience(10)
            
            return redirect('forum_topic', topic_id=topic.id)
    else:
        form = ForumPostForm()
    
    return render(request, 'studio/forum_topic.html', {
        'topic': topic,
        'posts': posts,
        'form': form
    })

@login_required
def add_comment(request, content_type, object_id):
    """Add comment to games, news, reviews, etc."""
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.content_type = content_type
            comment.object_id = object_id
            comment.author = request.user
            comment.save()
            
            # Award experience for engagement
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.add_experience(5)
            
            # Redirect back to the content
            if content_type == 'game':
                return redirect('game_detail', pk=object_id)
            elif content_type == 'news':
                return redirect('news_detail', pk=object_id)
    
    return redirect('home')

@login_required
def upload_ugc(request, game_id):
    """Upload user-generated content"""
    game = get_object_or_404(Game, id=game_id)
    
    if request.method == 'POST':
        form = UGCForm(request.POST, request.FILES)
        if form.is_valid():
            ugc = form.save(commit=False)
            ugc.user = request.user
            ugc.game = game
            ugc.save()
            
            # Award experience for content creation
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            UserActivity.objects.create(
                user=request.user,
                activity_type='ugc',
                description=f'Uploaded {ugc.get_content_type_display()}: {ugc.title}',
                experience_gained=75
            )
            profile.add_experience(75)
            profile.award_achievement('content_creator')
            
            messages.success(request, 'Content uploaded successfully! It will be reviewed before appearing publicly.')
            return redirect('game_detail', pk=game.id)
        else:
            # Debug: Show form errors
            messages.error(request, f'UGC form errors: {form.errors}')
    else:
        form = UGCForm()
    
    return render(request, 'studio/upload_ugc.html', {
        'form': form,
        'game': game
    })

def community_showcase(request):
    """Community content showcase"""
    featured_content = UserGeneratedContent.objects.filter(is_featured=True, is_approved=True)[:6]
    recent_content = UserGeneratedContent.objects.filter(is_approved=True).exclude(is_featured=True)[:12]
    
    # Get top contributors
    from django.db.models import Count
    top_contributors = User.objects.annotate(
        content_count=Count('usergeneratedcontent')
    ).filter(content_count__gt=0).order_by('-content_count')[:5]
    
    return render(request, 'studio/community_showcase.html', {
        'featured_content': featured_content,
        'recent_content': recent_content,
        'top_contributors': top_contributors
    })

def review_hub(request):
    """Central hub for all review-related activities"""
    # Get games that can be reviewed
    games = Game.objects.all()[:12]  # Show 12 games
    
    # Get recent reviews if user is authenticated
    recent_reviews = None
    user_reviews_count = 0
    if request.user.is_authenticated:
        recent_reviews = CommunityGameReview.objects.filter(user=request.user).order_by('-created_at')[:5]
        user_reviews_count = CommunityGameReview.objects.filter(user=request.user).count()
    
    return render(request, 'studio/review_hub.html', {
        'games': games,
        'recent_reviews': recent_reviews,
        'user_reviews_count': user_reviews_count
    })

def rating_hub(request):
    """Central hub for game rating activities"""
    # Get games that can be rated
    games = Game.objects.all()[:12]
    
    # Get user's recent ratings
    user_ratings = None
    user_ratings_count = 0
    if request.user.is_authenticated:
        user_ratings = AdvancedGameRating.objects.filter(user=request.user).order_by('-created_at')[:5]
        user_ratings_count = AdvancedGameRating.objects.filter(user=request.user).count()
    
    return render(request, 'studio/rating_hub.html', {
        'games': games,
        'user_ratings': user_ratings,
        'user_ratings_count': user_ratings_count
    })

def forum_hub(request):
    """Hub page for forum features"""
    games = Game.objects.all()
    recent_posts = ForumTopic.objects.select_related('author', 'forum').order_by('-created_at')[:10]
    
    context = {
        'games': games,
        'recent_posts': recent_posts,
    }
    
    if request.user.is_authenticated:
        context['user_posts_count'] = ForumTopic.objects.filter(author=request.user).count()
    
    return render(request, 'studio/forum_hub.html', context)

@login_required
def rate_game(request, game_id):
    """Advanced game rating with multiple categories"""
    game = get_object_or_404(Game, id=game_id)
    existing_rating = AdvancedGameRating.objects.filter(user=request.user, game=game).first()
    
    if request.method == 'POST':
        form = AdvancedGameRatingForm(request.POST, instance=existing_rating)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.game = game
            rating.save()
            
            # Update game's average rating
            game.update_average_rating()
            
            # Award experience
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            if not existing_rating:
                profile.add_experience(25)
                profile.award_achievement('game_rater')
            
            messages.success(request, 'Rating submitted successfully!')
            return redirect('game_detail', pk=game.id)
        else:
            # Debug: Show form errors
            messages.error(request, f'Rating form errors: {form.errors}')
    else:
        form = AdvancedGameRatingForm(instance=existing_rating)
    
    return render(request, 'studio/rate_game.html', {
        'form': form,
        'game': game,
        'existing_rating': existing_rating
    })

@login_required
def like_review(request, review_id):
    """Mark review as helpful/unhelpful via AJAX"""
    if request.method == 'POST':
        review = get_object_or_404(CommunityGameReview, id=review_id)
        helpful, created = ReviewHelpful.objects.get_or_create(
            user=request.user,
            review=review,
            defaults={'is_helpful': True}
        )
        
        if not created:
            helpful.delete()
            review.helpful_count -= 1
        else:
            review.helpful_count += 1
        
        review.save(update_fields=['helpful_count'])
        
        return JsonResponse({
            'helpful_count': review.helpful_count,
            'is_liked': created
        })
    
    return JsonResponse({'error': 'Invalid request'})

@login_required
def like_ugc(request, content_id):
    """Like user-generated content via AJAX"""
    if request.method == 'POST':
        content = get_object_or_404(UserGeneratedContent, id=content_id)
        like, created = UGCLike.objects.get_or_create(
            user=request.user,
            content=content
        )
        
        if not created:
            like.delete()
            content.like_count -= 1
        else:
            content.like_count += 1
        
        content.save(update_fields=['like_count'])
        
        return JsonResponse({
            'like_count': content.like_count,
            'is_liked': created
        })
    
    return JsonResponse({'error': 'Invalid request'})

@login_required
def like_comment(request, comment_id):
    """Like/dislike comment via AJAX"""
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        is_like = request.POST.get('is_like', 'true') == 'true'
        
        like, created = CommentLike.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'is_like': is_like}
        )
        
        if not created:
            if like.is_like == is_like:
                like.delete()
                # Update likes count
                likes_count = CommentLike.objects.filter(comment=comment, is_like=True).count()
                comment.likes_count = likes_count
                comment.save(update_fields=['likes_count'])
                return JsonResponse({'action': 'removed', 'likes_count': likes_count})
            else:
                like.is_like = is_like
                like.save()
        
        # Update likes count
        likes_count = CommentLike.objects.filter(comment=comment, is_like=True).count()
        comment.likes_count = likes_count
        comment.save(update_fields=['likes_count'])
        
        return JsonResponse({
            'action': 'liked' if is_like else 'disliked',
            'likes_count': likes_count
        })
    
    return JsonResponse({'error': 'Invalid request'})

def review_guide(request):
    """Help guide for writing reviews"""
    return render(request, 'studio/review_guide.html')

def rating_guide(request):
    """Guide for rating games"""
    return render(request, 'studio/rating_guide.html')

def forum_rules(request):
    """Forum rules and guidelines"""
    return render(request, 'studio/forum_rules.html')