import datetime
import json

from django.db import models
from django.utils.translation import ugettext as _

from . import utils
from .fields import ZoteroField


class ZoteroItem(models.Model):
    zotero_data = ZoteroField(blank=True, null=True)
    zotero_link = models.OneToOneField('ZoteroLink', blank=True, null=True,
                                       related_name='zotero_item')
    class Meta:
        abstract = True
    def get_zotero_fields(self):
        if self.zotero_data is None:
            return ()
        zotero_data = json.loads(self.zotero_data)
        zotero_data['itemType'] = _(zotero_data['itemType'])
        if self.zotero_link and self.zotero_link.date_information:
            date_parts = json.loads(self.zotero_link.date_information)
            for part in date_parts:
                zotero_data[part] = date_parts[part]
        if zotero_data['creators']:
            names = zotero_data.pop('creators')
            output = zotero_data.items()
            for name in names:
                output.append(
                    (name['creatorType'], utils.get_creator_name(name)) )
        else:
            output = zotero_data.items()
        return output

class ZoteroLink(models.Model):
    zotero_url = models.URLField(blank=True)
    date_information = models.TextField(blank=True)
    cached_archive = models.ForeignKey('CachedArchive', blank=True, null=True)
    cached_creator = models.ManyToManyField('CachedCreator', blank=True, null=True)
    modified = models.DateTimeField(editable=False)
    last_synced = models.DateTimeField(blank=True, null=True)
    def save(self, update_modified=True, *args, **kwargs):
        if update_modified:
            self.modified = datetime.datetime.now()
        super(ZoteroLink, self).save(*args, **kwargs)
        item_data = json.loads(self.zotero_item.zotero_data)
        prev_archive = self.cached_archive
        if 'archive' in item_data:
            # Cache name of archive if present
            archive_query = CachedArchive.objects.get_or_create(name=item_data['archive'])
            archive = archive_query[0]
            if self not in archive.zoterolink_set.all():
                archive.zoterolink_set.add(self)
            if prev_archive and prev_archive is not archive:
                # Delete old archive if no other documents refer to it
                if len(prev_archive.zoterolink_set.all()) < 1:
                    prev_archive.delete()
            archive.save()

class CachedArchive(models.Model):
    name = models.TextField()

class CachedCreator(models.Model):
    name = models.TextField()
