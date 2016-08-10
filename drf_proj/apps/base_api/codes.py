"""Api codes/errors"""

from django.utils.translation import ugettext_lazy as _


class Code(object):
    unset = object()

    def __init__(self, code_value, code_name, message=unset, data=unset):
        self.code_value = code_value
        self.code_name = code_name
        self._message = message
        self.data = data

    def __call__(self, code_value=None, code_name=None, message=None, data=None):
        kwargs = {
            'code_value': code_value or self.code_value,
            'code_name': code_name or self.code_name,
            'message': message or self._message,
            'data': data or self.data,
        }
        return Code(**kwargs)

    @property
    def message(self):
        return str(self._message) if self._message is not self.unset else self._message


class Codes(object):
    # Success
    OK = Code(0, 'OK')

    # Errors
    ERROR = Code(1000, 'Error', _('Something went wrong.'))
    API_ERROR = Code(1002, 'ApiError', _('Api logic faced some issues processing the request.'))
    MULTIPLE_ERRORS = Code(2000, 'MultipleErrors', _('Multiple errors happened.'))
    DEPRECATED = Code(3000, 'DeprecationError', _('The api was deprecated. Please, upgrade to new version of the api.'))

    # System errors
    INTERNAL_ERROR = Code(1001, 'InternalError', _('An internal error occurred.'))
    TEMPORARILY_UNAVAILABLE = Code(1003, 'TemporarilyUnavailable')
    PARSE_ERROR = Code(1100, 'ParseError')

    BAD_REQUEST = Code(1101, 'BadRequest')
    NOT_FOUND = Code(1104, 'NotFound')
    METHOD_NOT_ALLOWED = Code(1105, 'MethodNotAllowed')

    # Client errors
    AUTHENTICATION_ERROR = Code(1200, 'AuthenticationError')
    AUTHORIZATION_ERROR = Code(1300, 'AuthorizationError')
    PERMISSION_DENIED = Code(1301, 'PermissionDenied')

    USER_IS_NOT_ACTIVE = Code(1311, 'UserIsNotActive')
    EMAIL_IS_NOT_CONFIRMED = Code(1312, 'EmailIsNotConfirmed')
    BETA_ACCESS_REQUIRED = Code(1313, 'BetaAccessRequired')
    EMAIL_CONFIRMATION_EXPIRED = Code(1314, 'EmailConfirmationExpired')

    CONFLICT_STATE = Code(1320, 'ConflictState')
    ALREADY_REGISTERED = Code(1321, 'AlreadyRegistered')
    ALREADY_LOGGED_IN = Code(1322, 'AlreadyLoggedIn')

    CLIENT_UPGRADE_REQUIRED = Code(1350, 'ClientUpgradeRequired')

    # - validation errors
    VALIDATION_ERROR = Code(1400, 'ValidationError')
    REQUIRED_VALUE = Code(1451, 'RequiredValue')

    NON_NULLABLE_VALUE = Code(1452, 'NonNullableValue')
    INVALID_VALUE = Code(1453, 'InvalidValue')
    NON_BLANK_VALUE = Code(1454, 'NonBlankValue')

    MIN_VALUE_LIMIT = Code(1455, 'MinValueLimit')
    MAX_VALUE_LIMIT = Code(1456, 'MaxValueLimit')
    MIN_STRING_LENGTH = Code(1457, 'MinStringValueLimit')
    MAX_STRING_LENGTH = Code(1458, 'MaxStringValueLimit')

    MAX_DIGITS_LIMIT = Code(1459, 'MaxDigitsLimit')
    MAX_DECIMAL_PLACES_LIMIT = Code(1460, 'MaxDecimalPlacesLimit')
    MAX_WHOLE_DIGITS_LIMIT = Code(1461, 'MaxWholeDigitsLimit')

    DATETIME_EXPECTED = Code(1462, 'DatetimeExpected')  # Expected a datetime but got a date

    INVALID_CHOICE = Code(1463, 'InvalidChoice')

    LIST_EXPECTED = Code(1464, 'ListExpected')  # Expected a list of items

    NO_FILENAME_ERROR = Code(1465, 'NoFilenameError')  # No filename could be determined
    EMPTY_FILE_ERROR = Code(1466, 'EmptyFileError')  # The submitted file is empty

    INVALID_IMAGE = Code(1467, 'InvalidImage')  # The submitted file is empty
    OBJECT_ALREADY_EXISTS = Code(1468, 'AlreadyExists')

    DATE_EXPECTED = Code(1469, 'DateExpected')  # Expected a date but got a datetime
    IMMUTABLE_VALUE = Code(1470, 'ImmutableValue')
    EXPIRED_VALUE = Code(1471, 'ExpiredValue')

    # validation mapping
    # - validation aliases
    class ValidationAliases(object):
        DEFAULT = 'default'
        REQUIRED = 'required'
        NULL = 'null'
        INVALID = 'invalid'
        BLANK = 'blank'
        MIN_LENGTH = 'min_length'
        MAX_LENGTH = 'max_length'
        MAX_STRING_LENGTH = 'max_string_length'
        MIN_VALUE = 'min_value'
        MAX_VALUE = 'max_value'
        MAX_DIGITS = 'max_digits'
        MAX_DECIMAL_PLACES = 'max_decimal_places'
        MAX_WHOLE_DIGITS = 'max_whole_digits'
        DATE = 'date'
        DATETIME = 'datetime'
        INVALID_CHOICE = 'invalid_choice'
        NOT_A_LIST = 'not_a_list'
        NO_NAME = 'no_name'
        EMPTY = 'empty'
        INVALID_IMAGE = 'invalid_image'
        ALREADY_EXISTS = 'already_exists'
        IMMUTABLE = 'immutable'
        EXPIRED = 'expired'

    # - validation alias -> code mapping
    validation_errors_map = {
        ValidationAliases.DEFAULT: VALIDATION_ERROR,
        ValidationAliases.REQUIRED: REQUIRED_VALUE,
        ValidationAliases.NULL: NON_NULLABLE_VALUE,
        ValidationAliases.INVALID: INVALID_VALUE,
        ValidationAliases.BLANK: NON_BLANK_VALUE,
        ValidationAliases.IMMUTABLE: IMMUTABLE_VALUE,
        ValidationAliases.EXPIRED: EXPIRED_VALUE,

        ValidationAliases.MIN_LENGTH: MIN_STRING_LENGTH,
        ValidationAliases.MAX_LENGTH: MAX_STRING_LENGTH,
        ValidationAliases.MAX_STRING_LENGTH: MAX_STRING_LENGTH,  # Guard against malicious string inputs.
                                                                 # Refers number types

        ValidationAliases.MIN_VALUE: MIN_VALUE_LIMIT,
        ValidationAliases.MAX_VALUE: MAX_VALUE_LIMIT,

        ValidationAliases.MAX_DIGITS: MAX_DIGITS_LIMIT,
        ValidationAliases.MAX_DECIMAL_PLACES: MAX_DECIMAL_PLACES_LIMIT,
        ValidationAliases.MAX_WHOLE_DIGITS: MAX_WHOLE_DIGITS_LIMIT,

        ValidationAliases.DATE: DATETIME_EXPECTED,
        ValidationAliases.DATETIME: DATE_EXPECTED,

        ValidationAliases.INVALID_CHOICE: INVALID_CHOICE,
        ValidationAliases.NOT_A_LIST: LIST_EXPECTED,

        ValidationAliases.NO_NAME: NO_FILENAME_ERROR,
        ValidationAliases.EMPTY: NO_FILENAME_ERROR,

        ValidationAliases.INVALID_IMAGE: INVALID_IMAGE,
        ValidationAliases.ALREADY_EXISTS: OBJECT_ALREADY_EXISTS,
    }

    # exceptions mapping
    exceptions_map = {
        'AuthenticationFailed': AUTHENTICATION_ERROR,
        'NotAuthenticated': AUTHENTICATION_ERROR,
        'AuthorizationFailed': AUTHORIZATION_ERROR,
        'Exception': INTERNAL_ERROR,
        'Http404': NOT_FOUND,
        'DoesNotExist': NOT_FOUND,
        'ObjectDoesNotExist': NOT_FOUND,
        'EmailConfirmationHasExpired': EMAIL_CONFIRMATION_EXPIRED,
        'ApiDeprecated': DEPRECATED,
        'DeprecationWarning': DEPRECATED,
    }

    for code in list(locals().values()):
        if isinstance(code, Code):
            exceptions_map[code.code_name] = code
    del code

    @classmethod
    def codes(cls):
        codes = {}
        for code_name, code in vars(cls).items():
            if isinstance(code, Code):
                codes[code_name] = (code.code_value, code.code_name)

        return codes
