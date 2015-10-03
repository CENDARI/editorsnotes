from collections import OrderedDict
from itertools import chain
import json
import os
from datetime import datetime

from pyelasticsearch import ElasticSearch, IndexAlreadyExistsError
from pyelasticsearch.exceptions import InvalidJsonResponseError

from editorsnotes.main.models import Note, Document, Topic
from editorsnotes.main.utils import xhtml_to_text
from editorsnotes.search.utils import clean_query_string
from cendari.semantic import semantic_uri, semantic_query_latlong, schema_topic, topic_schema

import logging
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.realpath(__file__))

topic_field = {
    'EVT': 'event',
    'ORG': 'org',
    'PER': 'person',
    'PUB': 'ref',
    'PLA': 'place'
}

def format_location(loc):
    return ', '.join(map(str, loc))


# Copy from editorsnotes.search.index
# For some reason, I cannot import it??
# Then drift-away to fit Cendari's needs
class OrderedResponseElasticSearch(ElasticSearch):
    def _decode_response(self, response):
        try:
            json_response = json.loads(response.content,
                                       object_pairs_hook=OrderedDict)
        except ValueError:
            logger.error("Invalid response received %s", str(response))
            raise InvalidJsonResponseError(response)
        return json_response

class CendariIndex(object):
    document_types = [ Note, Document, Topic ]

    def __init__(self, name='cendari', alias=True):
        self.name = name
        self.alias = alias
        self.is_open = False
        self.update_list = set()
        self.delete_list = set()

    def _open(self):
        pass

    def open(self):
        from django.conf import settings

        if self.is_open:
            return self.es
        logger.info('opening ElasticSearch index %s', self.name)
        if not hasattr(self, 'es'):
            self.es = OrderedResponseElasticSearch(settings.ELASTICSEARCH_URLS)
        self.is_open = True
        try:
            self.created = self.create()
        except IndexAlreadyExistsError as ex:
            self.created = False
        self.ensure_mapping(self.real_name)
        self._open()
        return self.es

    def get_settings(self):
        return {}

    def generate_real_name(self):
        return self.name+datetime.now().strftime('_%Y-%m-%d_%H:%M:%S')

    def create(self):
        aliases = self.open().aliases(self.name)
        if len(aliases)>1:
            raise RuntimeError('Unexpected multiple aliases for %s: %s', self.name, alias.keys())
        elif len(aliases)==0: # no alias or index exist, create index and maybe alias
            if self.alias:
                self.real_name = self.generate_real_name()
            else:
                self.real_name = self.name
            logger.debug("Creating index '%s'", self.real_name)
            created = self.open().create_index(self.real_name, self.get_settings())
            if self.alias:
                logger.info("Aliasing index '%s' as '%s'", self.real_name, self.name)
                self.open().update_aliases(actions=[{ "add": { "alias": self.name, "index": self.real_name}}])
        else:
            # len(alias)==1, either an alias exists or the index is already created
            self.real_name = aliases.keys()[0]
            logger.debug("Index '%s' already created", self.name)
            created = False # self.open().create_index(self.real_name, self.get_settings()) # raises err
        return created

    def delete(self):
        logger.info("Deleting index '%s'", self.name)
        aliases = self.open().aliases(self.name)
        if len(aliases)>1:
            raise RuntimeError('Unexpected multiple aliases for %s: %s', self.name, alias.keys())
        elif len(aliases)==0:
            logger.info("Already deleted index '%s'", self.name)
            return # already deleted
        real_name = aliases.keys()[0]
        if real_name != self.name:
            logger.info("Deleting alias '%s' for index '%s'", self.name, real_name)
            self.open().update_aliases(actions=[{ "remove": { "alias": self.name, "index": real_name}}])
        logger.info("Deleting real index '%s'", real_name)
        ret = self.open().delete_index(real_name)
        self.is_open = False
        return ret

    def delete_document(self):
        ret = self.open().delete_all(self.name, 'document')
        self.is_open = False
        return ret

    def delete_entity(self):
        ret = self.open().delete_all(self.name, 'entity')
        self.is_open = False
        return ret

    def ensure_mapping(self, name):
        mappings = self.open().get_mapping(name)\
                              .get(name,{})\
                              .get('mappings',{})\
                              .keys()
        if 'document' not in mappings:
            logger.info("Creating 'document' mapping in %s", name)
            self.open().put_mapping(name, 'document',
                                    self.get_mapping_document())
        if 'entity' not in mappings:
            logger.info("Creating 'entity' mapping in %s", name)
            self.open().put_mapping(name, 'entity',
                                    self.get_mapping_entity())

    def get_mapping_document(self):
        with open(os.path.join(current_dir, 'mapping_document.json')) as f:
            return json.load(f)
        return {}

    def get_mapping_entity(self):
        with open(os.path.join(current_dir, 'mapping_entity.json')) as f:
            return json.load(f)

    def collect_topics(self,node):
        topics = {
            'EVT': [],
            'ORG': [],
            'PER': [],
            'PUB': [],
            'ART': [],
            'PLA': [],
            'TAG': []
        }
        for ta in node.related_topics.all():
            topic = ta.topic
            if topic is None or topic.topic_node is None:
                pass
            elif topic.topic_node.type=='EVT':
                date = topic.date
#                if date is None:
#                    date = utils.parse_well_known_date(topic.preferred_name)
                if date:
                    topics[topic.topic_node.type].append(date)
            elif topic.topic_node.type=='PLA':
                place = { 'name': topic.preferred_name }
                loc = semantic_query_latlong(topic)
                if loc: place['location'] = format_location(loc)
                topics[topic.topic_node.type].append(place)
            else:
                topics[topic.topic_node.type].append(topic.preferred_name)
        return topics

    def document_to_cendari(self, doc):
        id=str(semantic_uri(doc))
        contributors = set(doc.get_all_updaters())
        contributors.add(doc.creator)
        topics=self.collect_topics(doc)
        title=xhtml_to_text(doc.description)
        if doc.has_transcript():
            text = xhtml_to_text(doc.transcript.content)
        else:
            text=''
        document = {
            'uri': id,
            'artifact': 'document',
            'application': 'nte',
            'contributor': [
                {"name": c.username, "email": c.email} for c in contributors
            ],
            'creator': {
                "name": doc.creator.username,
                "email": doc.creator.email
            },
            'created': doc.created,
            'updated': doc.last_updated,
            'format': 'application/xhtml+xml', # nothing better eg. xhtml+rdfa
            'title': title,
            'text': text,
            'project': doc.project.slug,
            'groups_allowed': doc.project.slug,
             # FIXME when I know how to test public projects
            'users_allowed': [ doc.creator.username ],
        }
        if topics['EVT']: document['date'] = topics['EVT']
        if topics['ORG']: document['org'] = topics['ORG']
        if topics['PER']: document['person'] = topics['PER']
        if topics['PLA']:
            pla = topics['PLA']
            document['place'] = map(lambda p: p['name'], pla)
            document['location'] = [l['location'] for l in pla if 'location' in l ]
        # 'publisher': publishers,
        if topics['PUB']: document['ref'] = topics['PUB']
        if topics['TAG']: document['tag'] = topics['TAG']
#        if document is not None:
#            self.es.index(self.name, 'document', document, id, refresh=True)
        return document

    def note_to_cendari(self, note):
        id=str(semantic_uri(note))
        contributors = set(note.get_all_updaters())
        contributors.add(note.creator)
        topics=self.collect_topics(note)
        text=xhtml_to_text(note.content)
        document = {
            'uri': id,
            'application': 'nte',
            'artifact': 'note',
            'contributor': [
                {"name": c.username, "email": c.email} for c in contributors
            ],
            'creator': {
                "name": note.creator.username,
                "email": note.creator.email
            },
            'created': note.created,
            'updated': note.last_updated,
            'format': 'application/xhtml+xml', # nothing better eg. xhtml+rdfa
            'title': note.title,
            'text': text,
            'project': note.project.slug,
            'groups_allowed': note.project.slug,
             # FIXME when I know how to test public projects
            'users_allowed': [ note.creator.username ]
        }
        if topics['EVT']: document['date'] = topics['EVT']
        if topics['ORG']: document['org'] = topics['ORG']
        if topics['PER']: document['person'] = topics['PER']
        if topics['PLA']:
            pla = topics['PLA']
            document['place'] = map(lambda p: p['name'], pla)
            document['location'] = [ l['location'] for l in pla if 'location' in l]
        # 'publisher': publishers,
        if topics['PUB']: document['ref'] = topics['PUB']
        if topics['TAG']: document['tag'] = topics['TAG']
#        if document is not None:
#            self.es.index(self.name, 'document', document, id, refresh=True)
        return document

    def topic_to_cendari(self, topic):
        if not topic.topic_node: return
        id=str(semantic_uri(topic))
        type = topic.topic_node.type
        document = {
            'uri': id,
            'application': 'nte',
            'title': topic.preferred_name,
            'creator': topic.creator.username,
            'created': topic.created,
            'updated': topic.last_updated,
            'project': topic.project.slug,
            'groups_allowed': topic.project.slug,
        }
        if topic.summary: document['text'] = xhtml_to_text(topic.summary)
        loc = semantic_query_latlong(topic)
        if loc: document['location'] = format_location(loc)
        if type in topic_schema:
            document['class'] = topic_schema[type]
        if type in topic_field:
            document[topic_field[type]] = topic.preferred_name
        if topic.date:
            document['date'] = topic.date
        return document

    def object_changed(self, obj):
        if type(obj) not in self.document_types: return
        id = str(semantic_uri(obj))
        if id in self.delete_list: # was removed, just update now
            self.delete_list.remove(id)
        self.update_list.add(obj)
        if isinstance(obj, Topic) and obj.topic_node.type=='PLA':
            # touch all notes and documents so their places get updated
            # either location is added or removed, who knows?
            for t in obj.topic_node.related_objects():
                if isinstance(t, Note) or isinstance(t, Document):
                    self.object_changed(t)

    def object_deleted(self, obj):
        if type(obj) not in self.document_types: return
        id = str(semantic_uri(obj))
        if obj in self.update_list: # was updated, just remove now
            self.update_list.remove(obj)
        self.delete_list.add(id)

    def delete_ops(self):
        for id in self.delete_list:
            doc_type = 'document' if '/topic/' in id else 'entity'
            yield es.delete(id=id, doc_type=doc_type)

    def index_ops(self):
        for obj in self.update_list:
            if isinstance(obj, Note):
                doc = self.note_to_cendari(obj)
                doc_type = 'document'
            elif isinstance(obj, Document):
                doc = self.document_to_cendari(obj)
                doc_type = 'document'
            elif isinstance(obj, Topic):
                doc = self.topic_to_cendari(obj)
                doc_type = 'entity'
            else:
                continue
            yield self.es.index_op(doc, doc_type=doc_type)

    def process_update_list(self):
        # Should I test the values returned by bulk?
        if len(self.delete_list):
            self.open().bulk(self.delete_ops(), index=self.name)
            self.delete_list = set()
        if len(self.update_list):
            self.open().bulk(self.index_ops(), index=self.name)
            self.update_list = set()

    def search_model(self, model, query, **kwargs):
        return self.open().search(query,
                                  index=self.name, doc_type='document',
                                  **kwargs)

    def get_location(self, id):
        ret = self.open().get(index=self.name, doc_type='entity', id=id, fields='location')
        if ret['found'] and 'location' in ret['fields']:
            locs = ret['fields']['location']
            if isinstance(locs, list):
                locs = locs[0]
            return locs
        return None

    def search(self, query, highlight=False, **kwargs):
        self.open()
        if isinstance(query, basestring):
            prepared_query = {
                'query': {
                    'query_string': { 'query': clean_query_string(query) }
                }
            }

        else:
            prepared_query = query

        if 'project' in kwargs:
            project = kwargs.pop('project')
            prepared_query['filter'] = {
                "term": { 'project': project }
            }

        if highlight:
            prepared_query['highlight'] = {
                'number_of_fragments': 3,
                'fragment_size': 150,
                'no_match_size': 150,
                'fields': {'text': {}, 'label': {}, 'abstract': {}},
                'pre_tags': ['<span class="highlighted">'],
                'post_tags': ['</span>']
            }

        #pprint.pprint(prepared_query)
        return self.open().search(prepared_query, index=self.name, **kwargs)


def cendari_get_project_topics(topic_type,project_name,name_prefix):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "query_string": {
                            "default_field": "topic.serialized.type",
                            "query": topic_type
                        }
                    },
                    {
                        "query_string": {
                            "default_field": "topic.serialized.project.name",
                            "query": project_name
                        }
                    },
                    {
                        "prefix": {
                            "topic.serialized.preferred_name": name_prefix.lower()
                        }
                    }
                ],
                "must_not": [],
                "should": []
            }
        },
        "from": 0,
        "size": 10,
        "sort": [],
        "facets": {}
    }

    es = ElasticSearch('http://localhost:9200/')
    results = es.search(query, index='editorsnotes-items')

    return results
   
