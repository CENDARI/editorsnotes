from django.core.management.base import BaseCommand
from django.conf import settings

import sys
import traceback
from datetime import datetime
from pprint import pprint

from ... import cendari_index, CendariIndex
from elasticsearch import Elasticsearch
from elasticsearch.helpers import reindex

class Command(BaseCommand):
    help = 'Change elasticsearch mappings'
    def handle(self, *args, **kwargs):
        index_name = cendari_index.name
        new_name = cendari_index.generate_real_name()
        new_index = CendariIndex(new_name, alias=False)
        es = new_index.open() # magically apply the new mappings
        aliases = es.aliases(index_name)
        old_name = None
        if len(aliases)>1:
            raise RuntimeError('Unexpected multiple aliases for %s: %s', index_name, aliases.keys())
        elif len(aliases)==0:
            # no alias created yet, let's do it since editorsnote has never run then
            es.update_aliases(actions=[{ "add": { "alias": index_name, "index": new_name }}])
        else:
            old_name = aliases.keys()[0]
        if old_name:
            try:
                print "Reindexing, it can take a while..."
                oes=Elasticsearch(settings.ELASTICSEARCH_URLS)
                ret=reindex(oes, old_name, new_name)
                print "Reindex returned:"
                pprint(ret)
            except Exception as e:
                traceback.print_exc(e)

            if not aliases[old_name]['aliases']:
                print('Index %s exists and cannot be aliased to %s, removing it...', index_name,new_name)
                es.delete_index(old_name)
                es.update_aliases(actions=[{ "add": { "alias": index_name, "index": new_name }}])
            else:
                es.update_aliases(actions=[
                    { "remove": {
                        "alias": index_name,
                        "index": old_name
                    }},
                    { "add": {
                        "alias": index_name,
                        "index": new_name
                    }}
                ])
            print 'You can now delete the old index %s' % old_name
            print "curl -XDELETE '%s/%s/'" % (settings.ELASTICSEARCH_URLS, old_name)
