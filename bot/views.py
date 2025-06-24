from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
@require_POST
def webhook(request):
    """Webhook endpoint for Telegram bot"""
    try:
        data = json.loads(request.body)
        return HttpResponse("OK")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=400)
