import pycurl
import urllib
import json
import re

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

__all__ = [ 'DATA_API_URL', 'cendari_clean_name', 'CendariDataAPIException', 'CendariDataAPI' ]

DATA_API_URL = 'http://localhost:42042/v1/'

def cendari_clean_name(name):
    name = name.split('@')[0]
    if len(name) < 2:
        raise CendariDataAPIException('name too short (should be > 2)')
    name = re.sub(r'[^a-z0-9_-]', '_', name.lower())
    if len(name) > 30:
        name = name[:30]
    #print "name is: "
    #print name,len(name)
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

    def delete_dataspace(self,id):
        if not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')
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
        if not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')
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
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        print('Status: %d' % status)
        c.close()
        body = buffer.getvalue()
        #print(body)
        if status<200 or status>=300:
            raise CendariDataAPIException(body)
        results=json.loads(body)
        return results
        

    def get_resources(self,url,filter=None):
        if not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')
        if not filter:
            filter = ''
        else:
            filter='?'+filter
        return self.read_url(url+filter)

    def create_resource(self,dataspaceId,fileName=None,fileContents=None,name=None,format=None,title=None,desc=None,setId=None):
        if not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')
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
        if not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')
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
        if not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')
        if not id:
            id = ''
        return self.read_url(self.url+'users'+id)

    def get_privileges(self,userId=None,dataspaceId=None,role=None):
        if not self.key:
            raise CendariDataAPIException('Not Logged-in to Cendari Data API')
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
