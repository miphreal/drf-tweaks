import logging

from corsheaders.middleware import CorsMiddleware as _CorsMiddleware
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from semantic_version import Version, Spec


logger = logging.getLogger(__name__)


class CorsMiddleware(MiddlewareMixin, _CorsMiddleware):
    pass


class ApiClientRestrictionMiddleware(MiddlewareMixin):
    CLIENT_HEADER = 'HTTP_X_CLIENT_VERSION'
    SUPPORTED_CLIENTS = (
        ('ios', Spec('>=1.0.0')),
        ('chrome-ext', Spec('>=0.1.2')),
    )
    HTTP_CODE = 418

    def html_response(self):
        response = HttpResponse(
            '<html><title>Upgrade required</title>'
            '<body><h1>'
            'Your version of application is out of date '
            'and will not be supported anymore. Please upgrade.'
            '</h1></body></html>', content_type='text/html')
        response.status_code = self.HTTP_CODE
        return response

    def api_response(self):
        response = HttpResponse(
            '{"status": "ClientUpgradeRequired",'
            '"msg": "Your version of application is out of date '
            'and will not be supported anymore. Please upgrade.",'
            '"code": 1350,"data": null}', content_type='application/json')
        response.status_code = self.HTTP_CODE
        return response

    def unsupported(self, request):
        http_accept = request.META.get('HTTP_ACCEPT', 'application/json')
        if http_accept == '*/*':
            http_accept = 'application/json'
        if 'application/json' in http_accept:
            return self.api_response()
        return self.html_response()

    def is_supported_client(self, client_version, request):
        client_name, tmp, client_version = (client_version or '').strip().partition('/')
        try:
            client_name = client_name.strip().lower()
            client_version = client_version.strip().lower()
            client_version = Version(client_version, partial=True)
            request.client_name = client_name
            request.client_version = client_version
            request.client_version_info = '{}/{}'.format(client_name, client_version)
        except ValueError as e:
            logger.warning('Incorrect client version: %s', e)
            return False

        for supported_client, supported_versions in self.SUPPORTED_CLIENTS:
            if supported_client == client_name and client_version in supported_versions:
                return True

        return False

    def process_request(self, request):
        client_version_info = request.META.get(self.CLIENT_HEADER)
        request.client_version_info = client_version_info
        request.client_name = None
        request.client_version = None

        if client_version_info and not self.is_supported_client(client_version_info, request):
            return self.unsupported(request=request)
