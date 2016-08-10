from django.contrib.auth import login, logout, authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_proj.apps.base_api.base_views import BaseView
from drf_proj.apps.base_api.exceptions import UserIsNotActive
from drf_proj.apps.base_api.validators import BaseValidator
from drf_proj.apps.base_api.serializers import BaseSerializer


#
# Validator
class CredentialsValidator(BaseValidator):
    username = serializers.CharField()
    password = serializers.CharField(max_length=32)


# Serializer
class UserSerializer(BaseSerializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    username = serializers.CharField()
    is_authenticated = serializers.BooleanField()


#
# Controller
class LoginView(BaseView):
    rst_doc = 'docs/login.rst'
    permission_classes = (AllowAny,)
    validator_class = CredentialsValidator
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return Response(self._serialize_obj(self.request.user))
        return Response({'is_authenticated': False})

    def create(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(request)

        user = None
        validator = self.get_validator(data=request.data)

        if validator.is_valid(raise_exception=True):
            user = authenticate(**validator.validated_data)
            if user is not None:
                if not user.is_active:
                    raise UserIsNotActive()
                login(request, user)

        if user is not None:
            return Response(self._prepare_response(user))
        raise AuthenticationFailed(detail='The email (username) or password you entered is not valid.')
