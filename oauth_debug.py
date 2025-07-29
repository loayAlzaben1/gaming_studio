"""
OAuth debugging page to help diagnose 403 errors
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

@csrf_exempt
def oauth_debug(request):
    """Debug OAuth configuration"""
    try:
        # Check sites
        sites = Site.objects.all()
        site_info = [f"{s.id}: {s.domain} ({s.name})" for s in sites]
        
        # Check Google OAuth apps
        google_apps = SocialApp.objects.filter(provider='google')
        oauth_info = []
        for app in google_apps:
            oauth_info.append(f"App: {app.name}")
            oauth_info.append(f"Client ID: {app.client_id}")
            oauth_info.append(f"Has Secret: {'Yes' if app.secret else 'No'}")
            oauth_info.append(f"Sites: {[s.domain for s in app.sites.all()]}")
            oauth_info.append("---")
        
        # Generate OAuth URLs for testing
        client_id = "1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com"
        base_url = "https://accounts.google.com/oauth/authorize"
        redirect_uri = "https://gaming-studio.onrender.com/accounts/google/login/callback/"
        
        # Multiple test URLs with different parameters
        test_urls = [
            f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope=openid%20email%20profile&response_type=code&state=debug_test",
            f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope=email%20profile&response_type=code&state=debug_minimal",
            f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope=openid&response_type=code&state=debug_openid_only",
        ]
        
        return HttpResponse(f"""
<!DOCTYPE html>
<html>
<head><title>OAuth Debug</title></head>
<body>
    <h1>🔍 OAuth Configuration Debug</h1>
    
    <h2>Sites Configuration:</h2>
    <ul>{"".join([f"<li>{s}</li>" for s in site_info])}</ul>
    
    <h2>Google OAuth Apps:</h2>
    <div>{"<br>".join(oauth_info) if oauth_info else "❌ No Google OAuth apps found!"}</div>
    
    <h2>Test OAuth URLs:</h2>
    <p><strong>Try these different OAuth configurations:</strong></p>
    <ol>
        <li><a href="{test_urls[0]}" target="_blank">Full Scope Test (openid email profile)</a></li>
        <li><a href="{test_urls[1]}" target="_blank">Minimal Scope Test (email profile)</a></li>
        <li><a href="{test_urls[2]}" target="_blank">OpenID Only Test</a></li>
    </ol>
    
    <h2>Required Google Console Settings:</h2>
    <p><strong>Make sure these URIs are in your Google Console:</strong></p>
    <ul>
        <li>https://gaming-studio.onrender.com/accounts/google/login/callback/</li>
        <li>http://127.0.0.1:8000/accounts/google/login/callback/</li>
        <li>http://localhost:8000/accounts/google/login/callback/</li>
        <li>https://gaming-studio.onrender.com/accounts/google/login/</li>
        <li>https://gaming-studio.onrender.com/accounts/social/login/cancelled/</li>
    </ul>
    
    <h2>Callback Test:</h2>
    <p><a href="/accounts/google/login/callback/?code=test&state=test">Test Callback URL</a></p>
    
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ccc; }}
        a {{ color: #007bff; }}
        ul, ol {{ margin-left: 20px; }}
    </style>
</body>
</html>
""")
    except Exception as e:
        return HttpResponse(f"Debug Error: {e}")
