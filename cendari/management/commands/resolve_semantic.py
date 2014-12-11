from django.core.management.base import BaseCommand, CommandError

from editorsnotes.main.models import Topic
from cendari.semantic import Semantic, topic_to_schema, dbpedia_lookup, semantic_resolve_topic, semantic_process_topic

from optparse import make_option
import sys
from urllib import urlparse

def ask_resolution(name,results):
    ans=None
    while ans is None:
        print "0: None"
        for i in range(0,len(results)):
            print "%d: %s (%s)" % ((i+1), results[i]['label'], results[i]['uri'])
        line=sys.stdin.readline()
        line.strip()
        if len(line)==0:
            return None
        try:
            n=int(line)
            if n==0:
                return None
            n -= 1
            if n < len(results):
                return results[n]['uri']
        except ValueError:
            print >>sys.stderr, "Not a number"
        try:
            url=urlparse(line)
            if line.startswith('http://dbpedia.org/'):
                return line
            print >>sys.stderr, "Resource should start with http://dbpedia.org: %s" % line
        except:
            print >>sys.stderr, "Not an url: %s" % line

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-f',
                    '--force',
                    action='store_true',
                    help='force reloading cache'),
    )
    def handle(self, *labels, **options):
        if labels:
            query=Topic.objects.filter(preferred_name__in = labels)
        else:
            query=Topic.objects.all()
            
        for topic in query:
            if topic.rdf is not None and not (labels or options['force']):
                continue
            if topic.topic_node.type not in ['PLA', 'ORG', 'PER']: 
                continue
            if options['force']:
                if topic.rdf:
                    semantic_resolve_topic(topic,topic.rdf)
                continue
            schematype = topic_to_schema(topic.topic_node.type)
            prefix = "http://schema.org/"
            dbontology = schematype[len(prefix):]
            print topic.preferred_name, dbontology
            response = dbpedia_lookup(topic.preferred_name, dbontology)
            results = response['results']
            print "Received %d responses." % len(results)
            if len(results) != 0:
#                print results
                ans=ask_resolution(topic.preferred_name, results)
                if ans is not None:
                    semantic_resolve_topic(topic,ans)
