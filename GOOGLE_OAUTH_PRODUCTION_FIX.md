# Google OAuth Configuration for Production

## Problem
When users try to sign in with Google, they get this error:
```
Error 400: redirect_uri_mismatch
```

## Solution

### Step 1: Update Google Cloud Console

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project**: "Gaming Studio"
3. **Navigate to**: APIs & Services → Credentials
4. **Find your OAuth client**: Should be named something like "Web application client"
5. **Click Edit** on your OAuth 2.0 Client ID
6. **In "Authorized redirect URIs" section, add these URLs**:

```
https://gaming-studio.onrender.com/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
http://localhost:8000/accounts/google/login/callback/
```

7. **Click Save**

### Step 2: Wait for Changes to Propagate
- Google OAuth changes can take 5-10 minutes to become active
- Try logging in again after waiting

### Step 3: Test the Login
1. Go to: https://gaming-studio.onrender.com
2. Click "Login" 
3. Choose "Continue with Google"
4. Should work without redirect_uri_mismatch error

## Current OAuth Client Details
- **Client ID**: 49621374950-b7knjfh86kkn2norpblsgsjk87sg632n.apps.googleusercontent.com
- **Project**: Gaming Studio

## Important Notes
- The redirect URI must be EXACTLY: `https://gaming-studio.onrender.com/accounts/google/login/callback/`
- Include the trailing slash `/`
- Use `https://` for production, not `http://`
- Keep the localhost URLs for development testing

## Testing
After making changes, test:
1. Production: https://gaming-studio.onrender.com
2. Local development: http://127.0.0.1:8000

Both should work for Google OAuth sign-in.
