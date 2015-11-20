import os
import re
import calendar
from datetime import datetime
from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.mail import mail_admins
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect)
from django.shortcuts import render_to_response, get_object_or_404, redirect

from django.template import RequestContext
from django.utils.functional import lazy 
from django.utils import simplejson

from editorsnotes.main import models as main_models
from editorsnotes.search import en_index

from cendari.search import cendari_index
from cendari.search.facets import cendari_filter, cendari_aggregations, cendari_faceted_search
from cendari.search.index import cendari_get_project_topics

from cendari import utils
from cendari.image import  ProjectAdminView, scan_to_dict
from editorsnotes.admin.views.topics import TopicAdminView
from editorsnotes.admin.views.notes import NoteAdminView
from editorsnotes.admin.views.documents import DocumentAdminView, TranscriptAdminView
from editorsnotes.admin.views.projects import add_project, change_project
from editorsnotes.admin import forms

from editorsnotes.refine import utils as rutils
from editorsnotes.refine.models import TopicCluster
from editorsnotes.main.templatetags.display import as_html
from django.core.urlresolvers import reverse
from forms import ImportFromJigsawForm
from sendfile import sendfile
from semantic import *
import json

from editorsnotes.admin import forms
import reversion

import traceback
import pprint

from itertools import chain

import StringIO
import pycurl
import urllib
from django.core.exceptions import PermissionDenied

import operator
import requests

import logging
logger = logging.getLogger(__name__)


def about_cendari(request):
        return render_to_response(
        'aboutCendari.html', context_instance=RequestContext(request))

def browse_cendari(request):
    max_count = 6
    o = {}
    for model in [main_models.Note, main_models.Document]:
        model_name = model._meta.module_name
        listname = '%s_list' % model_name
	if request.user.is_superuser:
		query_set = model.objects.order_by('-last_updated')
	else:
		query_set = model.objects.filter(pk__in=[obj.id for obj in model.objects.all() if obj.get_affiliation().is_owned_by(request.user)]).order_by('-last_updated')
        items = list(query_set[:max_count])
        o[listname] = items

    model = main_models.TopicNode
    model_name = model._meta.module_name
    listname = '%s_list' % model_name
    if request.user.is_superuser:
	    query_set = model.objects.order_by('-last_updated')
	    items = list(query_set[:max_count])
    else:		
            #query_set = model.objects.filter(pk__in=[tn.id for tn in model.objects.all() if tn.get_connected_projects()[0].is_owned_by(request.user)]).order_by('-last_updated')
	    #query_set = model.objects.filter(pk__in=[tn.id for tn in model.objects.all() if (pr for pr in tn.get_connected_projects() if pr.is_owned_by(request.user))]).order_by('-last_updated')
	    #TO-DO: query above does not work, below is a quick fix:
	    tns = []
	    for tn in model.objects.all():
		    connected_projects = tn.get_connected_projects()
		    for pr in connected_projects:
			    if(pr.is_owned_by(request.user)):
			       tns.append(tn)
	    items = tns[:max_count]
    o[listname] = items

    if request.user.is_superuser:
	    o['projects'] = Project.objects.all().order_by('name')
    else:
	    o['projects'] = request.user.get_authorized_projects().order_by('name')
    return render_to_response(
        'browsecendari.html', o, context_instance=RequestContext(request))
    
def _sort_citations(instance):
    cites = { 'all': [] }
    for c in main_models.Citation.objects.filter(
        content_type=ContentType.objects.get_for_model(instance), 
        object_id=instance.id):
        cites['all'].append(c)
    cites['all'].sort(key=lambda c: c.ordering)
    return cites

def _check_project_privs_or_deny(user, project_slug):
        project_slug = utils.get_project_slug(project_slug)
        if not user.is_authenticated():
            raise PermissionDenied("anonymous access not allowed")
        project = None
        if project_slug is None:
            projects = user.get_authorized_projects()
            if not projects:
                raise PermissionDenied("insufficient priviledges for %s" % user.username)
            #(NB) handle superusers
            if user.is_superuser:
                for p in projects:
                    project_role = user._get_project_role(p)
                    if project_role is not None:                
                        project = p
                        break
                if project is None:
                    logger.warn("superuser does not have own projects.")
                    project = projects[0]
            else:
                project = projects[0]
        else:
            project = get_object_or_404(Project, slug=project_slug)
        if not user.superuser_or_belongs_to(project) and not project.is_owned_by(user):
            raise PermissionDenied("not authorized on %s project" % project_slug)
        return project

def user_login(request):
    logger.debug('in login request meta is :')
    logger.debug(request.META)

    logger.debug('in login request session is :')
    logger.debug(request.session)

   

    if 'eppn' in request.META:
        if 'REMOTE_USER' in request.META:
            request.session['REMOTE_USER'] = request.META['REMOTE_USER']
           
            if 'REMOTE_USER' in request.session:
                logger.debug('REMOTE_USER is in session')
                logger.debug('session REMOTE_USER:')
                logger.debug(request.session['REMOTE_USER'])
            else:
                logger.debug('REMOTE_USER is not in the session')
        else:
            logger.debug('no REMOTE_USER in meta')
        return redirect('index_view')
    else:
        logger.debug('no eppn in meta')
    return redirect('index_view')

def get_projects_owned_by_user(user):
    owned_projects = []
    authorized_projects = user.get_authorized_projects()

    for p in authorized_projects:
        if p.is_owned_by(user):
            owned_projects.append(p)

    return owned_projects

def _check_privs(user, obj):
    project = obj.get_affiliation()
    if not user.superuser_or_belongs_to(project) and not project.is_owned_by(user):
        #print "not superuser_or_belongs_to"
        raise PermissionDenied("not authorized on %s project" % obj.slug)
    return obj

# @login_required
#@check_project_privs
def index(request,project_slug=None):
    project_slug = utils.get_project_slug(project_slug)
    logger.debug('in index request meta is :')
    logger.debug(request.META)
    if 'REMOTE_USER' in request.session:
        logger.debug('in login request session is :')
        logger.debug(request.session['REMOTE_USER'])
    
    user = request.user
    #if project_slug is None:
    #    project = user.get_authorized_projects()[0]
    #else:
    #    project = Project.objects.get(slug=project_slug)
    # project =  _check_project_privs_or_deny(request.user, project_slug)
    o ={}
    if user.is_authenticated():
        project =  get_projects_owned_by_user(request.user)[0]
    else:
        public_projects = utils.get_public_projects()
        project = public_projects[0] if len(public_projects)>0 else None
    o['project'] =  project 
    return render_to_response(
        'emptytab.html', o, context_instance=RequestContext(request))

class EditNoteAdminView(NoteAdminView):
    template_name = 'editnote.html'
    def save_object(self, form, formsets):
        #print "Save_object on note"
        user = self.request.user
        obj, action = super(EditNoteAdminView, self).save_object(form, formsets)
        semantic_process_note(obj, user)
        return obj, action

class EditDocumentAdminView(DocumentAdminView):
    template_name = 'editdocument.html'
    def save_object(self, form, formsets):
        #print "Save_object on document"
        user = self.request.user
        obj, action = super(EditDocumentAdminView, self).save_object(form, formsets)
        semantic_process_document(obj, user)
        return obj, action

@login_required
def scan(request, scan_id, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    #print "scan view"
    o = {}
    scan = get_object_or_404(main_models.Scan, id=scan_id)
    if not scan.needs_image_viewer():
        return scan_image(request, scan_id, project_slug)
    if not scan.tiff_file_exists():
        scan.create_tiff_file()
        raise PermissionDenied("Tiff file is being built, try again...")
    info = scan_to_dict(scan)
    if info is None:
        raise PermissionDenied("Tiff file is being built, try again...")
    o['image'] = info['path']
    o['scan'] = scan
    o['server'] = settings.IIPSRV
    o['credit'] = 'INRIA Aviz for the Cendari project'
    o['options'] = json.dumps(info)
    return render_to_response(
        'scan.html',
        { 'scan':o,'project_slug': project_slug}, 
        context_instance=RequestContext(request))

@login_required
def scan_image(request, scan_id, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    scan = get_object_or_404(main_models.Scan, id=scan_id)
    if scan.document.project.slug != project_slug:
        raise PermissionDenied("not authorized on %s project" % project_slug)
    return sendfile(request, os.path.abspath(scan.image.path))

@login_required
def scan_tiffimage(request, scan_id, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    scan = get_object_or_404(main_models.Scan, id=scan_id)
    if scan.document.project.slug != project_slug:
        raise PermissionDenied("not authorized on %s project" % project_slug)
    if not scan.tiff_file_exists():
        scan.create_tiff_file()
        raise PermissionDenied("Tiff file is being built, try again...")
    return sendfile(request, scan.get_tiff_path())


class EditTopicAdminView(TopicAdminView):
    template_name = 'edittopic.html'
    def save_object(self, form, formsets):
        #print "Save_object on topic"
        user = self.request.user
        obj, action = super(EditTopicAdminView, self).save_object(form, formsets)
        semantic_resolve_topic(obj)
        return obj, action

def edit_topic_node(request, topic_node_id):
    o = {}
    node_qs = main_models.TopicNode.objects.select_related()
    o['topic_node'] = get_object_or_404(node_qs, id=topic_node_id)
    return render_to_response(
        'edittopicnode.html', o, context_instance=RequestContext(request))
    
class EditTranscriptAdminView(TranscriptAdminView):
    template_name = 'edittranscript.html'
    
    #print "transcript view"
    
    def get_object(self, document_id):
        self.document = get_object_or_404(
            main_models.Document, id=document_id, project_id=self.project.id)
        return self.document.transcript if self.document.has_transcript() else None
    def save_object(self, form, formsets):
        #print "Save_object on transcript"
        user = self.request.user
        obj, action = super(EditTranscriptAdminView, self).save_object(form, formsets)
        semantic_process_transcript(obj, user)
        return obj, action

@login_required
@reversion.create_revision()
def cendari_project_add(request):
    #print request
    o = {}
    user = request.user
    o['user']= request.user
    project = user.get_authorized_projects()[0]
    # o['user_has_perm'] = user.is_superuser
    o['user_has_perm'] = True
    o['mode'] = 'add'
     #or utils.is_project_creator(user)
    # if not (user.is_superuser or utils.is_project_creator(user)):
    #     return HttpResponseForbidden(
    #         content='You do not have permission to create a new project.')

    if request.method == 'POST':
        form = forms.ProjectCreationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            project = form.save()
            role = project.roles.get_or_create_by_name('Owner')
            role.users.add(user)
            messages.add_message(
                request, messages.SUCCESS,
                'New project ({}) created.'.format(project.name))
            return HttpResponseRedirect(project.get_absolute_url())
        else:
            o['form'] = form
    else:
        o['form'] = forms.ProjectCreationForm(user=request.user)
        #print "fin creation projet", request.method
    o['project']=project

    users = list(main_models.User.objects.all())
    users.remove(request.user)

    return render_to_response(
        'editproject.html',o, context_instance=RequestContext(request))




# TODO add reversion / revision

# @login_required
@reversion.create_revision()
def cendari_project_change(request, project_id):
    o = {}
    if request.user.is_authenticated():
        project = _check_privs(request.user, get_object_or_404(Project, id=project_id))
    else:
       project = get_object_or_404(Project, id=project_id)
       return redirect('project_read_view',project_slug=project.slug)
    o['user']= request.user
    o['user_has_perm'] =  request.user.has_project_perm(project, 'main.change_project') or  project.is_owned_by(user)
    if not ['user_has_perm']:
        return redirect('project_read_view',project_slug=project.slug)
    o['slug_aliases'] = project.slug_aliases.all()
    o['mode'] = 'edit'
    # if not user.has_project_perm(project, 'main.change_project') and not project.is_owned_by(user):
    #     return HttpResponseForbidden(
    #         content='You do not have permission to edit the details of %s' % project.name)

    if request.method == 'POST':
        form = forms.ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.add_message(
                request, messages.SUCCESS,
                'Details of %s saved.' % (project.name))
            redirect_url = request.GET.get('return_to', request.path)
            return HttpResponseRedirect(redirect_url)
        else:
            o['form'] = form

    else:
        o['form'] = forms.ProjectForm(instance=project)
    o['project']=project

    users = list(main_models.User.objects.all())
    users.remove(request.user)
    o['users'] = users

    return render_to_response(
        'editproject.html', o, context_instance=RequestContext(request))

def cendari_project_view(request,project_slug):
    project_slug = utils.get_project_slug(project_slug)
    project = get_object_or_404(Project, slug=project_slug)
    if not utils.project_is_public(project):
        _check_project_privs_or_deny(request.user, project_slug)
    o ={}
    o['project']=project
    return render_to_response(
        'editproject.html', o, context_instance=RequestContext(request))

def editnote(request, note_id):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.creator = request.user
            obj.save()
            if request.is_ajax():
                return HttpResponse(json.dumps(
                        {'value': obj.as_text(),
                         'id': obj.id}
                        ), content_type="application/json");
            return HttpResponse('Thanks')
    if note_id == "0":
        note = main_models.Note(id=0)
    else:
        note = get_object_or_404(main_models.Note, id=note_id)
    form = NoteForm(instance=note)
    max_count = 6
    o = {}
    for model in [main_models.Topic, main_models.Note, main_models.Document]:
        model_name = model._meta.module_name
        listname = '%s_list' % model_name
        query_set = model.objects.order_by('-last_updated')
        items = list(query_set[:max_count])
        o[listname] = items
    o['project_list'] = main_models.Project.objects.all().order_by('name')
    o['note'] = note
    if note_id != "0":
        o['history'] = reversion.get_unique_for_object(note)
        o['topics'] = [ ta.topic for ta in note.topics.all() ]
        o['cites'] = main_models.Citation.objects.get_for_object(note)
    form = admin_forms.NoteForm(instance=note)
    o['form'] = form
    return render_to_response(
        'editnote.html', o, context_instance=RequestContext(request))

@login_required
@transaction.commit_on_success
def import_from_jigsaw(request, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    project =  _check_project_privs_or_deny(request.user, project_slug)
    if request.method == 'POST':
        form = ImportFromJigsawForm(request.POST, request.FILES)
        if form.is_valid():
            #p = main_models.Project.objects.get(slug=project_slug)
            p =  _check_project_privs_or_deny(request.user, project_slug)
            utils.import_from_jigsaw(request.FILES['file'], request.user, p)
            return HttpResponseRedirect(reverse('index_view'))
    else:
        form = ImportFromJigsawForm()
    return render_to_response(
            'importfromjigsaw.html', 
            { 'form': form, 'project': project },
            context_instance=RequestContext(request))

def small_vis(request, project_slug):
    return render_to_response('smallvis.html',{'project_slug':project_slug})


# Serve aggregated data used to drive the small visualizations panel
# FIXME: No longer returns counts. Need to perform aggregation using Elastic Search instead of Haystack
#        Currently replaced by small_vis_data_lazy
def small_vis_data(request, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    #indexed_topics = SearchQuerySet().models(main_models.Topic)
    if not utils.project_is_public(get_object_or_404(Project, slug=project_slug)):
        _check_project_privs_or_deny(request.user, project_slug) # only 4 check
    indexed_topics = main_models.Topic.objects.filter(project__slug=project_slug)
    topics_list = []
    for t in indexed_topics:
        timestamp = calendar.timegm(t.date.timetuple()) * 1000 if t.date else ''
        v = {'preferred_name':t.preferred_name, 
             'type':t.topic_node.type, 
             'date':timestamp,
             'id':t.id,}
             #'count':it.related_docs_count}
        try:
            ll = semantic_query_latlong(t)
        except Exceptions as e:
            logger.error('Error in small_vis_data', e)
            #traceback.print_exc(e)
        if ll:
            v['latlong'] = ', '.join(map(str, ll))
        topics_list.append(v)
    return HttpResponse(json.dumps(topics_list), mimetype='application/json')


# Serve aggregated data used to drive the small visualizations panel
# - Performs all the aggregation at request time rather than using an index.

def small_vis_data_lazy(request, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    topics_dict = {}
    if not utils.project_is_public(get_object_or_404(Project, slug=project_slug)):
        _check_project_privs_or_deny(request.user, project_slug) # only 4 check
    documents = main_models.Document.objects.filter(project__slug=project_slug)#[:100] #For debugging 
    #print 'docs: %d' % (len(documents))
    for document in documents:
        topics = document.get_all_related_topics()
        #print 'len of topics: %d ' % len(topics)
        for t in topics:
            timestamp = calendar.timegm(t.date.timetuple()) * 1000 if t.date else ''
            v = {'preferred_name':t.preferred_name, 
                 'type':t.topic_node.type, 
                 'date':timestamp,
                 'id':t.topic_node.id, #(NB) was t.pk
		 'url':t.get_absolute_url()} #(NB) 
            ll = semantic_query_latlong(t)
            if ll:
                v['latlong'] = ', '.join(map(str, ll))
            
            dict_match = topics_dict.get(t.pk, v)
            if dict_match == v:
                topics_dict[t.pk] = v
            dict_match['count'] = dict_match.get('count', 0) + 1
            dict_match['doc_count'] = dict_match.get('doc_count', 0) + 1

    notes = main_models.Note.objects.filter(project__slug=project_slug)
    #print 'notes: %d' % (len(notes))
    for note in notes:
        for t in note.related_topics.all():
            t = t.topic
            timestamp = calendar.timegm(t.date.timetuple()) * 1000 if t.date else ''
            v = {'preferred_name':t.preferred_name, 
                 'type':t.topic_node.type, 
                 'date':timestamp,
                 'id':t.topic_node.id, #(NB) was t.pk
		 'url':t.get_absolute_url()} #(NB) 
            ll = semantic_query_latlong(t)
            if ll:
                v['latlong'] = ', '.join(map(str, ll))
                #print "LatLong of %s: %s" % (t.preferred_name, v['latlong'])

            dict_match = topics_dict.get(t.pk, v)
            if dict_match == v:
                topics_dict[t.pk] = v
            dict_match['count'] = dict_match.get('count', 0) + 1
            dict_match['note_count'] = dict_match.get('note_count', 0) + 1
    return HttpResponse(json.dumps(topics_dict.values()), mimetype='application/json')

#project =  _check_project_privs_or_deny(request.user, project_slug)




def getResourcesData(request, project_slug, sfield):  
    project_slug = utils.get_project_slug(project_slug)
    my_tree = {
        'title':'My resources:',
        'key':'root',
        'isFolder':'true',
        'addClass': '',
        'url':'',
        'children': []
    }
    my_projects = {
        'title':'My projects',
        'key':'my_projects',
        'isFolder':'true',
        'addClass':'',
        'url':'',
        'children' : []
    }
    other_projects = {
        'title':'Other projects',
        'key':'other_projects',
        'isFolder':'true',
        'addClass':'',
        'url':'',
        'children' : []
    }
    public_projects = {
        'title':'Public projects',
        'key':'public_projects',
        'isFolder':'true',
        'addClass':'',
        'url':'',
        'children' : []
    }
    

    if request.user.is_authenticated():
        projects = request.user.get_authorized_projects().order_by('name').distinct('name')
        main_project =  _check_project_privs_or_deny(request.user, project_slug)
        print "I am hereeeeeeeee"
    elif project_slug != 'no_project':
        project = get_object_or_404(Project, slug=project_slug)
        if not utils.project_is_public(project):
            main_project =  _check_project_privs_or_deny(request.user, project_slug)
        else:
            main_project = project
    else:
        main_project = None
    # utils.get_image_placeholder_document(request.user,main_project)
    if request.user.is_authenticated():
        if request.user.is_superuser:
            for p in projects:
                p_role = p.get_role_for(request.user)
                if p_role!=None:
                    my_project = {
                        'title': p.name,
                        'key': p.slug,
                        'isFolder':'true',
                        'addClass': '',
                        'url':'',
                        'isLazy':'true',
                        'project_id': p.id,
                        'children' : []
                    }
                    my_projects['children'].append(my_project)
                else:
                    other_project = {
                        'title': p.name,
                        'key': p.slug,
                        'isFolder': 'true',
                        'addClass': '',
                        'url':'',
                        'isLazy':'true',
                        'project_id':p.id,
                        'children' : []
                    }
                    other_projects['children'].append(other_project)
            my_tree['children'].append(my_projects)
            my_tree['children'].append(other_projects)
        else:
            #copied from cendari.admin2
            owned_projects = projects
            for p in owned_projects:
                my_project = {
                    'title': p.name,
                    'key': p.slug,
                    'isFolder':'true',
                    'addClass':'',
                    'url':'',
                    'isLazy':'true',
                    'project_id':p.id,
                    'children' : []
                }
                my_projects['children'].append(my_project)
            my_tree['children'].append(my_projects)
    published_projects = utils.get_public_projects()

    for p in published_projects:
        published_project = {
            'title': p.name,
            'key': p.slug,
            'isFolder':'true',
            'addClass':'',
            'url':'',
            'isLazy':'true',
            'project_id':p.id,
            'children' : []
        }
        public_projects['children'].append(published_project)
    my_tree['children'].append(public_projects)

    res = json.dumps(my_tree, encoding="utf-8")
    response_dict = request.GET['callback'] + "(" + res + ")"

    return HttpResponse(response_dict, mimetype='application/json')

def getLazyProjectData(request, project_slug, sfield):
    project_slug = utils.get_project_slug(project_slug)
    if not utils.project_is_public(get_object_or_404(Project, slug=project_slug)):
        _check_project_privs_or_deny(request.user, project_slug) # only 4 check
    if request.user.is_authenticated():
        projects = request.user.get_authorized_projects() 
    else:
        projects =utils.get_public_projects()   
    for p in projects:
        image_place_holder   = utils.get_image_placeholder_document(request.user,p)
        if p.slug == project_slug:
            result_list = []
            max_count = 10000
            for model in [main_models.Note, main_models.Document, main_models.Topic]:
                model_name = model._meta.module_name  
                if model_name == 'topic':
                    node_title = 'Entities (%d)' % len(main_models.topics.TYPE_CHOICES)
                    topic_list = getTopicResources(request, p.slug, sfield)
                    result_list.append({
                        'title':node_title,
                        'key': p.slug+'.topics',
                        'isFolder':'true',
                        'addClass': '',
                        'url':'',
                        'children': topic_list
                    })
                elif model_name == 'note':
                    query_set = model.objects.filter(project__slug=p.slug).order_by('-last_updated')[:max_count]
                    set_count = query_set.count()
                    node_title = (model_name + 's').title() + ' (' + str(set_count)  + ')'
                    note_list = getNoteResources(request, p.slug, sfield); 
                    result_list.append({
                        'title':node_title,
                        'key': p.slug+'.'+str(model_name)+'s',
                        'isFolder':'false',
                        'addClass':'',
                        'url':'',
                        'children':note_list
                    })
                elif model_name == 'document':
                    query_set = model.objects.filter(project__slug=p.slug).order_by('-last_updated')[:max_count]
                    set_count = query_set.count() -1 #due to placeholder (hidden) document
                    node_title = (model_name + 's').title() + ' (' + str(set_count)  + ')'
                    document_list = getDocumentResources_Faster(request, p.slug, sfield)
                    result_list.append({
                        'title':node_title,
                        'key': p.slug+'.'+str(model_name)+'s',
                        'isFolder':'false',
                        'addClass':'',
                        'url':'',
                        'children':document_list
                    })
    res = json.dumps(result_list, encoding="utf-8")
    response_dict = request.GET['callback'] + "(" + res + ")"
    return HttpResponse(response_dict, mimetype='application/json')

def getTopicResources(request, project_slug, sfield):
    project_slug = utils.get_project_slug(project_slug)
    if not utils.project_is_public(get_object_or_404(Project, slug=project_slug)):
        _check_project_privs_or_deny(request.user, project_slug) # only 4 check
    project = Project.objects.filter(slug=project_slug)[0]
    max_count = 10000
    topic_count = 0
    topic_list = []
    topic_types = main_models.topics.TYPE_CHOICES
    sorted_topic_types =  sorted(topic_types, key = lambda x: (x[0], x[1]))
    for (topic_type, topic_name) in sorted_topic_types:
        my_list = []
    	if sfield == "created" or sfield == "last_updated":
            query_set = main_models.Topic.objects\
              .filter(project__slug=project_slug,topic_node__type=topic_type,deleted=False)[:max_count] 
            o_query_set = sorted(query_set, key=operator.attrgetter(sfield))  
    	elif sfield == "-created" or sfield == "-last_updated":
            query_set = main_models.Topic.objects\
              .filter(project__slug=project_slug,topic_node__type=topic_type,deleted=False)[:max_count] 
            o_query_set = sorted(query_set, key=operator.attrgetter(sfield[1:]), reverse=True) 
    	elif sfield == "-alpha":
            o_query_set = main_models.Topic.objects.filter(project__slug=project_slug,topic_node__type=topic_type,deleted=False)\
            .extra(select={'lower_sfield': 'lower(preferred_name)'}).order_by('-lower_sfield')[:max_count]  
                #query_set = main_models.Topic.objects\
                #  .filter(project__slug=project_slug,topic_node__type=topic_type,deleted=False)[:max_count]   
    	    #o_query_set = sorted(query_set, key=operator.attrgetter('preferred_name'), reverse=True)
    	else:
            o_query_set = main_models.Topic.objects.filter(project__slug=project_slug,topic_node__type=topic_type,deleted=False)\
            .extra(select={'lower_sfield': 'lower(preferred_name)'}).order_by('lower_sfield')[:max_count]  
                #query_set = main_models.Topic.objects\
                #  .filter(project__slug=project_slug,topic_node__type=topic_type,deleted=False)[:max_count]  
	    #o_query_set = sorted(query_set, key=operator.attrgetter('preferred_name'))              
	set_count = len(o_query_set)
        topic_count += 1
        # active_topics = utils.get_all_active_topics_for_project(project)
        clusters = TopicCluster.objects.filter(topics__topic_node__type=topic_type,topics__project=project).distinct()
        clustered_topics = []
        for cluster in  clusters:
            topic_children = []
            for topic in cluster.topics.all():
                clustered_topics.append(topic)
                if (topic.topic_node.type != "EVT" and topic.rdf!=None and topic.rdf.strip() != '') or (topic.topic_node.type == "EVT" and topic.date!=None) :#TO BE CHANGED: check if the dbpedia entry is stored in the tuple store rather than rdf field
                    toresolve_flag = ''
                else:
                    toresolve_flag = ' *'
                topic_children.append({
                    'title': unicode(topic)+toresolve_flag,
                    'key': str(project_slug)+'.topic.'+str(topic.id),
                    'url':topic.get_absolute_url(),
                    'class':'topic_item'
                })
            my_list.append({
                'title' : unicode(cluster.message),
                'key' : str(project_slug)+'.topic_cluster.'+str(cluster.id),
                'isFolder':'true',
                'addClass':'',
                'url':'',
                'children':topic_children
            })
        for e in o_query_set:
            #to make sure both url and node key have the same topic_id (when a topic exists in multiple probjects)
            #my_list.append({'title':str(e), 'key':str(project_slug)+'.topic.'+str(e.id), 'url':e.get_absolute_url()})

            # if not e in active_topics:
            #     set_count -=1
            #     continue
            if e in clustered_topics:
                continue
            url_parts = e.get_absolute_url().split('/')
            topic_id_index = len(url_parts) - 2
            topic_id = url_parts[topic_id_index];
            if (e.topic_node.type != "EVT" and e.rdf!=None and e.rdf.strip() != '') or (e.topic_node.type == "EVT" and e.date!=None) :#TO BE CHANGED: check if the dbpedia entry is stored in the tuple store rather than rdf field
                toresolve_flag = ''
            else:
                toresolve_flag = ' *'
            my_list.append({
                'title': unicode(e)+toresolve_flag,
                'key': str(project_slug)+'.topic.'+str(topic_id),
                'url':e.get_absolute_url(),
	            'class':'topic_item'
            })
            node_title = topic_name + ' (' + str(set_count)  + ')'
    	css_class = '<span class="dynatree-topicfolder u' + topic_name + '">'
        topic_list.append({
            'title': css_class + topic_name+'</span>'+ ' (' + str(set_count)  + ')',
            'key' :str(project_slug)+'.topic.'+str(topic_type),
            'isFolder':'true',
            'isTopicFolder':'true',
            'topicType':topic_type,
            'addClass':'',
            'url':'',
            'children':my_list
        })
    return topic_list

def getNoteResources(request, project_slug, sfield):
    project_slug = utils.get_project_slug(project_slug)
    if not utils.project_is_public(get_object_or_404(Project, slug=project_slug)):
        _check_project_privs_or_deny(request.user, project_slug) # only 4 check
    max_count = 10000
    node_count = 0
    note_list = []
    if sfield == "created" or sfield == "-created" or sfield == "last_updated" or sfield == "-last_updated":
       	query_set = main_models.Note.objects.filter(project__slug=project_slug).order_by(sfield)[:max_count]   
    elif sfield == "-alpha":
    	query_set = main_models.Note.objects.filter(project__slug=project_slug).order_by('-title')[:max_count]      
    else:	
    	query_set = main_models.Note.objects.filter(project__slug=project_slug).order_by('title')[:max_count]
    set_count = query_set.count()
    for e in query_set:
        node_count += 1
        note_list.append({'title':str(e), 'key':str(project_slug)+'.note.'+str(e.id), 'addClass':'', 'url':e.get_absolute_url()})
    return note_list

def getDocumentResources(request, project_slug, sfield):
    project_slug = utils.get_project_slug(project_slug)
    if not utils.project_is_public(get_object_or_404(Project, slug=project_slug)):
        current_project = _check_project_privs_or_deny(request.user, project_slug) # only 4 check
    else:
        current_project = get_object_or_404(Project, slug=project_slug)

    if(current_project):
        image_place_holder = utils.get_image_placeholder_document(request.user,current_project)

    max_count = 10000
    doc_list = []   
    if sfield == "created" or sfield == "-created" or sfield == "last_updated" or sfield == "-last_updated":
       	query_set = main_models.Document.objects.filter(project__slug=project_slug).order_by(sfield)[:max_count]   
    elif sfield == "-alpha":
    	sql_query = 'select *, xpath('+str("'")+'/p/text()'+str("'")+', description) as desc_raw from main_document where project_id = '+ str(project_id) +' order by ordering DESC'
    	query_set =  main_models.Document.objects.raw(sql_query)
    else:
    	sql_query = 'select *, xpath('+str("'")+'/p/text()'+str("'")+', description) as desc_raw from main_document where project_id ='+ str(project_id) +' order by ordering'
    	query_set =  main_models.Document.objects.raw(sql_query)
    for e in query_set:  
        if e.id == image_place_holder.id:
            continue
        doc = {
            'title':str(e),
            'key':str(project_slug)+'.document.'+str(e.id),
            'addClass':'',
            'url':e.get_absolute_url(),
            'children':[]
        }
        doc_list.append(doc)        
    return doc_list


ID_RE = re.compile(r'/documents/(\d+)/$')

def getDocumentResources_Faster(request, project_slug, sfield):
    project_slug = utils.get_project_slug(project_slug)
    if not utils.project_is_public(get_object_or_404(Project, slug=project_slug)):
        current_project = _check_project_privs_or_deny(request.user, project_slug) # only 4 check
    else:
        current_project = get_object_or_404(Project, slug=project_slug)
        
    image_place_holder = -1

    if current_project:
        image_place_holder = utils.get_image_placeholder_document(request.user,current_project)

    doc_list = []   
    sort_field = ""
    sort_order = ""

    if sfield == "last_updated":
    	sort_field = "updated"
    	sort_order = "asc"
    elif sfield == "-last_updated":
    	sort_field = "updated"
    	sort_order = "desc"
    elif sfield == "-alpha":
    	sort_field = "title"
    	sort_order = "desc"
    else:
    	sort_field = "title"
    	sort_order = "asc"

    es_query = {
        "query": {"constant_score":  {"filter": {"term": {"project": project_slug }}}},
        "fields": ['title'],
        "sort": [
            {sort_field: { "order": sort_order, "ignore_unmapped" : "true" }}
        ]
    }
    es_results = cendari_index.search(es_query, doc_type='document')
    #pprint.pprint(es_results)

    
    for r in es_results["hits"]["hits"]:
        if 'fields' not in r:
            continue
	doc_title = r["fields"]["title"]
	doc_url = r["_id"]
        found = ID_RE.search(doc_url)
        if found:
            doc_id = found.group(1)
        else:
            continue
	doc_key = project_slug+'.document.'+doc_id
       	#if doc_id == str(image_place_holder.id):
        #    continue
	doc = {
		    'title': doc_title,
		    'key': doc_key,
		    'addClass': '',
		    'url': doc_url,
		    'children': []
	}
	doc_list.append(doc)

    return doc_list


@login_required
def getProjectID(request, project_slug, new_slug):
    project_slug = utils.get_project_slug(project_slug)
    _check_project_privs_or_deny(request.user, project_slug) # only 4 check
    _check_project_privs_or_deny(request.user, new_slug) # only 4 check
    editorsnotes.admin.views.projects.change_project(request, new_slug)
    projects = request.user.get_authorized_projects()
    selected_project = list((x for x in request.user.get_authorized_projects() if x.slug == new_slug))
    selected_project_id = selected_project[0].id #there should only be one project with slug == new_slug
    res = {'project_id':selected_project_id}
    ret = json.dumps(res, encoding="utf-8")
    return HttpResponse(ret, mimetype='application/json') 

@login_required
def getTopicType(request, project_slug, topic_id):
    project_slug = utils.get_project_slug(project_slug)
    _check_project_privs_or_deny(request.user, project_slug) # only 4 check
    #editorsnotes.admin.views.projects.change_project(request, project_slug)
    topic_node_query_set = main_models.TopicNode.objects.filter(id=topic_id)
    topic_type = topic_node_query_set[0].type
    res = {'topic_type':topic_type}
    ret = json.dumps(res, encoding="utf-8")
    return HttpResponse(ret, mimetype='application/json') 

def querySPARQL(request,q):
    if request.method == 'GET':
        q = q.replace('@', '?') # the ? don't work well in urls
    #print "querySPARQL is %s" % q
    res = semantic_query(q, request.user)
    res = list(res)
    ret = json.dumps(res, encoding="utf-8")
    return HttpResponse(ret, mimetype='application/json') 

def proxyRDFaCE(request):
    txt = request.POST['query']; response = { }
    request_body = txt.replace("\\n","\n").replace("\\r","\n").replace("\\","")
    urlDBpedia = "http://spotlight.dbpedia.org/rest/annotate"
    body = urllib.urlencode({'text': request_body})
    request ="text=" + body + "&confidence=0.2&support=20"
    buf = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, urlDBpedia)   
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.HTTPHEADER, ["Content-Type:application/x-www-form-urlencoded" , "Accept: application/json"])
    c.setopt(pycurl.POSTFIELDS, request)
    c.setopt(pycurl.WRITEFUNCTION, buf.write)
    c.perform()
    c.close()
    response = buf.getvalue()
    return HttpResponse(response, mimetype='application/json') 

def resources(request, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    return render_to_response('resources.html',dict(project_slug=project_slug))



def project_index(request, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    return render_to_response('project_index.html',dict(project_slug=project_slug))

# dummy: to be reimplemented!

import reversion
import editorsnotes.admin.views.projects
from editorsnotes.main.models import Project

@login_required
@reversion.create_revision()
def change_project(request, project_id):
    o = {}
    project = _check_privs(request.user, get_object_or_404(Project, id=project_id))
    return editorsnotes.admin.views.projects.change_project(request, project.slug)

def faceted_search(request,project_slug=None):
    o = cendari_faceted_search(request,project_slug)
    # o={}
    o['p_slug']=project_slug
    return render_to_response(
        'cendarisearch.html', o, context_instance=RequestContext(request))

def trame_search(request):
    trame_url = "http://git-trame.fefonlus.it/Rest.php?&type=freetext&q="+request.GET.get('q', '')+"&dbs="+request.GET.get('dbs', '127|129')
    # trame_url = "http://git-trame.fefonlus.it/Rest.php?&type=freetext&q=petrus&dbs=127|129"
    r = requests.post(trame_url)
    return HttpResponse(r.content, mimetype='application/json')

def nerd_service(request):
    url = 'http://traces1.saclay.inria.fr/nerd/service/processNERDText'
    params={
        "text": request.GET['text'],
        "onlyNER":"false",
        "sentence":"false",
        "format":"JSON",
        "customisation":"generic"
    }
    r = requests.get(url,params=params)

    return HttpResponse(r.content, mimetype='application/json')



def find_date(request,project_slug,topic_node_id):
    project_slug = utils.get_project_slug(project_slug)
    response_dates= []
    topic_qs = main_models.Topic.objects.select_related('topic_node', 'creator', 'last_updater', 'project').prefetch_related('related_topics__topic')
    topic = get_object_or_404(topic_qs,topic_node_id=topic_node_id,project__slug=project_slug)
    eventDates = semantic_find_dates(topic)
    print '!!!!!!!!!!!!!!!!!'
    print "RESULT IS"
    print eventDates
    print '!!!!!!!!!!!!!!!!!'
    if eventDates != []:
        #print '............................................. RETREIVED DATE IS = ' + eventDates[0]
        for d in eventDates:
            if utils.parse_well_known_date(d):
                response_dates.append(d)
    return HttpResponse(simplejson.dumps(response_dates), content_type="application/json")


def get_project_topics(request,project_slug=None):
    project_slug = utils.get_project_slug(project_slug)
    p = Project.objects.filter(slug=project_slug)[0]
    data = simplejson.dumps(cendari_get_project_topics(request.GET['topic_type'],p.name,request.GET['topic_name_prefix']))

    return HttpResponse(data, mimetype='application/json')

@login_required
def search(request,project_slug=None):
    project_slug = utils.get_project_slug(project_slug)
    #user = request.user
    #if project_slug is None:
    #    projects = user.get_authorized_projects()
    #    if not projects:
    #        return HttpResponseForbidden()
    #    project = projects[0]
    #    project_slug = project.slug
    #else:
    #    project = Project.objects.get(slug=project_slug)

    #if not user.superuser_or_belongs_to(project):
    #    return HttpResponseForbidden()
    project =  _check_project_privs_or_deny(request.user, project_slug)
    q = request.GET.get('q', {'query': {'match_all': {}}})
    results = en_index.search(q, highlight=True, size=50, project=project_slug)
    
    o = {
        'project': project,
        'results': results['hits']['hits'],
        'query': q if isinstance(q, basestring) else None
    }
    return render_to_response(
        'searchCendari.html', o, context_instance=RequestContext(request))
    
    
@login_required
def iframe_view(request,type):
    if type =='issuereport' :
        url = "https://dev.dariah.eu/jira/secure/CreateIssue.jspa?pid=10900&issuetype=1"
        title = "Issue Report"
    elif type == 'survey':
        url = "https://docs.google.com/forms/d/1d4l8P9eVKGOHIW6MQ-hYSKzZOyOJmnh6QRtJr4lOJJE/viewform?usp=send_form"
        title = "Survey"
    else:
        url = "https://www.google.fr/?gfe_rd=cr&ei=VL3HU-uIKayA8QerzoBA&gws_rd=ssl"
        title="Random"
    
    return render_to_response(
                              'iframe.html',{'iframe_url':url, 'title':title}, context_instance=RequestContext(request))
    
class NoteCendari(NoteAdminView):
    template_name = 'noteCendariEdit.html'
    def save_object(self, form, formsets):
         #print "Save_object on note"
         user = self.request.user
        # obj, action = super(EditNoteAdminView, self).save_object(form, formsets)
#         semantic_process_note(obj, user)
         #return obj, action
    def get_context_data(self, **kwargs):
        context = super(NoteCendari, self).get_context_data(**kwargs)       
        context['object_type'] = 'note'
        context['image_place_holder'] =  utils.get_image_placeholder_document(self.request.user,self.project)
        return context

class DocumentCendari(DocumentAdminView):
    template_name = 'documentCendariEdit.html'
    def get_breadcrumb(self):
        breadcrumbs = (
            (self.project.name, self.project.get_absolute_url()),
        )
        if self.object is None:
            breadcrumbs += (
                ('Add', None),
            )
        else:
            breadcrumbs += (
                (self.object.as_text(), self.object.get_absolute_url()),
                ('Edit', None)
            )
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super(DocumentCendari, self).get_context_data(**kwargs)       
        context['object_type'] = 'document'
        context['image_place_holder'] =  utils.get_image_placeholder_document(self.request.user,self.project)
        return context

class EntityCendari(TopicAdminView):
    template_name = 'entityCendari.html'

@login_required
def editNoteCendari(request, note_id, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    o['user'] = request.user
    user = request.user
    project = _check_project_privs_or_deny(user, project_slug)

    qs = main_models.Note.objects.select_related('license', 'project__default_license').prefetch_related('related_topics')
    note = get_object_or_404(qs, id=note_id, project__slug=project_slug)
    if note.is_private:
         can_view = (request.user.is_authenticated() and request.user.has_project_perm(note.project, 'main.view_private_note'))
         if not can_view:
            #print 'USER CANNOT VIEW NOTE'
            raise PermissionDenied()
    o['project'] = note.project
    o['breadcrumb'] = (
        (note.project.name, note.project.get_absolute_url()),
        ("Notes", reverse('all_notes_view', kwargs={'project_slug': note.project.slug})),
        (note.title, None),
    )
    o['note'] = note
    o['project_slug'] = project_slug
    o['object_type'] = 'note'
    o['object_id'] = note_id
    o['topic_type'] = 'NA'
    o['license'] = note.license or note.project.default_license
    o['history'] = reversion.get_unique_for_object(note)
    o['topics'] = [ta.topic for ta in o['note'].related_topics.all()]
    o['image_place_holder'] =  utils.get_image_placeholder_document(request.user,note.project)
    o['sections'] = note.sections\
            .order_by('ordering', 'note_section_id')\
            .all()\
            .select_subclasses()\
            .select_related('citationns__document__project',
                            'notereferencens__note_reference__project')
    o['can_edit'] = (
        request.user.is_authenticated() and
        request.user.has_project_perm(o['note'].project, 'main.change_note'))

    return render_to_response( 'noteCendariEdit.html', o, context_instance=RequestContext(request))

def readNoteCendari(request, note_id, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    o['user'] = request.user

    if not utils.project_is_public(get_object_or_404(Project, slug=project_slug)):
        _check_project_privs_or_deny(request.user, project_slug)

    qs = main_models.Note.objects.select_related('license', 'project__default_license').prefetch_related('related_topics')
    note = get_object_or_404(qs, id=note_id, project__slug=project_slug)
    if note.is_private:
         can_view = (request.user.is_authenticated() and request.user.has_project_perm(note.project, 'main.view_private_note'))
         if not can_view:
             raise PermissionDenied()
    o['project'] = note.project
    o['breadcrumb'] = (
        (note.project.name, note.project.get_absolute_url()),
        ("Notes", reverse('all_notes_view', kwargs={'project_slug': note.project.slug})),
        (note.title, None),
    )
    o['note'] = note
    o['project_slug'] = project_slug
    o['object_type'] = 'note'
    o['object_id'] = note_id
    o['topic_type'] = 'NA'
    o['license'] = note.license or note.project.default_license
    o['history'] = reversion.get_unique_for_object(note)
    o['topics'] = [ta.topic for ta in o['note'].related_topics.all()]
    o['sections'] = note.sections\
            .order_by('ordering', 'note_section_id')\
            .all()\
            .select_subclasses()\
            .select_related('citationns__document__project',
                            'notereferencens__note_reference__project')
    o['can_edit'] = (
        request.user.is_authenticated() and
        request.user.has_project_perm(o['note'].project, 'main.change_note'))

    return render_to_response( 'noteCendariRead.html', o, context_instance=RequestContext(request))

@login_required
def versionHistoryNoteCendari(request, note_id, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    qs = main_models.Note.objects.select_related('license', 'project__default_license').prefetch_related('related_topics')
    note = get_object_or_404(qs, id=note_id, project__slug=project_slug)
    if note.is_private:
        can_view = (request.user.is_authenticated() and request.user.has_project_perm(note.project, 'main.view_private_note'))
        if not can_view:
            raise PermissionDenied()
    o['note_id'] =note.id
    o['project'] = note.project
    o['version_list'] = reversion.get_for_object(note)
    return render_to_response( 'noteCendariVersionHistory.html', o, context_instance=RequestContext(request))

@login_required
def versionNoteCendari(request, note_id, project_slug,version_id):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    qs = main_models.Note.objects.select_related('license', 'project__default_license').prefetch_related('related_topics')
    note = get_object_or_404(qs, id=note_id, project__slug=project_slug)
    if note.is_private:
        can_view = (request.user.is_authenticated() and request.user.has_project_perm(note.project, 'main.view_private_note'))
        if not can_view:
            raise PermissionDenied()

    o['project'] = note.project
    
    version  = reversion.get_for_object(note).filter(id=version_id)[0]
    o['version'] = version
    if request.method == 'POST':
        version.revert()
    note = version.object_version.object
    o['breadcrumb'] = (
        (note.project.name, note.project.get_absolute_url()),
        ("Notes", reverse('all_notes_view', kwargs={'project_slug': note.project.slug})),
        (note.title, None),
    )
    o['note'] = note
    o['project_slug'] = project_slug
    o['object_type'] = 'note'
    o['object_id'] = note_id
    o['topic_type'] = 'NA'
    o['license'] = note.license or note.project.default_license
    o['history'] = reversion.get_unique_for_object(note)
    o['topics'] = [ta.topic for ta in o['note'].related_topics.all()]
    o['image_place_holder'] =  utils.get_image_placeholder_document(request.user,note.project)
    o['sections'] = note.sections\
            .order_by('ordering', 'note_section_id')\
            .all()\
            .select_subclasses()\
            .select_related('citationns__document__project',
                            'notereferencens__note_reference__project')
    o['can_edit'] = (
        request.user.is_authenticated() and
        request.user.has_project_perm(o['note'].project, 'main.change_note'))

    return render_to_response( 'noteCendariVersion.html', o, context_instance=RequestContext(request))

@login_required
def editDocumentCendari(request, project_slug, document_id):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    o['user'] = request.user
    _check_project_privs_or_deny(request.user, project_slug)
    qs = main_models.Document.objects.select_related('project')
    o['document'] = get_object_or_404(main_models.Document, id=document_id, project__slug=project_slug)
    o['project_slug'] = project_slug
    o['breadcrumb'] = (
        (o['document'].project.name, o['document'].project.get_absolute_url()),
#        ('Documents', reverse('all_documents_view',kwargs={'project_slug': o['document'].project.slug})),
        (o['document'].as_text(), None)
    )
    o['project'] = o['document'].project
    o['object_type'] = 'document'
    o['object_id'] = document_id
    o['topic_type'] = 'NA'
    o['image_place_holder'] =  utils.get_image_placeholder_document(request.user,o['document'].project)

    o['topics'] = (
        [ ta.topic for ta in o['document'].related_topics.all() ] +
        [ c.content_object for c in o['document'].citations.filter(content_type=ContentType.objects.get_for_model(main_models.Topic)) ])
    o['scans'] = o['document'].scans.all()

    # o['domain'] = Site.objects.get_current().domain
    o['domain'] = reverse('document_view', kwargs={'project_slug': project_slug,'document_id':document_id})
    # print "--------------------"
    # print o['domain']
    # print "--------------------"
    notes = [ns.note for ns in main_models.CitationNS.objects\
            .select_related('note')\
            .filter(document=o['document'])]
    note_topics = [ [ ta.topic for ta in n.related_topics.all() ] for n in notes ]
    o['notes'] = zip(notes, note_topics)

    if o['document'].zotero_data:
        o['zotero_data'] = as_readable(o['document'].zotero_data)
        if o['document'].zotero_link:
            o['zotero_url'] = o['document'].zotero_link.zotero_url
            o['zotero_date_information'] = o['document'].zotero_link.date_information
    return render_to_response('documentCendariEdit.html', o, context_instance=RequestContext(request))


def readDocumentCendari(request, project_slug, document_id):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    o['user'] = request.user
    if not utils.project_is_public(get_object_or_404(Project, slug=project_slug)):
        _check_project_privs_or_deny(request.user, project_slug)
    qs = main_models.Document.objects.select_related('project')
    o['document'] = get_object_or_404(main_models.Document, id=document_id, project__slug=project_slug)
    o['project_slug'] = project_slug
    o['breadcrumb'] = (
        (o['document'].project.name, o['document'].project.get_absolute_url()),
#        ('Documents', reverse('all_documents_view',kwargs={'project_slug': o['document'].project.slug})),
        (o['document'].as_text(), None)
    )
    o['project'] = o['document'].project
    o['object_type'] = 'document'
    o['object_id'] = document_id
    o['topic_type'] = 'NA'
    o['topics'] = (
        [ ta.topic for ta in o['document'].related_topics.all() ] +
        [ c.content_object for c in o['document'].citations.filter(content_type=ContentType.objects.get_for_model(main_models.Topic)) ])
    o['scans'] = o['document'].scans.all()

    # o['domain'] = Site.objects.get_current().domain
    o['domain'] = reverse('document_view', kwargs={'project_slug': project_slug,'document_id':document_id})
    # print "--------------------"
    # print o['domain']
    # print "--------------------"
    notes = [ns.note for ns in main_models.CitationNS.objects\
            .select_related('note')\
            .filter(document=o['document'])]
    note_topics = [ [ ta.topic for ta in n.related_topics.all() ] for n in notes ]
    o['notes'] = zip(notes, note_topics)

    if o['document'].zotero_data:
        o['zotero_data'] = as_readable(o['document'].zotero_data)
        if o['document'].zotero_link:
            o['zotero_url'] = o['document'].zotero_link.zotero_url
            o['zotero_date_information'] = o['document'].zotero_link.date_information
    return render_to_response('documentCendariRead.html', o, context_instance=RequestContext(request))

@login_required   
def versionHistoryDocumentCendari(request, document_id, project_slug):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    o['user'] = request.user
    qs = main_models.Document.objects.select_related('project')
    document = get_object_or_404(main_models.Document, id=document_id, project__slug=project_slug)
    o['project_slug'] = project_slug
    
    o['document_id'] =document.id
    o['project'] = document.project
    o['version_list'] = reversion.get_for_object(document)
    return render_to_response( 'documentCendariVersionHistory.html', o, context_instance=RequestContext(request))

@login_required
def versionDocumentCendari(request, document_id, project_slug,version_id):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    o['user'] = request.user
    qs = main_models.Document.objects.select_related('project')
    document = get_object_or_404(main_models.Document, id=document_id, project__slug=project_slug)

    o['project_slug'] = project_slug

    o['project'] = document.project
    version  = reversion.get_for_object(document).filter(id=version_id)[0]
    if request.method == 'POST':
        version.revert()
    o['version'] = version
    o['document'] = version.object_version.object
    o['project_slug'] = project_slug
    o['breadcrumb'] = (
        (o['document'].project.name, o['document'].project.get_absolute_url()),
#        ('Documents', reverse('all_documents_view',kwargs={'project_slug': o['document'].project.slug})),
        (o['document'].as_text(), None)
    )
    o['project'] = o['document'].project
    o['object_type'] = 'document'
    o['object_id'] = document_id
    o['topic_type'] = 'NA'
    o['image_place_holder'] =  utils.get_image_placeholder_document(request.user,o['document'].project)

    o['topics'] = (
        [ ta.topic for ta in o['document'].related_topics.all() ] +
        [ c.content_object for c in o['document'].citations.filter(content_type=ContentType.objects.get_for_model(main_models.Topic)) ])
    o['scans'] = o['document'].scans.all()

    # o['domain'] = Site.objects.get_current().domain
    o['domain'] = reverse('document_view', kwargs={'project_slug': project_slug,'document_id':document_id})
    # print "--------------------"
    # print o['domain']
    # print "--------------------"
    notes = [ns.note for ns in main_models.CitationNS.objects\
            .select_related('note')\
            .filter(document=o['document'])]
    note_topics = [ [ ta.topic for ta in n.related_topics.all() ] for n in notes ]
    o['notes'] = zip(notes, note_topics)

    if o['document'].zotero_data:
        o['zotero_data'] = as_readable(o['document'].zotero_data)
        if o['document'].zotero_link:
            o['zotero_url'] = o['document'].zotero_link.zotero_url
            o['zotero_date_information'] = o['document'].zotero_link.date_information

    return render_to_response( 'documentCendariVersion.html', o, context_instance=RequestContext(request))

@login_required
def editEntityCendari(request, project_slug, topic_node_id):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    o['user'] = request.user
    _check_project_privs_or_deny(request.user, project_slug)
    #print "getting topic_qs"
    topic_qs = main_models.Topic.objects.select_related('topic_node', 'creator', 'last_updater', 'project').prefetch_related('related_topics__topic')
    #print "getting topic object"
    o['topic'] = topic = get_object_or_404(topic_qs,topic_node_id=topic_node_id,project__slug=project_slug)
    o['cluster'] = rutils.get_cluster_for_topic(topic)
    o['project'] = topic.project
    o['project_slug'] = project_slug
    o['object_type'] = 'topic'
    o['object_id'] = topic_node_id
    o['topic_type'] = topic.topic_node.type
    o['topic'].date = utils.change_to_well_known_format(o['topic'].date)
    o['aliases'] = topic.alternate_names.all()
    #print 20*'.'+ 'topic.summary = " + str(topic.summary)
    o['breadcrumb'] = (
        (topic.project.name, topic.project.get_absolute_url()),
        ('Topics', reverse('all_topics_view', kwargs={'project_slug': topic.project.slug})),(topic.preferred_name, None)
    )
    topic_query = {'query': {'term': {'serialized.related_topics.id': topic.id }}}
    topic_query['size'] = 1000
    #print "searching for models"
    model_searches = ( en_index.search_model(model, topic_query) for model in
                       (main_models.Document, main_models.Note, main_models.Topic) )
    documents, notes, topics = (
        [ result['_source']['serialized'] for result in search['hits']['hits'] ]
        for search in model_searches)
    #print "filtering documents"
    # o['documents'] = main_models.Document.objects.filter(id__in=[d['id'] for d in documents])
    o['related_topics'] = main_models.Topic.objects.filter(id__in=[t['id'] for t in topics])
    note_objects = main_models.Note.objects.in_bulk([n['id'] for n in notes])
    #print len(note_objects)
    #print note_objects
    for note in notes:
        if ('id' in note.keys()) and (note['id'] in note_objects.keys()):
            related_topics = list((topic for topic in note['related_topics']
                                   if topic['url'] != request.path))
            note_objects[note['id']] = (note_objects[note['id']], related_topics,)
    # o['notes'] = note_objects.values()
    


    o['documents']  = []
    o['notes']      = []



    for d in topic.get_related_documents():
        if d.project in request.user.get_affiliated_projects():
            o['documents'].append(d)

    for n in topic.get_related_notes():
        if n.project in request.user.get_affiliated_projects():
            o['notes'].append(n)

    # o['documents']  = topic.get_related_documents()
    # o['notes']      = topic.get_related_notes()


    return render_to_response(
        'entityCendariEdit.html', o, context_instance=RequestContext(request))


def readEntityCendari(request, project_slug, topic_node_id):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    o['user'] = request.user
    if not utils.project_is_public(get_object_or_404(Project, slug=project_slug)):
        _check_project_privs_or_deny(request.user, project_slug)
    #print "getting topic_qs"
    topic_qs = main_models.Topic.objects.select_related('topic_node', 'creator', 'last_updater', 'project').prefetch_related('related_topics__topic')
    #print "getting topic object"
    o['topic'] = topic = get_object_or_404(topic_qs,topic_node_id=topic_node_id,project__slug=project_slug)
    o['cluster'] = rutils.get_cluster_for_topic(topic)
    o['project'] = topic.project
    o['project_slug'] = project_slug
    o['object_type'] = 'topic'
    o['object_id'] = topic_node_id
    o['topic_type'] = topic.topic_node.type
    o['topic'].date = utils.change_to_well_known_format(o['topic'].date)
    o['aliases'] = topic.alternate_names.all()
    #print 20*'.'+ 'topic.summary = " + str(topic.summary)
    o['breadcrumb'] = (
        (topic.project.name, topic.project.get_absolute_url()),
        ('Topics', reverse('all_topics_view', kwargs={'project_slug': topic.project.slug})),(topic.preferred_name, None)
    )
    topic_query = {'query': {'term': {'serialized.related_topics.id': topic.id }}}
    topic_query['size'] = 1000
    #print "searching for models"
    model_searches = ( en_index.search_model(model, topic_query) for model in
                       (main_models.Document, main_models.Note, main_models.Topic) )
    documents, notes, topics = (
        [ result['_source']['serialized'] for result in search['hits']['hits'] ]
        for search in model_searches)
    #print "filtering documents"
    # o['documents'] = main_models.Document.objects.filter(id__in=[d['id'] for d in documents])
    o['related_topics'] = main_models.Topic.objects.filter(id__in=[t['id'] for t in topics])
    note_objects = main_models.Note.objects.in_bulk([n['id'] for n in notes])
    #print len(note_objects)
    #print note_objects
    for note in notes:
        if ('id' in note.keys()) and (note['id'] in note_objects.keys()):
            related_topics = list((topic for topic in note['related_topics']
                                   if topic['url'] != request.path))
            note_objects[note['id']] = (note_objects[note['id']], related_topics,)
    # o['notes'] = note_objects.values()
    


    o['documents']  = []
    o['notes']      = []



    for d in topic.get_related_documents():
        if d.project in request.user.get_affiliated_projects():
            o['documents'].append(d)

    for n in topic.get_related_notes():
        if n.project in request.user.get_affiliated_projects():
            o['notes'].append(n)

    # o['documents']  = topic.get_related_documents()
    # o['notes']      = topic.get_related_notes()


    return render_to_response(
        'entityCendariRead.html', o, context_instance=RequestContext(request))


def transcript(request, project_slug, document_id):
    project_slug = utils.get_project_slug(project_slug)
    transcript = get_object_or_404(Transcript, document_id=document_id)
    return HttpResponse(transcript)

def footnote(request, project_slug, document_id, footnote_id):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    o['footnote'] = get_object_or_404(Footnote, id=footnote_id)
    o['project_slug'] = project_slug
    o['thread'] = { 'id': 'footnote-%s' % o['footnote'].id, 
                    'title': o['footnote'].footnoted_text() }
    return render_to_response(
        'footnote.html', o, context_instance=RequestContext(request))

def rdfa_view_note(request, project_slug, note_id):
    project_slug = utils.get_project_slug(project_slug)
    user = request.user
    if not user.is_authenticated():
        raise PermissionDenied("anonymous access not allowed")
    note = get_object_or_404(main_models.Note, id=note_id)
    project = note.project
    if project.slug!=project_slug:
        raise PermissionDenied("Note %d does not belong to project %s"%(note_id,project_slug))
    if not user.superuser_or_belongs_to(project):
        raise PermissionDenied("not authorized on %s project" % project.slug)
    return HttpResponse(semantic_rdfa(note, note.content),
                        content_type="application/xhtml+xml")
    
def rdfa_view_document(request, project_slug, document_id):
    project_slug = utils.get_project_slug(project_slug)
    user = request.user
    if not user.is_authenticated():
        raise PermissionDenied("anonymous access not allowed")
    document = get_object_or_404(main_models.Document, id=document_id)
    project = document.project
    if project.slug!=project_slug:
        raise PermissionDenied("Document %d does not belong to project %s"%(document_id,project_slug))
    if not user.superuser_or_belongs_to(project):
        raise PermissionDenied("not authorized on %s project" % project.slug)
    return HttpResponse(semantic_rdfa(document, document.description),
                        content_type="application/xhtml+xml")

def rdfa_download_note(request, project_slug, note_id):
    response = rdfa_view_note(request, project_slug, note_id)
    response['Content-Disposition'] = 'attachment; filename="note_%s_%s.xml"'%(project_slug, note_id)
    return response

def rdfa_download_document(request, project_slug, document_id):
    response = rdfa_view_document(request, project_slug, document_id)
    response['Content-Disposition'] = 'attachment; filename="document_%s_%s.xml"'%(project_slug, document_id)
    return response

def image_browse(request,project_slug,document_id):
    project_slug = utils.get_project_slug(project_slug)
    o = {}
    user = request.user


    if not user.is_authenticated():
        raise PermissionDenied("anonymous access not allowed")
    document = get_object_or_404(main_models.Document, id=document_id)
    project = document.project

    print document
    print document.project
    print document.creator
    print project.slug
    print project_slug
    if project.slug!=project_slug:
        raise PermissionDenied("Document %d does not belong to project %s"%(document_id,project_slug))
    if not user.superuser_or_belongs_to(project):
        raise PermissionDenied("not authorized on %s project" % project.slug)

    o['document']       = document
    o['project']        = document.project
    o['object_type']    = 'document'
    o['object_id']      = document_id
    o['topic_type']     = 'NA'
    o['scans']          = o['document'].scans.all()
    o['project_slug']   = document.project.slug
    return render_to_response(
        'image_browser.html', o, context_instance=RequestContext(request))

# @login_required
# def cendari_chat(request, project_slug):
#     return render_to_response('cendari_chat.html',dict(project_slug=project_slug))

@login_required
def autocomplete_search(request):
    term = request.GET.getlist('term')[0]
    schema = request.GET.getlist('term_schema')[0]
    filter_terms = cendari_filter(request.user)
    q = {
        "query": {
            "match": { "title": term.lower() }
        }
    }
    if (schema != 'Thing'):
        filter_terms += [{"term": { "class": "http://schema.org/"+schema }}]

    if len(filter_terms)==1:
        q['filter'] = filter_terms[0]
    elif len(filter_terms)>1:
        q['filter'] = {"bool" : { "must" : filter_terms } }

    q = {'query': {'filtered': q} }
    version = cendari_index.version()
    if version > '1.6':
        q['functions'] = [
            {'filter': { 'term': { 'application': 'nte'}},
             'weight': 10 },
            {'field_value_factor': {
                "field": "pageviews",
                "factor": 0.1,
                "modifier": "log1p",
                "missing": 1 }
            }
        ]
        q['score_mode'] = 'sum'
        q = {'query': { 'function_score': q } }

    q["from"] = 0
    q["size"] = 30
#    q["sort"] = {
#        "pageviews": { "order": "desc", "ignore_unmapped" : True, "missing" : "_last"}
#    }

    results = cendari_index.search(q, doc_type='entity')
    res = json.dumps(results, encoding="utf-8")
    return HttpResponse(res, mimetype='application/json') 

def create_cluster(request,project_slug):
    project_slug = utils.get_project_slug(project_slug)
    if ('action' in request.POST) and (request.POST['action'] == 'create'):
        if 'topic' in request.POST:
            result_query = main_models.Topic.objects.filter(id=request.POST['topic'])
            if result_query.count()>0:
                topic  = result_query.all()[0]
                cluster = rutils.add_topics_to_cluster([topic])
                semantic_process_cluster(cluster)
                return HttpResponse(json.dumps({'id': cluster.id}), content_type="application/json");

@login_required
def show_cluster(request,project_slug,cluster_id):
    project_slug = utils.get_project_slug(project_slug)
    query_result = TopicCluster.objects.filter(id=cluster_id)
    cluster = query_result[0] if query_result.count()!= 0 else None
    
    if request.method == "POST":
        
        
        topics_to_be_removed = []
        topics_to_be_added   = []
        for key in request.POST:
            value = request.POST[key]
            if key == 'message':
                cluster.message = value
            elif 'cluster_topic' in key:
                query_result =main_models.Topic.objects.filter(id=key.split('_')[-1])
                if query_result.count()!= 0:
                    topics_to_be_removed.append(query_result[0])                
            elif 'project_topic' in key:
                query_result =main_models.Topic.objects.filter(id=key.split('_')[-1])
                if query_result.count()!= 0:
                    topics_to_be_added.append(query_result[0])
        
        if len(topics_to_be_removed) >0 :
            rutils.delete_topics_from_cluster(topics_to_be_removed,cluster)
        if len(topics_to_be_added) >0 :
            for topic in topics_to_be_added:
                rutils.add_topic_to_cluster(topic,cluster)
    
        cluster.save()
        semantic_process_cluster(cluster)
        if cluster.topics.count() == 0:
            cluster.delete()

    o ={}
    project = _check_project_privs_or_deny(request.user,project_slug)
    
    o['object_type'] = 'cluster'
    o['cluster'] = cluster
    topics = list()
    if cluster.topics.count()>0:
        for topic in project.topics.filter(topic_node__type = cluster.topics.all()[0].topic_node.type):
            if not topic in o['cluster'].topics.all():
                topics.append(topic)
        o['project_topics'] = topics
    else:
        o['project_topics'] = project.topics.all()
    return render_to_response(
        'clusterShowCendari.html', o, context_instance=RequestContext(request))




def add_project_slug(request,project_id):
    response = {}
    if request.method == 'POST':
        print ':::::::::::::::::::::::::::::::'
        if 'name' in request.POST and 'project_id' in request.POST and request.POST['name'] :
            new_alias = request.POST['name']
            project_id = request.POST['project_id']
            print new_alias
            print project_id
            query_set = Project.objects.filter(id=project_id)
            project = query_set[0] if len(query_set)>0 else  None
            if project != None:
                user = request.user if request.user else project.creator
                if (main_models.Project.objects.filter(slug=new_alias).count() == 0) and (main_models.ProjectSlugAlias.objects.filter(name=new_alias).count() == 0):
                    project.slug_aliases.create(creator=user,name=new_alias)
                    project.save()
                    response['status'] = 'success'
                    response['message'] = 'project alias saved'
                else:
                    response['status'] = 'error'
                    response['message'] = 'alias already exists'
            else:
                response['status'] = 'error'
                response['message'] = 'project wasn\'t found'
        else:
            response['status'] = 'error'
            response['message'] = 'missing information'
    
    print response
    return HttpResponse(json.dumps(response), content_type="application/json");

