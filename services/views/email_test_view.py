# services/views/email_test_api_view.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from services.utils.emails.email_service import EmailService

@csrf_exempt
@require_http_methods(["POST"])
def testar_template_email_api_view(request):
    """
    API para testar envio de e-mail via CURL ou POST JSON.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))

        subject = data.get("subject", "Teste de E-mail")
        to = data["to"]
        template_html = data["template_html"]
        context = data.get("context", {})

        email_service = EmailService(
            subject=subject,
            to_email=to,
            template_name=template_html,
            context=context
        )
        email_service.send()

        return JsonResponse({
            "status": "sent",
            "message": f"E-mail enviado com sucesso para {to} usando template {template_html}."
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
