# -*- coding: utf-8 -*-
from rest_framework.views import exception_handler

import os.path
from datetime import datetime
import re
import unicodedata
import guess_language as gl
from lxml import etree
from pytz import timezone, utc
from django.conf import settings
from django.utils.encoding import smart_text
from editorsnotes.main.models import Document, Transcript, Topic, TopicNode, TopicAssignment
import urllib
import json

import pdb

import logging

logger = logging.getLogger('cendari.utils')

WELL_KNOWN_DATE_FORMATS=[
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
    "%Y-%m-%d"
]

def parse_well_known_date(str):
    for format in WELL_KNOWN_DATE_FORMATS:
        try:
            return datetime.strptime(str, format)
        except ValueError:
            pass
    return None

def get_or_create_topic(user, name, type, project, date=None):
    #pdb.set_trace()
    res = list(Topic.objects.filter(preferred_name=name,project=project))
    cnt = len(res)
    if cnt==0:
        print "Creating topic '%s' of type '%s'" % (name.encode("utf-8"), type)
        topic_node, c = TopicNode.objects.get_or_create(_preferred_name=name,
                                                        type=type,
                                                        defaults={'creator': user,
                                                                 'last_updater': user})
        t=Topic(creator=user, last_updater=user, preferred_name=name, topic_node=topic_node, project=project)
        
        if type=='EVT':
            t.date = date
            if (t.date):
                print "Parsed %s into a proper date %s" % (name,t.date.isoformat())
        t.save()
#        t.topic_node.type=type
        if not c: t.topic_node.save()
    elif res[0].topic_node.type==type:
        t=res[0]
    else:
        return None
            
    return t

def import_from_jigsaw(f, user, project):
    name = f.name

    parser = etree.XMLParser();
    try:
        for chunk in f.chunks():
            parser.feed(chunk)
        root = parser.close();
    except etree.LxmlError as e:
        return Empty
    return import_from_jigsaw_root(root, user, project)

# get rid of previously imported documents
    
def import_from_jigsaw_root(root, user, project):
    order = 1
    for node in root:
        id = node.findtext("docID")
        text = node.findtext("docText")
        #text.tag = 'div'
        docs = list(Document.objects.filter(import_id=id))
        if len(docs)==0:
            d = Document(creator=user, last_updater=user, import_id=id, description=id, ordering=order, project=project)
            d.save()
            t = Transcript(creator=user, last_updater=user, document=d, content=text)
            t.save()
        else:
            d = docs[0]
            d.last_updater = user
            d.description = id
            d.order = order
        d.language = gl.guessLanguageName(text)
        order += 1
        d.save()

        date = node.find("docDate")
        if date is not None and date.text:
            try:
#                pdb.set_trace()
                dt = datetime.strptime(date.text, "%m/%d/%Y")
                res = list(Topic.objects.filter(date=dt))
                cnt = len(res)
                if cnt==0:
                    normalized = "Date: %d/%d/%d" % (dt.year, dt.month, dt.day)
                    t=get_or_create_topic(user, normalized, 'EVT', project, dt)
                    t.date = dt
                    #t=Topic(creator=user, last_updater=user, preferred_name=normalized, date=dt, type='EVT',project=project)
                    t.save()
                else:
                    t=res[0]
                d.related_topics.create(creator=user, topic=t)
            except ValueError as e:
                pass
        for p in node.findall("concept"):
            name=p.text
            t=get_or_create_topic(user, name, 'TAG',project)
            if t:
        	d.related_topics.create(creator=user, topic=t)
            else:
                print "Cannot create topic(%s,type=%s)" % (t,'TAG')
            
        for p in node.findall("person"):
            name=p.text
            t=get_or_create_topic(user, name, 'PER',project)
            if t:
                d.related_topics.create(creator=user, topic=t)
            else:
                print "Cannot create topic(%s,type=%s)" % (t,'PER')
        for p in node.findall("location"):
            name=p.text
            t=get_or_create_topic(user, name, 'PLA',project)
            if t:
                d.related_topics.create(creator=user, topic=t)
            else:
                print "Cannot create topic(%s,type=%s)" % (t,'PLA')

FREEBASE_PEOPLE_QUERY = [{
  "type": "/people/deceased_person",
  "name": None,
  "id": None,
  "mid": None,
  "/people/deceased_person/date_of_death": None,
  "/people/deceased_person/date_of_death>": "1914-01-01",
  "/people/person/date_of_birth": None,
  "/people/person/date_of_birth<": "1900-01-01",
  "/people/person/gender": None
}]

def import_people_from_freebase(user):
    query=json.dumps(FREEBASE_PEOPLE_QUERY)
    params = urllib.urlencode({'lang': "/lang/en", 'query': query})
    f = urllib.urlopen("https://www.googleapis.com/freebase/v1/mqlread/?%s" % params)
    ret=json.loads(f.read())
    for p in ret['result']:
        mid = p['mid']
        if mid:
            try:
#            if True:
                params = urllib.urlencode({"query": mid, "output": "(description)"})
                url = 'https://www.googleapis.com/freebase/v1/search?%s' % params
                print url
                f = urllib.urlopen(url)
                print "Reading desc of %s (%s)" % (p['name'], mid)
                desc = json.loads(f.read())
                if desc['status'] == "200 OK":
#                    pdb.set_trace()
                    r=desc['result']
                    s=r[0]
                    t=s['output']
                    v=t['description']
                    p['contents'] = u'\n'.join(v['/common/topic/description'])
                    print p['contents']
            except:
                print "Exception"
                pass


def _has_project_perms(user):
    return ( user.has_perm('main.add_project') and 
             user.has_perm('main.change_project') and 
             user.has_perm('main.delete_project') and 
             user.has_perm('main.view_project'))
def is_project_creator(user):
    return user.is_staff and _has_project_perms(user)


def custom_exception_handler(exc):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc)

    # Now add the HTTP status code to the response.
    if response is not None:
        logger.debug('Received exception %s: %s', type(exc), response.status_code)
        response.data['status_code'] = response.status_code
    else:
        logger.debug('Received exception %s', type(exc))
    return response

def update_delete_status(project):
    topics = project.topics.all()
    for topic in topics:
        if len(topic.get_related_documents()) == len(topic.get_related_notes()) == 0:
            topic.deleted = True
            topic.save()
        else:
            topic.deleted = False
            topic.save()
