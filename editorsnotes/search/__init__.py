from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from reversion import post_revision_commit

from editorsnotes.main import models as main_models

from .index import ENIndex, ActivityIndex
from .types import DocumentTypeAdapter

__all__ = ['en_index', 'activity_index']

class DocumentAdapter(DocumentTypeAdapter):
    display_field = 'serialized.description'
    highlight_fields = ('serialized.description',)
    def get_mapping(self):
        mapping = super(DocumentAdapter, self).get_mapping()
        mapping[self.type_label]['properties']['serialized']['properties'].update({
            'zotero_data': {
                'properties': {
                    'itemType': {'type': 'string', 'index': 'not_analyzed'},
                    'publicationTitle': {'type': 'string', 'index': 'not_analyzed'},
                    'archive': {'type': 'string', 'index': 'not_analyzed'},
                }
            }
        })
        return mapping

en_index = ENIndex()
en_index.register(main_models.Note,
                  display_field='serialized.title',
                  highlight_fields=('serialized.title',
                                    'serialized.content',
                                    'serialized.sections'))
en_index.register(main_models.Topic,
                  display_field='serialized.preferred_name',
                  highlight_fields=('serialized.preferred_name',
                                    'serialized.summary'))

en_index.register(main_models.Document, adapter=DocumentAdapter)

activity_index = ActivityIndex()

@receiver(post_revision_commit)
def update_activity_index(instances, revision, versions, **kwargs):
    handled = [(instance, version) for (instance, version)
               in zip(instances, versions)
               if issubclass(instance.__class__, main_models.base.Administered)]
    for instance, version in handled:
        activity_index.handle_edit(instance, version)

@receiver(post_save)
def update_elastic_search_handler(sender, instance, created, **kwargs):
    klass = instance.__class__
    if klass in en_index.document_types:
        document_type = en_index.document_types[klass]
        if created:
            document_type.index(instance)
        else:
            document_type.update(instance)
    elif isinstance(instance, main_models.notes.NoteSection):
        update_elastic_search_handler(sender, instance.note, False)

@receiver(post_delete)
def delete_es_document_handler(sender, instance, **kwargs):
    klass = instance.__class__
    if klass in en_index.document_types:
        document_type = en_index.document_types[klass]
        document_type.remove(instance)
