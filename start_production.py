#!/usr/bin/env python
"""
Production server startup script for Render deployment
Runs deployment setup then starts the Django server
"""
import os
import sys
import subprocess

def main():
    print("🚀 Gaming Studio Production Startup")
    print("=" * 40)
    
    # Run deployment script first
    print("📦 Running production deployment setup...")
    try:
        result = subprocess.run([sys.executable, 'deploy_production.py'], 
                              capture_output=False, text=True)
        if result.returncode == 0:
            print("✅ Deployment setup completed")
        else:
            print("⚠️ Deployment setup had issues but continuing...")
    except Exception as e:
        print(f"❌ Deployment setup failed: {e}")
        print("🔄 Continuing with server startup...")
    
    print("\n🌐 Starting Django production server...")
    
    # Start Django server with production settings
    port = int(os.environ.get('PORT', 8000))
    host = '0.0.0.0'
    
    # Use gunicorn for production if available, otherwise use Django dev server
    try:
        # Try gunicorn first (production WSGI server)
        subprocess.run([
            'gunicorn', 
            '--bind', f'{host}:{port}',
            '--workers', '3',
            '--timeout', '120',
            'gaming_studio.wsgi:application'
        ])
    except FileNotFoundError:
        # Fallback to Django dev server
        print("📝 Using Django development server (install gunicorn for production)")
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', f'{host}:{port}'
        ])

if __name__ == "__main__":
    main()
