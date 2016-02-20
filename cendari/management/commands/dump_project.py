from django.core.management.base import LabelCommand, CommandError
from django.core import serializers
from editorsnotes.main.models import *

from optparse import make_option
import sys
from itertools import chain
import pdb

class Command(LabelCommand):
    arg = 'Project_name'
    label = 'Project name'
    help = 'Dumps the specified project'
    option_list = LabelCommand.option_list + (
        make_option('-f',
                    '--format',
                    action='store',
                    default='json',
                    type='choice', choices=['json', 'xml', 'yaml'],

                    help='Object serialization format: json, xml, yaml [default: json]'),
        make_option('-o',
                    '--output',
                    action='store',
                    default=False,
                    help='Output file name, defaults to stdout'),
    )

    def handle_label(self, project_slug, **options):
#        pdb.set_trace()
        try:
            project = Project.objects.get(slug=project_slug)
            out = open(options['output'], 'w') if options['output'] else sys.stdout
            format = options['format']
            FormatSerializer = serializers.get_serializer(format)
            serializer = FormatSerializer()
            documents = Document.objects.filter(project=project)
            transcripts = []
            scans = []
            citations = []
            for d in documents:
                if d.transcript: transcripts.append(d.transcript) 
                if d.scan_count: scans.extend(d.scans.all()) 
                for c in d.citations.all(): citations.append(c)
            notes = Note.objects.filter(project=project)
            topics = Topic.objects.filter(project=project)
            serializer.serialize([project]+
                                 transcripts+
                                 scans+
                                 citations+
                                 list(notes)+
                                 list(topics), 
#chain(documents, notes, topics),
                                 stream=out)
            if out != sys.stdout:
                out.close()
        except TypeError as e:
            raise

