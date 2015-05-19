from collections import OrderedDict
from itertools import chain
import json
import os
import logging

from pyelasticsearch import ElasticSearch, IndexAlreadyExistsError
from pyelasticsearch.exceptions import InvalidJsonResponseError

from editorsnotes.main.models import Note, Document, Topic
from editorsnotes.main.utils import xhtml_to_text
from editorsnotes.search.utils import clean_query_string
from cendari.semantic import semantic_uri, semantic_query_latlong, schema_topic, topic_schema


logger = logging.getLogger('cendari.search.index')

current_dir = os.path.dirname(os.path.realpath(__file__))

topic_field = {
    'EVT': 'event',
    'ORG': 'org',
    'PER': 'person',
    'PUB': 'ref',
    'PLA': 'place'
}

def format_location(loc):
    return "%f, %d" % (loc[0], loc[1])

# Copy from editorsnotes.search.index
# For some reason, I cannot import it??
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

    def __init__(self):
        if not hasattr(self, 'get_name'):
            raise NotImplementedError('Must implement get_name method')
        self.name = self.get_name()
        self.is_open = False
        self.update_list = set()
        self.delete_list = set()

    def _open(self):
        pass

    def open(self):
        from django.conf import settings

        if self.is_open:
            return self.es
        print('opening ElasticSearch')
        if not hasattr(self, 'es'):
            self.es = OrderedResponseElasticSearch(settings.ELASTICSEARCH_URLS)
        self.is_open = True
        #if not self.exists():
        try:
            logger.info('Creating Cendari index')
            self.create()
            self.created = True
        except IndexAlreadyExistsError as ex:
            self.created = False
        if not self.mapping_exists():
            self.put_mapping()
        self._open()
        return self.es

    def get_settings(self):
        return {}

    def create(self):
        print 'Creating index '+self.name
        created = self.open().create_index(self.name, self.get_settings())
        return created

    def delete(self):
        ret = self.open().delete_index(self.name)
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

    def get_name(self):
        return 'cendari'

    def exists(self):
        #server_url, _ = self.open().servers.get()
        resp = self.open().session.head(server_url + '/' + 'cendari')
        return resp.status_code == 200

    def mapping_exists(self):
        exists = self.open().get_mapping(self.name)\
                            .get(self.name,{})\
                            .get('mappings',{})\
                            .keys()
        return 'document' in exists

    def put_mapping(self):
        print "Creating mapping"
        self.open().put_mapping(self.name, 'document',
                                self.get_mapping_document())
        self.open().put_mapping(self.name, 'entity',
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
        id=semantic_uri(doc)
        contributors = set(doc.get_all_updaters())
        contributors.add(doc.creator)
        topics=self.collect_topics(doc)
        text=xhtml_to_text(doc.description)
        if doc.has_transcript():
            text += xhtml_to_text(doc.transcript.content)
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
            'format': 'application/xhtml+xml', # nothing better eg. xhtml+rdfa
            'text': text,
            'groups_allowed': doc.project.slug,
             # FIXME when I know how to test public projects
            'users_allowed': [ doc.creator.username ]
            
        }
        if topics['EVT']: document['date'] = topics['EVT']
        if topics['ORG']: document['org'] = topics['ORG']
        if topics['PER']: document['person'] = topics['PER']
        if topics['PLA']:
            pla = topics['PLA']
            document['place'] = map(lambda p: p['name'], pla)
            document['location'] = [ format_location(l['location']) for l in pla if 'location' in l ]
        # 'publisher': publishers,
        if topics['PUB']: document['ref'] = topics['PUB']
        if topics['TAG']: document['tag'] = topics['TAG']
#        if document is not None:
#            self.es.index(self.name, 'document', document, id, refresh=True)
        return document

    def note_to_cendari(self, note):
        id=semantic_uri(note)
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
            'format': 'application/xhtml+xml', # nothing better eg. xhtml+rdfa
            'text': text,
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
        id=semantic_uri(topic)
        type = topic.topic_node.type
        document = {
            'uri': id,
            'application': 'nte',
            'title': topic.preferred_name,
            'creator': topic.creator.username,
            'groups_allowed': topic.project.slug,
        }
        if topic.summary: document['text'] = xhtml_to_text(topic.summary)
        loc = semantic_query_latlong(topic)
        if loc: document['location'] = loc
        if type in topic_schema:
            document['class'] = topic_schema[type]
        if type in topic_field:
            document[topic_field[type]] = topic.preferred_name
        if topic.date:
            document['date'] = topic.date
        return document

    def object_changed(self, obj):
        if type(obj) not in self.document_types: return
        id = semantic_uri(obj)
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
        id = semantic_uri(obj)
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
            project = kwargs['project']
            del kwargs['project']
            prepared_query['filter'] = {
                "term": { 'groups_allowed': project }
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
