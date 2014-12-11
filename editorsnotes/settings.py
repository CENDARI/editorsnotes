###################
# Locale settings #
###################

# These settings are defaults: change in settings_local.py if desired
TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'
DATETIME_FORMAT = 'N j, Y, P'
USE_L10N = False
USE_I18N = True


########################
# Datebase information #
########################

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2'
        # The rest of the DB configuration is done in settings_local.py
    }
}
SOUTH_DATABASE_ADAPTERS = {
    'default': 'south.db.postgresql_psycopg2'
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'zotero_cache'
    },
    'compress': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'compress_cache'
    }
}
COMPRESS_CACHE_BACKEND = 'compress'

SOUTH_TESTS_MIGRATE = False


#################
# Site settings #
#################

SITE_ID = 1
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
ROOT_URLCONF = 'editorsnotes.urls'

## CENDARI ADD
IIPSRV = 'http://cendari.saclay.inria.fr/fcgi-bin/iipsrv.fcgi'

AUTH_USER_MODEL = 'main.User'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_browserid.auth.BrowserIDBackend',
)

# CENDARI ADD
# This is a 1.2.7 style configuration not used by version 2+ of haystack
#HAYSTACK_SITECONF = 'editorsnotes.search_sites'
#HAYSTACK_SEARCH_ENGINE = 'xapian'
# This is a version 2+ of haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

#################
# Path settings #
#################
import os

EN_PROJECT_PATH = os.path.abspath(os.path.join(
    os.path.normpath(os.path.dirname(__file__)),
    os.path.pardir
))

TEMPLATE_DIRS = (
    os.path.join(EN_PROJECT_PATH, 'editorsnotes', 'templates'),
)
STATICFILES_DIRS = (
    os.path.join(EN_PROJECT_PATH, 'editorsnotes', 'static'),
)

# Override these variables in settings_local.py if desired
DEBUG = False
try:
    from settings_local import STORAGE_PATH
except ImportError:
    STORAGE_PATH = EN_PROJECT_PATH


# CENDARI ADD
HAYSTACK_XAPIAN_PATH = os.path.abspath(os.path.join(STORAGE_PATH, 'searchindex'))
#MEDIA_ROOT = os.path.abspath(os.path.join(STORAGE_PATH, 'uploads'))


MEDIA_ROOT = os.path.join(STORAGE_PATH, 'uploads')
STATIC_ROOT = os.path.join(STORAGE_PATH, 'static')


#CENDARI ADD
SEMANTIC_PATH = os.path.abspath(os.path.join(STORAGE_PATH, 'rdfstore'))

###################
# Everything else #
###################

TEST_RUNNER = 'editorsnotes.testrunner.CustomTestSuiteRunner'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'editorsnotes.main.context_processors.browserid',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django_browserid',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'reversion',
    'south',
    'compressor',
    'licensing',
    'rest_framework',
    'rest_framework.authtoken',
    'editorsnotes.main',
    'editorsnotes.djotero',
    #'editorsnotes.refine',
    'editorsnotes.admin',
    'editorsnotes.api',
    'editorsnotes.search',
    'editorsnotes_app',
    
    #CENDARI ADD
    'django.contrib.admin',
    'django.contrib.admindocs',
    'widget_tweaks' ,
    'django_rq',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
BROWSERID_CREATE_USER = 'editorsnotes.main.views.auth.create_invited_user'

LESSC_BINARY = os.path.join(EN_PROJECT_PATH, 'node_modules', '.bin', 'lessc')
COMPRESS_YUGLIFY_BINARY = os.path.join(EN_PROJECT_PATH, 'node_modules', '.bin', 'uglifyjs')

REST_FRAMEWORK = {
    #'FILTER_BACKEND': 'editorsnotes.api.filters.HaystackFilterBackend',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication'
    )
}

# Add in local settings
from settings_local import *
DATABASES['default'].update(POSTGRES_DB)
try:
    INSTALLED_APPS = INSTALLED_APPS + LOCAL_APPS
except NameError:
    pass

COMPRESS_JS_FILTERS = ['compressor.filters.yuglify.YUglifyJSFilter']
COMPRESS_PRECOMPILERS = (
    ('text/less', LESSC_BINARY + (' --source-map-map-inline ' if DEBUG else '') + ' {infile} {outfile}'),
)


