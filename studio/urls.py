from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('games/', views.games, name='games'),
    path('news/', views.news, name='news'),
    path('team/', views.team, name='team'),
    path('contact/', views.contact, name='contact'),
    path('donate/', views.donate, name='donate'),
    path('donate/success/', views.donate_success, name='donate_success'),
    path('community/', views.community, name='community'),
    path('cancel/', views.cancel, name='cancel'),  # Ensure this is included
]