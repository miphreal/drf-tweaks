from .base import *  # noqa


DEBUG = True
SECRET_KEY = '%z#=i1irp$s4%g_gnv=-lt$$1@cvna(-15+a3om14ap1=+2iq)'
ALLOWED_HOSTS = [
    '*',
]
if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer'
    )