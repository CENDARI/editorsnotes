from django.core.management.base import BaseCommand
import json, sys


from ... import cendari_index

from elasticsearch import Elasticsearch, helpers

class Command(BaseCommand):
    help = 'Remove elasticsearch cendari document index'
    def handle(self, *args, **kwargs):
        es = cendari_index.open()

        def litef_documents(json):
            for doc in json:
                if doc is not None:
                    uri = doc['uri']
                    if isinstance(uri, list):
                        doc['uri'] = uri[0]
                    yield es.index_op(doc, doc_type='document')

        if len(args) > 0:
            js = json.load(args[0])
        else:
            js = json.load(sys.stdin)
        res=es.bulk(litef_documents(js), index=cendari_index.name)
        with open('add_litef.out.json', 'w') as f:
            json.dump(res, f)
