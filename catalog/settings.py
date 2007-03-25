AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
DEBUG= True
TEMPLATE_DEBUG = DEBUG
ADMINS = ( )
MANAGERS = ADMINS

DATABASE_ENGINE = ''
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = "PST8PDT"

CACHE_BACKEND = 'simple:///'

LANGUAGE_CODE = 'en-us'
SITE_ID = 1 
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/media/'

# You should set this to something long and cryptic
SECRET_KEY = ''

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.doc.XViewMiddleware",
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
)

INSTALLED_APPS = ('catalog')
