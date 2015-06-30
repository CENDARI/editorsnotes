from editorsnotes.main.models import Project
from . import cendari_index
import pprint
from ..utils import bounding_box_to_precision, date_range_to_interval

CENDARI_FACETS = [
    "application",
    "artifact",
    "contributor",
    "creator",
    "event",
    "format",
    "language",
    "org",
    "person",
    "place",
    "publisher",
    "ref",
    "tag",
    "project"
]

def cendari_filter(user=None,project_slugs=None):
    if user is None:
        filter = [
            { "missing": { "field" : "groups_allowed" } },
            { "missing": { "field" : "users_allowed" } }
        ]
    else:
        if user.is_superuser:
            return []
        username=user.username
        if project_slugs is None:
            groups=[proj.slug for proj in user.get_affiliated_projects()]
        else:
            groups=project_slugs

        filter = [
            {"bool": { "should": [
                { "missing": { "field" : "groups_allowed" } },
                { "terms": { "groups_allowed" : groups } }
            ] } },
            {"bool": { "should": [
                { "missing": { "field" : "users_allowed" } },
                { "term": { "users_allowed" : username } }
            ] } }
        ]

        # filter = [
        #     { "or": [
        #         { "missing": { "field" : "groups_allowed" } },
        #         { "terms": { "groups_allowed" : groups } }
        #     ] },
        #     { "or": [
        #         { "missing": { "field" : "users_allowed" } },
        #         { "term": { "users_allowed" : username } }
        #     ] }
        # ]
    return filter

def geo_bounds_precision(geo_bounds):
    if not geo_bounds:
        return 2
    (lat1, long1, lat2, long2) = geo_bounds
    return bounding_box_to_precision(lat1, long1, lat2, long2, 70)

def date_range_interval(date_range):
    #pprint.pprint(date_range)
    #return '2y'
    return date_range_to_interval(date_range[0], date_range[1], 20)

def cendari_aggregations(size={},default_size=10,geo_bounds=None,date_range=None):
    interval = date_range_interval(date_range)
    precision = geo_bounds_precision(geo_bounds)
    aggs = {
        'date': {
            "date_histogram" : {
                "field" : "date",
                "interval" : interval,
                "min_doc_count": 0
            }
        },
        'location': {
            "geohash_grid" : {
                "field" : "location",
                "precision" : precision,
                "size": 5000
            }
        }
    }
    for facet in CENDARI_FACETS:
        s =  size[facet] if facet in size else default_size
        aggs[facet] = {
            "terms": {
                "field": facet,
                "size": s,
                "min_doc_count": 0
            }
        }
        aggs[facet+'_cardinality'] = { 
            "cardinality": {
                "field": facet
            }
        }
    return aggs

def build_es_query(request,project_slug):
    terms = {}
    q = {}
    filter_terms = []
    query_terms = []
    filter_terms = cendari_filter(request.user)
    date_range = None
    geo_bounds = None
    query = request.REQUEST.get('q', '')
    if query is not None and len(query)!=0:
        query_terms.append({'match': {'_all': query} })
    else:
        query = ''
    if 'selected_facets' in request.REQUEST \
      and request.REQUEST['selected_facets']:
        facets=request.REQUEST.getlist('selected_facets')
        for facet in facets:
            values =facet.split(':')
            facet = values[0]
            values = values[1:]
            if facet in terms:
                terms[facet] += values
            else:
                terms[facet] = values

    if project_slug:
        if 'project' in terms:
            values = terms['project']
            if project_slug not in values:
                terms['project'].append(project_slug)
        else:
            terms['project'] = [project_slug]

    filter_terms += [{"terms": {key: val}} for (key, val) in terms.items()]

    if 'bounds' in request.REQUEST:
        bounds=map(float, request.REQUEST['bounds'].split(','))
        geo_bounds = bounds
        filter_terms += [{"geo_bounding_box" :
                          {"location": {
                              "top_left": ', '.join(map(str, bounds[:2])),
                                  "bottom_right": ', '.join(map(str, bounds[2:4]))
                              }
                          }
                        }]

    if 'daterange' in request.REQUEST:
        daterange=map(long, request.REQUEST['daterange'].split(','))
        date_range = [datetime.fromtimestamp(daterange[0]).isoformat(),
                      datetime.fromtimestamp(daterange[1]).isoformat()]
        filter_terms += [{"range" :
                          {"date": { "gte": date_range[0], "lte": date_range[1] } }
                        }]

    if len(query_terms)==1:
        q['query'] = query_terms[0]
    elif len(query_terms)>1:
        q['query'] = { "bool" : { "must" : query_terms } }
    if len(filter_terms)==1:
        q['filter'] = filter_terms[0]
    elif len(filter_terms)>1:
        q['filter'] = {"bool" : { "must" : filter_terms } }
    # craft a filtered query out of the query
    # because aggregation use the result of the query
    # and ignore the filter alone
    q = {'query': { 'filtered': q } }
    return (q, query, geo_bounds, date_range)

def cendari_faceted_search(request,project_slug=None):
    (q, query, geo_bounds, date_range) = build_es_query(request, project_slug)

    # Prepare the aggregations

    # 1 - term facets
    buckets = {}
    if 'show_facets' in request.REQUEST \
      and request.REQUEST['show_facets']:
      facets_shown = request.REQUEST.getlist('show_facets')
      for facet in facets_shown:
          (facet,value) = facet.split(':')
          buckets[facet] = int(value)

    # 2 - geo and date facets
    range_requests = {}
    if geo_bounds is None:
        range_requests["location_range"] = {"geo_bounds": {"field": "location"}}
    if date_range is None:
        range_requests["date_range"] = {"stats": {"field": "date"}}

    if len(range_requests):
        # Need to do a first query to get the actual ranges
        # so we can split it/them into the right # of buckets
        q['aggregations'] = range_requests
        results = cendari_index.search(q,size=0)
        pprint.pprint(results)
        if 'date_range' in results['aggregations']:
            date_range = [ long(results['aggregations']['date_range']['min']),
                           long(results['aggregations']['date_range']['max']) ]
        if 'location_range' in results['aggregations']:
            geo_bounds = results['aggregations']['location_range']['bounds']
            top_left = [ geo_bounds['top_left']['lat'], geo_bounds['top_left']['lon']]
            bottom_right = [ geo_bounds['bottom_right']['lat'], geo_bounds['bottom_right']['lon']]
            geo_bounds = [ top_left[0], top_left[1], bottom_right[0], bottom_right[1] ]
    
    q['fields'] = ['uri', 'title']
    size = int(request.REQUEST.get('size', 50))
    q['size'] = size
    frm = int(request.REQUEST.get('from', 0))
    q['from'] = frm
    q['aggregations'] = cendari_aggregations(size=buckets, geo_bounds=geo_bounds, date_range=date_range)
    #pprint.pprint(q)
    results = cendari_index.search(q, highlight=True, size=size)
    # with open('res.log', 'w') as out:
    #     pprint.pprint(results, stream=out)
    res = []
    total = int(results['hits']['total'])
    sizes = {
        'total': total,
        'size': size,
        'from': frm,
        'last': frm+size,
        'pages': total / size,
        'page': int(frm / size),
    }
    for h in results['hits']['hits']:
        highlight = []
        if 'highlight' in h:
            for field, values in h['highlight'].items():
                highlight += values
            info = { 'uri': h['fields']['uri'][0], 
                     'highlight': highlight }
            res.append(info)
        elif 'title' in h['fields']:
            info = { 'uri': h['fields']['uri'][0], 
                     'highlight': h['fields']['title'] }
            res.append(info)
        else:
            info = { 'uri': h['fields']['uri'][0], 
                     'highlight': '' }

    facets = results['aggregations']
    cardinalities = []
    for key,details in facets.iteritems():
        if key.endswith('_cardinality'):
            cardinalities.append(key)
            continue
        elif '_' in key: # non_facet names contain a _
            continue
        if key+'_cardinality' in facets:
            details['value_count'] = facets[key+'_cardinality']['value']
        elif key=='location':
            details['value_count'] = len(details['buckets'])
            details['bounds'] = geo_bounds
        elif key=='date':
            details['bounds'] = date_range
        else:
            details['value_count'] = len(details['buckets'])

    for c in cardinalities:
        del facets[c]

    o = {
#        'project': project,
        'facets': facets,
        'sizes': sizes,
        'results': res,
        'query': query if isinstance(query, basestring) else ''
    }
    return o
