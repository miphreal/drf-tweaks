from rest_framework.routers import DefaultRouter

from .auth import LoginView, LogoutView
from .test import TestView


router = DefaultRouter()

# auth
router.register(r'login', LoginView, base_name='api-user.auth.login.password')
router.register(r'logout', LogoutView, base_name='api-user.auth.logout')

# test
router.register(r'test', TestView, base_name='api-user.test')


urlpatterns = router.urls
