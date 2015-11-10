from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import transaction
from django.db.models import get_models, Model
from editorsnotes.main.models import Topic, AlternateName
from models import TopicCluster, BadClusterPair
from lxml import etree

import reversion
import re

# importing the following so that reversion sees registered models
from editorsnotes import admin

def get_preferred_topic_name(topics):
    """
    Returns a tuple of (Preferred name, [rest of names])
    """
    topics = sorted(topics, key=lambda t: t.created)

    # Basic check for LOC personal name heading format. If none of the names
    # match this, the oldest one is used.
    PREFERRED_NAME_FMT = re.compile('.*?\d{4}-(?:\d{4})?.?$')

    preferred_name = ''
    rest_of_names = [t.preferred_name for t in topics]

    for topic in topics:
        if not preferred_name and re.match(
            PREFERRED_NAME_FMT, topic.preferred_name):
            preferred_name = topic.preferred_name
    if not preferred_name:
        preferred_name = topics[0].preferred_name
    rest_of_names.remove(preferred_name)

    return preferred_name, rest_of_names

def get_combined_article(topics):
    """
    Returns combined topic articles, separated by <hr />
    """
    article = ''
    combined = False

    for topic in topics:
        if topic.has_summary():
            article += '<hr />' if article else ''
            combined = True if article else False
            article += etree.tostring(topic.summary)

    # If multiple articles were combined, to be valid xhtml they must have a
    # single root node
    article = '<div>%s</div>' % article if combined else article

    return etree.fromstring(article) if article else None

@transaction.commit_on_success
def merge_topics(topics, user):
    """
    Combine multiple topics into one. First argument is either a list or a
    QuerySet, second is a User. Accepts between 2 and 5 topics.
    """
    if not 2 <= len(topics) <= 5:
        return
    topics = sorted(topics, key=lambda t: t.created)

    # Create revisions for each topic before merging
    with reversion.create_revision():
        comment = 'Merged topics: %s' % (' and '.join(
            ['%s [id: %s]' % (t.preferred_name, str(t.id)) for t in topics]))
        for topic in topics:
            topic.save()
            reversion.set_user(user)
            reversion.set_comment(comment)

    # Topic with the oldest creation date will be the one merged into
    merged_topic = topics[0]

    # Get preferred & alternate names for the new topic, to be saved later.
    preferred_name, alternate_names = get_preferred_topic_name(topics)

    # New topic article
    combined_article = get_combined_article(topics)
    merged_topic.summary = (etree.tostring(combined_article)
                            if combined_article is not None else None)

    # Change foreign key references & references in revisions
    for topic in topics:
        for cite in topic.summary_citations.all():
            cite.topic = merged_topic
            cite.save()
        for ta in topic.assignments.all():
            ta.topic = merged_topic
            ta.save()
        for alias in topic.aliases.all():
            alias.topic = merged_topic
            alias.save()
        for version in reversion.get_for_object(topic):
            version.object = merged_topic
            version.object_id_int = int(version.object.id)
            version.save()

    # Delete all old topics but keep names as aliases
    topics.remove(merged_topic)
    for topic_to_remove in topics:
        topic_to_remove.delete()
    for new_alias in alternate_names:
        AlternateName.objects.create(topic=merged_topic, name=new_alias, creator=user)

    # Update topic affiliation
    merged_topic.affiliated_projects.clear()
    for project in merged_topic.get_project_affiliation():
        merged_topic.affiliated_projects.add(project)

    # Give the merged topic a new slug & save
    merged_topic.preferred_name = preferred_name
    merged_topic.slug = Topic.make_slug(topic.preferred_name)
    merged_topic.save()

    return merged_topic





def topic_is_member_of_cluster(topic,cluster):
    return cluster.topics.filter(id = topic.id).count() >=1

def add_topic_to_cluster(topic,cluster):
    if not topic_is_member_of_cluster(topic,cluster):
        topic_cluster = get_cluster_for_topic(topic)
        if topic_cluster == None:
            cluster.topics.add(topic)
        else:        
            cluster = merge_clusters(cluster,topic_cluster)

def merge_clusters(cluster1,cluster2):
    for topic in cluster2.topics.all():
        if not topic_is_member_of_cluster(topic,cluster1):
            cluster1.topics.add(topic)
    delete_cluster(cluster2)
    return cluster1

def get_cluster_for_topic(topic):
    query_result  = TopicCluster.objects.filter(topics__in=[topic])
    len_query_result = query_result.count() 
    if len_query_result== 0 :
        return None
    elif len_query_result == 1:
        return query_result[0]
    else :
        cluster_list = list(query_result)
        c1 = cluster_list.pop()
        for c in cluster_list:
            c1 = merge(c1,c)
        return c1


def add_topics_to_cluster(topics):
    len_topics = len(topics)

    if len_topics == 0:
        return None
    elif len_topics == 1:
        topic = topics[0]
        cluster = get_cluster_for_topic(topic)
        if cluster == None:
            cluster  = TopicCluster.objects.create(creator=topic.creator,message=topic.preferred_name)
            add_topic_to_cluster(topic,cluster)
        return cluster
    else:
        main_topic = None
        main_cluster = None
        index = -1
        topics = list(topics)
        for i in range(0, len_topics):
            main_topic = topics[i]
            main_cluster = get_cluster_for_topic(main_topic)
            index = i
            if main_cluster != None:
                break;

        if main_cluster == None:
            main_topic = topics.pop()
            main_cluster = TopicCluster.objects.create(creator=main_topic.creator,message=main_topic.preferred_name)
            add_topic_to_cluster(main_topic,main_cluster)
        else:
            topics.pop(index)

        for topic in topics:
            add_topic_to_cluster(topic,main_cluster)

        return main_cluster

    return None

def delete_topics_from_cluster(topics,cluster):
    for topic in topics:
        if topic_is_member_of_cluster(topic,cluster):
            cluster.topics.remove(topic)

def delete_cluster(cluster):
    cluster.delete()

