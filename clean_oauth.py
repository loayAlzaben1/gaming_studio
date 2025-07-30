"""
CLEAN OAUTH SOLUTION - Bypass broken allauth pages entirely
Direct Google OAuth integration without relying on allauth login/signup pages
"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
import requests
import json
import secrets

@csrf_exempt
def clean_login(request):
    """Clean login page with direct Google OAuth"""
    return HttpResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Gaming Studio - Sign In</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white; 
            margin: 0; 
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            max-width: 420px; 
            width: 100%;
            background: rgba(255,255,255,0.95); 
            color: #333;
            padding: 50px 40px; 
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }
        .logo { font-size: 4em; margin-bottom: 10px; }
        h1 { margin: 0 0 10px 0; font-size: 2.2em; color: #2c3e50; }
        .subtitle { color: #7f8c8d; margin-bottom: 40px; font-size: 1.1em; }
        .google-btn { 
            background: #fff;
            color: #757575;
            border: 1px solid #dadce0;
            padding: 12px 24px; 
            text-decoration: none; 
            border-radius: 50px; 
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin: 10px 0;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.2s;
            width: 100%;
            box-sizing: border-box;
        }
        .google-btn:hover { 
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            border-color: #c6c6c6;
        }
        .google-icon {
            width: 20px; 
            height: 20px; 
            margin-right: 12px;
        }
        .links { 
            margin-top: 30px; 
            font-size: 14px;
        }
        .links a { 
            color: #3498db; 
            text-decoration: none; 
            margin: 0 15px;
        }
        .links a:hover { 
            text-decoration: underline; 
        }
        .status {
            background: #e8f5e8;
            color: #2d5a2d;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎮</div>
        <h1>Welcome Back!</h1>
        <p class="subtitle">Sign in to Gaming Studio</p>
        
        <div class="status">
            ✅ OAuth system ready!<br>
            Direct Google integration active
        </div>
        
        <a href="/auth/google/" class="google-btn">
            <svg class="google-icon" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
        </a>
        
        <div class="links">
            <a href="/clean-signup/">Don't have an account? Sign up</a><br>
            <a href="/">← Back to Home</a>
        </div>
    </div>
</body>
</html>
""")

@csrf_exempt
def clean_signup(request):
    """Clean signup page with direct Google OAuth"""
    return HttpResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Gaming Studio - Create Account</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            background: linear-gradient(135deg, #8e44ad 0%, #3498db 100%);
            color: white; 
            margin: 0; 
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            max-width: 420px; 
            width: 100%;
            background: rgba(255,255,255,0.95); 
            color: #333;
            padding: 50px 40px; 
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }
        .logo { font-size: 4em; margin-bottom: 10px; }
        h1 { margin: 0 0 10px 0; font-size: 2.2em; color: #8e44ad; }
        .subtitle { color: #7f8c8d; margin-bottom: 40px; font-size: 1.1em; }
        .google-btn { 
            background: #fff;
            color: #757575;
            border: 1px solid #dadce0;
            padding: 12px 24px; 
            text-decoration: none; 
            border-radius: 50px; 
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin: 10px 0;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.2s;
            width: 100%;
            box-sizing: border-box;
        }
        .google-btn:hover { 
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            border-color: #c6c6c6;
        }
        .google-icon {
            width: 20px; 
            height: 20px; 
            margin-right: 12px;
        }
        .links { 
            margin-top: 30px; 
            font-size: 14px;
        }
        .links a { 
            color: #8e44ad; 
            text-decoration: none; 
            margin: 0 15px;
        }
        .links a:hover { 
            text-decoration: underline; 
        }
        .status {
            background: #e8f5e8;
            color: #2d5a2d;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎮</div>
        <h1>Join Gaming Studio!</h1>
        <p class="subtitle">Create your account in seconds</p>
        
        <div class="status">
            ✅ Quick signup ready!<br>
            One click with Google
        </div>
        
        <a href="/auth/google/" class="google-btn">
            <svg class="google-icon" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign up with Google
        </a>
        
        <div class="links">
            <a href="/clean-login/">Already have an account? Sign in</a><br>
            <a href="/">← Back to Home</a>
        </div>
    </div>
</body>
</html>
""")

@csrf_exempt
def google_auth_start(request):
    """Start Google OAuth flow"""
    # Generate a secure state parameter
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state
    
    # Google OAuth URL
    client_id = "1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com"
    redirect_uri = "https://gaming-studio.onrender.com/auth/google/callback/"
    scope = "openid email profile"
    
    auth_url = f"https://accounts.google.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code&state={state}"
    
    return HttpResponseRedirect(auth_url)

@csrf_exempt
def google_auth_callback(request):
    """Handle Google OAuth callback"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    # Verify state parameter
    if state != request.session.get('oauth_state'):
        return HttpResponse("Invalid state parameter", status=400)
    
    if not code:
        return HttpResponse("No authorization code received", status=400)
    
    try:
        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'client_id': "1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com",
            'client_secret': "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",  # Updated July 30, 2025
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': "https://gaming-studio.onrender.com/auth/google/callback/",
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            return HttpResponse(f"Failed to get access token: {token_json}", status=400)
        
        # Get user info from Google
        user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={token_json['access_token']}"
        user_response = requests.get(user_info_url)
        user_data = user_response.json()
        
        # Create or get user
        email = user_data.get('email')
        name = user_data.get('name', email.split('@')[0])
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': user_data.get('given_name', ''),
                'last_name': user_data.get('family_name', ''),
            }
        )
        
        # Log the user in
        login(request, user)
        
        # Success page
        return HttpResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to Gaming Studio!</title>
    <meta http-equiv="refresh" content="3;url=/">
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #2c3e50, #3498db); color: white; }}
        .success {{ background: rgba(255,255,255,0.9); color: #2c3e50; padding: 40px; border-radius: 20px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="success">
        <h1>🎉 Welcome to Gaming Studio!</h1>
        <p>Successfully signed in as <strong>{name}</strong></p>
        <p>Redirecting to home page...</p>
        <p><a href="/">Continue to Gaming Studio</a></p>
    </div>
</body>
</html>
""")
        
    except Exception as e:
        return HttpResponse(f"Authentication failed: {str(e)}", status=500)
