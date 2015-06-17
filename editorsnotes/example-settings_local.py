######################
# Required variables #
######################

SECRET_KEY = ''
POSTGRES_DB = {
    'NAME': '',
    'USER': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': ''
}

SEMANTIC_STORE = 'Sleepycat'
#SEMANTIC_PATH = os.path.abspath(os.path.join(STORAGE_PATH, 'rdfstore'))
#SEMANTIC_STORE = 'Virtuoso'

SEMANTIC_NAMESPACE = 'http://localhost:8000/'
#SEMANTIC_NAMESPACE = 'http://notes.cendari.daria.eu/'

VIRTUOSO = {
    'dba_password': 'dba',
    'dav_password': 'dav',
    'HOST': 'localhost'
}

CENDARI_DATA_API_SERVER = "http://localhost:42042/v1/"

LDAP_GROUP_MAPS = { 
    'admin_groups': '***semicolon-separated list of group names***',
    'editor_groups': '***semicolon-separated list of group names***',
    'contributor_groups': '***semicolon-separated list of group names***',
    'user_groups': '***semicolon-separated list of group names***'
}

ELASTICSEARCH_ENABLED = True

# Each ElasticSearch index created will be prefixed with this string.
ELASTICSEARCH_PREFIX = 'editorsnotes'

# As defined in pyelasticsearch, ELASTICSEARCH_URLS should be:
#
# A URL or iterable of URLs of ES nodes. These are full URLs with port numbers,
# like ``http://elasticsearch.example.com:9200``.
#
ELASTICSEARCH_URLS = 'http://127.0.0.1:9200'

# The base URL for your site, with protocol, hostname, and port (if not 80 for
# http or 443 for https). This will be used to construct fully-qualified URLs
# from hyperlinks in the Elasticsearch index.
ELASTICSEARCH_SITE = 'http://127.0.0.1:8000'


SITE_URL = '127.0.0.1'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('My Name', 'myemail@gmail.com'),
)
MANAGERS = ADMINS


#############
# Overrides #
#############

# TIME_ZONE = ''
# LANGUAGE_CODE = ''
# DATETIME_FORMAT = ''
# USE_L10N = True
# USE I18N = True


# Edit STORAGE_PATH to change where uploads, static files, and search indexes
# will be stored, or change each of the settings individually.
# STORAGE_PATH = ''

# MEDIA_ROOT = ''
# STATIC_ROOT = ''

# Point this to the Less CSS compiler if it is not on PATH
# LESSC_BINARY = ''


######################
# Optional variables #
######################

# Set the following variables to connect to an instance of Open Refine and
# enable clustering topics and documents.
GOOGLE_REFINE_HOST = '127.0.0.1'
GOOGLE_REFINE_PORT = '3333'

# Set the following to be able to write all Zotero data to a central library.
ZOTERO_API_KEY = ''
ZOTERO_LIBRARY = ''

# Define locally installed apps here
LOCAL_APPS = (
    'editorsnotes_app',
    'cendari',
    'djadmin2',
    'djadmin2.themes.djadmin2theme_default', # for the default theme
    'rest_framework', # for the browsable API templates
    'floppyforms', # For HTML5 form fields
    'crispy_forms', # Required for the default theme's layout
    'djangoChat',
    )

ROOT_URLCONF = 'cendari.urls'

## CENDARI ADD

IIPSRV = 'http://localhost/fcgi-bin/iipsrv.fcgi'

RQ_QUEUES = {
    'high': {
        'USE_REDIS_CACHE': 'redis-cache',
    },
    'low': {
        'USE_REDIS_CACHE': 'redis-cache',
    },


## CENDARI ADD

#IIPSRV = 'http://cendari.saclay.inria.fr/fcgi-bin/iipsrv.fcgi'
#RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    }
}

# for use with django development server only. DO NOT USE IN PRODUCTION
SENDFILE_BACKEND = 'sendfile.backends.development'
#
# "simple" backend that uses Django file objects to attempt to stream files
# from disk (note middleware may cause files to be loaded fully into memory)
#
#SENDFILE_BACKEND = 'sendfile.backends.simple'
#
# sets X-Sendfile header (as used by mod_xsendfile/apache and lighthttpd)
#SENDFILE_BACKEND = 'sendfile.backends.xsendfile'
#
# sets Location with 200 code to trigger internal redirect (daemon
# mode mod_wsgi only - see below)
#SENDFILE_BACKEND = 'sendfile.backends.mod_wsgi'
#
#  sets X-Accel-Redirect header to trigger internal redirect to file
#SENDFILE_BACKEND = 'sendfile.backends.nginx'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'editorsnotes': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'cendari': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'cendari.semantic': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'cendari.utils': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}
