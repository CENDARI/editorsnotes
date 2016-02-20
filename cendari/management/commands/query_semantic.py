from django.core.management.base import BaseCommand, CommandError

from cendari.semantic import semantic_query

import sys

class Command(BaseCommand):
    def handle(self, *labels, **options):
        if not labels:
            raise CommandError('Enter a sparql expression.')
        query=" ".join(labels)
        try:
            res=semantic_query(query)
            for r in res:
                print r
        except:
            raise CommandError('Query error: %s' % sys.exc_info()[0])
