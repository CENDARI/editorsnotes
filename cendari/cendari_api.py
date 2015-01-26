import pycurl
import urllib
import json

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

__all__ = [ 'DATA_API_URL', 'CendariDataAPIException', 'CendariDataAPI' ]

DATA_API_URL = 'http://localhost:42042/v1/'

class CendariDataAPIException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)


class CendariDataAPI(object):
    def __init__(self, url, key=None):
        self.url = url
        self.key = key

    def session(self,eppn, mail, cn):
        if self.key:
            return self.key
        postfields = json.dumps({'eppn': eppn, 'mail': mail, 'cn': cn })
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.url+'session')
        c.setopt(pycurl.HTTPHEADER, ["Content-type: application/json"])
        c.setopt(pycurl.POST, True)
        c.setopt(pycurl.POSTFIELDS, postfields)
        c.setopt(pycurl.WRITEDATA, buffer)
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        #print('Status: %d' % status)
        c.close()
        if status==200:
            body = buffer.getvalue()
            #print(body)
            results=json.loads(body)
            # {"sessionKey": "xyz"}
            self.key = str(results['sessionKey'])
        return self.key

    def read_url(self,url):
        results = []
        while url is not None:
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(pycurl.HTTPHEADER, ["Authorization:"+self.key, "Content-type:application/json"])
            c.setopt(pycurl.WRITEDATA, buffer)
            c.perform()
            status = c.getinfo(c.RESPONSE_CODE)
            #print('Status: %d' % status)
            c.close()
            if status==200:
                body = buffer.getvalue()
                #print(body)
                res = json.loads(body)
                if 'data' in res:
                    results += res['data']
                if 'end' in res and res['end']==True:
                    url = None
                elif 'nextPage' in res:
                    url = res['nextPage']
                else:
                    url = None
            else:
                url = None
        return results

    def get_dataspace(self,id=None):
        if not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')
        if not id:
            id = ''
        return self.read_url(self.url+'dataspaces/'+id)

    def get_resources(self,url):
        if not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')
        return self.read_url(url)

    def users(self,id=None):
        if not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')
        return []

    def privileges(self,id=None):
        if not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')
        return []


import pprint
import sys

def test():
    api = CendariDataAPI(sys.argv[1], sys.argv[2])
    #api = CendariDataAPI(sys.argv[1])
    #key = api.session(eppn='me', mail='myself@home',cn='I')
    #print key
    ds = api.get_dataspace()
    print "Available dataspaces: %d" % len(ds)

    for d in ds:
        print "Dataspace: %s" % d['name']
        res = api.get_resources(d['resources'])
        print "  Available resources: %d" % len(res)
        for r in res:
            print '  %s' % r['name']

if __name__ == '__main__':
    test()
