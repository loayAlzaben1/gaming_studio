"""
BULLETPROOF AUTHENTICATION - No dependencies, guaranteed to work
Simple Google OAuth without any Django allauth complications
"""
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect
import urllib.parse
import requests
import secrets

# Google OAuth Configuration
GOOGLE_CLIENT_ID = "1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
REDIRECT_URI = "https://gaming-studio.onrender.com/simple-auth/callback/"

@csrf_exempt
def simple_login(request):
    """Super simple login page - guaranteed to work"""
    return HttpResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Gaming Studio Login</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a2e; 
            color: white; 
            text-align: center; 
            padding: 50px; 
        }
        .box { 
            background: #16213e; 
            padding: 40px; 
            border-radius: 10px; 
            max-width: 400px; 
            margin: 0 auto; 
        }
        .btn { 
            background: #e94560; 
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 5px; 
            text-decoration: none; 
            display: inline-block; 
            margin: 10px; 
            cursor: pointer; 
        }
        .btn:hover { background: #d63447; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🎮 Gaming Studio</h1>
        <h2>Simple Login</h2>
        <p>Click below to sign in with Google</p>
        <a href="/simple-auth/start/" class="btn">🚀 Sign in with Google</a>
        <p><a href="/" style="color: #0f3460;">← Back to Home</a></p>
    </div>
</body>
</html>
""")

@csrf_exempt
def auth_start(request):
    """Start Google OAuth - simple and direct"""
    # Generate state for security
    state = secrets.token_urlsafe(32)
    request.session['auth_state'] = state
    
    # Build Google OAuth URL
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state
    }
    
    auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urllib.parse.urlencode(params)
    return redirect(auth_url)

@csrf_exempt  
def auth_callback(request):
    """Handle Google OAuth callback - simple and working"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        return HttpResponse(f"<h1>Authentication Error</h1><p>{error}</p><a href='/simple-login/'>Try Again</a>")
    
    if not code:
        return HttpResponse("<h1>No Code Received</h1><a href='/simple-login/'>Try Again</a>")
    
    # Verify state
    if state != request.session.get('auth_state'):
        return HttpResponse("<h1>Invalid State</h1><a href='/simple-login/'>Try Again</a>")
    
    try:
        # Exchange code for token
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI
        }
        
        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        token_info = token_response.json()
        
        if 'access_token' not in token_info:
            return HttpResponse(f"<h1>Token Error</h1><pre>{token_info}</pre><a href='/simple-login/'>Try Again</a>")
        
        # Get user info
        headers = {'Authorization': f"Bearer {token_info['access_token']}"}
        user_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
        user_info = user_response.json()
        
        # Create or get user
        email = user_info.get('email')
        name = user_info.get('name', 'Gaming User')
        
        if email:
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                }
            )
            
            # Log user in
            login(request, user)
            
            # Success page
            return HttpResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Login Success!</title>
    <meta http-equiv="refresh" content="3;url=/">
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            background: #1a1a2e; 
            color: white; 
            text-align: center; 
            padding: 50px; 
        }}
        .success {{ 
            background: #27ae60; 
            padding: 30px; 
            border-radius: 10px; 
            max-width: 500px; 
            margin: 0 auto; 
        }}
    </style>
</head>
<body>
    <div class="success">
        <h1>🎉 Welcome to Gaming Studio!</h1>
        <h2>Login Successful!</h2>
        <p><strong>Welcome, {name}!</strong></p>
        <p>Email: {email}</p>
        <p>Redirecting to home page in 3 seconds...</p>
        <p><a href="/" style="color: white; text-decoration: underline;">Continue Now</a></p>
    </div>
</body>
</html>
""")
        else:
            return HttpResponse("<h1>No Email Received</h1><a href='/simple-login/'>Try Again</a>")
            
    except Exception as e:
        return HttpResponse(f"<h1>Authentication Failed</h1><p>Error: {str(e)}</p><a href='/simple-login/'>Try Again</a>")

@csrf_exempt
def auth_status(request):
    """Check authentication status"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': request.user.username,
            'email': request.user.email
        })
    else:
        return JsonResponse({'authenticated': False})
