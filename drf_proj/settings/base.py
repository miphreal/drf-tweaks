import os


ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
BASE_DIR = os.path.join(ROOT_DIR, 'drf_proj')

DEBUG = False
SECRET_KEY = None
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'storages',
    'rest_framework',
    'corsheaders',

    'drf_proj.apps.core',
    'drf_proj.apps.base_api',
    'drf_proj.apps.client_api',
]

MIDDLEWARE = [
    'drf_proj.apps.base_api.middlewares.CorsMiddleware',
    'drf_proj.apps.base_api.middlewares.ApiClientRestrictionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'drf_proj.urls'
WSGI_APPLICATION = 'drf_proj.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(ROOT_DIR, 'db.sqlite3'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Authentication
AUTHENTICATION_BACKENDS = [
    'drf_proj.apps.base_api.authentication.EmailAuthBackend',
    'drf_proj.apps.base_api.authentication.UsernameAuthBackend',
]

# API Settings
API_LATEST_VERSION_URLS = 'drf_proj.apps.client_api.v1.urls'
API_DEPRECATED_VERSIONS = {
    '0.0.1', 
}
API_PENDING_DEPRECATION_VERSIONS = {
    '0.0.2': '2020-12-31',
}
REST_FRAMEWORK = {
    'DEFAULT_VERSION': '1.1.0',
    'ALLOWED_VERSIONS': (
        '0.0.2',
        '1.0.0', '1.1.0',
        'latest',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'drf_proj.apps.base_api.renderers.JsonRenderer',
        'drf_proj.apps.base_api.renderers.VendorJsonRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.DjangoFilterBackend',
        'drf_proj.apps.base_api.ordering_backend.CustomOrderingBackend',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'drf_proj.apps.base_api.authentication.APIAuthentication',
    ],
    'DEFAULT_METADATA_CLASS': 'drf_proj.apps.base_api.metadata.CustomMetadata',
    'VIEW_DESCRIPTION_FUNCTION': 'drf_proj.apps.base_api.renderers.get_view_description',
    'EXCEPTION_HANDLER': 'drf_proj.apps.base_api.renderers.exception_proxy_handler',
    'DEFAULT_VERSIONING_CLASS': 'drf_proj.apps.base_api.versioning.CustomVersioning',

    'PAGINATE_BY': 10,
    'MAX_PAGINATE_BY': 100,
    'PAGINATE_BY_PARAM': 'limit',
    'ORDERING_PARAM': 'sorting',
}

PAGINATE_OFFSET_PARAM = 'offset'
PAGINATE_PAGE_PARAM = 'page'
PAGINATE_LIMIT_PARAM = 'limit'

# CORS setup
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
    'your_domain.org',
)
CORS_ORIGIN_REGEX_WHITELIST = (
    r'^.*\.your_domain\.org$',
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
    'x-client-version',
    'user-agent',
    'accept-encoding',
)