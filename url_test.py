"""
URL test page to verify OAuth routing
"""
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  
def url_test(request):
    """Test page to show available URLs"""
    try:
        # Try to get the allauth URLs
        google_login_url = "/accounts/google/login/"
        google_callback_url = "/accounts/google/login/callback/"
        
        return HttpResponse(f"""
<!DOCTYPE html>
<html>
<head><title>URL Test</title></head>
<body>
    <h1>🔍 URL Routing Test</h1>
    <h2>Available URLs:</h2>
    <ul>
        <li><a href="/signup/">Custom Signup Page</a></li>
        <li><a href="/login/">Custom Login Page</a></li>
        <li><a href="{google_login_url}">Google Login (allauth)</a></li>
        <li><a href="{google_callback_url}">Google Callback (should give error without params)</a></li>
        <li><a href="/accounts/login/">Allauth Login</a></li>
        <li><a href="/accounts/signup/">Allauth Signup</a></li>
    </ul>
    
    <h2>OAuth Test:</h2>
    <p><a href="https://accounts.google.com/oauth/authorize?client_id=1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com&redirect_uri=https://gaming-studio.onrender.com/accounts/google/login/callback/&scope=openid%20email%20profile&response_type=code&state=url_test" class="button">🔍 Test Google OAuth</a></p>
    
    <style>
        .button {{ background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
    </style>
</body>
</html>
""")
    except Exception as e:
        return HttpResponse(f"Error: {e}")
