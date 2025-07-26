# Google OAuth Setup Instructions

## Current Issue
You're getting "redirect_uri_mismatch" error because your Google Cloud Console doesn't have OAuth clients configured.

## Step-by-Step Fix:

### 1. Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### 2. Select Your Project
Make sure you're in the correct project (Gaming Studio)

### 3. Enable Google+ API (if not enabled)
- Go to "APIs & Services" → "Library"
- Search for "Google+ API" 
- Click "Enable"

### 4. Configure OAuth Consent Screen
- Go to "APIs & Services" → "OAuth consent screen"
- Choose "External"
- Fill in:
  - **App name**: Gaming Studio
  - **User support email**: loay.alzaben0785590738@gmail.com
  - **App logo**: (optional)
  - **App domain**: gaming-studio.onrender.com
  - **Developer contact**: loay.alzaben0785590738@gmail.com
- Save and continue through all steps

### 5. Create OAuth 2.0 Client ID
- Go to "APIs & Services" → "Credentials"
- Click "CREATE CREDENTIALS" → "OAuth 2.0 Client ID"
- Choose "Web application"
- **Name**: Gaming Studio Web Client

### 6. Configure Authorized URLs

**Authorized JavaScript origins:**
```
https://gaming-studio.onrender.com
http://127.0.0.1:8000
http://localhost:8000
```

**Authorized redirect URIs:**
```
https://gaming-studio.onrender.com/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
http://localhost:8000/accounts/google/login/callback/
```

### 7. Save and Get Credentials
After clicking "CREATE", you'll get:
- **Client ID**: (copy this)
- **Client Secret**: (copy this)

### 8. Update Django (if you get new credentials)
If you created new credentials, run this command locally:

```bash
python manage.py update_google_oauth --client-id YOUR_NEW_CLIENT_ID --client-secret YOUR_NEW_CLIENT_SECRET --production
```

Then commit and push the changes.

## Current Credentials (if you want to reuse them)
The system is already configured with these credentials:
- **Client ID**: 49621374950-b7knjfh86kkn2norpblsgsjk87sg632n.apps.googleusercontent.com
- **Client Secret**: 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

You just need to add the redirect URIs to your Google Cloud Console OAuth client.

## Testing
After configuration:
1. Go to: https://gaming-studio.onrender.com/accounts/login/
2. Click "Sign in with Google"
3. Should work without redirect_uri_mismatch error
