import pycurl
import urllib
import json
import pprint
import sys

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

try:
    # python 3
    from urllib.parse import urlencode
except ImportError:
    # python 2
    from urllib import urlencode

DATA_API_URL = 'http://localhost:42042/v1/'

class CendariDataAPI(object):
    def __init__(self, url):
        self.url = url

    def login(self,eppn, mail, cn):
        postfields = json.dumps({'eppn': eppn, 'mail': mail, 'cn': cn })
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.url+'session')
        c.setopt(pycurl.HTTPHEADER, ["Content-type: application/json"])
        c.setopt(pycurl.POST, True)
        c.setopt(pycurl.POSTFIELDS, postfields)
        c.setopt(pycurl.WRITEDATA, buffer)
        c.perform()
        print('Status: %d' % c.getinfo(c.RESPONSE_CODE))
        c.close()
        body = buffer.getvalue()
        print(body)
        return body
