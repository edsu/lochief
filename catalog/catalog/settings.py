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

#CACHE_BACKEND = 'simple:///'
#CACHE_BACKEND = 'locmem:///'
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHE_MIDDLEWARE_SECONDS = 3600

LANGUAGE_CODE = 'en-us'
DEFAULT_CHARSET='utf-8'
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
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.cache.CacheMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.doc.XViewMiddleware",
    "django.middleware.gzip.GZipMiddleware",
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
)

INSTALLED_APPS = ('catalog')
