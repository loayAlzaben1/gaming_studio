from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from decimal import Decimal
import json
import os
import paypalrestsdk

# PayPal Configuration
try:
    paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
    paypal_client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
    
    if paypal_client_id and paypal_client_secret:
        paypalrestsdk.configure({
            "mode": "sandbox",  # Change to "live" for production
            "client_id": paypal_client_id,
            "client_secret": paypal_client_secret
        })
        PAYPAL_AVAILABLE = True
        print("✅ PayPal configured successfully")
    else:
        PAYPAL_AVAILABLE = False
        print("⚠️ PayPal credentials not found")
except Exception as e:
    PAYPAL_AVAILABLE = False
    print(f"❌ PayPal configuration error: {e}")

# Safe model imports with error handling
try:
    from .models import Game, TeamMember, ContactMessage, Donation, SponsorTier, DonationGoal
    MODELS_AVAILABLE = True
except Exception as e:
    print(f"Warning: Models not available: {e}")
    MODELS_AVAILABLE = False
    Game = None
    TeamMember = None
    ContactMessage = None
    Donation = None
    SponsorTier = None
    DonationGoal = None

try:
    from .forms import ContactForm, DonationForm
    FORMS_AVAILABLE = True
except Exception as e:
    print(f"Warning: Forms not available: {e}")
    FORMS_AVAILABLE = False
    ContactForm = None
    DonationForm = None

def home(request):
    featured_games = []
    team_members = []
    
    if MODELS_AVAILABLE and Game:
        try:
            featured_games = list(Game.objects.filter(is_featured=True)[:6])
        except Exception as e:
            print(f"Home view Game query error: {e}")
            featured_games = []
    
    if MODELS_AVAILABLE and TeamMember:
        try:
            team_members = list(TeamMember.objects.all()[:4])
        except Exception as e:
            print(f"Home view TeamMember query error: {e}")
            team_members = []
    
    return render(request, 'studio/home.html', {
        'featured_games': featured_games,
        'team_members': team_members,
    })

def games(request):
    if not MODELS_AVAILABLE or not Game:
        return render(request, 'studio/simple_message.html', {
            'title': 'Games Coming Soon',
            'message': 'Game database is being set up. Please check back later!'
        })
    
    try:
        games_list = Game.objects.all()
        paginator = Paginator(games_list, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'studio/games.html', {'page_obj': page_obj})
    except Exception as e:
        print(f"Games view error: {e}")
        return render(request, 'studio/simple_message.html', {
            'title': 'Games Coming Soon',
            'message': 'Game database is being set up. Please check back later!'
        })

def game_detail(request, pk):
    try:
        game = get_object_or_404(Game, pk=pk)
        return render(request, 'studio/game_detail.html', {'game': game})
    except:
        return render(request, 'studio/simple_message.html', {
            'title': 'Game Not Found',
            'message': 'Game database is being set up. Please check back later!'
        })

def team(request):
    team_members = []
    
    if MODELS_AVAILABLE and TeamMember:
        try:
            team_members = list(TeamMember.objects.all())
        except Exception as e:
            print(f"Team view error: {e}")
            team_members = []
    
    return render(request, 'studio/team.html', {'team_members': team_members})

def contact(request):
    if not FORMS_AVAILABLE or not ContactForm:
        return render(request, 'studio/simple_message.html', {
            'title': 'Contact Form Unavailable',
            'message': 'Contact form is being set up. Please check back later!'
        })
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            if MODELS_AVAILABLE and ContactMessage:
                try:
                    contact_message = ContactMessage(
                        name=form.cleaned_data['name'],
                        email=form.cleaned_data['email'],
                        subject=form.cleaned_data['subject'],
                        message=form.cleaned_data['message']
                    )
                    contact_message.save()
                    messages.success(request, 'Your message has been sent successfully!')
                except Exception as e:
                    print(f"Contact save error: {e}")
                    messages.error(request, 'There was an error sending your message. Please try again later.')
            else:
                messages.info(request, 'Contact system is being set up. Your message cannot be saved right now.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'studio/contact.html', {'form': form})

# Placeholder view functions for all the missing URLs
def toggle_wishlist(request, pk):
    return JsonResponse({'error': 'Authentication required'}, status=401)

def user_wishlist(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Wishlist Unavailable',
        'message': 'Authentication required to view wishlist.'
    })

def game_collection_list(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Collections Unavailable', 
        'message': 'Authentication required to view collections.'
    })

def create_game_collection(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Collections Unavailable',
        'message': 'Authentication required to create collections.'
    })

def news(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'News Coming Soon',
        'message': 'News section is under development.'
    })

def donate(request):
    """Handle donation via PayPal - works without authentication"""
    
    # Check if PayPal and forms are available
    if not PAYPAL_AVAILABLE or not FORMS_AVAILABLE or not DonationForm:
        return render(request, 'studio/simple_message.html', {
            'title': 'Donations Temporarily Unavailable',
            'message': 'Donation system is being configured. Please check back later!'
        })
    
    # Initialize default values
    sponsor_tiers = []
    active_goals = []
    total_donations = Decimal('0.00')
    general_progress = 0
    donations = []

    # Try to get donation data if database is available
    try:
        if MODELS_AVAILABLE and SponsorTier:
            sponsor_tiers = list(SponsorTier.objects.all().order_by('min_amount'))
    except Exception as e:
        print(f"SponsorTier error: {e}")
        sponsor_tiers = []
    try:
        if MODELS_AVAILABLE and DonationGoal:
            active_goals = list(DonationGoal.objects.filter(status='active').order_by('-start_date'))
    except Exception as e:
        print(f"DonationGoal error: {e}")
        active_goals = []
    try:
        if MODELS_AVAILABLE and Donation:
            total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            general_goal = Decimal('1000.00')
            general_progress = min((total_donations / general_goal) * 100, 100)
            donations = list(Donation.objects.select_related('sponsor_tier').order_by('-donated_at')[:10])
    except Exception as e:
        print(f"Donation error: {e}")
        total_donations = Decimal('0.00')
        general_progress = 0
        donations = []

    try:
        if request.method == "POST":
            form = DonationForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                donor_name = form.cleaned_data['donor_name'] or "Anonymous"
                donor_email = form.cleaned_data['donor_email']
                donation_type = form.cleaned_data['donation_type']
                # Store form data in session for later use
                request.session['donation_data'] = {
                    'donor_name': donor_name,
                    'donor_email': donor_email,
                    'donation_type': donation_type,
                    'amount': str(amount),
                }
                try:
                    # Create payment description
                    description = f"{'Recurring' if donation_type != 'one_time' else 'One-time'} donation of ${amount:.2f} to Gaming Studio by {donor_name}"
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
                        messages.error(request, f"Payment creation failed. Please try again.")
                except Exception as e:
                    print(f"PayPal error: {e}")
                    messages.error(request, "Payment system error. Please try again later.")
        else:
            form = DonationForm()
    except Exception as e:
        print(f"Donation page error: {e}")
        form = DonationForm()

    context = {
        'form': form,
        'total_donations': total_donations,
        'general_progress': general_progress,
        'donations': donations,
        'sponsor_tiers': sponsor_tiers,
        'active_goals': active_goals,
    }
    return render(request, 'studio/donate.html', context)

def donate_success(request):
    """Handle successful PayPal donation"""
    
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    if not payment_id or not payer_id:
        return render(request, 'studio/simple_message.html', {
            'title': 'Payment Error',
            'message': 'Payment verification failed. Please contact support if you were charged.'
        })
    
    try:
        # Get payment details from PayPal
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Payment successful
            print(f"Payment {payment_id} executed successfully")
            
            # Get donation data from session
            donation_data = request.session.get('donation_data', {})
            
            # Try to save to database if available
            if MODELS_AVAILABLE and Donation and donation_data:
                try:
                    # Create donation record
                    donation = Donation(
                        donor_name=donation_data.get('donor_name', 'Anonymous'),
                        donor_email=donation_data.get('donor_email', ''),
                        amount=Decimal(donation_data.get('amount', '0')),
                        donation_type=donation_data.get('donation_type', 'one_time'),
                        paypal_payment_id=payment_id,
                        status='completed'
                    )
                    donation.save()
                    print(f"Donation saved to database: ${donation.amount} from {donation.donor_name}")
                except Exception as e:
                    print(f"Error saving donation to database: {e}")
            
            # Clear session data
            if 'donation_data' in request.session:
                del request.session['donation_data']
            
            return render(request, 'studio/success.html', {
                'donor_name': donation_data.get('donor_name', 'Anonymous'),
                'amount': donation_data.get('amount', '0'),
                'payment_id': payment_id
            })
        else:
            print(f"Payment execution failed: {payment.error}")
            return render(request, 'studio/simple_message.html', {
                'title': 'Payment Failed',
                'message': 'Payment could not be processed. Please try again.'
            })
            
    except Exception as e:
        print(f"Payment verification error: {e}")
        return render(request, 'studio/simple_message.html', {
            'title': 'Payment Error',
            'message': 'Payment verification failed. Please contact support if you were charged.'
        })

def cancel(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Cancelled',
        'message': 'Operation was cancelled.'
    })

def newsletter_subscribe(request):
    return JsonResponse({'error': 'Newsletter subscription unavailable'}, status=400)

def dashboard(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Dashboard Unavailable',
        'message': 'Authentication required to access dashboard.'
    })

def profile_edit(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Profile Unavailable', 
        'message': 'Authentication required to edit profile.'
    })

def profile_view(request, username=None):
    return render(request, 'studio/simple_message.html', {
        'title': 'Profile Unavailable',
        'message': 'Authentication required to view profiles.'
    })

def follow_user(request, username):
    return JsonResponse({'error': 'Authentication required'}, status=401)

def my_donations(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Donations Unavailable',
        'message': 'Authentication required to view donations.'
    })

def settings(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Settings Unavailable',
        'message': 'Authentication required to access settings.'
    })

def game_analytics_summary(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Analytics Unavailable',
        'message': 'Staff access required for analytics.'
    })

def review_guide(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Review Guide',
        'message': 'Review guide is under development.'
    })

def review_hub(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Review Hub',
        'message': 'Review hub is under development.'
    })

def rating_hub(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Rating Hub', 
        'message': 'Rating hub is under development.'
    })

def forum_hub(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Forum Hub',
        'message': 'Forum hub is under development.'
    })

def write_review(request, game_id):
    return render(request, 'studio/simple_message.html', {
        'title': 'Reviews Unavailable',
        'message': 'Authentication required to write reviews.'
    })

def game_forum(request, game_id):
    return render(request, 'studio/simple_message.html', {
        'title': 'Forum Unavailable',
        'message': 'Authentication required to access forums.'
    })

def rate_game(request, game_id):
    return JsonResponse({'error': 'Authentication required'}, status=401)

def upload_ugc(request, game_id):
    return render(request, 'studio/simple_message.html', {
        'title': 'Upload Unavailable',
        'message': 'Authentication required to upload content.'
    })

def create_topic(request, forum_id):
    return render(request, 'studio/simple_message.html', {
        'title': 'Forum Unavailable',
        'message': 'Authentication required to create topics.'
    })

def forum_topic(request, topic_id):
    return render(request, 'studio/simple_message.html', {
        'title': 'Forum Unavailable', 
        'message': 'Authentication required to view topics.'
    })

def add_comment(request, content_type, object_id):
    return JsonResponse({'error': 'Authentication required'}, status=401)

def community_showcase(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Community Showcase',
        'message': 'Community showcase is under development.'
    })

def like_review(request, review_id):
    return JsonResponse({'error': 'Authentication required'}, status=401)

def like_ugc(request, content_id):
    return JsonResponse({'error': 'Authentication required'}, status=401)

def like_comment(request, comment_id):
    return JsonResponse({'error': 'Authentication required'}, status=401)

def rating_guide(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Rating Guide',
        'message': 'Rating guide is under development.'
    })

def forum_rules(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Forum Rules',
        'message': 'Forum rules are under development.'
    })
