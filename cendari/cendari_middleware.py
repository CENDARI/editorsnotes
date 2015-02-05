from django.contrib.auth.middleware import RemoteUserMiddleware
from django.conf import settings

class CendariUserMiddleware(RemoteUserMiddleware):
    def process_request(self, request):
        user = request.user
        print 'Cendari Middelware called with user %s' % user
        super(CendariUserMiddleware, self).process_request(request)
        try:

            memberof = request.META['isMemberOf']
            print 'On a Cendari server'
            group_maps = settings.LDAP_GROUP_MAPS
            groups=memberof.split(';')
            is_admin = False
            is_editor = False
            for group in groups:
                if group in group_maps['admin_groups']:
                    is_admin = True
                    print "User is admin"
                    break
                elif group in group_maps['editor_groups']:
                    print "User is editor"
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
        except ValueError:
            raise ImproperlyConfigured("LDAP_GROUP_MAPS must be configured in the settings file'")
