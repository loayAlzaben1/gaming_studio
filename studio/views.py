from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
import paypalrestsdk
import os
from dotenv import load_dotenv
from .models import ContactMessage, Donation, Game, TeamMember
from .forms import DonationForm
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal

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
    """Handle donation via PayPal."""
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    goal = Decimal('1000.00')
    progress = min((total_donations / goal) * 100, 100)
    donations = Donation.objects.order_by('-donated_at')[:5]

    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            donor_name = form.cleaned_data['donor_name'] or "Anonymous"
            request.session['donor_name'] = donor_name
            try:
                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {"payment_method": "paypal"},
                    "transactions": [{
                        "amount": {"total": f"{amount:.2f}", "currency": "USD"},
                        "description": f"Donation of ${amount:.2f} to Gaming Studio by {donor_name}"
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
                    return render(request, 'studio/donate.html', {'form': form, 'error': f"Payment creation failed: {payment.error}", 'total_donations': total_donations, 'progress': progress, 'donations': donations})
            except paypalrestsdk.exceptions.UnauthorizedAccess as e:
                print(f"UnauthorizedAccess error: {e}")
                messages.error(request, f"Payment failed due to authorization error: {e}")
                return render(request, 'studio/donate.html', {'form': form, 'total_donations': total_donations, 'progress': progress, 'donations': donations})
            except Exception as e:
                print(f"Unexpected error during payment creation: {e}")
                messages.error(request, f"An unexpected error occurred: {e}")
                return render(request, 'studio/donate.html', {'form': form, 'total_donations': total_donations, 'progress': progress, 'donations': donations})
        else:
            return render(request, 'studio/donate.html', {'form': form, 'total_donations': total_donations, 'progress': progress, 'donations': donations})
    else:
        form = DonationForm()
    return render(request, 'studio/donate.html', {'form': form, 'total_donations': total_donations, 'progress': progress, 'donations': donations})

def donate_success(request):
    """Handle successful donation and save to database."""
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    if not payment_id or not payer_id:
        return HttpResponse("Missing paymentId or PayerID in the request.")

    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            amount = float(payment.transactions[0].amount.total)
            donor_name = request.session.get('donor_name', 'Anonymous')
            donation = Donation(
                amount=amount,
                donor_name=donor_name,
                donated_at=payment.create_time
            )
            donation.save()
            if 'donor_name' in request.session:
                del request.session['donor_name']
            messages.success(request, f"Thank you, {donor_name}, for your generous donation of ${amount:.2f}!")
            return render(request, 'studio/success.html', {'donation': donation})
        else:
            print(f"Payment execution failed: {payment.error}")
            return HttpResponse(f"Payment execution failed: {payment.error}")
    except paypalrestsdk.exceptions.UnauthorizedAccess as e:
        print(f"UnauthorizedAccess error: {e}")
        return HttpResponse(f"Payment execution failed due to authorization error: {e}")
    except Exception as e:
        print(f"Unexpected error during payment execution: {e}")
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
    return redirect('home')