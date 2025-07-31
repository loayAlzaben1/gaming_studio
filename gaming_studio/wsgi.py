"""
WSGI config for gaming_studio project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')

# Emergency DB setup (guarantee tables before app loads)
try:
    import emergency_db_setup
    emergency_db_setup.create_essential_tables()
    print("✅ Emergency DB setup completed at WSGI startup!")
except Exception as e:
    print(f"⚠️ Emergency DB setup error at WSGI startup: {e}")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
