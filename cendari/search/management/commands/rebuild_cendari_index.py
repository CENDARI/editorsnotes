from django.core.management.base import BaseCommand
from editorsnotes.main.models import Note, Document, Topic

from ... import cendari_index

class Command(BaseCommand):
    help = 'Rebuild elasticsearch index'
    def handle(self, *args, **kwargs):
        for model in [ Note, Document ]:
            ct = model.objects.count()
            self.stdout.write(u'Creating {:,} "{}" documents'.format(
                ct, model._meta.object_name))
            for obj in model.objects.all():
                cendari_index.object_changed(obj)
        cendari_index.process_update_list()

