from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_proj.apps.base_api.base_views import BaseView


class TestView(BaseView):
    """
    Test API endpoint
    """
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        if request.query_params.get('exception'):
            raise NotFound('test exception')

        return Response({
            'api_version': str(self.version),
            'camelized_data_property': 'data_value'
        })
