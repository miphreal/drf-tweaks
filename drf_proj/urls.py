from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url


urlpatterns = [
    url(r'^api/(?P<version>1\.\d{1,4}(\.\d{1,4})?)/', include(settings.API_LATEST_VERSION_URLS)),
    url(r'^api/((?P<version>\d{1,4}(\.\d{1,4}(\.\d{1,4})?)?)/)?', include(settings.API_LATEST_VERSION_URLS)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
