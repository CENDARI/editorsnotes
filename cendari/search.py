from collections import OrderedDict
from itertools import chain
import json

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.conf import settings

from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import InvalidJsonResponseError

__all__ = ['cendari_index']

# Copy from editorsnotes.search.index
# For some reason, I cannot import it??
class OrderedResponseElasticSearch(ElasticSearch):
    def _decode_response(self, response):
        try:
            json_response = json.loads(response.content,
                                       object_pairs_hook=OrderedDict)
        except ValueError:
            raise InvalidJsonResponseError(response)
        return json_response

class CendariIndex(object):
    def __init__(self):
        if not hasattr(self, 'get_name'):
            raise NotImplementedError('Must implement get_name method')
        self.name = self.get_name()
        self.is_open = False

    def _open(self):
        pass

    def open(self):
        if self.is_open:
            return self.es
        print('opening ElasticSearch')
        self.es = OrderedResponseElasticSearch(settings.ELASTICSEARCH_URLS)
        self.is_open = True
        if not self.exists():
            self.create()
            self.created = True
        else:
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
        self.open()
        return self.open().delete_index(self.name)

    def get_name(self):
        return 'cendari'

    def exists(self):
        server_url, _ = self.open().servers.get()
        resp = self.es.session.head(server_url + '/' + 'cendari')
        return resp.status_code == 200

    def mapping_exists(self):
        exists = self.open().get_mapping(self.name)\
                            .get(self.name,{})\
                            .get('mappings',{})\
                            .keys()
        return 'document' in exists

    def put_mapping(self):
        print "Creating mapping"
        self.open().put_mapping(self.name, 'document', self.get_mapping())

    def get_mapping(self):
        mapping = {
            "document" : {
                "_id" : { "path" : "uri" },
                "properties" : {
                    "application" : {
                        "type" : "string",
                        "index" : "not_analyzed"
                    },
                    "artifact" : {
                        "type" : "string",
                        "index" : "not_analyzed"
                    },
                    "contributor" : {
                        "properties" : {
                            "email" : {
                                "type" : "string",
                                "index" : "not_analyzed"
                            },
                            "name" : {
                                "type" : "string",
                                "index" : "not_analyzed"
                            }
                        }
                    },
                    "creator" : {
                        "properties" : {
                            "email" : {
                                "type" : "string",
                                "index" : "not_analyzed"
                            },
                            "name" : {
                                "type" : "string",
                                "index" : "not_analyzed"
                            }
                        }
                    },
                    "date" : {
                        "type" : "date",
                        "format" : "dateOptionalTime"
                    },
                    "event" : {
                        "type" : "string",
                        "index" : "not_analyzed"
                    },
                    "format" : {
                        "type" : "string",
                        "index" : "not_analyzed"
                    },
                    "language" : {
                        "type" : "string",
                        "index" : "not_analyzed"
                    },
                    "length" : {
                        "type" : "long"
                    },
                    "org" : {
                        "type" : "string",
                        "index" : "not_analyzed"
                    },
                    "person" : {
                        "properties" : {
                            "email" : {
                                "type" : "string",
                                "index" : "not_analyzed"
                            },
                            "name" : {
                                "type" : "string",
                                "index" : "not_analyzed"
                            }
                        }
                    },
                    "place" : {
                        "properties" : {
                            "location" : {
                                "type" : "geo_point",
                                "geohash" : True,
                                "fielddata" : {
                                    "format" : "compressed",
                                    "precision" : "3m"
                                }
                            },
                            "name" : {
                                "type" : "string",
                                "index" : "not_analyzed"
                            }
                        }
                    },
                    "publisher" : {
                        "type" : "string",
                        "index" : "not_analyzed"
                    },
                    "ref" : {
                        "type" : "string",
                        "index" : "not_analyzed"
                    },
                    "tag" : {
                        "type" : "string",
                        "index" : "not_analyzed"
                    },
                    "text" : {
                        "type" : "string"
                    },
                    "title" : {
                        "type" : "string"
                    },
                    "uri" : {
                    "type" : "string",
                        "index" : "not_analyzed"
                    },
                    "groups_allowed" : {
                        "type" : "string"
                    },
                    "users_allowed" : {
                        "type" : "string"
                    }
                }
            }
        }
        return mapping

cendari_index = CendariIndex()

#@receiver(post_save) not yet
def update_elastic_cendari_handler(sender, instance, created, **kwargs):
    if not cendari_index.is_open:
        cendari_index.open()
    klass = instance.__class__
    print "Ready to save on cendari index"
    # if klass in en_index.document_types:
    #     document_type = en_index.document_types[klass]
    #     if created:
    #         document_type.index(instance)
    #     else:
    #         document_type.update(instance)
    # elif isinstance(instance, main_models.notes.NoteSection):
    #     update_elastic_search_handler(sender, instance.note, False)

#@receiver(post_delete) not yet
def delete_elastic_cendari_handler(sender, instance, **kwargs):
    if not cendari_index.is_open:
        cendari_index.open()
    klass = instance.__class__
    print "Ready to delete from cendari index"
    # if klass in en_index.document_types:
    #     document_type = en_index.document_types[klass]
    #     document_type.remove(instance)



def index_note_to_cendari(note):
    id=note.get_absolute_url()
    contributors = note.get_all_updaters()
    contributors.append(note.creator)
    dates=[]
    events=[]
    languages=[]
    orgs=[]
    persons=[]
    places=[]
    publishers=[]
    refs=[]
    tags=[]
    
    document = {
        'uri': id,
        'application': 'nte',
        'contributor': [
            {"name": c.username, "email": c.email} for c in contributors
        ],
        'creator': {
            "name": note.creator.username,
            "email": note.creator.email
        },
        'date': dates,
        'event': events,
        'format': 'application/xhtml+xml', # nothing better eg. xhtml+rdfa
        'language': languages,
        'org': orgs,
        'person': persons,
        'place': places,
        'publisher': publishers,
        'ref': refs,
        'tag': tags,
        'text': text,
        'groups_allowed': note.project.slug,
        'users_allowed': []
    }
    self.es.index(self.name, 'document', document, id,refresh=True)
