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

CACHE_BACKEND = 'locmem:///'

LANGUAGE_CODE = 'en-us'
SITE_ID = 1 
MEDIA_URL = 'http://localhost:8008/site_media'
ADMIN_MEDIA_PREFIX = '/media/'

SECRET_KEY = 'g&4kmzrz@5#o&zi13490jmklsrklqiwer5mlze(j*9cxoia6j-2aji!'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
   #  'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.doc.XViewMiddleware",
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
#     "c:/projects/helios/savitr/templates",
 )

INSTALLED_APPS = ( 'catalog', )
