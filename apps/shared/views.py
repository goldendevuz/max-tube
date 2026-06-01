from django.http import JsonResponse

def health_check(request):
    """Simple health endpoint for Docker healthcheck."""
    return JsonResponse({"status": "ok"})
