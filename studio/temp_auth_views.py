from django.shortcuts import render
from django.http import JsonResponse

def temporary_login(request):
    """Temporary login page until allauth is properly configured"""
    return render(request, 'studio/temp_auth.html', {
        'page_title': 'Login - Coming Soon',
        'message': 'Authentication system is being configured. Please check back soon!'
    })

def temporary_signup(request):
    """Temporary signup page until allauth is properly configured"""
    return render(request, 'studio/temp_auth.html', {
        'page_title': 'Sign Up - Coming Soon', 
        'message': 'User registration will be available soon!'
    })
