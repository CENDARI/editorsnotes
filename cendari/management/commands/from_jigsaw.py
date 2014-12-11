from django.core.management.base import LabelCommand, CommandError

from django.contrib.auth import get_user_model
from django.db import transaction
from cendari.utils import import_from_jigsaw_root

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
from django.utils.encoding import smart_text
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
