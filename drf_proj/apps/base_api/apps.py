from django.apps import AppConfig
from django.core.checks import register, Error
from django.utils.translation import ugettext_lazy as _


def codes_check(app_configs, **kwargs):
    from .codes import Codes

    messages = []

    used_codes = set()

    for name, (code_value, code_name) in Codes.codes().items():
        if code_value in used_codes:
            messages.append(
                Error(msg=(
                    'Code "{}" = {} is already presented in codes. '
                    'Please, choose another code value.'.format(name, code_value)
                ), id='api.E001', obj=(code_value, code_name))
            )
        used_codes.add(code_value)

    return messages


class ApiConfig(AppConfig):
    name = 'drf_proj.apps.base_api'
    verbose_name = _('Base Api App')

    def ready(self):
        register('api')(codes_check)
