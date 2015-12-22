from django.core.management.base import BaseCommand, CommandError
from editorsnotes.main.models import Topic

import sys

def ask_delete(name):
    print "delete %s: [Y]es/No"%name
    line=sys.stdin.readline()
    line.strip()
    return len(line)==0 or line[0]=='y' or line[0]=='Y'

class Command(BaseCommand):
    def handle(self, *labels, **options):
        todelete = []
        for topic in Topic.objects.all():
            if (len(topic.get_related_notes())+len(topic.get_related_documents()))==0:
                if ask_delete("%d: %s"%(topic.id, topic.preferred_name)):
                    todelete.append(topic)
        for topic in todelete:
            topic.delete()

            
