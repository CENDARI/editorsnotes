from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


import sys
this_mod = sys.modules[__name__]

def run():
    """
    dynamically applies the patches defined below
    to be executed ASAP after app loading, by example in __init__.py
    of the current package (cendari)
    """
    for pname,patch in this_mod.__dict__.items():
        if hasattr(patch,'target_class'):
            print "class %s" % pname
            target = patch.target_class
            print target
            for attr, val in patch.__dict__.items():
                if attr.startswith("__"): continue
                if attr == 'target_class': continue
                print "Patch %s:%s" % (target, attr)
                #print "meta::",target._meta.fields
                fields = [e.name for e in target._meta.fields]
                #https://djangosnippets.org/snippets/2300/
                locfields = [e.name for e in target._meta.local_fields]
                has_attr = hasattr(target, attr)
                target.add_to_class(attr,val)
                if attr in locfields:
                    lastattr = target._meta.fields.pop()
                    for i,attr in enumerate(target._meta.fields):
                        if attr == lastattr.name:
                            target._meta.fields[i] = lastattr
                            break
                    lastattr = target._meta.local_fields.pop()
                    for i,attr in enumerate(target._meta.local_fields):
                        if attr == lastattr.name:
                            target._meta.local_fields[i] = lastattr
                            break
                    
###################################################################
# Note :                                                          #
# In order to patch a class being part of the editorsnotes models #
# (let's call it Foo) you have to :                               #
# 1) import Foo in this module                                    #
# 2) Create below a new class called FooPatch (naming convention) #
# 3) add the attribute:                                           #
#            target_class = Foo                                   #
#    to FooPatch class                                            #
# 4) Add to FooPatch the attributes and methods you want to       #
# declare on Foo (they are going to be migrated from FooPatch to  #
# Foo on call of run() function)                                  #
###################################################################

###################################################################
# Import the classis to be patched and other useful modules :     #
###################################################################

from editorsnotes.main.models import (Transcript, 
                                      topics, Note, Project, Scan)
from editorsnotes.main.models.topics import *
from editorsnotes.main.models.notes import *
from editorsnotes.main.models.notes import *
from editorsnotes.main.models.documents import *
from editorsnotes.main.models.base import *
from editorsnotes.main.models.auth import *

from cendari.iipimagestorage import IIPImageStorage
iipimage_storage = IIPImageStorage()
from cendari.fields import RDFField

###################################################################
# Add your class patches here :                                   #
###################################################################



class TrancriptPatch(object):
    target_class = Transcript
    project = Transcript.get_affiliation
    def get_absolute_url(self):
        return reverse('transcript_edit_view', None, [self.document.id])
    def save(self, *args, **kwargs):
        super(Transcript, self).save(*args, **kwargs)

import editorsnotes.main.models.topics

editorsnotes.main.models.topics.TYPE_CHOICES = (
    ('EVT', 'Event'),
    ('ORG', 'Organization'),
    ('PER', 'Person'),
    ('PUB', 'Publication'),
    ('ART', 'Artifact'),
    ('PLA', 'Place'),
#   ('DAT', 'Date'),
    ('TAG', 'Tag'))


class TopicPatch(object):
    target_class = Topic
    date = models.DateTimeField(editable=True, db_index=True, null=True,blank=True)
    rdf = RDFField(null=True,blank=True)
    
    def related_objects(self, model=None):
        qs = TopicAssignment.objects.filter(topic__topic_node_id=self.id)
        if model is not None:
            model_ct = ContentType.objects.get_for_model(model)
            model_assignments = qs.filter(content_type_id=model_ct.id)
            return model.objects.filter(
                id__in=model_assignments.values_list('object_id', flat=True)
            )
        else:
            return [obj.content_object for obj in qs] 

    def get_related_notes(self):
        notes = self.topic_node.related_objects(Note)
        return notes
    def get_related_documents(self):
        documents = self.topic_node.related_objects(Document)
        return documents

class NotePatch(object):
    target_class = Note
    def get_all_related_topics(self):
        topics = []
        topics += [ta.topic for ta in self.related_topics.all()]
        return set(topics) 
    def get_all_related_topics_ids(self):
        topics = []
        topics += [ta.topic.pk for ta in self.related_topics.all()]
        return topics
    
class DocumentPatch(object):
    target_class = Document
    def get_form_kwargs(self):
        print "KWARGS"
        kwargs = super(ModelFormMixin, self).get_form_kwargs()
        if hasattr(self, 'object') and self.object:
            kwargs.update({'instance': self.object})
        else:
            has_project_field = all([
                hasattr(self.model, 'project'),
                hasattr(self.model.get_affiliation, 'field'),
                hasattr(self.model.get_affiliation.field, 'related'),
                self.model.get_affiliation.field.related.parent_model == Project
            ])
            if has_project_field:
                # Then create an instance with the project already set
                instance = self.model(project=self.project)
                kwargs.update({ 'instance': instance })

        return kwargs
    def get_all_related_topics(self):
        topics = []
        topics += [ta.topic for ta in self.related_topics.all()]
        return set(topics) 

class ProjectPatch(object):
    target_class = Project
    def get_absolute_url(self):
        return reverse('project_view', None, [self.id])
    # fix a bug present in editorsnotes to be removed when editorsnotes is fixed
    def get_role_for(self, user):
        qs = self.roles.filter(group__user=user,role='Editor')
        return qs.get() if qs.exists() else None
    def is_owned_by(self, user):
        qs = self.roles.filter(group__user=user,role='Owner')
        return qs.exists()


class ScanPatch(object):
    target_class = Scan
    image = models.ImageField(storage=iipimage_storage, upload_to='scans/%Y/%m')


class UserPatch(object):
    target_class = User
    def get_authorized_projects(self):
        if self.is_superuser:
            return Project.objects.all()
        return self.get_affiliated_projects()
    def get_an_authorized_project(self):
        if self.is_superuser:
            return Project.objects.all()[0]
        else: 
            return self.get_affiliated_projects()[0]
    def superuser_or_belongs_to(self, project):
        if self.is_superuser:
            return True
        return self.belongs_to(project)
    # fix a bug present in editorsnotes to be removed when editorsnotes is fixed
    def _get_project_role(self, project):
        role_attr = '_{}_role_cache'.format(project.slug)
        if not hasattr(self, role_attr):
            setattr(self, role_attr, project.get_role_for(self))
        return getattr(self, role_attr)

            
import editorsnotes.main.fields
from lxml.html.clean import Cleaner

editorsnotes.main.fields.cleaner = Cleaner(style=True,safe_attrs_only=False) #[jdf] fix for RDFa
