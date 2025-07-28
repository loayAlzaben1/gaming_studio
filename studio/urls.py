from django.urls import path
from . import views
from .health_check import health_check
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
    
    # Help and Guide Pages
    path('help/reviews/', views.review_guide, name='review_guide'),
    
    # Community Hub Pages
    path('hub/reviews/', views.review_hub, name='review_hub'),
    path('hub/ratings/', views.rating_hub, name='rating_hub'),
    path('hub/forums/', views.forum_hub, name='forum_hub'),
    
    # Community Features URLs
    path('games/<int:game_id>/review/', views.write_review, name='write_review'),
    path('games/<int:game_id>/forum/', views.game_forum, name='game_forum'),
    path('games/<int:game_id>/rate/', views.rate_game, name='rate_game'),
    path('games/<int:game_id>/upload/', views.upload_ugc, name='upload_ugc'),
    path('forum/<int:forum_id>/create-topic/', views.create_topic, name='create_topic'),
    path('topic/<int:topic_id>/', views.forum_topic, name='forum_topic'),
    path('comment/<str:content_type>/<int:object_id>/', views.add_comment, name='add_comment'),
    path('community/', views.community_showcase, name='community_showcase'),
    path('review/<int:review_id>/like/', views.like_review, name='like_review'),
    path('ugc/<int:content_id>/like/', views.like_ugc, name='like_ugc'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    
    # Health check endpoint for debugging
    path('health/', health_check, name='health_check'),
    
    # Guide Pages
    path('guides/review/', views.review_guide, name='review_guide'),
    path('guides/rating/', views.rating_guide, name='rating_guide'),
    path('forum/rules/', views.forum_rules, name='forum_rules'),
]