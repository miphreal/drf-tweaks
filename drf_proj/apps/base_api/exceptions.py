from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException, AuthenticationFailed, PermissionDenied, ValidationError


class ApiError(APIException):
    pass


class TemporarilyUnavailable(ApiError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('Service is temporarily unavailable, please try later.')


class ConflictState(ApiError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('Conflict state.')


class AlreadyRegistered(ConflictState):
    default_detail = _('Already registered.')


class AlreadyLoggedIn(ConflictState):
    default_detail = _('Already logged in.')


class UserIsNotActive(PermissionDenied, ApiError):
    default_detail = _('User is not active.')


class EmailIsNotConfirmed(PermissionDenied, ApiError):
    default_detail = _('The email was not confirmed.')


class EmailConfirmationHasExpired(ApiError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('The email confirmation token has expired.')


class ApiValidationError(ValidationError, ApiError):
    def __init__(self, detail, code=None, case=None, data=None):
        from .patch import pack_validation_message

        self.code = code
        self.case = case

        if code and (isinstance(detail, str) or
                     getattr(detail, '_delegate_text', False)):  # proxy object
            detail = pack_validation_message(detail, code, case, data)

        super(ApiValidationError, self).__init__(detail)


class ApiDeprecated(ApiError):
    status_code = status.HTTP_410_GONE
