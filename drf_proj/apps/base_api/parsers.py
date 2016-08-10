from djangorestframework_camel_case.util import underscoreize, camel_to_underscore
from rest_framework.settings import api_settings


class CamelCaseQueryStringParser(object):
    parsing_values = (
        api_settings.ORDERING_PARAM,
        'fields',
    )

    @classmethod
    def parse(cls, request):
        from django.http.request import QueryDict
        tmp = QueryDict('', mutable=True)
        data = underscoreize(dict(request.GET))
        for k, v in data.items():
            if k in cls.parsing_values:
                if isinstance(v, str):
                    v = camel_to_underscore(v)
                elif isinstance(v, list):
                    v = [(camel_to_underscore(v_) if isinstance(v_, str) else v_) for v_ in v]
            tmp.setlistdefault(k, v)
        return tmp
