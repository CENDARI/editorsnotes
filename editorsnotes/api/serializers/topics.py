from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import Field
from rest_framework.reverse import reverse

from editorsnotes.main.models import Topic, TopicNode

from .base import (RelatedTopicSerializerMixin, ProjectSpecificItemMixin,
                   ProjectSlugField, URLField)
from .documents import CitationSerializer
 # Cendari code E.G. aviz
from cendari.semantic import semantic_resolve_topic, semantic_query_latlong
from cendari.utils import WELL_KNOWN_DATE_FORMATS, parse_well_known_date

class TopicNodeSerializer(serializers.ModelSerializer):
    name = Field(source='_preferred_name')
    url = URLField('api:api-topic-nodes-detail', ('id',))
    alternate_forms = serializers.SerializerMethodField('get_alternate_forms')
    project_topics = serializers.SerializerMethodField('get_project_value')
    date = serializers.DateTimeField(required=False,input_formats=WELL_KNOWN_DATE_FORMATS,)
    
    class Meta:
        model = TopicNode
        fields = ('id', 'name', 'url', 'alternate_forms', 'type',
                  'project_topics', 'rdf', 'date')
    def get_alternate_forms(self, obj):
        topics = obj.project_topics.select_related('alternate_names')
        alternate_forms = set() 
        alternate_forms.update(topic.preferred_name for topic in topics)
        alternate_forms.update(
            alternate_name.name
            for topic in topics
            for alternate_name in topic.alternate_names.all())
        alternate_forms.remove(obj._preferred_name)
        return list(alternate_forms)
    def get_project_value(self, obj):
        return [OrderedDict((
            ('project_name', topic.project.name),
            ('project_url', reverse('api:api-project-detail',
                            args=(topic.project.slug,),
                            request=self.context['request'])),
            ('preferred_name', topic.preferred_name),
            ('url', reverse('api:api-topics-detail',
                                  args=(topic.project.slug, obj.id),
                                  request=self.context['request']))))
            for topic in obj.project_topics.select_related('project')]

class AlternateNameField(serializers.SlugRelatedField):
    def field_from_native(self, data, files, field_name, into):
        if self.read_only:
            return
        into[field_name] = data.get(field_name, [])

class TopicSerializer(RelatedTopicSerializerMixin, ProjectSpecificItemMixin,
                      serializers.ModelSerializer):
    topic_node_id = Field(source='topic_node.id')
    type = Field(source='topic_node.type')
    alternate_names = AlternateNameField(slug_field='name', many=True)
    url = URLField(lookup_arg_attrs=('project.slug', 'topic_node_id'))
    project = ProjectSlugField()
    citations = CitationSerializer(source='summary_cites', many=True, read_only=True)
    date = serializers.DateTimeField(required=False,input_formats=WELL_KNOWN_DATE_FORMATS,)
   
    # Cendari code E.G. aviz
    latlong = serializers.SerializerMethodField('get_lat_long')
    class Meta:
        model = Topic
        # Cendari code E.G. aviz -- added rdf to fields
        fields = ('id', 'topic_node_id', 'preferred_name', 'type', 'url',
                  'alternate_names', 'related_topics', 'project',
                  'last_updated', 'summary', 'citations','rdf', 'date','latlong')
    def save_object(self, obj, **kwargs):
        if not obj.id:
            topic_node_id = self.context.get('topic_node_id', None)
            if topic_node_id is None and 'view' in self.context:
                topic_node_id = self.context['view'].kwargs.get(
                    'topic_node_id', None)
            if topic_node_id is None:
                topic_node = TopicNode.objects.create(
                    _preferred_name=obj.preferred_name,
                    creator_id=obj.creator_id,
                    last_updater_id=obj.creator_id)
                topic_node_id = topic_node.id
            obj.topic_node_id = topic_node_id

        alternate_names = obj._related_data.pop('alternate_names')
        super(TopicSerializer, self).save_object(obj, **kwargs)
        self.save_alternate_names(obj, alternate_names)
        # Cendari code E.G. aviz
        if self.context['request']:
            if 'date_custom' in self.context['request'].DATA :
                date_tbs = parse_well_known_date(self.context['request'].DATA['date_custom'], False)   
                if date_tbs != None:
                    obj.date = date_tbs         
        semantic_resolve_topic(obj)
    def save_alternate_names(self, obj, alternate_names):
        to_create = set(alternate_names)
        to_delete = []

        queryset = self.fields['alternate_names'].queryset or []
        for alternate_name_obj in queryset:
            name = alternate_name_obj.name
            if name in alternate_names:
                to_create.remove(name)
            else:
                to_delete.append(alternate_name_obj)

        for alternate_name_obj in to_delete:
            alternate_name_obj.delete()

        user = self.context['request'].user
        for name in to_create:
            obj.alternate_names.create(name=name, creator_id=user.id)


    # Cendari code E.G. aviz
    def get_lat_long(self,topic):
        return semantic_query_latlong(topic)

