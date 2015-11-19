# -*- coding: utf-8 -*-

from collections import Counter

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import receiver

import reversion
from licensing.models import License

from .. import fields
from ..management import get_all_project_permissions
from base import URLAccessible, CreationMetadata

# Cendari code E.G. aviz
from django.core.urlresolvers import reverse

__all__ = ['User', 'UserFeedback', 'Project', 'ProjectRole', 'ProjectInvitation', 'FeaturedItem','ProjectSlugAlias']


# CENDARI : UserFeedback  and PURPOSE_CHOICES are  added

class User(AbstractUser, URLAccessible):
    zotero_key = models.CharField(max_length='24', blank=True, null=True)
    # Cendari code E.G. aviz
    zotero_uid = models.CharField(max_length='10', blank=True, null=True)
    class Meta:
        app_label = 'main'
    def _get_display_name(self):
        "Returns the full name if available, or the username if not."
        display_name = self.username
        if self.first_name:
            display_name = self.first_name
            if self.last_name:
                display_name = '%s %s' % (self.first_name, self.last_name)
        return display_name
    display_name = property(_get_display_name)
    @models.permalink
    def get_absolute_url(self):
        return ('user_view', [str(self.username)])
    def as_text(self):
        return self.display_name
    def belongs_to(self, project):
        return project.get_role_for(self) is not None
    def get_affiliated_projects(self):
        return Project.objects.filter(roles__group__user=self).distinct('slug')
    def get_affiliated_projects_with_roles(self):
        roles = ProjectRole.objects.filter(group__user=self)
        return [(role.project, role) for role in roles]
    def _get_project_role(self, project):
        role_attr = '_{}_role_cache'
        if not hasattr(self, role_attr):
            setattr(self, role_attr, project.get_role_for(self))
        return getattr(self, role_attr)
    def _get_project_permissions(self, project):
        """
        Get all of a user's permissions within a project.

        I thought about implementing this in an authentication backend, where a
        perm would be `{projectslug}-{app}.{perm}` instead of the typical
        `{app}.{perm}`, but this is more explicit. If we ever decide to roll
        this UserProfile into a custom User model, it would make sense to move
        this method to a custom backend.
        """
        role = self._get_project_role(project)
        if self.is_superuser or (role is not None and role.is_super_role):
            perm_list = get_all_project_permissions()
        elif role is None:
            perm_list = []
        else:
            perm_list = role.get_permissions()
        return set(['{}.{}'.format(perm.content_type.app_label, perm.codename)
                    for perm in perm_list])
    def get_project_permissions(self, project):
        perms_attr = '_{}_permissions_cache'.format(project.slug)
        if not hasattr(self, perms_attr):
            setattr(self, perms_attr, self._get_project_permissions(project))
        return getattr(self, perms_attr)
    def has_project_perm(self, project, perm):
        """
        Returns whether a user has a permission within a project.

        Perm argument should be a string consistent with how Django handles
        permissions in its admin: `{app_label}.{permission.codename}`
        """
        if self.is_superuser:
            return True
        return perm in self.get_project_permissions(project)
    def has_project_perms(self, project, perm_list):
        return all(self.has_project_perm(project, p) for p in perm_list)
    @staticmethod
    def get_activity_for(user, max_count=50):
        return activity_for(user, max_count=50)

    # Cendari code E.G. aviz
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

    def _has_project_perms(user):
        return 

    def is_project_creator(self):
        return is_staff and \
          self.has_perm('main.add_project') and \
          self.has_perm('main.change_project') and \
          self.has_perm('main.delete_project') and \
          self.has_perm('main.view_project')


PURPOSE_CHOICES = (
    (1, 'Feedback'),
    (2, 'Bug report'),
    (9, 'Other')
)

class UserFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    purpose = models.IntegerField(choices=PURPOSE_CHOICES)
    message = models.TextField()
    class Meta:
        app_label = 'main'


class UpdatersMixin(object):
    """
    Mixin with method for determining all updaters of a model.
    """
    def get_all_updaters(self):
        ct = ContentType.objects.get_for_model(self.__class__)
        qs = reversion.models.Revision.objects\
                .select_related('user', 'version')\
                .filter(version__content_type_id=ct.id,
                        version__object_id_int=self.id)
        user_counter = Counter([revision.user for revision in qs])
        return [user for user, count in user_counter.most_common()]

class ProjectPermissionsMixin(object):
    """
    A mixin for objects which are meant to have an affiliated project.

    If a model inherits from this class, project-specific permissions will
    automatically be handled for it. This includes Django's default permissions
    (add, change, delete), as well as any custom permissions.

    Inheriting models must implement a get_affiliation method that returns
    objects' affiliated project.
    """
    def get_affiliation(self):
        raise NotImplementedError(
            'Must define get_affiliation method which returns the project for this model.')


class ProjectManager(models.Manager):
    def for_user(self, user):
        return self.select_related('roles__group__user')\
                .filter(roles__group__user=user)

class Project(models.Model, URLAccessible, ProjectPermissionsMixin):
    name = models.CharField(max_length='80')
    slug = models.SlugField(help_text='Used for project-specific URLs and groups', unique=True)
    image = models.ImageField(upload_to='project_images', blank=True, null=True)
    description = fields.XHTMLField(blank=True, null=True)
    default_license = models.ForeignKey(License, default=1)
    is_public = models.BooleanField(default=False)
    objects = ProjectManager()
    class Meta:
        app_label = 'main'
        permissions = (
            (u'view_project_roster', u'Can view project roster.'),
            (u'change_project_roster', u'Can edit project roster.'),
        )
    @models.permalink
    def get_absolute_url(self):
        return ('project_view', [self.slug])
    def get_affiliation(self):
        return self
    def as_text(self):
        return self.name
    def has_description(self):
        return self.description is not None
    @property
    def members(self):
        role_groups = self.roles.values_list('group_id', flat=True)
        return User.objects.filter(groups__in=role_groups)
    def members_by_role(self):
        roles = ProjectRole.objects.for_project(self).select_related('user')
        return
    def get_role_for(self, user):
        qs = self.roles.filter(group__user=user)
        return qs.get() if qs.exists() else None
    @staticmethod
    def get_activity_for(project, max_count=50):
        return activity_for(project, max_count=max_count)

    # Cendari code E.G. aviz
    def get_absolute_url(self):
        return reverse('project_view', None, [self.id])
    # fix a bug present in editorsnotes to be removed when editorsnotes is fixed
    def get_role_for(self, user):
        qs = self.roles.filter(group__user=user,role='Editor')
        return qs.get() if qs.exists() else None
    def is_owned_by(self, user):
        qs = self.roles.filter(group__user=user,role='Owner')
        return qs.exists()


class ProjectSlugAlias(CreationMetadata, ProjectPermissionsMixin):
    project = models.ForeignKey(Project, related_name='slug_aliases')
    name = models.CharField(max_length=200)
    class Meta:
        app_label = 'main'
        unique_together = ('id','name')
    def __unicode__(self):
            return self.name

@receiver(models.signals.post_save, sender=Project)
def create_editor_role(sender, instance, created, **kwargs):
    "Creates an editor role after a project has been created."

    # Only create role if this is a newly created project, and it is not being
    # loaded from a fixture (in that case, "raw" is true in kwargs)
    if created and not kwargs.get('raw', False):
        instance.roles.get_or_create_by_name('Editor', is_super_role=True)
    return

##################################
# Supporting models for projects #
##################################
def called_from_project(func):
    """
    Wrapper for ProjectRoleManager methods meant to be called from a project.
    """
    def wrapped(self, *args, **kwargs):
        if not isinstance(getattr(self, 'instance', None), Project):
            raise AttributeError('Method only accessible via a project instance.')
        return func(self, *args, **kwargs)
    return wrapped

class ProjectRoleManager(models.Manager):
    use_for_related_field = True
    def create_project_role(self, project, role, **kwargs):
        """
        Create a project role & related group by the role name.
        """
        group_name = u'{}-{}'.format(project.slug, role)
        role_group = Group.objects.create(name=group_name)
        return self.create(project=project, role=role, group=role_group,
                           **kwargs)
    def for_project(self, project):
        return self.filter(project=project)
    @called_from_project
    def get_or_create_by_name(self, role, **kwargs):
        """
        Get or create a project role by role name. Only callable from Projects.

        kwargs are only used in creating a project; lookup is by role name only.
        """
        project = self.instance
        try:
            role = self.get(project=project, role=role)
        except ProjectRole.DoesNotExist:
            role = self.create_project_role(project, role, **kwargs)
        return role
    @called_from_project
    def clear_for_user(self, user):
        """
        Clear all role assignments for a user. Only callable from Projects.
        """
        project_group_ids = self.values_list('group_id')
        assigned_groups = user.groups.filter(id__in=project_group_ids)
        user.groups.remove(*assigned_groups)
        return
    @called_from_project
    def get_for_user(self, user):
        qs = self.for_project(self.instance)\
                .select_related()\
                .filter(group__user=user)
        return qs.get() if qs.exists() else None

class ProjectRole(models.Model):
    """
    A container for project members for use with project-level permissions.

    Basically an augmented version of django's Group model from contrib.auth,
    but only related to a group via a one-to-one relationship instead of
    replacing the model entirely.

    A "super_role" role will have all permissions possible inside a project.
    Other roles can have permissions assigned through the project group.

    Roles should be typically be created and accessed through project instances,
    e.g. `project.roles.get_or_create_by_name('editor')`
    """
    project = models.ForeignKey(Project, related_name='roles')
    is_super_role = models.BooleanField(default=False)
    role = models.CharField(max_length=40)
    group = models.OneToOneField(Group)
    objects = ProjectRoleManager()
    class Meta:
        app_label = 'main'
        unique_together = ('project', 'role',)
    def __unicode__(self):
        return u'{} - {}'.format(self.project.name, self.role)
    def _get_valid_permissions(self):
        if not hasattr(self, '_valid_permissions_cache'):
            self._valid_permissions_cache = get_all_project_permissions()
        return self._valid_permissions_cache
    def delete(self, *args, **kwargs):
        group = self.group
        ret = super(ProjectRole, self).delete(*args, **kwargs)
        group.delete()
        return ret
    def get_permissions(self):
        if self.is_super_role:
            return self._get_valid_permissions()
        else:
            return set(self.group.permissions.all())
    def add_permissions(self, *perms):
        for perm in perms:
            if perm not in self._get_valid_permissions():
                raise ValueError(
                    '{} is not a valid project-specific permission.'.format(perm))
            self.group.permissions.add(perm)
        return
    def remove_permissions(self, *perms):
        for perm in perms:
            self.group.permissions.remove(perm)
        return
    def clear_permissions(self):
        self.group.permissions.clear()
        return
    @property
    def users(self):
        return self.group.user_set

class ProjectInvitation(CreationMetadata):
    class Meta:
        app_label = 'main'
    project = models.ForeignKey(Project)
    email = models.EmailField()
    project_role = models.ForeignKey(ProjectRole)
    def __unicode__(self):
        return '{} ({})'.format(self.email, self.project.name)

class FeaturedItem(CreationMetadata, ProjectPermissionsMixin):
    class Meta:
        app_label = 'main'
    project = models.ForeignKey(Project)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    def __unicode__(self):
        return u'(%s)-- %s' % (self.project.slug, self.content_object.__repr__())
    def get_affiliation(self):
        return self.project

class RevisionProject(models.Model):
    revision = models.OneToOneField(reversion.models.Revision,
                                    related_name='project_metadata')
    project = models.ForeignKey(Project)
    # If a project is deleted, so is this. Should this be changed? Should we not
    # allow projects to be deleted?
    class Meta:
        app_label = 'main'

def activity_for(model, max_count=50):
    u'''
    Return recent activity for a user or project.
    '''
    if isinstance(model, User):
        user_ids = [model.id]
    elif isinstance(model, Project):
        user_ids = [u.id for u in model.members.all()]
    else:
        raise TypeError(
            'Argument must either be an instance of a User or a Project')

    activity = []
    checked_object_ids = {
        'topic': [],
        'note': [],
        'document': [],
        'transcript': []
    }

    for entry in reversion.models.Version.objects\
            .select_related('content_type__name', 'revision')\
            .order_by('-revision__date_created')\
            .filter(content_type__app_label='main',
                    content_type__model__in=checked_object_ids.keys(),
                    revision__user_id__in=user_ids):
        if entry.object_id in checked_object_ids[entry.content_type.name]:
            continue
        checked_object_ids[entry.content_type.name].append(entry.object_id)
        if entry.type == reversion.models.VERSION_DELETE:
            continue
        obj = entry.object
        if obj is None:
            continue
        activity.append({
            'what': obj,
            'when': entry.revision.date_created
        })
        if len(activity) == max_count:
            break
    return activity, checked_object_ids
