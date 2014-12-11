from django.contrib.auth.decorators import login_required
import reversion
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponseForbidden, HttpResponseRedirect, HttpResponseBadRequest)
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
#from editorsnotes.admin.views.projects import 
from  editorsnotes.admin import forms
from django.contrib import messages
from cendari import utils
#from cendari import forms 
#from  import forms
@login_required
@reversion.create_revision()
def add_project(request):
    o = {}
    user = request.user

    if not (user.is_superuser or utils.is_project_creator(user)):
        return HttpResponseForbidden(
            content='You do not have permission to create a new project.')

    if request.method == 'POST':
        form = forms.ProjectCreationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            project = form.save()
            role = project.roles.get_or_create_by_name('Owner')
            role.users.add(user)
            messages.add_message(
                request, messages.SUCCESS,
                'New project ({}) created.'.format(project.name))
            return HttpResponseRedirect(reverse("admin2:main_project_index"))
        else:
            o['form'] = form
    else: 
        o['form'] = forms.ProjectCreationForm(user=request.user)
    return render_to_response(
        'project_change.html', o, context_instance=RequestContext(request))
  
