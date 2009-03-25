# Copyright 2007 Casey Durfee
# Copyright 2007 Gabriel Farrell
#
# This file is part of Kochief.
# 
# Kochief is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Kochief is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Kochief.  If not, see <http://www.gnu.org/licenses/>.

# Django settings for the Kochief project.

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'

# Base URL of the project, either absolute or relative.  
# Must include a trailing slash.
BASE_URL = '/'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = BASE_DIR + 'kochief.db'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# dummy ugettext -- see http://www.djangoproject.com/documentation/i18n/
ugettext = lambda s: s

LANGUAGES = (
    ('fr', ugettext('French')),
    ('en', ugettext('English')),
)

SITE_ID = 1 

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = BASE_DIR + 'media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = BASE_URL + 'media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = BASE_URL + 'admin/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'cr7)b7e+bq*u%a6f8a2d_rrcd3r_r@d3u32c-1*4^mk6fc0fsl'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.doc.XViewMiddleware",
    "django.middleware.gzip.GZipMiddleware",
)

ROOT_URLCONF = 'kochief.urls'

TEMPLATE_DIRS = (
    BASE_DIR + 'templates/',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'kochief.discovery',
    'kochief.cataloging',
)

CACHE_BACKEND = 'locmem:///'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "kochief.discovery.context_processors.search_history",
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True


## Settings specific to this project (that is, non-Django) ##

SOLR_URL = 'http://localhost:8983/solr/test/'

SOLR_SCHEMA = BASE_DIR + 'solr/conf/schema.xml'

# III, Unicorn, or Horizon -- affects both display and index/ingest
ILS = ''

# MAJAX_URL is for use with http://libx.org/majax/ 
# (has no effect if ILS != 'III')
MAJAX_URL = ''

# Set CATALOG_RECORD_URL to something else if you want to pass through
# to your catalog, e.g. 'http://innopac.library.drexel.edu/record=%s'.
# The %s is replaced by the item id.
CATALOG_RECORD_URL = ''

# Number of facet terms to display by default.
MAX_FACET_TERMS_BASIC = 4    

# Number of facet terms to display when you hit "show more".
MAX_FACET_TERMS_EXPANDED = 25 

# Number of terms to display for index facets.
INDEX_FACET_TERMS = 20

# Facet display on the index page.  Note that values for "field" are 
# appended with "_facet".  If sort_by_count is False, terms will be 
# sorted "in their natural index order" according to Solr docs -- 
# usually alphabetical.
INDEX_FACETS = [
    { 
        'name': ugettext('Names'), 
        'field': 'personal_name', 
        'sort_by_count': True, 
    }, 
    { 
        'name': ugettext('Subjects'), 
        'field': 'subject', 
        'sort_by_count': True, 
    },    
    { 
        'name': ugettext('Languages'), 
        'field': 'language', 
        'sort_by_count': True, 
    },                            
]

# Facet display in the results sidebar.
FACETS = [
    { 
        'name': ugettext('Name'), 
        'field': 'name', 
        'sort_by_count': True, 
    }, 
    { 
        'name': ugettext('Topic'), 
        'field': 'topic', 
        'sort_by_count': True, 
    },    
    { 
        'name': ugettext('Genre'), 
        'field': 'genre', 
        'sort_by_count': True, 
    },                            
    { 
        'name': ugettext('Language'), 
        'field': 'language', 
        'sort_by_count': True, 
    },                            
    { 
        'name': ugettext('Dubbed Language'), 
        'field': 'language_dubbed', 
        'sort_by_count': True, 
    }, 
    { 
        'name': ugettext('Subtitled Language'), 
        'field': 'language_subtitles', 
        'sort_by_count': True, 
    }, 
    { 
        'name': ugettext('Format'), 
        'field': 'format', 
        'sort_by_count': True, 
    },                         
    { 
        'name': ugettext('Place'), 
        'field': 'place', 
        'sort_by_count': True, 
    },    
    { 
        'name': ugettext('Author'), 
        'field': 'author',
        'sort_by_count': True, 
    },
    { 
        'name': ugettext('Year of Publication'), 
        'field': 'year', 
        'sort_by_count': True, 
    },
#    {
#        'name': ugettext('Dewey Range'), 
#        'field': 'callnumlayerone', 
#        'sort_by_count': False, 
#    },
#    { 
#        'name': ugettext('Dewey Range'), 
#        'field': 'callnumlayertwo', 
#        'sort_by_count': False, 
#    }, 
#    { 
#        'name': ugettext('Availability'), 
#        'field': 'availability', 
#        'sort_by_count': False, 
#    },
]

ITEMS_PER_PAGE = 20

# Sort options for results, by (DISPLAY, SOLR_PARAM).
SORTS = (
    (ugettext('newest'), 'year desc'),
    (ugettext('oldest'), 'year asc'),
    (ugettext('relevance'), ''),
    (ugettext('title'), 'title_sort asc'),
)

SEARCH_CACHE_TIME = 6000    # in seconds

# Import for local overrides
try:
    from settings_local import *
except ImportError:
    pass

