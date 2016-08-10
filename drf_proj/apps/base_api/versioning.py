from django.conf import settings
from rest_framework import exceptions
from rest_framework.versioning import BaseVersioning, _MediaType, unicode_http_header

from .exceptions import ApiDeprecated


class CustomVersioning(BaseVersioning):
    """Custom versioning schema:
    priority:
    - version in URL (e.g. /api/2.5.0/login)
    - version in Accept header (e.g. Accept: application/vnd.drf+json; version=2.5.0)
    """
    def determine_version(self, request, *args, **kwargs):
        version = kwargs.get(self.version_param)

        if not version:
            media_type = _MediaType(request.accepted_media_type)
            version = media_type.params.get(self.version_param)
            version = unicode_http_header(version)

        if version and not self.is_allowed_version(version):
            if version in settings.API_DEPRECATED_VERSIONS:
                raise ApiDeprecated('{!s} version of {!s} API is DEPRECATED.'.format(version, request.path_info))
            raise exceptions.NotFound('{!s} version of {!s} API is not found.'.format(version, request.path_info))

        elif not version:
            return self.default_version

        return version

    def reverse(self, viewname, args=None, kwargs=None, request=None, format=None, **extra):
        if request and request.version is not None:
            kwargs = {} if (kwargs is None) else kwargs
            kwargs[self.version_param] = request.version

        return super(CustomVersioning, self).reverse(
            viewname, args, kwargs, request, format, **extra
        )
