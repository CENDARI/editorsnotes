from editorsnotes.main.utils import xhtml_to_text
from editorsnotes.main.templatetags.display import as_html
from editorsnotes.main.models.topics import get_or_create_topic,get_topic_with_rdf, Topic
from editorsnotes.refine import utils as rutils
from models import PlaceTopicModel

from django.conf import settings
from django.utils import six
from django.core import signals
from django.db.models import Count
from django.utils.http import urlquote
import utils as utils

from lxml import etree, html
from lxml.html import builder as E

from rdflib import Dataset, Graph, ConjunctiveGraph, URIRef, Literal, BNode
from rdflib.store import Store
from rdflib.plugin import get as plugin
from rdflib.namespace import Namespace, NamespaceManager, RDF, RDFS, OWL

from virtuoso.vstore import Virtuoso
from virtuoso.vsparql import Result

from threading import local

import urllib
import urllib2
import urlparse
import json
import sys, traceback
import re

import time
from pyelasticsearch import ElasticSearch


__all__ = [
    'EDM',
    'CENDARI',
    'SCHEMA',
    'DBPPROP',
    'GRS',
    'GEO',
    'DBOWL',
    'semantic',
    'semantic_process_note',
    'semantic_process_document',
    'semantic_process_transcript',
    'semantic_process_topic',
    'semantic_query',
    'semantic_query_latlong',
    'semantic_resolve_topic',
    'semantic_rdfa',
    'semantic_find_dates',
    'semantic_process_cluster',
    'semantic_triples'
]


import logging
logger = logging.getLogger(__name__)

if hasattr(settings,'SEMANTIC_NAMESPACE'):
    SEMANTIC_NAMESPACE=settings.SEMANTIC_NAMESPACE
else:
    SEMANTIC_NAMESPACE=settings.SITE_URL
    
if not SEMANTIC_NAMESPACE[-1] == '/':
    SEMANTIC_NAMESPACE += '/'
CENDARI = Namespace(SEMANTIC_NAMESPACE)

#CENDARI = Namespace("http://pro2.cendari.dariah.eu/enotes/")
SCHEMA  = Namespace("http://schema.org/")
DBPPROP  = Namespace("http://dbpedia.org/property/")
GRS     = Namespace("http://www.georss.org/georss/")
GEO     = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
DBOWL   = Namespace("http://dbpedia.org/ontology/")
EDM     = Namespace("http://www.europeana.eu/schemas/edm/")
SKOS    = Namespace("http://www.w3.org/2004/02/skos/core#")

INIT_NS = {
    'owl': OWL, 
    'cendari': CENDARI,
    'schema': SCHEMA,
    'dbpprop': DBPPROP,
    'grs': GRS,
    'geo': GEO,
    'dbpedia-owl': DBOWL,
    'edm': EDM,
    'skos': SKOS,
}

WRONG_PREFIX = "http://dbpedia.org/page/"

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def fix_uri(uri):
    if uri.startswith(WRONG_PREFIX):
        uri = "http://dbpedia.org/resource/"+uri[len(WRONG_PREFIX):]
    loc=list(urlparse.urlsplit(uri))
    if not is_ascii(loc[2]):
        loc[2] = urlquote(loc[2].encode('utf8'))
    loc[2] = loc[2].replace(u'%2C',',')
    loc = urlparse.urlunsplit(loc)
    return loc

def check_domain(url_string, domain):
    o = urlparse.urlparse(url_string)
    if o.hostname:
        return domain in o.hostname.split('.')
    else:
        return False

class SemanticHandler(object):
    def __init__(self):
        try:
            if settings.SEMANTIC_STORE=='Sleepycat':
                self.store = settings.SEMANTIC_STORE
                self.store_path = settings.SEMANTIC_PATH
            elif settings.SEMANTIC_STORE=='Virtuoso':
                pwd=settings.VIRTUOSO.get('dba_password','dba')
                uid=settings.VIRTUOSO.get('dba_user','dba')
                dsn=settings.VIRTUOSO.get('dsn','VOS')
                self.connection = ('DSN=%s;UID=%s;PWD=%s;WideAsUTF16=Y' % (dsn, uid, pwd))
                self.store = 'Virtuoso'
            else:
                raise ImproperlyConfigured("SEMANTIC_STORE invalid in the settings file'")
        except ValueError:
            raise ImproperlyConfigured("SEMANTIC_PATH must be configured in the settings file'")
        self._connection = local()

    def dataset(self):
        #pdb.set_trace()
        if hasattr(self._connection, 'dataset'):
            return getattr(self._connection, 'dataset')
        if self.store=='Sleepycat':
            dataset = Dataset(store=self.store, default_union=True)
            dataset.open(self.store_path, create = True)
        else:
            self.store = Virtuoso(self.connection)
            #dataset = Dataset(store=self.store, default_union=True)
            dataset = ConjunctiveGraph(store=self.store,identifier=CENDARI)
            self.store.connection # force connection
        setattr(self._connection, 'dataset', dataset)
        nm = NamespaceManager(dataset)
        for (prefix, ns) in INIT_NS.iteritems():
            nm.bind(prefix, ns)
        dataset.namespace_manager = nm
        return dataset

    def graph(self, identifier):
        if isinstance(identifier, six.string_types):
            uri = URIRef(identifier)
        if self.store == 'Sleepycat':
            return self.dataset().graph(identifier)
        return self.dataset().get_context(identifier)

    def remove_graph(self, g):
        if self.store == 'Sleepycat':
            self.dataset().remove_graph(g)
        g.remove((None, None, None))
        return g

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

    def commit(self):
        if self.store!='Sleepycat':
            self.store.commit()

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


# GEO_QUERY = None

# def get_query_geo():
#     global GEO_QUERY
#     if GEO_QUERY is None:
#         GEO_QUERY = semantic_prepare_query("""SELECT ?name ?pos ?loc
#         WHERE {
#            ?pos cendari:name ?name.
#            ?pos a schema:Place.
#            ?pos owl:sameAs+ ?db.
#            ?db grs:point ?loc
#         }""")
#     return GEO_QUERY

# def semantic_query_geo():
#     return semantic_query(get_query_geo())

def semantic_query_latlong(topic):
    if topic.topic_node.type != 'PLA':
        return None
    if hasattr(topic, 'location'):
        return topic.location.latlong
    if topic.rdf is None:
        return None
    url = topic.rdf
    try:
        g = Semantic.graph(url)
        o = g.value(g.identifier, GRS['point'])
        if o:
            latlong = map(float, unicode(o).split(' '))
            location = PlaceTopicModel(topic, lat=latlong[0], lon=latlong[1])
            return latlong
    except Exception as e:
        logger.warn('Problem in RDF: %s', e)
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
URL =  URIRef("http://schema.org/url") 

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
    entities = []
    if not (isinstance(xml, str) or isinstance(xml, unicode)):
        xml=as_html(xml)
    xml = ("<div about='%s'>" % uri) + xml + "</div>"
    g.parse(data=xml, format='rdfa')
#    for s,p,o in g.triples( (None, None, None) ):
#        print ("%s %s %s" % (unicode(s), unicode(p), unicode(o))).encode('ascii', 'replace')
    for s,p,o in g.triples( (None, RDF.type, None) ):
        # if o==SCHEMA['CreativeWork']:
        #     v = g.value(s, URL)
        # else:
        v = g.value(s, NAME)
        if not v: continue
        e = { "value": unicode(v),
              "type": schema_to_topic(unicode(o)),
              "rdfsubject": s,
              "rdfvalue": v,
              "rdftype": o}
        entities.append(e)
        logger.debug("Entity %s: %s", e["type"], e["value"])
    return entities


def list_diff(a,b):
    return list(set(a)-set(b))

def semantic_update_topics(existing_topics,new_topics):
    to_be_deleted = []
    to_be_added   = []
    to_be_added = list_diff(new_topics,existing_topics)
    to_be_deleted = list_diff(existing_topics,new_topics)

    return (to_be_added,to_be_deleted)

def create_topics_for(entity, topics, user):
    done=set()
    for t in topics:
        value = t['value']
        if value in done:
            continue
        done.add(value)
        topic=get_or_create_topic(user, value, t['type'], entity.project)
        if topic is None:
            continue
        entity.related_topics.create(creator=user, topic=topic)
        rdftopic = semantic_uri(topic)
        subject = t['rdfsubject']
        if (topic.rdf is not None) and (not check_domain(topic.rdf,'dbpedia')):
            topic.rdf = None
            topic.save()
        elif topic.rdf is None and subject.startswith('http'):
            topic.rdf = unicode(subject)
            topic.save()
        elif topic.rdf is None and t['type']=='PUB' and value.startswith('http'):
            topic.rdf = value
            topic.save()
        elif t['type']=='EVT':
            logger.debug('working with EVT entity...')
            if utils.parse_well_known_date(value, True):
                topic.date = utils.parse_well_known_date(value, True)
                logger.debug('Found a valid date: %s', topic.date)
                topic.save()    
        else:
            results_reg = re.search('\[(.*?)\]', value)
            if results_reg!=None:
                results_reg = str(results_reg.group(0))
                explicit_date = results_reg[1:-1]
                if utils.parse_well_known_date(explicit_date, True):
                    topic.date = utils.parse_well_known_date(explicit_date, True)
                    logger.debug('Found a valid date between []: %s', topic.date)
                    topic.save()


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

    # This note is a creative work
    g.add( (g.identifier, RDF.type, SCHEMA['CreativeWork']) )
    g.add( (g.identifier, SCHEMA['creator'], semantic_uri(note.creator)) )
    g.add( (g.identifier, SCHEMA['dateCreated'], Literal(note.created)) )
    g.add( (g.identifier, SCHEMA['dateModified'], Literal(note.last_updated)) )
    g.add( (g.identifier, CENDARI['name'], Literal(note.title)) )

    #pdb.set_trace()
   
    xml = note.content
    start_time = time.time()
    topics = xml_to_topics(xml, uri) 
    logger.debug("Time for xml to topics :  %s seconds " % (time.time() - start_time))
    start_time = time.time()
    note.related_topics.all().delete()
    logger.debug("Time for deleting all topics:  %s seconds " % (time.time() - start_time))

    start_time = time.time()
    create_topics_for(note, topics, user)
    logger.debug("Time for iterating :  %s seconds " % (time.time() - start_time))  

    start_time = time.time()

    semantic.commit()
    logger.debug("Time for semantic commit :  %s seconds " % (time.time() - start_time))

    semantic_merge_project_topics(note.project)



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
    g.add( (g.identifier, SCHEMA['creator'], semantic_uri(document.creator)) )
    g.add( (g.identifier, SCHEMA['dateCreated'], Literal(document.created)) )
    g.add( (g.identifier, SCHEMA['dateModified'], Literal(document.last_updated)) )
    #g.add( (g.identifier, CENDARI['name'], Literal(xhtml_to_text(document.description))) )

    topics = xml_to_topics(document.description, uri) 
    #E.G. add this until I figure something else
    if(document.transcript):
        topics += xml_to_topics(document.transcript.content, uri)

    document.related_topics.all().delete()
    create_topics_for(document, topics, user)

    semantic.commit()
    semantic_merge_project_topics(document.project)

def semantic_process_transcript(transcript,user=None):
    """Extract the semantic information from a document's transcript,
    creating topics on behalf of the specific user."""
    logger.info("semantic transcript")
    if transcript is None:
        return
    if transcript.document is None:
        return
    semantic_process_document(transcript.document,user)


from SPARQLWrapper import SPARQLWrapper, JSON
def semantic_find_dates(topic,uri=None):
    if not uri:
        return # uri = semantic_uri(topic)
    from .search import cendari_index
    eventDates = None
    d = cendari_index.get_dates(uri)
    if d:
        eventDates = [str(date).replace("T00:00:00","") for date in d]

    if eventDates is None:
        logger.info('Querying SPARQL at dbpedia for %s', uri)
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery("""     
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?eventDate WHERE {
                <"""+uri+""">
                <http://dbpedia.org/property/date> ?eventDate
           }
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        eventDates = []
        for result in results["results"]["bindings"]:
            d = result["eventDate"]["value"]
            if not d in eventDates:
                eventDates.append(d)
    return eventDates

# Cendari code E.G. aviz
# change for alising
def semantic_unmerge_topics(master,alias,project):
    alias.unmerge()

    master_uri = semantic_uri(master)
    master_g = Semantic.graph(master_uri)

    alias_uri = semantic_uri(alias)
    alias_g = Semantic.graph(alias_uri)
    
    master_g.remove( (master_g.identifier, OWL['sameAs'], Literal(alias.preferred_name)) )
    master_g.remove( (master_g.identifier, OWL['sameAs'], alias_g) )

    return master

def semantic_merge_topics(master,alias):
    # alias.merge_into(master)

    master_uri = semantic_uri(master)
    master_g = Semantic.graph(master_uri)

    alias_uri = semantic_uri(alias)
    alias_g = Semantic.graph(alias_uri)

    master_g.add( (master_g.identifier, OWL['sameAs'], alias_g) )
    master_g.add( (master_g.identifier, OWL['sameAs'], Literal(alias.preferred_name)) )
    return master

def semantic_merge_project_topics(project):
    rdfs = project.topics.exclude(deleted=True).values('rdf').annotate(dcount=Count('rdf')).order_by('dcount')
    for rdf in rdfs :
        if rdf['rdf'] == None:
            continue
        if rdf['dcount'] == 1 :
            continue
        topics = project.topics.filter(rdf=rdf['rdf'])
        len_topics = len(topics)

        if not len_topics>1:
            continue

        cluster = rutils.add_topics_to_cluster(topics)
        semantic_process_cluster(cluster)

        # main_topic = topics[0]
        # # print topics
        # # break
        # for i in range(1,len_topics):
        #     semantic_merge_topics(main_topic,topics[i])


def semantic_process_topic(topic,user=None,doCommit=True):
    """Extract the semantic information from a topic."""
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
    g.add( (g.identifier, SCHEMA['creator'], semantic_uri(topic.creator)) )
    g.add( (g.identifier, SCHEMA['dateCreated'], Literal(topic.created)) )
    g.add( (g.identifier, SCHEMA['dateModified'], Literal(topic.last_updated)) )
    g.add( (g.identifier, CENDARI['name'], Literal(topic.preferred_name)) )


    if topic.rdf is not None:
        uri = fix_uri(topic.rdf)
        g.add( (g.identifier, OWL['sameAs'], URIRef(uri)) )
        if uri != topic.rdf:
            logger.debug(u'Fixing rdf URI from %s to %s', topic.rdf, uri)
            topic.rdf = uri
            topic.save()
    #[NB] get date for events
    #if topic.topic_node.type == 'EVT':
        #eventDates = semantic_find_dates(topic,uri)
        
    if doCommit:
        semantic.commit()

    semantic_merge_project_topics(topic.project)

def semantic_process_cluster(cluster,user=None,doCommit=True):
    if cluster == None:
        return

    if user is None:
        user = cluster.creator
    # Cleanup entities related to note
    uri = semantic_uri(cluster)
    g = Semantic.graph(uri)
    Semantic.remove_graph(g)
    if cluster.topics.count()>0:
        # This is not a creative work
        g.add( (g.identifier, RDF.type, SCHEMA['ItemList']) )
        g.add( (g.identifier, SCHEMA['creator'], semantic_uri(cluster.creator)) )
        g.add( (g.identifier, SCHEMA['dateCreated'], Literal(cluster.created)) )
        g.add( (g.identifier, SCHEMA['itemListOrder'], Literal('Unordered')) )
        g.add( (g.identifier, SCHEMA['numberOfItems'], Literal(str(cluster.topics.count()))) )

        for topic in cluster.topics.all():
            t_uri = semantic_uri(topic)
            #t_g = Semantic.graph(t_uri)
            g.add( (g.identifier, SCHEMA['itemListElement'], Literal(t_uri)))

    if doCommit:
        semantic.commit()

imported_relations = set([
    # Place
    RDF.type,
    DBPPROP['latitude'],
    DBPPROP['longitude'],
    DBPPROP['latd'],
    DBPPROP['latm'],
    DBPPROP['lats'],
    DBPPROP['longd'],
    DBPPROP['longm'],
    DBPPROP['longs'],
    DBPPROP['latDeg'],
    DBPPROP['latMin'],
    DBPPROP['latSec'],
    DBPPROP['lonDeg'],
    DBPPROP['lonMin'],
    DBPPROP['lonSec'],
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
    DBPPROP['birthDate'],
    DBPPROP['birthPlace'],
    DBPPROP['deathDate'],
    DBPPROP['deathPlace'],
    # Event/battle
    DBOWL['date'], 
    DBOWL['place'],
])

no_duplicates = set([
    DBPPROP['latitude'],
    DBPPROP['longitude'],
    DBPPROP['latd'],
    DBPPROP['latm'],
    DBPPROP['lats'],
    DBPPROP['longd'],
    DBPPROP['longm'],
    DBPPROP['longs'],
    DBPPROP['latDeg'],
    DBPPROP['latMin'],
    DBPPROP['latSec'],
    DBPPROP['lonDeg'],
    DBPPROP['lonMin'],
    DBPPROP['lonSec'],
        GRS['point'],
    GEO['lat'],
    GEO['long'],
    GEO['geometry'],
    # Person
    DBOWL['birthDate'],
    DBOWL['birthPlace'],
    DBOWL['deathDate'],
    DBOWL['deathPlace'],
    DBPPROP['birthDate'],
    DBPPROP['birthPlace'],
    DBPPROP['deathDate'],
    DBPPROP['deathPlace'],
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
    topic.save()
    semantic_process_topic(topic,doCommit=False)
    if topic.rdf is None or topic.rdf=='':
        semantic.commit()
        return

    rdf_url = fix_uri(topic.rdf)
    logger.debug(u"Trying to resolve topic %s from url '%s'", unicode(topic), unicode(rdf_url))
    uri = URIRef(rdf_url)
    g = Semantic.graph(identifier=uri)
    if len(g) != 0 and not force:
        logger.debug('Uri %s already resolved', unicode(uri))
        return # already resolved
    return load_dbpedia(uri, topic.id)

def load_dbpedia(uri, topicid):
    rdf_url = str(uri)
    logger.debug("parsing uri %s", rdf_url)
    loaded = Graph(identifier=uri)

    try:
        logger.info('Downloading %s', rdf_url)
        loaded.parse(location=uri)
    except Exception as e:
        logger.warning("Exception in parsing code from url %s: %s", rdf_url, e)
        return

    topic = Topic.objects.get(id=topicid)
    type = URIRef(topic_to_schema(topic.topic_node.type))
    
    logger.info("Loaded %s of type %s: %d triples", rdf_url, unicode(type), len(loaded))

    if (uri, RDF.type, type) in loaded:
        logger.info ("Ontology in %s contains %s as expected", rdf_url, unicode(type))
    elif topic.topic_node.type=='PLA' and (uri, RDF.type, GEO['SpatialThing']) in loaded:
        logger.warning("%s: Missing type %s", rdf_url, unicode(type))
        loaded.add( (uri, RDF.type, type) )
    else:
        logger.warning("%s: Missing type %s", rdf_url, unicode(type))

    g = Semantic.graph(identifier=uri)
    Semantic.remove_graph(g)
    
    for s,p,o in loaded.triples( (uri, None, None) ):
        if p in imported_relations:
            if p in no_duplicates and (uri, p, None) in g:
                logger.info("Skipping duplicate %s %s %s", s, p, o)
            else:
                logger.info("Adding %s %s %s", s, p, o)
                g.add( (s, p, o) )

    if topic.topic_node.type != 'PLA': return
    loc = g.value(uri, GRS['point'])
    while not loc:
        logger.info("No grs:point in RDF, chasing for lat/long")
        o = g.value(uri, GEO['geometry'])

        match = []
        if o and \
          (match.append(re.match(r"POINT\(([^ ]+) ([^ ]+)\)", unicode(o))) or any(match)):
            loc = match.pop().group(2)+' '+match.pop().group(1)
            g.add( (uri, GRS['point'], Literal(loc)) )
            logger.info("Found in geo:geometry")
            break
        lat = g.value(uri, GEO['lat'])
        lon = g.value(uri, GEO['long'])
        if lat and lon:
            loc = str(lat)+" "+str(lon)
            g.add( (uri, GRS['point'], Literal(loc)) )
            logger.info("Found in geo:lat/geo:long: %s", g.value(uri, GRS['point']))
            break

        lat = g.value(uri, DBPPROP['latitude'])
        lon = g.value(uri, DBPPROP['longitude'])
        if lat and lon:
            loc = str(lat)+" "+str(lon)
            g.add( (uri, GRS['point'], Literal(loc)) )
            logger.info("Found in dbp:latitude/dbp:longitude: %s", g.value(uri, GRS['point']))
            break

        lat = g.value(uri, DBPPROP['latd'])
        latmin = g.value(uri, DBPPROP['latm'])
        lats = g.value(uri, DBPPROP['lats'],default=0)
        lon = g.value(uri, DBPPROP['longd'])
        lonmin = g.value(uri, DBPPROP['longm'])
        lons = g.value(uri, DBPPROP['longs'],default=0)
        if lat and latmin and lon and lonmin:
            # Degrees + minutes/60 + seconds/3600
            lat = float(lat) + float(latmin)/60.0 + float(lats)/3600.0
            lon = float(lon) + float(lonmin)/60.0 + float(lons)/3600.0
            loc = "%f %f" % (lat, lon)
            loc = str(lat)+" "+str(lon)
            g.add( (uri, GRS['point'], Literal(loc)) )
            logger.info("Found in dbp:latd/dbp:longd: %s", g.value(uri, GRS['point']))
            break

        lat = g.value(uri, DBPPROP['latDeg'])
        latmin = g.value(uri, DBPPROP['latMin'])
        lats = g.value(uri, DBPPROP['latSec'],default=0)        
        lon = g.value(uri, DBPPROP['lonDeg'])
        lonmin = g.value(uri, DBPPROP['lonMin'])
        lons = g.value(uri, DBPPROP['lonSec'],default=0)
        if lat and latmin and lon and lonmin:
            # Degrees + minutes/60 
            lat = float(lat) + float(latmin)/60.0 + float(lats)/3600.0
            lon = float(lon) + float(lonmin)/60.0 + float(lons)/3600.0
            loc = "%f %f" % (lat, lon)
            g.add( (uri, GRS['point'], Literal(loc)) )
            logger.info("Found in dbprop:latDeg/dbprop:lonDeg: %s", g.value(uri, GRS['point']))
            break

        logger.warning('No lat/long information in RDF for %s', unicode(uri))
        break
        # chase in geonames later
    semantic.commit()
    if loc:
        logger.info("Lat/Lon is %s", loc)
        latlong = map(float, loc.split(' '))
        location = None
        if hasattr(topic, 'location'):
            location = topic.location
        else:
            location = PlaceTopicModel(topic, lat=latlong[0], lon=latlong[1])
    return loc

def semantic_refresh_topic(topic):
    if topic.rdf is None or topic.topic_node.type == 'DAT':
        return
    uri = unicode(topic.rdf.identifier)
    if uri:
        semantic_resolve_topic(topic, uri)

def semantic_rdfa(obj, xml):
    uri = semantic_uri(obj)
    g = Semantic.graph(uri)
    
    head = E.HEAD()
    for s,p,o in g.triples( (URIRef(uri), None, None) ):
        head.append(E.META(property=unicode(p), content=unicode(o)))
    document = E.HTML(head, E.BODY(xml, about=uri), version="XHTML+RDFa 1.0")
    return etree.tostring(document, encoding='utf8', pretty_print=True)

def semantic_triples(obj):
    uri = semantic_uri(obj)
    g = Semantic.graph(uri)
    for s,p,o in g.triples( (URIRef(uri), None, None) ):
        yield dict(p=p,o=o)
