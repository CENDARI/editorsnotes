from django.core.management.base import LabelCommand, CommandError

from django.contrib.auth import get_user_model
from django.db import transaction
from cendari.utils import get_or_create_topic

from optparse import make_option
import sys
from urllib import urlparse
import os.path
from datetime import datetime
import re
import unicodedata
import guess_language as gl
from lxml import etree
from pytz import timezone, utc
from django.conf import settings
from editorsnotes.main.models import Document, Transcript, Topic, TopicAssignment, Project
from django.utils.text import slugify

class Command(LabelCommand):
    arg = 'jigsaw_filename'
    label = 'Jigsaw filename'
    help = 'Loads from file.'
    option_list = LabelCommand.option_list + (
        make_option('-u',
                    '--username',
                    action='store',
                    default='fekete',
                    help='username that will create/update documents'),
        make_option('-p',
                    '--project',
                    action='store',
                    default='default',
                    help='Project that will contain documents'),
        make_option('-f',
                    '--force-update',
                    action='store_true',
                    default=False,
                    help='update documents whether or not they have changed'),
    )

    def handle(self, *labels, **options):
        for label in labels:
            try:
                self.do_label(label, options)
            except CommandError as e:
                print e

    def do_label(self, filename, options):
        if not os.path.isfile(filename):
            raise CommandError('%s is not a file.' % filename)
        try:
            user = get_user_model().objects.get(username=options['username'])
        except get_user_model().DoesNotExist:
            raise CommandError('unknown user: %s' % options['username'])

        project, created = Project.objects.get_or_create(name=options['project'], slug=slugify(unicode(options['project'])))
        if project is None:
            print 'Project not created'
        else:
            project.save()
            print 'Project is %s' % project.name
        import_from_jigsaw(filename, user, project)

def import_from_jigsaw(filename, user, project):
    name = filename

    try:
        doc = etree.parse(filename)
    except etree.LxmlError as e:
        raise CommandError('could not parse %s:\n  %s' % (filename, e))
    root = doc.getroot()
    with transaction.commit_on_success():
        return import_from_jigsaw_root(root, user, project)

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
