from editorsnotes.main.utils import xhtml_to_text
from editorsnotes.main.templatetags.display import as_html
from editorsnotes.main.models.topics import get_or_create_topic,get_topic_with_rdf
from models import PlaceTopicModel

from django.conf import settings
from django.utils import six
from django.core import signals
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
import pdb

__all__ = [
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
    'semantic_rdfa'
]

import logging
logger = logging.getLogger(__name__)

if hasattr(settings,'SEMANTIC_NAMESPACE'):
    CENDARI = Namespace(settings.SEMANTIC_NAMESPACE)
else:
    CENDARI = Namespace("http://localhost:8000/")

#CENDARI = Namespace("http://pro2.cendari.dariah.eu/enotes/")
SCHEMA  = Namespace("http://schema.org/")
DBPPROP  = Namespace("http://dbpedia.org/property/")
GRS     = Namespace("http://www.georss.org/georss/")
GEO     = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
DBOWL   = Namespace("http://dbpedia.org/ontology/")
FREEBASE = Namespace("http://rdf.freebase.com/ns/")

INIT_NS = {
    'owl': OWL, 
    'cendari': CENDARI,
    'schema': SCHEMA,
    'dbpprop': DBPPROP,
    'grs': GRS,
    'geo': GEO,
    'dbpedia-owl': DBOWL,
    'ns': FREEBASE
}

WRONG_PREFIX = "http://dbpedia.org/page/"

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def fix_uri(uri):
    if uri.startswith(WRONG_PREFIX):
        uri = "http://dbpedia.org/resource/"+uri[len(WRONG_PREFIX):]
    loc=list(urlparse.urlsplit(uri))
    if not is_ascii(loc[2]):
        loc[2] = urllib.quote(loc[2].encode('utf8'))
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
    if topic.topic_node.type != 'PLA':
        return None
    if hasattr(topic, 'location'):
        return topic.location.latlong
    if topic.rdf is None:
        return None
    url = topic.rdf
    g = Semantic.graph(url)
    o = g.value(g.identifier, GRS['point'])
    if o:
        latlong = map(float, unicode(o).split(' '))
        location = PlaceTopicModel(topic, lat=latlong[0], lon=latlong[1])
        return latlong
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

def fix_links(xml):
    """
    Transform <a href='uri'>...</a> into
    <span class="r_entity r_creativework" typeof="schema:CreativeWork">
      <a class="r_prop r_url" property="schema:url" href='<uri>'>...</a>
    </span>
    to become proper RDFa and also to be understood by the RDFace editor.

    # test simple case
    >>> from lxml import html
    >>> import lxml.html.usedoctest
    
    >>> xml = html.fragment_fromstring('<div><a href="http://example.com">example</a></div>')
    >>> fix_links(xml)
    True
    >>> print html.tostring(xml)
    <div><span class="r_entity r_creativework" typeof="schema:CreativeWork"><a class="r_prop r_url" property="schema:url" href="http://example.com">example</a></span></div>

    >>> xml = html.fragment_fromstring('<div>Simple <a href="http://example.com">example</a> to test</div>')
    >>> fix_links(xml)
    True
    >>> print html.tostring(xml)
    <div>Simple <span class="r_entity r_creativework" typeof="schema:CreativeWork"><a class="r_prop r_url" property="schema:url" href="http://example.com">example</a></span> to test</div>

    # Also, make sure that if the structure is right, it's not changed:
    >>> xml=html.fragment_fromstring('<div>Simple <span class="r_entity r_creativework" typeof="schema:CreativeWork"><a class="r_prop r_url" property="schema:url" href="http://example.com">example</a></span> to test</div>')
    >>> fix_links(xml)
    False
    >>> print html.tostring(xml)
    <div>Simple <span class="r_entity r_creativework" typeof="schema:CreativeWork"><a class="r_prop r_url" property="schema:url" href="http://example.com">example</a></span> to test</div>
    
    # More complicated are almost-good configuration that need not to be touched
    >>> xml=html.fragment_fromstring('<div>Simple <span class="r_entity r_somethingelse" typeof="schema:Thing"><a class="r_prop r_url" property="schema:url" href="http://example.com">example</a></span> to test</div>')
    >>> fix_links(xml)
    False
    >>> print html.tostring(xml)
    <div>Simple <span class="r_entity r_somethingelse" typeof="schema:Thing"><a class="r_prop r_url" property="schema:url" href="http://example.com">example</a></span> to test</div>
    """
    if xml is None:
        return False
    changed = False
    for (el, at, lnk, pos) in xml.iterlinks():
        o = u'schema:CreativeWork'
        if el.tag=='a' and el.get("href"):
            parent = el.getparent()
            span = parent
            if not el.get('property'):
                changed = True
                el.set('property', "schema:url")
                el.set('class', el.get('class', default='')+"r_prop r_url")
            elif el.get('property') != "schema:url":
                # don't change it
                continue # restart at the next for loop

            if parent.tag=='span' and parent.get('typeof')==o:
                pass # do nothing
            elif parent.get('typeof',o)!=o:
                continue # the parent already has a typeof
            elif parent.tag=='span' and parent.get('typeof') is None:
                changed = True
                parent.set('typeof', o)
            elif parent.tag!='span':
                changed = True
                span=el.makeelement('span')
                span.set('typeof', o)
                span.tail = el.tail
                el.tail = ''
                parent.replace(el, span)
                span.append(el)

            cls = span.get('class')
            if cls is None:
                changed = True
                span.set('class', 'r_entity r_creativework')
            else:
                c=re.split(r'[ ]+', cls)
                if 'r_entity' not in c:
                    changed = True
                    c.append('r_entity')
                if 'r_creativework' not in c:
                    changed = True
                    c.append('r_creativework')
                if changed:
                    span.set('class', u' '.join(c))
    return changed

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
    g.add( (g.identifier, SCHEMA['creator'], URIRef(note.creator.get_absolute_url()[1:])) )
    g.add( (g.identifier, SCHEMA['dateCreated'], Literal(note.created)) )
    g.add( (g.identifier, SCHEMA['dateModified'], Literal(note.last_updated)) )
    g.add( (g.identifier, CENDARI['name'], Literal(note.title)) )

    #pdb.set_trace()
   
#    if fix_links(note.content):
#        note.save()

    xml = note.content
#    print '---------------------------'
#    print as_html(note.content)
    topics = xml_to_topics(xml, uri) 
#    print topics
#    print '---------------------------'
    done=set()
    note.related_topics.all().delete()
    for t in topics:
        topic=get_or_create_topic(user, t['value'], t['type'],note.project)
        if topic is None:
            continue
        if topic not in done:
            done.add(topic)
            note.related_topics.create(creator=user, topic=topic)
            rdftopic = semantic_uri(topic)
            subject = t['rdfsubject']
            value = t['value']
            g.add( (subject, OWL.sameAs, rdftopic) )
            g.add( (g.identifier, SCHEMA['mentions'], rdftopic) )

            if (not topic.rdf is None) and (not check_domain(topic.rdf,'dbpedia')):
                topic.rdf = None
                topic.save()

            if topic.rdf is None and subject.startswith('http'):
                topic.rdf = unicode(subject)
                topic.save()
            elif topic.rdf is None and t['type']=='PUB'\
                 and value.startswith('http'):
                topic.rdf = value
                topic.save()
            elif t['type']=='EVT':
         	if utils.parse_well_known_date(value):
                	topic.date = utils.parse_well_known_date(value)
			topic.rdf = value
                	logger.debug('Found a valid date: %s', topic.date)
			topic.save()	
 		else:
			results_reg = re.search('\[(.*?)\]', value)
			if results_reg!=None:
				results_reg = str(results_reg.group(0))
				explicit_date = results_reg[1:len(results_reg)-1]
				if utils.parse_well_known_date(explicit_date):
                			topic.date = utils.parse_well_known_date(explicit_date)
					# topic.rdf = explicit_date
                			logger.debug('Found a valid date between []: %s', topic.date)
					topic.save()	
    semantic.commit()



def semantic_process_document(document,user=None):
    """Extract the semantic information from a note,
    creating topics on behalf of the specific user."""
    if document is None:
        return

#    pdb.set_trace()
    if user is None:
        user = document.last_updater
#    if fix_links(document.description):
#        document.save()
    # Cleanup entities related to document
    uri = semantic_uri(document)
    g = Semantic.graph(uri)
    Semantic.remove_graph(g)

    # This not is a creative work
    g.add( (g.identifier, RDF.type, SCHEMA['CreativeWork']) )
    g.add( (g.identifier, SCHEMA['creator'], URIRef(document.creator.get_absolute_url()[1:])) )
    g.add( (g.identifier, SCHEMA['dateCreated'], Literal(document.created)) )
    g.add( (g.identifier, SCHEMA['dateModified'], Literal(document.last_updated)) )
    #g.add( (g.identifier, CENDARI['name'], Literal(xhtml_to_text(document.description))) )

    topics = xml_to_topics(document.description, uri) 
    #E.G. add this until I figure something else
    if(document.transcript):
        topics += xml_to_topics(document.transcript.content, uri)

    done=set()
    document.related_topics.all().delete()
    for t in topics:
        topic=get_or_create_topic(user, t['value'], t['type'], document.project)
        if topic is None:
            continue
        if topic not in done:
            done.add(topic)
            rdftopic = semantic_uri(topic)
            document.related_topics.create(creator=user, topic=topic)
            subject = t['rdfsubject']
            value = t['value']
            g.add( (subject, OWL.sameAs, rdftopic) )
            g.add( (g.identifier, SCHEMA['mentions'], rdftopic) )
            if topic.rdf is None and subject.startswith('http'):
                topic.rdf = unicode(subject)
                topic.save()
            elif topic.rdf is None and t['type']=='PUB'\
                 and value.startswith('http'):
                topic.rdf = value
                topic.save()
            elif t['type']=='EVT':
		print 'working with EVT entity...'
         	if utils.parse_well_known_date(value):
                	topic.date = utils.parse_well_known_date(value)
			# topic.rdf = value
                	logger.debug('Found a valid date: %s', topic.date)
			topic.save()	
 		else:
			results_reg = re.search('\[(.*?)\]', value)
			if results_reg!=None:
				results_reg = str(results_reg.group(0))
				explicit_date = results_reg[1:len(results_reg)-1]
				if utils.parse_well_known_date(explicit_date):
                			topic.date = utils.parse_well_known_date(explicit_date)
					# topic.rdf = explicit_date
                			logger.debug('Found a valid date between []: %s', topic.date)
					topic.save()	
    semantic.commit()

def semantic_get_topic_graph(obj):
    uri = semantic_uri(obj)
    g = Semantic.graph(uri)
    return g



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

    # Cleanup entities related to note11
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
        topic=get_or_create_topic(user, t['value'], t['type'], transcript.document.project)
        if topic is None:
            continue
        if topic not in done:
            done.add(topic)
            rdftopic = semantic_uri(topic)
            transcript.document.related_topics.create(creator=user, topic=topic)
            subject = t['rdfsubject']
            value = t['value']
            g.add( (subject, OWL.sameAs, rdftopic) )
            g.add( (g.identifier, SCHEMA['mentions'], rdftopic) )
            if topic.rdf is None and subject.startswit0h('http'):
                topic.rdf = unicode(subject)
                topic.save()
            elif t['type']=='EVT':
         	if utils.parse_well_known_date(value):
                	topic.date = utils.parse_well_known_date(value)
			topic.rdf = value
                	logger.debug('Found a valid date: %s', topic.date)
			topic.save()	
 		else:
			results_reg = re.search('\[(.*?)\]', value)
			if results_reg!=None:
				results_reg = str(results_reg.group(0))
				explicit_date = results_reg[1:len(results_reg)-1]
				if utils.parse_well_known_date(explicit_date):
                			topic.date = utils.parse_well_known_date(explicit_date)
                			logger.debug('Found a valid date between []: %s', topic.date)
					topic.save()	
    semantic.commit()  


# def semantic_get_indetifier_from_rdf(topic_rdf):
#     dataset = Semantic.dataset()
#     graph_identifiers = set(dataset.subjects(OWL['sameAs'], URIRef(topic_rdf)))
#     if not graph_identifiers:
#         return None

#     return list(graph_identifiers)[0]


def semantic_get_topic_graph(obj):
    uri = semantic_uri(obj)
    g = Semantic.graph(uri)
    return g

def semantic_check_user_alias(topic,user):
    t = get_topic_with_rdf(topic.rdf)
    if t== None:
        return topic
    g = semantic_get_topic_graph(t)

    g.add((g.identifier,OWL['sameAs'],Literal(topic.preferred_name)))

    t.alternate_names.create(name=topic.preferred_name,creator=user)
    for alt_name in topic.alternate_names.all():
        t.alternate_names.add(alt_name)
        g.add((g.identifier,OWL['sameAs'],Literal(alt_name.name)))
    topic.deleted = True
    return t  
    


def semantic_process_topic(topic,user=None,doCommit=True):
    """Extract the semantic information from a topic."""
    logger.info("inside semantic_process_topic ")
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
        uri = fix_uri(topic.rdf)
        if uri != topic.rdf:
            logger.debug(u'Fixing rdf URI from %s to %s', topic.rdf.encode('ascii','xmlcharrefreplace'), uri)
            topic.rdf = uri
            topic.save()
        g.add( (g.identifier, OWL['sameAs'], URIRef(topic.rdf)) )
    if doCommit:
        semantic.commit()

imported_relations = set([
    # Place
    RDF.type,
    DBPPROP['latitude'],
    DBPPROP['longitude'],
    DBPPROP['latMin'],
    DBPPROP['latDeg'],
    DBPPROP['lonMin'],
    DBPPROP['lonDeg'],
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
    FREEBASE['topic_server.geolocation_latitude'],
    FREEBASE['topic_server.geolocation_longitude'],
])

no_duplicates = set([
    DBPPROP['latitude'],
    DBPPROP['longitude'],
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
    if topic.rdf is None:
        semantic.commit()
        return

    rdf_url = topic.rdf
    logger.debug(u'Trying to resolve topic %s from url %s', unicode(topic), unicode(rdf_url))
    uri = URIRef(rdf_url)
    g = Semantic.graph(identifier=uri)
    if len(g) != 0 and not force:
        logger.debug('Uri %s already resolved', unicode(uri))
        return # already resolved

    logger.debug("parsing uri %s", unicode(uri))
    loaded = Graph(identifier=uri)

    try:
        loaded.parse(location=uri)
    except:
        logger.warning("Exception in parsing code from url %s", unicode(rdf_url))
        if rdf_url.startswith('http://rdf.freebase') or rdf_url.startswith('https://rdf.freebase'):
            try:
                rdf = urllib2.urlopen(rdf_url).read()
                rdf = re.sub(r'\\x(..)', r'\\u00\1', rdf)
                loaded.parse(data=rdf, format="n3")
            except:
                traceback.print_exc(file=sys.stdout)
                pass

    type = URIRef(topic_to_schema(topic.topic_node.type))
    
    logger.info("Loaded %s of type %s: %d triples", unicode(rdf_url), unicode(type), len(loaded))

    if (uri, RDF.type, type) in loaded:
        logger.info ("Ontology in %s contains %s as expected", unicode(rdf_url), unicode(type))
    elif topic.topic_node.type=='PLA' and (uri, RDF.type, GEO['SpatialThing']) in loaded:
        logger.warning("%s: Missing type %s", unicode(rdf_url), unicode(type))
        loaded.add( (uri, RDF.type, type) )
    else:
        logger.warning("%s: Missing type %s", unicode(rdf_url), unicode(type))

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

        lat = g.value(uri, DBPPROP['latDeg'])
        latmin = g.value(uri, DBPPROP['latMin'])
        lon = g.value(uri, DBPPROP['lonDeg'])
        lonmin = g.value(uri, DBPPROP['lonMin'])
        if lat and latmin and lon and lonmin:
            # Degrees + minutes/60 
            lat = float(lat) + float(latmin)/60.0
            lon = float(lon) + float(lonmin)/60.0
            loc = "%f %f" % (lat, lon)
            g.add( (uri, GRS['point'], Literal(loc)) )
            logger.info("Found in dbprop:latDeg/dbprop:lonDeg: %s", g.value(uri, GRS['point']))
            break

        lat = g.value(uri, FREEBASE['topic_server.geolocation_latitude'])
        lon = g.value(uri, FREEBASE['topic_server.geolocation_longitude'])
        if lat and lon:
            loc = str(lat)+" "+str(lon)
            g.add( (uri, GRS['point'], Literal(loc)) )
            logger.info("Found in ns:latitude/ns:longitude: %s", g.value(uri, GRS['point']))
            break

        logger.warning('No lat/long information in RDF for %s', unicode(uri))
        break
        # chase in geonames later
    semantic.commit()
    if loc:
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

