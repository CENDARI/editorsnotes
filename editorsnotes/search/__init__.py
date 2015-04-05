from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from reversion import post_revision_commit

from editorsnotes.main import models as main_models

from .index import ENIndex, ActivityIndex
from .types import DocumentTypeAdapter

__all__ = ['en_index', 'activity_index', 'ElasticSearchIndex']


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

#[jdf] Deferred registration of models to avoid connecting to ES
def register_models(en_index):
    en_index.register(main_models.Note,
                      display_field='serialized.title',
                      highlight_fields=('serialized.title',
                                        'serialized.content',
                                        'serialized.sections'))
    en_index.register(main_models.Topic,
                      display_field='serialized.preferred_name',
                      highlight_fields=('serialized.preferred_name',
                                        'serialized.summary',
                                        'serialized.rdf',
                                        'serialized.date'))
    en_index.register(main_models.Document, adapter=DocumentAdapter)

print "Creating the EditorsNotes index" 

en_index = ENIndex(onOpen=register_models)

activity_index = ActivityIndex()

@receiver(post_revision_commit)
def update_activity_index(instances, revision, versions, **kwargs):
    handled = [(instance, version) for (instance, version)
               in zip(instances, versions)
               if issubclass(instance.__class__, main_models.base.Administered)]
    for instance, version in handled:
        if not activity_index.is_open:
            activity_index.open()
        activity_index.handle_edit(instance, version)

@receiver(post_save)
def update_elastic_search_handler(sender, instance, created, **kwargs):
    klass = instance.__class__
    #if klass in en_index.document_types:
    if klass in [ main_models.Document, main_models.Note, main_models.Topic]:
        if not en_index.is_open:
            en_index.open()
        document_type = en_index.document_types[klass]
        if created:
            document_type.index(instance)
        else:
            document_type.update(instance)
    elif isinstance(instance, main_models.notes.NoteSection):
        if not en_index.is_open:
            en_index.open()
        update_elastic_search_handler(sender, instance.note, False)

@receiver(post_delete)
def delete_es_document_handler(sender, instance, **kwargs):
    klass = instance.__class__
    #if klass in en_index.document_types:
    if klass in [ main_models.Document, main_models.Note, main_models.Topic]:
        if not en_index.is_open:
            en_index.open()
        document_type = en_index.document_types[klass]
        document_type.remove(instance)
