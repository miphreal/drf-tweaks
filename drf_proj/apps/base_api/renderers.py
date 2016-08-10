import logging
import os
import re
import sys

from django.conf import settings
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import Http404
from django.utils.encoding import smart_text
from rest_framework import exceptions, status
from rest_framework.renderers import JSONRenderer as _JSONRenderer
from rest_framework.response import Response
from rest_framework.utils import formatting

from .codes import Codes, Code
from .patch import unpack_validation_message


logger = logging.getLogger(__name__)


def exception_proxy_handler(exc, ctx):
    """
    Proxies exceptions to the response (so renderers can generated corresponding output)

    Sets corresponding http code.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    headers = {}

    if isinstance(exc, exceptions.NotAuthenticated):
        exc.status_code = status_code = exceptions.NotAuthenticated.status_code

    elif isinstance(exc, exceptions.APIException):
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['X-Throttle-Wait-Seconds'] = '%d' % exc.wait
        status_code = exc.status_code

    elif isinstance(exc, (Http404, ObjectDoesNotExist)):
        status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exc, PermissionDenied):
        status_code = status.HTTP_403_FORBIDDEN

    if status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        logger.exception(exc)

    return Response(data=exc, status=status_code, headers=headers)


class CustomJSONRenderer(_JSONRenderer):
    """
    Renderer which serializes to structured response {msg: .., status: .., code: .., data: .., meta: ..}
    """
    debug_internal_errors = settings.DEBUG

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = None
        if renderer_context and 'response' in renderer_context:
            response = renderer_context['response']
            request = renderer_context.get('request')
            if request and getattr(request, 'version', None) in settings.API_PENDING_DEPRECATION_VERSIONS:
                response['Warning'] = '299 - "Pending Deprecation: maintained until {}"'.format(
                    settings.API_PENDING_DEPRECATION_VERSIONS[request.version]
                )

        data = self._transform_response(payload=data, response=response)

        return super(CustomJSONRenderer, self).render(
            data, accepted_media_type=accepted_media_type, renderer_context=renderer_context)

    def _transform_response(self, payload, response=None):
        meta = None
        overwrite_status = None
        overwrite_msg = None

        if hasattr(response, 'extra'):
            meta = response.extra.get('meta', None)
            overwrite_status = response.extra.get('status_text', None)
            overwrite_msg = response.extra.get('msg_text', None)

        if isinstance(payload, Exception):
            code, data = self._handle_exception(payload)

        elif isinstance(payload, Code):
            code, data = payload, payload.data
            if data is Code.unset:
                data = None

        else:
            data = payload
            code = Codes.OK

        resp = self._prepare_api_response(data, code, meta)

        if overwrite_msg is not None:
            resp['msg'] = overwrite_msg

        if overwrite_status is not None:
            resp['status'] = overwrite_status

        return resp

    def _prepare_api_response(self, data, code, meta=None):
        resp = self._serialize_code(code)
        resp['data'] = data  # the `data` parameter has higher priority than `code.data`

        if meta is not None:
            resp['meta'] = meta

        return resp

    def _serialize_code(self, code, case=None, data=None, **extra):
        serialized_data = {
            'code': code.code_value,
            'status': code.code_name,
        }
        if code.data is not Code.unset:
            serialized_data['data'] = code.data

        serialized_data['msg'] = code.message if code.message is not Code.unset else None

        serialized_data.update(**extra)

        if case is not None:
            serialized_data['case'] = case

        if data:
            d = serialized_data.get('data', None)
            if d:
                d = d.copy()
            else:
                d = {}
            d.update(data)
            serialized_data['data'] = d

        return serialized_data

    def _unpack_validation_error(self, validation_error):
        message_code, validation_subcode, message, custom_data = unpack_validation_message(validation_error)

        # pulling corresponding response code from the map
        validation_code = Codes.validation_errors_map.get(message_code)

        if not validation_code:
            validation_code = Codes.validation_errors_map['default']

        return validation_code, validation_subcode, message, custom_data

    @classmethod
    def _flatten_validation_errors(cls, errors, field_prefix=''):
        for field, msg in errors.items():
            if isinstance(msg, dict):
                for sub_field, sub_msg in cls._flatten_validation_errors(msg, field):
                    yield sub_field, sub_msg
            else:
                yield (
                    '{}.{}'.format(field_prefix, field) if field_prefix else field,
                    msg
                )

    def _handle_exception(self, exc):
        data = None

        if isinstance(exc, (exceptions.APIException, Http404, PermissionDenied, ObjectDoesNotExist)):
            # api related errors
            code = Codes.exceptions_map.get(
                exc.__class__.__name__, Codes.API_ERROR)

            if code.message is Code.unset:
                code = code(message=str(exc))

            if isinstance(exc, exceptions.ValidationError):
                code, data = Codes.VALIDATION_ERROR, exc.detail

                errors = []

                if hasattr(data, 'items'):
                    for field, validation_errors in self._flatten_validation_errors(data):
                        field = re_camel_finder.sub(underscore_to_camel, field)

                        for validation_error in validation_errors:
                            validation_code, subcode, message, custom_data = self._unpack_validation_error(validation_error)
                            errors.append(self._serialize_code(
                                code=validation_code(message=message, data={'field': field}),
                                case=subcode, data=custom_data
                            ))

                    data = errors

                elif isinstance(data, (list, tuple)):
                    data = [self._serialize_code(c(message=m), case=sc, data=d) for c, sc, m, d in map(self._unpack_validation_error, data)]

                elif data:
                    code = code(message=str(data))
                    data = None

                if len(data) > 1:
                    code = Codes.MULTIPLE_ERRORS
                elif len(data) == 1:
                    # in case of one validation error, unpack it
                    data = data[0]

        else:
            # Ignore all other exceptions
            code = Codes.INTERNAL_ERROR
            if self.debug_internal_errors:
                logger.exception('Api responds with exception: %s', exc)

        return code, data


re_camel_finder = re.compile(r'[a-z]_[a-z]')


def underscore_to_camel(match):
    g = match.group()
    return g[0] + g[2].upper()


def camelize(data):
    if isinstance(data, dict):
        return {
            (re_camel_finder.sub(underscore_to_camel, key)
             if isinstance(key, str) else key): camelize(value)
            for key, value in data.items()
        }
    if isinstance(data, (list, tuple)):
        return [camelize(i) for i in data]
    return data


class JsonRenderer(CustomJSONRenderer):
    """Camelized output"""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return super(JsonRenderer, self).render(
            camelize(data), accepted_media_type=accepted_media_type, renderer_context=renderer_context)


class VendorJsonRenderer(JsonRenderer):
    media_type = 'application/vnd.drf+json'


def get_view_description(view_cls, html=False):
    from django_markwhat.templatetags.markup import restructuredtext
    description = view_cls.__doc__ or ''
    description = formatting.dedent(smart_text(description))
    if html:
        rst_doc = getattr(view_cls, 'rst_doc', None)
        if rst_doc:
            if isinstance(rst_doc, str):
                path = os.path.dirname(sys.modules[view_cls.__module__].__file__)
                path = os.path.join(path, rst_doc)
                with open(path) as rst:
                    return restructuredtext(rst.read())
            return restructuredtext(description)
        return formatting.markup_description(description)
    return description