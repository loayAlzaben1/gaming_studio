"""
Hybrid authentication pages that work with OAuth but use our beautiful UI
"""
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def hybrid_login(request):
    """Login page that works with OAuth but uses our beautiful UI"""
    # Check if this is an OAuth callback or error
    if request.GET.get('error') or request.GET.get('code'):
        # This is an OAuth response, let allauth handle it
        from allauth.socialaccount.views import login as allauth_login
        return allauth_login(request)
    
    # Otherwise show our beautiful login page
    return HttpResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Gaming Studio - Sign In</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: 'Arial', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            margin: 0; 
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            max-width: 400px; 
            width: 100%;
            background: rgba(0,0,0,0.8); 
            padding: 40px; 
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            text-align: center;
        }
        .logo { font-size: 3em; margin-bottom: 20px; }
        h1 { margin: 0 0 30px 0; font-size: 1.8em; }
        .button { 
            background: #4CAF50; 
            color: white; 
            padding: 15px 25px; 
            text-decoration: none; 
            border-radius: 8px; 
            display: inline-block; 
            margin: 10px;
            font-size: 1.1em;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            width: 80%;
        }
        .button:hover { 
            background: #45a049; 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .google-btn { 
            background: #db4437; 
            border: none;
        }
        .google-btn:hover { 
            background: #c23321; 
        }
        .links { 
            margin-top: 20px; 
        }
        .links a { 
            color: #ccc; 
            text-decoration: none; 
            margin: 0 10px;
        }
        .links a:hover { 
            color: white; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎮</div>
        <h1>Welcome Back to Gaming Studio!</h1>
        
        <a href="https://accounts.google.com/oauth/authorize?client_id=1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com&redirect_uri=https://gaming-studio.onrender.com/accounts/google/login/callback/&scope=openid%20email%20profile&response_type=code&state=gaming_studio" class="button google-btn">
            🔍 Continue with Google
        </a>
        
        <div class="links">
            <a href="/accounts/signup/">Don't have an account? Sign up</a><br>
            <a href="/">← Back to Home</a>
        </div>
    </div>
</body>
</html>
""")

@csrf_exempt  
def hybrid_signup(request):
    """Signup page that works with OAuth but uses our beautiful UI"""
    # Check if this is an OAuth callback or error
    if request.GET.get('error') or request.GET.get('code'):
        # This is an OAuth response, let allauth handle it
        from allauth.socialaccount.views import signup as allauth_signup
        return allauth_signup(request)
    
    # Otherwise show our beautiful signup page
    return HttpResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Gaming Studio - Sign Up</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: 'Arial', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            margin: 0; 
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            max-width: 400px; 
            width: 100%;
            background: rgba(0,0,0,0.8); 
            padding: 40px; 
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            text-align: center;
        }
        .logo { font-size: 3em; margin-bottom: 20px; }
        h1 { margin: 0 0 30px 0; font-size: 1.8em; }
        .button { 
            background: #4CAF50; 
            color: white; 
            padding: 15px 25px; 
            text-decoration: none; 
            border-radius: 8px; 
            display: inline-block; 
            margin: 10px;
            font-size: 1.1em;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            width: 80%;
        }
        .button:hover { 
            background: #45a049; 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .google-btn { 
            background: #db4437; 
            border: none;
        }
        .google-btn:hover { 
            background: #c23321; 
        }
        .links { 
            margin-top: 20px; 
        }
        .links a { 
            color: #ccc; 
            text-decoration: none; 
            margin: 0 10px;
        }
        .links a:hover { 
            color: white; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎮</div>
        <h1>Join Gaming Studio!</h1>
        
        <a href="https://accounts.google.com/oauth/authorize?client_id=1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com&redirect_uri=https://gaming-studio.onrender.com/accounts/google/login/callback/&scope=openid%20email%20profile&response_type=code&state=gaming_studio_signup" class="button google-btn">
            🔍 Sign up with Google
        </a>
        
        <div class="links">
            <a href="/accounts/login/">Already have an account? Sign in</a><br>
            <a href="/">← Back to Home</a>
        </div>
    </div>
</body>
</html>
""")
