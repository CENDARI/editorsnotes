from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from editorsnotes.main.models import Project
from .cendari_api import *

import logging
logger = logging.getLogger(__name__)

@receiver(post_save)
def update_elastic_cendari_handler(sender, instance, created, **kwargs):
    if isinstance(instance, Project) and cendari_data_api.has_key():
        p = instance
        pname = cendari_clean_name(p.name)
        try:
            logger.debug('creating remote project: %s', pname)
            api.create_dataspace('nte_'+pname,title=p.name)
        except CendariDataAPIException as e:
            logger.error('Problem synchonizing projects with DATA Api: %s', e)
        except:
            logger.error("Unexpected error: %s", sys.exc_info()[0])

@receiver(post_delete)
def delete_elastic_cendari_handler(sender, instance, **kwargs):
    if isinstance(instance, Project) and cendari_data_api.has_key():
        p = instance
        pname = cendari_clean_name(p.name)
        try:
            logger.debug('deleting remote project: %s', pname)
            # Need to retrieve the project id first
            #api.delete_dataspace(p.id)
        except CendariDataAPIException as e:
            logger.error('Problem synchonizing projects with DATA Api: %s', e)
        except:
            logger.error("Unexpected error: %s", sys.exc_info()[0])




