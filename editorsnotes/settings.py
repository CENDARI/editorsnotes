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
#    'django.contrib.auth.backends.ModelBackend',
    'cendari.cendari_backend.CendariUserBackend',
#    'django_browserid.auth.BrowserIDBackend',
)

# CENDARI ADD: supported mime types for uploads

UPLOAD_FILE_TYPES = [
    'image/tiff',
    'image/x-tiff',
    'image/png',
    'image/jpeg',
    'text/plain',
    'text/html',
    'application/pdf',
    'application/vnd.oasis.opendocument.text', # odt
    'application/vnd.oasis.opendocument.spreadsheet', # ods
    'application/vnd.ms-excel', # xls
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', # xlsx
    'application/msword', # doc
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # docx
    'audio/mpeg', # mp3
    'audio/mpeg3',
    'audio/x-mpeg-3',
    'audio/x-wav', # wav
    #NOT YET 'video/x-msvideo' # avi
]

IMAGE_FILE_TYPES = {
    'tiff': 'image/tiff',
    'tif': 'image/tiff',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
}

CENDARI_LOGO_TIFF = 'cendari/img/cendari_logo.tif'
CENDARI_LOGO_PNG = 'cendari/img/cendari_logo.png'

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
#    'editorsnotes.main.context_processors.browserid',
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
#    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'cendari.cendari_middleware.CendariUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
#    'django_browserid',
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
    'cendari',
    'cendari.search',
    #CENDARI ADD
    'django.contrib.admin',
    'django.contrib.admindocs',
    'widget_tweaks' ,
    'django_rq',
    # 'djangoChat',
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
    ),
    'EXCEPTION_HANDLER': 'cendari.utils.custom_exception_handler'
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


