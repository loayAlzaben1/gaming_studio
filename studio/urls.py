from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('', views.home, name='home'),
    path('games/', views.games, name='games'),
    path('games/<int:pk>/', views.game_detail, name='game_detail'),
    path('games/<int:pk>/wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.user_wishlist, name='user_wishlist'),
    path('collections/', views.game_collection_list, name='game_collection_list'),
    path('collections/create/', views.create_game_collection, name='create_game_collection'),
    path('news/', views.news, name='news'),
    path('team/', views.team, name='team'),
    path('contact/', views.contact, name='contact'),
    path('donate/', views.donate, name='donate'),
    path('donate/success/', views.donate_success, name='donate_success'),
    path('community/', views.community, name='community'),
    path('cancel/', views.cancel, name='cancel'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('profile/', views.profile_view, name='my_profile'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('my-donations/', views.my_donations, name='my_donations'),
    path('settings/', views.settings, name='settings'),
    path('account-settings/', lambda request: redirect('/accounts/email/'), name='account_settings'),
    # Admin analytics (staff only)
    path('admin/analytics/games/', views.game_analytics_summary, name='game_analytics_summary'),
]