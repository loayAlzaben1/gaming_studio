# Google OAuth Setup Guide for Gaming Studio

## Step 1: Google Cloud Console Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create or Select Project**
   - Click "Select a project" dropdown
   - Click "New Project"
   - Name: "Gaming Studio OAuth"
   - Click "Create"

3. **Enable APIs**
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" or "Google Identity API"
   - Click on it and press "Enable"

4. **Create OAuth Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Name: "Gaming Studio Web Client"

5. **Configure Authorized URIs**
   Add these URLs to "Authorized redirect URIs":
   - http://127.0.0.1:8000/accounts/google/login/callback/
   - http://localhost:8000/accounts/google/login/callback/
   - https://yourdomain.com/accounts/google/login/callback/ (for production)

6. **Get Your Credentials**
   - Copy the "Client ID" 
   - Copy the "Client Secret"

## Step 2: Update Django Settings

1. **Open Django Admin**
   - Go to: http://127.0.0.1:8000/admin/
   - Login with superuser account

2. **Update Social Application**
   - Go to "Social Applications"
   - Click on "Google OAuth (Development)"
   - Replace "Client ID" with your real Google Client ID
   - Replace "Secret key" with your real Google Client Secret
   - Save

## Step 3: Test OAuth

- Go to login page
- Click "Continue with Google"
- Should redirect to Google's OAuth consent screen
- After approval, should redirect back to your site

## Important Notes

- For development: Use http://127.0.0.1:8000 or http://localhost:8000
- For production: Use your actual domain with HTTPS
- Keep your client secret secure and never commit it to version control
- Consider using environment variables for production credentials

## Troubleshooting

- **Error 401: invalid_client** = Wrong client ID/secret
- **Error 400: redirect_uri_mismatch** = Redirect URI not configured in Google Cloud Console
- **Error 403: access_denied** = APIs not enabled or consent screen not configured
