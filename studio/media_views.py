from django.http import HttpResponse, Http404
from django.conf import settings
import os
import mimetypes
from django.views.decorators.cache import cache_control

@cache_control(max_age=3600)  # Cache for 1 hour
def serve_media(request, path):
    """Serve media files in production"""
    if settings.DEBUG:
        # In development, let Django's static serve handle this
        raise Http404("This view is only for production")
    
    try:
        # Build the full file path
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise Http404("Media file not found")
        
        # Determine the content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Read and serve the file
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Length'] = os.path.getsize(file_path)
            return response
            
    except Exception:
        raise Http404("Error serving media file")
