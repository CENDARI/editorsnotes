from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.signals import user_logged_in

from editorsnotes.main.models import (
    User, Project, ProjectInvitation, ProjectRole)

from cendari_api import *

content_type = ContentType.objects.get_for_model(Project)

if not Permission.objects.filter(content_type=content_type, codename='view_project'):
    obj=Permission.objects.create(content_type=content_type, codename='view_project')
    obj.save()

_permission_add = Permission.objects.get(content_type=content_type, codename='add_project')
_permission_chg = Permission.objects.get(content_type=content_type, codename='change_project')
_permission_del = Permission.objects.get(content_type=content_type, codename='delete_project')
_permission_view = Permission.objects.get(content_type=content_type, codename='view_project')

class CendariUserBackend(RemoteUserBackend):
    def configure_user(self, user):
        print "Configure user "+user.username
        # get data from the data api
        # create a private project for the user
        if not user.has_perm('main.add_project'):
            user.user_permissions.add(_permission_add)
        if not user.has_perm('main.change_project'):
            user.user_permissions.add(_permission_chg)
        if not user.has_perm('main.delete_project'):
            user.user_permissions.add(_permission_del)
        if not user.has_perm('main.view_project'):
            user.user_permissions.add(_permission_view)
        project, created=Project.objects.get_or_create(slug=user.username,
                                              defaults={'name': user.username})
        role = project.roles.get(role='Editor')
        role.users.add(user)
        project.save()
        return user

    def authenticate(self, remote_user):
        print("Received an authenticate with remote_user=%s" % (remote_user ))
        user=super(CendariUserBackend, self).authenticate(remote_user)
        print "Returning user: ", user
        return user

def login_user_synchronize(sender, user, request, **kwargs):
    print "Synchronized called on login for %s" % user
    if 'eppn' not in request.META: 
        print 'No eppn in META'
        return
    eppn = request.META['eppn']
    if 'mail' not in request.META:
        print 'No mail in META'
        return
    mail = request.META['mail']
    if 'cn' not in request.META:
        print 'No cn in META'
        return
    cn = request.META['cn']

    from django.conf import settings
    try:
        data_api_server = settings.CENDARI_DATA_API_SERVER
    except ValueError:
        raise ImproperlyConfigured("CENDARI_DATA_API_SERVER must be configured in the settings file'")
    try:
        api = CendariDataAPI(data_api_server)
        if not api.session(eppn, mail, cn):
            print "Cendari Data API refuses the connection"
            return
    except:
        print 'Cannot contact Cendari Data API'
        return
    dataspaces = api.get_dataspaces()
    dprojects = {}
    for d in dataspaces:
        if d['name'].startsWith('nte_'):
            name=d['name'][4:]
            dprojects[name] = d
            project, created=Project.objects.get_or_create(slug=pname, 
                                                           defaults={'name': pname })
            if created or user.superuser_or_belongs_to(project):
                role = project.roles.get(role='Editor') # TODO get privileges from API
                role.users.add(user)
    for p in user.get_authorized_projects():
        pname = cendari_clean_name(p.name)
        if pname not in dprojects:
            api.create_dataspace(pname,title=p.name)
    
user_logged_in.connect(login_user_synchronize)
