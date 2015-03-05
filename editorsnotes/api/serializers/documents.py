from collections import OrderedDict
import json

from lxml import etree
from rest_framework import serializers
from rest_framework.reverse import reverse

from editorsnotes.main.models import Document, Citation, Scan, Transcript

from .base import (RelatedTopicSerializerMixin, ProjectSpecificItemMixin,
                   URLField, ProjectSlugField, HyperlinkedProjectItemField,
                   TopicAssignmentField)

# Cendari code E.G. aviz
from cendari.semantic import semantic_process_document,semantic_process_transcript


class ZoteroField(serializers.WritableField):
    def to_native(self, zotero_data):
        return zotero_data and json.loads(zotero_data,
                                          object_pairs_hook=OrderedDict)
    def from_native(self, data):
        return data and json.dumps(data)

class HyperLinkedImageField(serializers.ImageField):
    def to_native(self, value):
        if not value.name:
            ret = None
        elif 'request' in self.context:
            ret = self.context['request'].build_absolute_uri(value.url)
        else:
            ret = value.url
        return ret

class ScanSerializer(serializers.ModelSerializer):
    creator = serializers.Field('creator.username')
    image = HyperLinkedImageField()
    image_thumbnail = HyperLinkedImageField(read_only=True)
    
     # Cendari code E.G. aviz
    image_thumbnail_url = serializers.SerializerMethodField('it_url')
    
    class Meta:
        model = Scan
        fields = ('id', 'image', 'image_thumbnail', 'ordering', 'created',
                  'creator','image_thumbnail_url',)
    
    # Cendari code E.G. aviz
    def it_url(self,scan):
        return scan.image_thumbnail.url

class DocumentSerializer(RelatedTopicSerializerMixin, ProjectSpecificItemMixin,
                         serializers.ModelSerializer):
    project = ProjectSlugField()

    # Cendari code E.G. aviz
    # added from the editors note repository
    transcript = serializers.SerializerMethodField('get_transcript_url')

    zotero_data = ZoteroField(required=False)
    url = URLField()
    scans = ScanSerializer(many=True, required=False, read_only=True)
    def get_validation_exclusions(self):
        # TODO: This can be removed in future versions of django rest framework.
        # It's necessary because for the time being, DRF excludes non-required
        # fields from validation (not something I find particularly useful, but
        # they must've had their reasons...)
        exclusions = super(DocumentSerializer, self).get_validation_exclusions()
        exclusions.remove('zotero_data')
        return exclusions
    
    class Meta:
        model = Document
        fields = ('id', 'description', 'url', 'project', 'last_updated',
                  'scans', 'transcript', 'related_topics', 'zotero_data',)
    # Cendari code E.G. aviz
    def save_object(self, obj, **kwargs):
        super(DocumentSerializer, self).save_object(obj, **kwargs)
        print "creating semantics for document"
        print obj
        semantic_process_document(obj)

    # Cendari code E.G. aviz
    # added from the editors note repository
    def get_transcript_url(self, obj):
        if not obj.has_transcript():
            return None
        return reverse('api:api-transcripts-detail',
                       args=(obj.project.slug, obj.id),
                       request=self.context.get('request', None))

# Cendari code E.G. aviz
# added from the editors note repository
class TranscriptSerializer(serializers.ModelSerializer):
    url = URLField(lookup_arg_attrs=('document.project.slug', 'document.id'))
    document = HyperlinkedProjectItemField(
        required=True, view_name='api:api-documents-detail')

    # Cendari code E.G. aviz
    def save_object(self, obj, **kwargs):
        super(TranscriptSerializer, self).save_object(obj, **kwargs)
        print "creating semantics for transcript"
        print obj
        semantic_process_transcript(obj)

    class Meta:
        model = Transcript

class CitationSerializer(serializers.ModelSerializer):
    url = URLField('api:api-topic-citations-detail',
                   ('content_object.project.slug', 'content_object.topic_node_id', 'id'))
    document = HyperlinkedProjectItemField(view_name='api:api-documents-detail')
    document_description = serializers.SerializerMethodField('get_document_description')
    class Meta:
        model = Citation
        fields = ('id', 'url', 'ordering', 'document', 'document_description', 'notes')
    def get_document_description(self, obj):
        return etree.tostring(obj.document.description)
