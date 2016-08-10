from rest_framework.routers import DefaultRouter

from .auth import LoginView, LogoutView


router = DefaultRouter()

# auth
router.register(r'login', LoginView, base_name='api-user.auth.login.password')
router.register(r'logout', LogoutView, base_name='api-user.auth.logout')


urlpatterns = router.urls
