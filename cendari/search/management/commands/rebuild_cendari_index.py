import traceback
from django.core.management.base import BaseCommand
from editorsnotes.main.models import Note, Document, Topic

from ... import cendari_index

class Command(BaseCommand):
    help = 'Rebuild elasticsearch index'
    def handle(self, *args, **kwargs):
        for model in [ Note, Document, Topic ]:
            ct = model.objects.count()
            self.stdout.write(u'Creating {:,} "{}" documents'.format(
                ct, model._meta.object_name))
            for obj in model.objects.all():
                try:
                    cendari_index.object_changed(obj)
                except Exception as e:
                    traceback.print_exc(e)
                
            cendari_index.process_update_list()

