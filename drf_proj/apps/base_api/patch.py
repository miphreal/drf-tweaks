import base64
import marshal

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import request, fields
from rest_framework.exceptions import ValidationError

from .parsers import CamelCaseQueryStringParser


# Patching rest_framework Request in order to allow querystring params camelcase conversion
@property
def query_params(self):
    """
    Camel case converter for querystring
    """
    if not hasattr(self, '__query_params'):
        self.__query_params = CamelCaseQueryStringParser.parse(self._request)
    return self.__query_params


def patch_request():
    request.Request.patched_query_params = request.Request.query_params
    request.Request.query_params = query_params


# Patching rest_framework Field, in order to intercept validation code for handling proper response output
def pack_validation_message(message, code, case=None, data=None):
    return base64.b64encode(marshal.dumps((str(message), code, case, data)))


def unpack_validation_message(packed_message):
    try:
        msg, code, case, data = marshal.loads(base64.b64decode(packed_message))
        return code, case, msg, data
    except (TypeError, base64.binascii.Error):
        return None, None, packed_message, None


def field_fail(self, key, **kwargs):
    """
    Attaches extra validation code to the message
    """
    try:
        self.patched_fail(key, **kwargs)
    except ValidationError as e:
        if isinstance(e.detail, list):
            e.detail = [pack_validation_message(m, key, getattr(e, 'case', None)) for m in e.detail]
        raise


def field_run_validators(self, value):
    """
    Attaches extra validation code to the messages
    """
    errors = []
    for validator in self.validators:
        if hasattr(validator, 'set_context'):
            validator.set_context(self)

        try:
            validator(value)
        except ValidationError as exc:
            if isinstance(exc.detail, dict):
                raise

            if isinstance(exc.detail, str):
                exc.detail = pack_validation_message(exc.detail,
                                                     getattr(validator, 'code', None),
                                                     getattr(exc, 'case', None))

            errors.extend(exc.detail)
        except DjangoValidationError as exc:
            errors.extend([pack_validation_message(m, exc.code) for m in exc.messages])
    if errors:
        raise ValidationError(errors)


def patch_base_field():
    fields.Field.patched_fail = fields.Field.fail
    fields.Field.fail = field_fail
    fields.Field.patched_run_validators = fields.Field.run_validators
    fields.Field.run_validators = field_run_validators
