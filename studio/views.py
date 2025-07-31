from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .models import Game, TeamMember, ContactMessage
from .forms import ContactForm
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

def home(request):
    featured_games = Game.objects.filter(is_featured=True)[:6]
    team_members = TeamMember.objects.all()[:4]
    return render(request, 'studio/home.html', {
        'featured_games': featured_games,
        'team_members': team_members,
    })

def games(request):
    games_list = Game.objects.all()
    paginator = Paginator(games_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'studio/games.html', {'page_obj': page_obj})

def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    return render(request, 'studio/game_detail.html', {'game': game})

def team(request):
    team_members = TeamMember.objects.all()
    return render(request, 'studio/team.html', {'team_members': team_members})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = ContactMessage(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message']
            )
            contact_message.save()
            messages.success(request, 'Your message has been sent successfully!')
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
    return render(request, 'studio/simple_message.html', {
        'title': 'Donations Unavailable',
        'message': 'Donation system is temporarily unavailable.'
    })

def donate_success(request):
    return render(request, 'studio/simple_message.html', {
        'title': 'Thank You',
        'message': 'Thank you for your support!'
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
