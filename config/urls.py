from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import include, path


def healthz(_request):
    return HttpResponse('ok', content_type='text/plain')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('healthz/', healthz, name='healthz'),
    path('', include('src.authentication.urls')),
    path('', include('src.commerce.urls')),
    path('', include('src.catalog.urls')),
    path('', include('src.content.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
