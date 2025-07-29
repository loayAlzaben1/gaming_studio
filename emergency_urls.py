"""
Emergency URL patterns to bypass authentication 500 errors
"""
from django.urls import path
from django.http import HttpResponse

def emergency_login(request):
    return HttpResponse("""
    <html><head><title>Gaming Studio - Maintenance</title></head>
    <body style="font-family:Arial;text-align:center;padding:50px;background:#1a1a2e;color:white;">
        <h1>🎮 Gaming Studio</h1>
        <h2>Authentication System Under Maintenance</h2>
        <p>We're fixing the production database. Gmail login will be restored shortly!</p>
        <a href="/" style="color:#4CAF50;">← Back to Home</a> | 
        <a href="/games/" style="color:#4CAF50;">View Games</a>
        <script>setTimeout(() => location.reload(), 30000);</script>
    </body></html>
    """)

def emergency_signup(request):
    return HttpResponse("""
    <html><head><title>Gaming Studio - Maintenance</title></head>
    <body style="font-family:Arial;text-align:center;padding:50px;background:#1a1a2e;color:white;">
        <h1>🎮 Gaming Studio - Join Us!</h1>
        <h2>Registration System Under Maintenance</h2>
        <p>Account creation with Gmail will be available once our database fix is complete!</p>
        <a href="/" style="color:#4CAF50;">← Back to Home</a> | 
        <a href="/games/" style="color:#4CAF50;">View Games</a>
        <script>setTimeout(() => location.reload(), 30000);</script>
    </body></html>
    """)

# Emergency URL patterns
emergency_patterns = [
    path('accounts/login/', emergency_login, name='emergency_login'),
    path('accounts/signup/', emergency_signup, name='emergency_signup'),
]
