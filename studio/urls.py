from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('', views.home, name='home'),
    path('games/', views.games, name='games'),
    path('news/', views.news, name='news'),  # Add this line
    path('team/', views.team, name='team'),
    path('contact/', views.contact, name='contact'),
    path('donate/', views.donate, name='donate'),
    path('donate/success/', views.donate_success, name='donate_success'),
    path('community/', views.community, name='community'),
    path('cancel/', views.cancel, name='cancel'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('my-donations/', views.my_donations, name='my_donations'),
    path('settings/', views.settings, name='settings'),
    path('account-settings/', lambda request: redirect('/accounts/email/'), name='account_settings'),
]