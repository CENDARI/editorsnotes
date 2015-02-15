from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from editorsnotes.main.models import Project

import sys

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

