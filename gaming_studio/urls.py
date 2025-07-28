from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from studio.media_views import serve_media

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('studio.urls')),
    path('accounts/', include('allauth.urls')),  # Restored full allauth functionality
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