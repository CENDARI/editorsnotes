#from django.contrib.auth.models import User, Project
from editorsnotes.main.models import (Project, Scan)
from django.http import (
    HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect)
from django.shortcuts import render_to_response, get_object_or_404
from django.http import (
    HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect)
import editorsnotes.settings
from django.core.urlresolvers import reverse

def check_project_privs(a_view):
    try:
        redirect_url = editorsnotes.settings.CENDARI_NO_PRIVS_REDIRECT
    except:
        redirect_url = '/accounts/login/'
    def _wrapped_view(request, *args, **kwargs):
        project_slug = None
        if 'project_slug' in kwargs:
            project_slug = kwargs.get('project_slug')
        user = request.user
        if not user.is_authenticated():
            print "user not auth!!"
            return HttpResponseForbidden()
        if project_slug is None:
            projects = user.get_authorized_projects()
            if not projects:
                print "project list empty!!"
                return HttpResponseRedirect(redirect_url)
            project = projects[0]
        else:
            project = get_object_or_404(Project, slug=project_slug)
        if not user.superuser_or_belongs_to(project):
            print "not superuser_or_belongs_to"
            return HttpResponseRedirect(redirect_url)
        return a_view(request, *args, **kwargs)
        
    return _wrapped_view
