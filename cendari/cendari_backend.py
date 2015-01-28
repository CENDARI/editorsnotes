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
        return user

def login_user_synchronize(sender, user, request, **kwargs):
    print "Synchronized called on login for %s" % user

    try:
        memberof = request.META['isMemberOf']
        print 'On a Cendari server'
        groups=memberof.split(';')
        is_admin = False
        is_editor = False
        for group in groups:
            if group in group_maps['admin_groups']:
                is_admin = True
                break
            elif group in group_maps['editor_groups']:
                is_editor = True
                break

        if is_admin:
            user.is_superuser = True
            user.is_active = True
            user.is_staff = True
        elif is_editor:
            user.is_superuser = False
            user.is_active = True
            user.is_staff = True
        else:
            user.is_superuser = False
            user.is_active = True
            user.is_staff = False
    except KeyError:
        pass

    pname = cendari_clean_name(user.username)
    print "Creating project %s" % pname
    project = Project.objects.filter(slug=pname)
    if len(project) != 0:
        project=project[0]
    else:
        project=Project.objects.create(slug=pname, name=user.username)
        project.save() # default roles are created at save time
    role = project.roles.get(role='Editor')
    role.users.add(user)

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
        if not api.session(eppn=eppn, mail=mail, cn=cn):
            print "Cendari Data API refuses the connection"
            return
    except:
        print 'Cannot contact the Cendari Data API at %s' % data_api_server
        return
    dataspaces = api.get_dataspace()
    dprojects = {}
    for d in dataspaces:
        if d['name'].startswith('nte_'):
            name=d['name'][4:]
            dprojects[name] = d
            project, created=Project.objects.get_or_create(slug=pname, 
                                                           defaults={'name': pname })
            if created or user.superuser_or_belongs_to(project):
                print 'creating local project: %s' % pname
                role = project.roles.get(role='Editor') # TODO get privileges from API
                role.users.add(user)
    for p in user.get_authorized_projects():
        pname = "nte_"+cendari_clean_name(p.name)
        if pname not in dprojects:
            print 'creating remote project: %s' % pname
            api.create_dataspace(pname,title=p.name)
    
user_logged_in.connect(login_user_synchronize)
