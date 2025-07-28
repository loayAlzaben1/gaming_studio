from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from studio.media_views import serve_media
from studio.temp_auth_views import temporary_login, temporary_signup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('studio.urls')),
    # Temporary auth URLs until allauth tables are created
    path('accounts/login/', temporary_login, name='account_login'),
    path('accounts/signup/', temporary_signup, name='account_signup'),
    # path('accounts/', include('allauth.urls')),  # Commented out temporarily
]

# Serve media files
if settings.DEBUG:
    # Development - use Django's built-in static serve
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Production - use custom media serving
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media, name='media'),
    ]

# Serve files from the project root (for Google verification HTML)
urlpatterns += static('/', document_root=settings.BASE_DIR)