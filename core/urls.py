import os
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from services.views.email_test_view import testar_template_email_api_view


# Tratamento de erro 404 customizado
handler404 = 'core.views.custom_404'

urlpatterns = [
    path('', lambda r: HttpResponse("API Alvelos ativa")),
    path('health/', lambda r: JsonResponse({"status": "ok"})),
    path('api/version/', lambda r: JsonResponse({"version": "1.0.0"})),

    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),

    # Endpoints reais
    # path('api/', include('services.urls')),
    path('api/auth/', include('authentication.urls')),
    path('testar-template-email/', testar_template_email_api_view, name='testar-template-email'),
]

# Arquivos estáticos e mídia (modo dev)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))
    urlpatterns += static(settings.MEDIA_URL, document_root=os.path.join(settings.BASE_DIR, 'media'))
