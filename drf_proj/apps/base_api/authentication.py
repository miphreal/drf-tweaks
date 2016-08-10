from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import SessionAuthentication


class APIAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        pass


class BaseAuthBackend(ModelBackend):

    def _authenticate(self, password=None, **auth_kw):
        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get(**auth_kw)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)


class UsernameAuthBackend(BaseAuthBackend):

    def authenticate(self, username, password=None, **kwargs):
        return self._authenticate(
            username__iexact=username,
            password=password
        )


class EmailAuthBackend(BaseAuthBackend):

    def authenticate(self, email, password=None, **kwargs):
        return self._authenticate(
            email__iexact=email,
            password=password
        )
