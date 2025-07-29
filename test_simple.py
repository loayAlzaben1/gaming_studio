"""
Simple test page to debug production issues
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def simple_test(request):
    """Ultra simple test page"""
    return HttpResponse("""
<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
    <h1>✅ Django is Working!</h1>
    <p>If you see this, the basic Django setup is OK.</p>
    <p>Time: {}</p>
</body>
</html>
""".format(str(request)))
