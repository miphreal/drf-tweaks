from django.contrib.auth import logout
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_proj.apps.base_api.base_views import BaseView


class LogoutView(BaseView):
    rst_doc = 'docs/logout.rst'
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return Response(None)
