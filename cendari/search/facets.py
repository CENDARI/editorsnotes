from editorsnotes.main.models import Project

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
            { "or": [
                { "missing": { "field" : "groups_allowed" } },
                { "terms": { "groups_allowed" : groups } }
            ] },
            { "or": [
                { "missing": { "field" : "users_allowed" } },
                { "term": { "users_allowed" : username } }
            ] }
        ]
    return filter

def cendari_aggregations(size={},default_size=10,precision=2,interval='1y'):
    aggs = {
        'date': {
            "date_histogram" : {
                "field" : "date",
                "interval" : interval,
                #"format" : "yyyy"
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
