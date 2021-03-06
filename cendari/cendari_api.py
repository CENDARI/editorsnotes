import pycurl
import urllib
import json
import re

import logging
logger = logging.getLogger(__name__)

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

from django.conf import settings

try:
    DATA_API_SERVER = settings.CENDARI_DATA_API_SERVER
except AttributeError:
    raise ImproperlyConfigured("CENDARI_DATA_API_SERVER must be configured in the settings file'")

try:
    DATA_API_TIMEOUT = settings.CENDARI_DATA_API_TIMEOUT
except AttributeError:
    DATA_API_TIMEOUT = 3

__all__ = [ 'DATA_API_SERVER', 'cendari_clean_name', 'CendariDataAPIException', 'CendariDataAPI', 'cendari_data_api' ]


def cendari_clean_name(name):
    name = name.split('@')[0]
    if len(name) < 2:
        raise CendariDataAPIException('name too short (should be > 2)')
    name = re.sub(r'[^a-z0-9_-]', '_', name.lower())
    if len(name) > 30:
        name = name[:30]
    return name

class CendariDataAPIException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class CendariDataAPI(object):
    def __init__(self, url, key=None):
        self.url = url
        self.key = key
        self.anonymous = False
        self.public_dataspaces = None

    def session(self,eppn=None, mail=None, cn=None, key=None, anonymous=False):
        self.public_dataspaces = None
        if key:
            self.key = key
            return
        if anonymous:
            self.anonymous = True
            self.key = None
            return
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
        logger.debug('Data API call return status: %d', status)
        c.close()
        if status==200:
            body = buffer.getvalue()
            #print(body)
            results=json.loads(body)
            # {"sessionKey": "xyz"}
            self.key = str(results['sessionKey'])
        else:
            self.key = None
        return self.key

    def has_key(self):
        return self.key != None

    def check_login(self):
        if not self.anonymous and not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')

    def close(self):
        self.key = None
        self.anonymous = False
        self.public_dataspaces = None

    def get_key(self):
        if self.anonymous:
            return "null"
        return self.key

    def read_url(self,url):
        results = []
        while url is not None:
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(pycurl.HTTPHEADER, ["Authorization:"+self.get_key(), "Content-type:application/json"])
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

    def get_public_dataspaces(self,force=False):
        if self.public_dataspaces is None or force:
            try:
                dataspaces=self.get_dataspace()
                public_ds = []
                for d in dataspaces:
                    name = d['name']
                    public_ds.append(name)
                    if name.startswith('nte_'):
                        public_ds.append(name[4:])
                self.public_dataspaces = public_ds
            except:
                self.public_dataspaces = []
        return self.public_dataspaces

    def get_dataspace(self,id=None):
        self.check_login()
        if not id:
            id = ''
        return self.read_url(self.url+'dataspaces/'+id)

    def delete_dataspace(self,id):
        self.check_login()
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.url+'dataspaces/'+id)
        c.setopt(pycurl.HTTPHEADER, ["Authorization:"+self.key, "Content-type: application/json"])
        c.setopt(pycurl.CUSTOMREQUEST, "DELETE")
        c.setopt(pycurl.WRITEDATA, buffer)
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        #print('Status: %d' % status)
        c.close()
        body = buffer.getvalue()
        #print(body)
        if status < 200 or status >= 300:
            raise CendariDataAPIException("Error %d: %s" % (status, body))
        results=body
        return results

    def create_dataspace(self,name,title=None,desc=None):
        self.check_login()
        # maybe test for name conformance
        fields = {'name': name}
        if title is not None:
            fields['title']= title
        if desc is not None:
            fields['description'] = desc
        postfields = json.dumps(fields)
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.url+'dataspaces')
        c.setopt(pycurl.HTTPHEADER, ["Authorization:"+self.key, "Content-type: application/json"])
        c.setopt(pycurl.POST, True)
        c.setopt(pycurl.POSTFIELDS, postfields)
        c.setopt(pycurl.WRITEDATA, buffer)
        c.setopt(pycurl.CONNECTTIMEOUT, DATA_API_TIMEOUT)
        c.setopt(pycurl.TIMEOUT, DATA_API_TIMEOUT)
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        print('Status: %d' % status)
        c.close()
        body = buffer.getvalue()
        #print(body)
        if status<200 or status>=300:
            raise CendariDataAPIException(("Trying to create dataspace '%s': \n"%name)+body)
        results=json.loads(body)
        return results
        

    def get_resources(self,url,filter=None):
        self.check_login()
        if not filter:
            filter = ''
        else:
            filter='?'+filter
        return self.read_url(url+filter)

    def create_resource(self,dataspaceId,fileName=None,fileContents=None,name=None,format=None,title=None,desc=None,setId=None):
        self.check_login()
        # maybe test for name conformance
        url = self.url+'dataspaces/%s/resources' % dataspaceId
        print "Url is %s" % url
        fields = []
        if name is not None:
            fields.append( ('name', name) )
        if format is not None:
            fields.append( ('format', format) )
        if title is not None:
            fields.append( ('title', title) )
        if desc is not None:
            fields.append( ('description', desc) )
        if setId is not None:
            fields.append( ('setId', setId) )
        c = pycurl.Curl()
        if fileName is not None:
            fields.append( ('file', ( c.FORM_FILE, fileName ) ) )
        elif fileContents is not None:
            fields.append( ('file', fileContents ) )
        pprint.pprint(fields)
        buffer = BytesIO()
        c.setopt(c.URL, url)
        c.setopt(pycurl.HTTPHEADER, ["Authorization:"+self.key])
        c.setopt(pycurl.HTTPPOST, fields)
        c.setopt(pycurl.WRITEDATA, buffer)
        c.setopt(pycurl.CONNECTTIMEOUT, DATA_API_TIMEOUT)
        c.setopt(pycurl.TIMEOUT, DATA_API_TIMEOUT)
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        print('Status: %d' % status)
        c.close()
        body = buffer.getvalue()
        print(body)
        if status < 200 or status >= 300:
            raise CendariDataAPIException(body)
        results=json.loads(body)
        return results

    def update_resource(self,dataspaceId,resId,fileName=None,fileContents=None,name=None,format=None,title=None,desc=None):
        self.check_login()
        # maybe test for name conformance
        url = self.url+'dataspaces/%s/resources/%s' % (dataspaceId, resId)
        print "Url is %s" % url
        fields = []
        if name is not None:
            fields.append( ('name', name) )
        if format is not None:
            fields.append( ('format', format) )
        if title is not None:
            fields.append( ('title', title) )
        if desc is not None:
            fields.append( ('description', desc) )
        c = pycurl.Curl()
        if fileName is not None:
            fields.append( ('file', ( c.FORM_FILE, fileName ) ) )
        elif fileContents is not None:
            fields.append( ('file', fileContents ) )
        pprint.pprint(fields)
        buffer = BytesIO()
        c.setopt(c.URL, url)
        c.setopt(pycurl.HTTPHEADER, ["Authorization:"+self.key])
        c.setopt(pycurl.HTTPPOST, fields)
        c.setopt(pycurl.CUSTOMREQUEST, "PUT")
        c.setopt(pycurl.WRITEDATA, buffer)
        c.setopt(pycurl.CONNECTTIMEOUT, DATA_API_TIMEOUT)
        c.setopt(pycurl.TIMEOUT, DATA_API_TIMEOUT)
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        print('Status: %d' % status)
        c.close()
        body = buffer.getvalue()
        print(body)
        if status < 200 or status >= 300:
            raise CendariDataAPIException(body)
        results=json.loads(body)
        return results

    def get_users(self,id=None):
        self.check_login()
        if not id:
            id = ''
        return self.read_url(self.url+'users'+id)

    def get_privileges(self,userId=None,dataspaceId=None,role=None):
        self.check_login()
        if userId:
            return self.read_url(self.url+'privileges?userId'+userId)
        elif dataspaceId:
            return self.read_url(self.url+'privileges/'+dataspaceId)
        elif role:
            if role in ["member", "editor", "admin"]:
                return self.read_url(self.url+'privileges/'+role)
            else:
                raise CendariDataAPIException('Invalid role: %s, should be "member", "editor", or "admin"' % role)
        else:
            return self.read_url(self.url+'privileges')


cendari_data_api = CendariDataAPI(DATA_API_SERVER)

import pprint
import sys, os

def test():
    #api = CendariDataAPI(sys.argv[1], sys.argv[2])
    api = CendariDataAPI(sys.argv[1])
    env = os.environ
    key = api.session(eppn=env['eppn'], mail=env['mail'],cn=env['cn'])
    print key
    ds = api.get_dataspace()
    print "Available dataspaces: %d" % len(ds)
    u = api.get_users()
    print "Available users(%d)" % len(u)
    for user in u:
        print '\tusername: %s' % user['username']
        print '\tfullname: %s' % user['fullname']
    p = api.get_privileges()
    print "Available privileges(%d)" % len(p)
    for priv in p:
        print '\trole: %s' % priv['role']
    c = None
    for d in ds:
        if d['name'] == 'nte_test':
            c = d
            break
    if c:
        pprint.pprint(c)
#        api.delete_dataspace(c['id'])
    try:
        c = api.create_dataspace(name='nte_test', title='Note Taking Environment test', desc='Test dataspace for the note-taking environment')
        print c
    except CendariDataAPIException as e:
        print "Exception creating dataspace nte_test: "+e.msg
    res = api.get_resources(c['resources'])
    rid=None
    print "  Available resources: %d" % len(res)
    for r in res:
        print '  %s' % r['name']
        if r['name']=='test':
            rid=r['id']
    ds = api.get_dataspace()
    print "Available dataspaces:"
    for d in ds:
        print "  "+d['name']

    r=None
    if rid:
        r=api.update_resource(c['id'],rid,fileName='cendari_api.py',name='test',format='text/plain',title='Test file')
    else:
        r=api.create_resource(c['id'],fileName='cendari_api.py',name='test',format='text/plain',title='Test file')
    pprint.pprint(r)
    # for d in ds:
    #     print "Dataspace: %s" % d['name']
    #     res = api.get_resources(d['resources'])
    #     print "  Available resources: %d" % len(res)
    #     for r in res:
    #         print '  %s' % r['name']

if __name__ == '__main__':
    test()
