from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.signals import user_logged_in
from django.conf import settings
from editorsnotes.main.models import Project
from django.contrib import auth
from cendari_api import DATA_API_SERVER, cendari_clean_name, CendariDataAPIException, cendari_data_api

import pprint

import logging
logger = logging.getLogger(__name__)
from sys import exc_info

DATA_API_SESSION_KEY = '_cendari_api_key'

ADMIN_GROUP_MAP = settings.LDAP_GROUP_MAPS['admin_groups'].split(';')
CONTRIBUTOR_GROUP_MAP = settings.LDAP_GROUP_MAPS['contributor_groups'].split(';')
USER_GROUP_MAP = settings.LDAP_GROUP_MAPS['user_groups'].split(';')

class CendariUserMiddleware(RemoteUserMiddleware):
    def process_request(self, request):
        if 'REMOTE_USER' in request.META:
            request.META['REMOTE_USER'] = cendari_clean_name(request.META['REMOTE_USER'])
        elif 'REMOTE_USER' in request.session:
            request.META['REMOTE_USER'] = cendari_clean_name(request.session['REMOTE_USER'])
        super(CendariUserMiddleware, self).process_request(request)
        user = request.user
        logger.debug('Cendari Middelware called with user %s', user)
        
        changed = False
        if user.is_authenticated():
            logger.debug('Cendari Middelware user %s is_authenticated', user)
        try:
            memberof = request.META['isMemberOf']
            logger.debug('Received isMemberOf information: %s', memberof)
            group_maps = settings.LDAP_GROUP_MAPS
            groups=memberof.split(';')
            is_admin = False
            is_editor = False
            for group in groups:
                if group in ADMIN_GROUP_MAP:
                    is_admin = True
                    logger.debug("User is admin")
                    break
                elif group in CONTRIBUTOR_GROUP_MAP:
                    logger.debug("User is editor")
                    is_editor = True
            if is_admin:
                if not user.is_superuser:
                    changed = True
                    user.is_superuser = True
                if not user.is_active:
                    changed = True
                    user.is_active = True
                if not user.is_staff:
                    changed = True
                    user.is_staff = True
            elif is_editor:
                if user.is_superuser:
                    changed = True
                    user.is_superuser = False
                if not user.is_active:
                    changed = True
                    user.is_active = True
                if not user.is_staff:
                    changed = True
                    user.is_staff = True
            else:
                if user.is_superuser:
                    changed = True
                    user.is_superuser = False
                if not user.is_active:
                    changed = True
                    user.is_active = True
                if user.is_staff:
                    changed = True
                    user.is_staff = False
        except KeyError:
            logger.debug('No isMemberOf information')
            cendari_data_api.session(anonymous=True)
        except ValueError:
            raise ImproperlyConfigured("LDAP_GROUP_MAPS must be configured in the settings file'")
        if changed:
            logger.debug('Changing user status to %s,%s,%s',
                         ('superuser' if user.is_superuser else 'not superuser'),
                         
                         ('active' if user.is_active else 'not active'),
                         ('staff' if user.is_staff else 'not staff'))
            user.save()


def login_user_synchronize(sender, user, request, **kwargs):
    logger.debug("Synchronized called on login for %s", user)

    pname = cendari_clean_name(user.username)
    project = Project.objects.filter(slug=pname)
    if len(project) != 0:
        logger.info("Project %s already created", pname)
        project=project[0]
    else:
        logger.info("Creating project %s", pname)
        project=Project.objects.create(slug=pname, name=user.username)
        project.save() # default roles are created at save time
    role = project.roles.get(role='Editor')
    role.users.add(user)
    role=project.roles.get_or_create_by_name('Owner', is_super_role=True)
    role.users.add(user)

    if 'eppn' not in request.META: 
        logger.debug('No eppn in META')
        return
    eppn = request.META['eppn']
    if 'mail' not in request.META:
        logger.debug('No mail in META')
        return
    mail = request.META['mail']
    if (';' in mail):
        i = mail.index(';')
        if i > 0:
            mail = mail[0:i]
    if 'cn' not in request.META:
        logger.debug('No cn in META')
        return
    cn = request.META['cn']
    logger.debug('Received Shibboleth data eppn=%s, mail=%s, cn=%s', eppn, mail, cn)

    api = cendari_data_api
    if DATA_API_SESSION_KEY in request.session:
        key = request.session[DATA_API_SESSION_KEY]
        logger.debug('Retrieved key in session: %s', key)
        api.session(key=key)
        return # Only do the dataspace creation when we create the key
    else:
        try:
            logger.debug('Getting key from DATA API')
            if not api.session(eppn=eppn, mail=mail, cn=cn):
                logger.warning("Cendari Data API refuses the connection")
                return
            request.session[DATA_API_SESSION_KEY] = api.key
            logger.debug('Received key from API: %s', api.key)
        except:
            logger.warning('Cannot contact the Cendari Data API at %s', DATA_API_SERVER)
            api.close()
            return
    try:
        api.get_public_dataspaces(force=True)
        dataspaces = api.get_dataspace()
        dprojects = {}
        for d in dataspaces:
            if d['name'].startswith('nte_'):
                name=d['name'][4:]
                dprojects[name] = d
                try:
                    project, created=Project.objects.get_or_create(slug=name, 
                                                                   defaults={'name': name })
                    if created and not user.superuser_or_belongs_to(project):
                        logger.debug('Adding editor role in local project: %s', pname)
                        role = project.roles.get(role='Editor') # TODO get privileges from API
                        role.users.add(user)
                except:
                    logger.error("Unexpected error creating group '%s': %s", name, sys.exc_info()[0])
        logger.info('dataspace with nte projects: %s', dprojects)
        for p in user.get_authorized_projects():
            pname = cendari_clean_name(p.name)
            if pname not in dprojects:
                logger.debug('creating remote project: %s', pname)
                try:
                    api.create_dataspace('nte_'+pname,title=p.name)
                except CendariDataAPIException as e:
                    logger.error('Problem creating project with DATA Api: %s', pname, e)
    except CendariDataAPIException as e:
        logger.error('Problem synchonizing projects with DATA Api: %s', e)
    except:
        logger.error("Unexpected error: %s", exc_info()[0])

user_logged_in.connect(login_user_synchronize)
