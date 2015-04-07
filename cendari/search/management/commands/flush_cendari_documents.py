from django.core.management.base import BaseCommand

from ... import cendari_index

class Command(BaseCommand):
    help = 'Remove elasticsearch cendari document index'
    def handle(self, *args, **kwargs):
        cendari_index.delete_document()
