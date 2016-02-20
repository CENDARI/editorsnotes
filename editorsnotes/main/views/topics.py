from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.base import RedirectView

from editorsnotes.search import en_index

from .. import utils
from ..models import (
    Project, Document, Citation, Note, Topic, LegacyTopic, TopicNode)

def _sort_citations(instance):
    cites = { 'all': [] }
    for c in Citation.objects.filter(
        content_type=ContentType.objects.get_for_model(instance), 
        object_id=instance.id):
        cites['all'].append(c)
    cites['all'].sort(key=lambda c: c.ordering)
    return cites


class LegacyTopicRedirectView(RedirectView):
    permanent = True
    query_string = True
    def get_redirect_url(self, topic_slug):
        legacy_topic = get_object_or_404(LegacyTopic, slug=topic_slug)
        return reverse('topic_node_view', args=(legacy_topic.merged_into_id,))

def topic_node(request, topic_node_id):
    o = {}
    node_qs = TopicNode.objects.select_related()
    o['topic_node'] = get_object_or_404(node_qs, id=topic_node_id)
    return render_to_response(
        'topic_node.html', o, context_instance=RequestContext(request))

def topic(request, project_slug, topic_node_id):
    o = {}
    topic_qs = Topic.objects.select_related('topic_node', 'creator',
                                            'last_updater', 'project')\
            .prefetch_related('related_topics__topic')
    o['topic'] = topic = get_object_or_404(topic_qs,
                                           topic_node_id=topic_node_id,
                                           project__slug=project_slug)
    o['project'] = topic.project
    o['breadcrumb'] = (
        (topic.project.name, topic.project.get_absolute_url()),
        ('Topics', reverse('all_topics_view',
                                kwargs={'project_slug': topic.project.slug})),
        (topic.preferred_name, None)
    )

    topic_query = {'query': {'term': {'serialized.related_topics.id': topic.id }}}
    topic_query['size'] = 1000

    model_searches = ( en_index.search_model(model, topic_query) for model in
                       (Document, Note, Topic) )
    documents, notes, topics = (
        [ result['_source']['serialized'] for result in search['hits']['hits'] ]
        for search in model_searches)

    o['documents'] = Document.objects.filter(id__in=[d['id'] for d in documents])
    o['related_topics'] = Topic.objects.filter(id__in=[t['id'] for t in topics])
    note_objects = Note.objects.in_bulk([n['id'] for n in notes])
    for note in notes:
        related_topics = list((topic for topic in note['related_topics']
                               if topic['url'] != request.path))
        note_objects[note['id']] = (note_objects[note['id']], related_topics,)
    o['notes'] = note_objects.values()

    return render_to_response(
        'topic.html', o, context_instance=RequestContext(request))

def all_topics(request, project_slug=None):
    "View all topics, either site-wide or within a project."

    # TODO: Use ElasticSearch

    o = {}

    if 'type' in request.GET:
        o['type'] = request.GET['type']
        o['fragment'] = ''
        template = 'topic-columns.include'
    else:
        o['type'] = 'PER'
        template = 'all-topics.html'

    if project_slug:
        o['project'] = get_object_or_404(Project, slug=project_slug)
        query_set = Topic.objects\
                .select_related('topic_node', 'project')\
                .filter(project_id=o['project'].id, topic_node__type=o['type'])
        o['breadcrumb'] = (
            (o['project'].name, o['project'].get_absolute_url()),
            ('Topics', None),
        )
    else:
        query_set = TopicNode.objects.filter(type=o['type'])
        o['breadcrumb'] = (
            ('Browse', reverse('browse_view')),
            ('Topics', None)
        )

    [o['topics_1'], o['topics_2'], o['topics_3']] = utils.alpha_columns(
        query_set, 'preferred_name', itemkey='topic')
    return render_to_response(
        template, o, context_instance=RequestContext(request))

