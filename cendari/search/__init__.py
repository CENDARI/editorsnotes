from django.db.models.signals import post_save, post_delete
from django.core.signals import request_finished
from django.dispatch import receiver

from editorsnotes.main import models as main_models

from .index import CendariIndex

cendari_index = CendariIndex()

@receiver(post_save)
def update_elastic_cendari_handler(sender, instance, created, **kwargs):
    cendari_index.object_changed(instance)

@receiver(post_delete)
def delete_elastic_cendari_handler(sender, instance, **kwargs):
    cendari_index.object_deleted(instance)

@receiver(request_finished)
def update_elastic_cendari_operations(**kwargs):
    cendari_index.process_update_list()
