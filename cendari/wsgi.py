import os, sys

sys.path = sys.path + ["/usr/local/cendari-vre/"] 



os.environ["DJANGO_SETTINGS_MODULE"] = "editorsnotes.settings"
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "editorsnotes.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
