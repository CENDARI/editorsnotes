from django.contrib.auth.middleware import RemoteUserMiddleware

class CendariUserMiddleware(RemoteUserMiddleware):
    from django.conf import settings

    try:
        group_maps = settings.LDAP_GROUP_MAPS
    except ValueError:
        raise ImproperlyConfigured("LDAP_GROUP_MAPS must be configured in the settings file'")

    def process_request(self, request):
        super(CendariUserMiddleware, self).process_request(request)
        try:
            memberof = request.META['isMemberOf']
        except KeyError:
            # not on a Cendari server, no need to continue
            return
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
        
