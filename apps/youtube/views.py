from django.http import JsonResponse

def index(request):
    """Simple health‑style endpoint for the YouTube app."""
    return JsonResponse({"status": "ok", "app": "youtube"})
