from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_proj.apps.base_api.base_views import BaseView


class TestView(BaseView):
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        return Response({
            'api_version': str(self.version),
            'camelized_data_property': 'data_value'
        })
