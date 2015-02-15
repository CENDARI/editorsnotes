import logging

from editorsnotes.main.models import Document, Transcript, Topic, TopicAssignment
from editorsnotes.main.utils import xhtml_to_text
from editorsnotes.main.templatetags.display import as_html

from django.conf import settings
from django.utils import six
from django.core import signals
import utils as utils

from rdflib import Dataset, Graph, URIRef, Literal, BNode

from rdflib.namespace import Namespace, NamespaceManager, RDF, RDFS, OWL

from threading import local

import urllib
import urllib2
import json
import sys, traceback
import pdb

logger = logging.getLogger('cendari.semantic')

CENDARI = Namespace("http://resources.cendari.dariah.eu/notes/")
#CENDARI = Namespace("http://pro2.cendari.dariah.eu/enotes/")
SCHEMA  = Namespace("http://schema.org/")
DBPROP  = Namespace("http://dbpedia.org/property/")
GRS     = Namespace("http://www.georss.org/georss/")
GEO     = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
DBOWL   = Namespace("http://dbpedia.org/ontology/")

INIT_NS = {
    'owl': OWL, 
    'cendari': CENDARI,
    'schema': SCHEMA,
    'dbprop': DBPROP,
    'grs': GRS,
    'geo': GEO,
    'dbpedia-own': DBOWL
}


class SemanticHandler(object):
    def __init__(self, store_path=None):
        if store_path is None:
            self.store_path = settings.SEMANTIC_PATH
        else:
            self.store_path = store_path
        self._connection = local()

    def dataset(self):
        if hasattr(self._connection, 'dataset'):
            return getattr(self._connection, 'dataset')
        dataset = Dataset(store='Sleepycat', default_union=True)
        dataset.open(self.store_path, create = True)
        setattr(self._connection, 'dataset', dataset)
        nm = NamespaceManager(dataset)
        for (prefix, ns) in INIT_NS.iteritems():
            nm.bind(prefix, ns)
        dataset.namespace_manager = nm
        return dataset

    def graph(self, identifier):
        if isinstance(identifier, six.string_types):
            uri = URIRef(identifier)
        return self.dataset().graph(identifier)

    def remove_graph(self, g):
        self.dataset().remove_graph(g)

    def query(self, query_object, processor='sparql',
              result='sparql', initNs=None, initBindings=None,
              **kwargs):
        return self.dataset().query(query_object, processor,
                                    result, initNs, initBindings,
                                    **kwargs)

    def _close(self):
        if hasattr(self._connection, 'dataset'):
            self.dataset().close()
            self._connection.dataset = None
            delattr(self._connection, 'dataset')
            logger.info("Closing SEMANTIC connection")

semantic = SemanticHandler()

def close_connection(**kwargs):
    global semantic
    semantic._close()



signals.request_finished.connect(close_connection)

class Semantic(object):
    @classmethod
    def dataset(cls):
        return semantic.dataset()
    @classmethod
    def graph(cls, identifier):
        return semantic.graph(identifier)
    @classmethod
    def remove_graph(cls, g):
        return semantic.remove_graph(g)
    @classmethod
    def query(cls, query_object, processor='sparql',
              result='sparql', initNs=None, initBindings=None,
              **kwargs):
        return semantic.query(query_object, processor,
                              result, initNs, initBindings,
                              **kwargs)
    @classmethod
    def serialize(self, destination=None, format="xml",
                  base=None, encoding=None, **args):
        return semantic.dataset().serialize(destination, format, base, encoding, **args)

def semantic_uri(obj):
    return CENDARI[obj.get_absolute_url()[1:]]

def semantic_query(q, user=None, initBindings=None):
    return Semantic.query(q, initNs = INIT_NS, initBindings=initBindings)

def semantic_prepare_query(q):
    from rdflib.plugins.sparql import prepareQuery
    return prepareQuery(q, initNs = INIT_NS )

GEO_QUERY = None

def get_query_geo():
    global GEO_QUERY
    if GEO_QUERY is None:
        GEO_QUERY = semantic_prepare_query("""SELECT ?name ?pos ?loc
        WHERE {
           ?pos cendari:name ?name.
           ?pos a schema:Place.
           ?pos owl:sameAs+ ?db.
           ?db grs:point ?loc
        }""")
    return GEO_QUERY

def semantic_query_geo():
    return semantic_query(get_query_geo())

def semantic_query_latlong(topic):
    if topic.topic_node.type != 'PLA' or topic.rdf is None:
        return None
    url = topic.rdf
    g = Semantic.graph(url)
    o = g.value(g.identifier, GRS['point'])
    if o:
        return map(float, str(o).split(' '))
    return None

schema_topic = {
    'http://schema.org/Event': 'EVT',
    'http://schema.org/Organization': 'ORG',
    'http://schema.org/Person': 'PER',
    'http://schema.org/CreativeWork': 'PUB',
    'http://schema.org/Thing': 'ART',
    'http://schema.org/Place': 'PLA',
    'http://schema.org/Thing': 'TAG'
}

topic_schema = dict((v,k) for k, v in schema_topic.iteritems())

NAME =  URIRef("http://schema.org/name") 

def schema_to_topic(schema):
    if schema in schema_topic:
        return schema_topic[schema]
    return ''

def topic_to_schema(topic):
    if topic in topic_schema:
        return topic_schema[topic]
    return None

def xml_to_topics(xml, uri):
    if xml is None:
        return []
    g = Semantic.graph(uri)
#    pdb.set_trace()
    if not (isinstance(xml, str) or isinstance(xml, unicode)):
        xml=as_html(xml)
    xml = ("<div about='%s'>" % uri) + xml + "</div>"
    g.parse(data=xml, format='rdfa')
    entities = []
    for s,p,o in g.triples( (None, RDF.type, None) ):
        v = g.value(s, NAME)
        if not v: continue
        e = { "value": v.value,
              "type": schema_to_topic(unicode(o)),
              "rdfsubject": s,
              "rdfvalue": v,
              "rdftype": o}
        entities.append(e)
        logger.debug("Entity %s: %s", e["type"], e["value"])
    return entities

def semantic_process_note(note,user=None):
    """Extract the semantic information from a note,
    creating topics on behalf of the specific user."""
    if note is None:
        return

    if user is None:
        user = note.last_updater
    # Cleanup entities related to note
    uri = semantic_uri(note)
    g = Semantic.graph(uri)
    Semantic.remove_graph(g)

    # This not is a creative work
    g.add( (g.identifier, RDF.type, SCHEMA['CreativeWork']) )
    g.add( (g.identifier, SCHEMA['creator'], URIRef(note.creator.get_absolute_url()[1:])) )
    g.add( (g.identifier, SCHEMA['dateCreated'], Literal(note.created)) )
    g.add( (g.identifier, SCHEMA['dateModified'], Literal(note.last_updated)) )
    g.add( (g.identifier, CENDARI['name'], Literal(note.title)) )

    topics = xml_to_topics(note.content, uri) 
    done=set()
    note.related_topics.all().delete()
    for t in topics:
        topic=utils.get_or_create_topic(user, t['value'], t['type'],note.project)
        if topic not in done:
            done.add(topic)
            rdftopic = semantic_uri(topic)
            note.related_topics.create(creator=user, topic=topic)
            g.add( (t['rdfsubject'], OWL.sameAs, rdftopic) )
            g.add( (g.identifier, SCHEMA['mentions'], rdftopic) )

def semantic_process_document(document,user=None):
    """Extract the semantic information from a note,
    creating topics on behalf of the specific user."""
    if document is None:
        return

#    pdb.set_trace()
    if user is None:
        user = document.last_updater
    # Cleanup entities related to document
    uri = semantic_uri(document)
    g = Semantic.graph(uri)
    Semantic.remove_graph(g)

    # This not is a creative work
    g.add( (g.identifier, RDF.type, SCHEMA['CreativeWork']) )
    g.add( (g.identifier, SCHEMA['creator'], URIRef(document.creator.get_absolute_url()[1:])) )
    g.add( (g.identifier, SCHEMA['dateCreated'], Literal(document.created)) )
    g.add( (g.identifier, SCHEMA['dateModified'], Literal(document.last_updated)) )
    g.add( (g.identifier, CENDARI['name'], Literal(document.description)) )

    topics = xml_to_topics(document.description, uri) 
    done=set()
    document.related_topics.all().delete()
    for t in topics:
        topic=utils.get_or_create_topic(user, t['value'], t['type'], document.project)
        if topic not in done:
            done.add(topic)
            rdftopic = semantic_uri(topic)
            document.related_topics.create(creator=user, topic=topic)
            g.add( (t['rdfsubject'], OWL.sameAs, rdftopic) )
            g.add( (g.identifier, SCHEMA['mentions'], rdftopic) )
   

def semantic_process_transcript(transcript,user=None):
    """Extract the semantic information from a note,
    creating topics on behalf of the specific user."""
    logger.info("semantic transcript")
    if transcript is None:
        return
    if transcript.document is None:
        return
    if user is None:
        user = transcript.document.last_updater

    # Cleanup entities related to note
    uri = semantic_uri(transcript.document)
    g = Semantic.graph(uri)
    Semantic.remove_graph(g)

    # This not is a creative work
    g.add( (g.identifier, RDF.type, SCHEMA['CreativeWork']) )
    g.add( (g.identifier, SCHEMA['creator'], URIRef(transcript.document.creator.get_absolute_url()[1:])) )
    g.add( (g.identifier, SCHEMA['dateCreated'], Literal(transcript.document.created)) )
    g.add( (g.identifier, SCHEMA['dateModified'], Literal(transcript.document.last_updated)) )
    g.add( (g.identifier, CENDARI['name'], Literal(transcript.document.description)) )

    topics = xml_to_topics(transcript.document.description, uri) 
    topics += xml_to_topics(transcript.content, uri) 
    done=set()
    transcript.document.related_topics.all().delete()
    for t in topics:
        topic=utils.get_or_create_topic(user, t['value'], t['type'], transcript.document.project)
        if topic not in done:
            done.add(topic)
            rdftopic = semantic_uri(topic)
            transcript.document.related_topics.create(creator=user, topic=topic)
            g.add( (t['rdfsubject'], OWL.sameAs, rdftopic) )
            g.add( (g.identifier, SCHEMA['mentions'], rdftopic) )
  

def semantic_process_topic(topic,user=None):
    """Extract the semantic information from a topic."""
    logger.info("indide semantic_process_topic ")
    if topic is None:
        return
    
    if user is None:
        user = topic.last_updater
    # Cleanup entities related to note
    uri = semantic_uri(topic)
    g = Semantic.graph(uri)
    Semantic.remove_graph(g)
    # This is not a creative work
    schema = topic_to_schema(topic.topic_node.type)

    if schema:
        g.add( (g.identifier, RDF.type, URIRef(schema)) )
    if topic.date:
        g.add( (g.identifier, SCHEMA['startDate'], Literal(topic.date)) )
    g.add( (g.identifier, SCHEMA['creator'], URIRef(topic.creator.get_absolute_url()[1:])) )
    g.add( (g.identifier, SCHEMA['dateCreated'], Literal(topic.created)) )
    g.add( (g.identifier, SCHEMA['dateModified'], Literal(topic.last_updated)) )
    g.add( (g.identifier, CENDARI['name'], Literal(topic.preferred_name)) )
    if topic.rdf is not None:
        g.add( (g.identifier, OWL['sameAs'], URIRef(topic.rdf)) )

imported_relations = set([
    # Place
    RDF.type,
    DBPROP['latitude'],
    DBPROP['longitude'],
    GRS['point'],
    RDFS.label,
    OWL['sameAs'],
    GEO['lat'],
    GEO['long'],
    GEO['geometry'],
    # Person
    DBOWL['birthDate'],
    DBOWL['birthPlace'],
    DBOWL['deathDate'],
    DBOWL['deathPlace'],
    DBPROP['birthDate'],
    DBPROP['birthPlace'],
    DBPROP['deathDate'],
    DBPROP['deathPlace'],
    # Event/battle
    DBOWL['date'], 
    DBOWL['place']
])

no_duplicates = set([
    DBPROP['latitude'],
    DBPROP['longitude'],
    GRS['point'],
    GEO['lat'],
    GEO['long'],
    GEO['geometry'],
    # Person
    DBOWL['birthDate'],
    DBOWL['birthPlace'],
    DBOWL['deathDate'],
    DBOWL['deathPlace'],
    DBPROP['birthDate'],
    DBPROP['birthPlace'],
    DBPROP['deathDate'],
    DBPROP['deathPlace'],
])

DBPEDIA_SERVICE_URL="http://lookup.dbpedia.org/api/search.asmx/KeywordSearch"

def dbpedia_lookup(label,type):
    params = {
        'QueryClass': type,
        'QueryString': label.encode('utf-8'),
    }
    url = DBPEDIA_SERVICE_URL+'?'+urllib.urlencode(params)
    req = urllib2.Request(url)
    req.add_header('Accept', 'application/json')
    return json.loads(urllib2.urlopen(req).read())


def semantic_resolve_topic(topic, force=False):
    rdf_url = topic.rdf
    logger.debug('Trying to resolve topic %s from url %s', str(topic), str(rdf_url))
    topic.save()
    semantic_process_topic(topic)
    if rdf_url is None:
        return
    uri = URIRef(rdf_url)
    g = Semantic.graph(identifier=uri)
    if len(g) != 0 and not force:
        logger.debug('Uri %s already resolved', str(uri))
        return # already resolved

    logger.debug("parsing uri %s", str(uri))
    loaded = Graph(identifier=uri)

    try:
        loaded.parse(location=uri)
    except:
        logger.warning("Exception in parsing code from url %s", str(rdf_url))
        #traceback.print_exc(file=sys.stdout)
        pass

    type = URIRef(topic_to_schema(topic.topic_node.type))
    
    logger.info("Loaded %s of type %s: %d triples", str(rdf_url), str(type), len(loaded))

    if (uri, RDF.type, type) in loaded:
        logger.info ("Ontology in %s contains %s as expected", str(rdf_url), str(type))
    elif topic.topic_node.type=='PLA' and (uri, RDF.type, GEO['SpatialThing']) in loaded:
        logger.warning("%s: Missing type %s", str(rdf_url), str(type))
        loaded.add( (uri, RDF.type, type) )
    else:
        logger.error("%s: Missing type %s", str(rdf_url), str(type))
        return
    Semantic.remove_graph(g)
    
    for s,p,o in loaded.triples( (uri, None, None) ):
        if p in imported_relations:
            if p in no_duplicates and (uri, p, None) in g:
                logger.info("Skipping duplicate %s %s %s", s, p, o)
            else:
                logger.info("Adding %s %s %s", s, p, o)
                g.add( (s, p, o) )

    if topic.topic_node.type == 'PLA' and not g.value(uri, GRS['point']):
        logger.info("No grs:point in RDF, chasing for lat/long")
        o = g.value(uri, GEO['geometry'])
        if o and str(o).startswith('POINT('):
            g.add( (uri, GRS['point'], str(o)[6:-1].split(' ')) )
            logger.info("Found in geo:geometry")
            return
        lat = g.value(uri, GEO['lat'])
        lon = g.value(uri, GEO['long'])
        if lat and lon:
            g.add( (uri, GRS['point'], lat+" "+lon) )
            return
        logger.warning('No lat/long information in RDF for %s', str(uri))
        # chase in geonames later
        

def semantic_refresh_topic(topic):
    if topic.rdf is None or topic.topic_node.type == 'DAT':
        return
    uri = unicode(topic.rdf.identifier)
    if uri:
        semantic_resolve_topic(topic, uri)
