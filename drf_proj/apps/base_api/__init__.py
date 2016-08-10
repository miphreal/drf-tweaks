#
# PATCHING
from .patch import patch_request, patch_base_field


default_app_config = 'drf_proj.apps.base_api.apps.ApiConfig'


patch_request()
patch_base_field()
