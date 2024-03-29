from django import forms
from django.contrib.auth.models import Group
from django.forms.models import (
    BaseModelFormSet, ModelForm, modelformset_factory, ValidationError)

from editorsnotes.main.management import get_all_project_permissions
from editorsnotes.main.models import (
    User, Project, ProjectInvitation, ProjectRole)

class ProjectRoleField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.role.title()

def make_project_invitation_formset(project):
    """
    Create a project invitation formset for a project

    Cannot be done by a simple modelformset_factory because we need to create
    the Form and FormSet on the fly to take into account existing project
    invitations.
    """

    if not isinstance(project, Project):
        raise ValueError('{} is not a project.'.format(project))

    project_invitations = ProjectInvitation.objects\
            .select_related('user', 'role')\
            .filter(project_id=project.id)

    class ProjectInvitationFormSet(BaseModelFormSet):
        def __init__(self, *args, **kwargs):
            kwargs['queryset'] = project_invitations
            super(ProjectInvitationFormSet, self).__init__(*args, **kwargs)

    class ProjectInvitationForm(ModelForm):
        project_role = ProjectRoleField(queryset=project.roles.all())
        class Meta:
            model = ProjectInvitation
            fields = ('email', 'project_role',)
        def __init__(self, *args, **kwargs):
            super(ProjectInvitationForm, self).__init__(*args, **kwargs)
            self.fields['email'].widget.attrs['placeholder'] = 'Email to invite'
        def clean_email(self):
            "Make sure email is unique for this project"
            data = self.cleaned_data['email']
            user = User.objects.filter(email=data)

            # Check if there are multiple users with this email address. If
            # there are, fail. In practice, there's no way this should actually
            # happen.
            if user.count() > 1:
                msg = 'Multiple users with this email address.'
                raise forms.ValidationError(msg)

            # Next, check if there is a user with this email already in the
            # project, and raise an error if there is.
            elif user.count() == 1 and project in user.get().get_affiliated_projects():
                msg = 'User with email {} already in project.'.format(data)
                raise forms.ValidationError(msg)

            # Next, check if there's already an invitation for this email
            # address.
            # TODO: Really, this should be a unique constraint on the model.
            existing_invite = ProjectInvitation.objects.filter(
                email=data, project_id=project.id)
            if not self.instance.id and existing_invite.count():
                msg = 'User with email {} already invited.'.format(data)
                raise forms.ValidationError(msg)

            return data

    return modelformset_factory(
        ProjectInvitation,
        formset=ProjectInvitationFormSet,
        form=ProjectInvitationForm,
        can_delete=True,
        extra=1
    )

def make_project_roster_formset(project):
    """
    Returns a formset for editing project members' roles.
    """
    if not isinstance(project, Project):
        raise ValueError('{} is not a project.'.format(project))

    project_roster = project.members.order_by('-last_login')

    class ProjectRosterFormSet(BaseModelFormSet):
        def __init__(self, *args, **kwargs):
            kwargs['queryset'] = project_roster
            super(ProjectRosterFormSet, self).__init__(*args, **kwargs)

    class ProjectMemberForm(ModelForm):
        project_role = ProjectRoleField(queryset=project.roles.all())
        class Meta:
            model = User
        def __init__(self, *args, **kwargs):
            super(ProjectMemberForm, self).__init__(*args, **kwargs)
            if not self.instance.pk:
                return
            self.initial['project_role'] = project.get_role_for(self.instance)
        def save(self, commit=True):
            user = self.instance
            existing_role = project.get_role_for(user)
            if existing_role != self.cleaned_data['project_role']:
                old_role = user.groups.get(name__startswith='{}_'.format(
                    project.slug))
                new_role = Group.objects.get(name__startswith='{}_{}'.format(
                    project.slug, self.cleaned_data['project_role']))
                user.groups.remove(old_role)
                user.groups.add(new_role)
            user.save()
            return user

    return modelformset_factory(
        User,
        formset=ProjectRosterFormSet,
        form=ProjectMemberForm,
        fields=(),
        extra=0
    )

def make_project_permissions_formset(project):
    roles = project.roles.all()
    project_perms= get_all_project_permissions().order_by('content_type')

    class ProjectRoleFormSet(BaseModelFormSet):
        def __init__(self, *args, **kwargs):
            kwargs['queryset'] = roles
            super(ProjectRoleFormSet, self).__init__(*args, **kwargs)

    class ProjectRoleForm(ModelForm):
        permissions = forms.ModelMultipleChoiceField(
            required=False,
            queryset=project_perms,
            widget=forms.CheckboxSelectMultiple)
        class Meta:
            model = ProjectRole
            fields = ('role', 'permissions',)
        def __init__(self, *args, **kwargs):
            super(ProjectRoleForm, self).__init__(*args, **kwargs)
            if self.instance and self.instance.is_super_role:
                self.fields['permissions'].widget.attrs['readonly'] = True
                self.fields['permissions'].widget.attrs['checked'] = True
            elif self.instance and self.instance.id:
                self.fields['permissions'].initial = self.instance.group.permissions.all()
        def save(self, *args, **kwargs):
            # We are NOT committing the change here, because we only save the
            # form if the object already exists. This is because it was
            # difficult to deal with the M2M relations (permissions => the new
            # group which is created along with the project role) when doing
            # that. We are calling save, however, to bound this form to an
            # instance if it exists, so that we can proceed in the right way
            # afterwards (create a ProjectRole manually if no existing instance;
            # save form otherwise).
            kwargs['commit'] = False
            obj = super(ProjectRoleForm, self).save(*args, **kwargs)

            perms = self.cleaned_data['permissions']
            if not obj.id:
                new_role = ProjectRole.objects.create_project_role(
                    project, self.cleaned_data['role'])
                new_role.group.permissions.add(*perms)
            else:
                obj.save()
                obj.group.permissions.clear()
                obj.group.permissions.add(*perms)
            return obj

    formset = modelformset_factory(ProjectRole,
                                   formset=ProjectRoleFormSet,
                                   form=ProjectRoleForm,
                                   can_delete=True,
                                   extra=1)
    formset.all_perms = project_perms
    return formset


BANNED_PROJECT_SLUGS = (
    'add',
)
# Cendari code E.G. aviz
class ProjectForm(ModelForm):
    editors = forms.MultipleChoiceField( widget=forms.CheckboxSelectMultiple,
                                          choices=[],required=False)
    class Meta:
        model = Project
        fields = ('name',  'image', 'description', 'default_license','editors','is_public',)
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        project = self.instance
        owners = [user for  role in project.roles.filter(role='Owner') for user in role.group.user_set.all()]
        users = [(u.username, "{} {}".format(u.first_name,u.last_name) if u.last_name else u.username) for u in User.objects.all() if u not in owners]
        self.fields["editors"].choices = [u for u in users if u not in owners]
        current_members = [u.username for u in project.members if  u not in owners]
        self.fields["editors"].initial =  current_members
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['name'].widget.attrs['readonly'] = True
    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)

        owners = [user for  role in project.roles.filter(role='Owner') for user in role.group.user_set.all()]

        previous_members = [u.username for u in project.members]
        current_members = self.cleaned_data["editors"]
        to_remove = [e for e in previous_members if e not in current_members]
        to_add = [e for e in current_members if e not in previous_members]
        role = project.roles.get(role='Editor')
        for user in User.objects.filter(username__in=to_add):
            role.users.add(user)
        for user in User.objects.filter(username__in=to_remove):
            if not user in owners:
                role.users.remove(user)
        project.save()
        return project
# Cendari code E.G. aviz
# class ProjectCreationForm(ModelForm):
#     editors = forms.MultipleChoiceField( widget=forms.CheckboxSelectMultiple,
#                                           choices=[])
#     class Meta:
#         model = Project
#         fields = ('name', 'slug', 'image', 'description', 'default_license','editors')
#     def __init__(self, *args, **kwargs):
#         user = kwargs['user']
#         del kwargs['user']
#         super(ProjectCreationForm, self).__init__(*args, **kwargs)
#         self.user = user
#         project = self.instance
#         owners = [user for  role in project.roles.filter(role='Owner') for user in role.group.user_set.all()]
#         users = [(u.username, "{} {}".format(u.first_name,u.last_name) if u.last_name else u.username) for u in User.objects.all() if u not in owners]
#         self.fields["editors"].choices = [u for u in users if u not in owners]
#         current_members = [u.username for u in project.members if  u not in owners]
#         self.fields["editors"].initial =  current_members
#     def save(self, commit=True):
#         project = super(ProjectCreationForm, self).save()

#         owners = [user for  role in project.roles.filter(role='Owner') for user in role.group.user_set.all()]

#         owners = [user for  role in project.roles.filter(role='Owner') for user in role.group.user_set.all()]
#         previous_members = [u.username for u in project.members if u not in owners ]
#         current_members = self.cleaned_data["editors"]
#         to_remove = [e for e in previous_members if e not in current_members]
#         to_add = [e for e in current_members if e not in previous_members]
#         role = project.roles.get(role='Editor')
#         for user in User.objects.filter(username__in=to_add):
#             role.users.add(user)
#         for user in User.objects.filter(username__in=to_remove):
#             if not user in owners:
#                 role.users.remove(user)
#         return project


class ProjectCreationForm(ModelForm):
    """
    Form for creating a project. Must be passed a user.
    """
    join_project = forms.BooleanField(initial=True,
                                      help_text='Join project after creation?')
    class Meta:
        model = Project
        fields = ('name', 'slug', 'image', 'description', 'default_license', 'join_project',)
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ProjectCreationForm, self).__init__(*args, **kwargs)
        self.user = user
    def clean_slug(self):
        data = self.cleaned_data['slug']
        if data in BANNED_PROJECT_SLUGS:
            raise ValidationError('This slug is a reserved word.')
        return data
    def save(self, *args, **kwargs):
        obj = super(ProjectCreationForm, self).save()
        if self.cleaned_data['join_project']:
            role = obj.roles.get(role='Editor')
            role.users.add(self.user)
        return obj


# original
# class ProjectForm(ModelForm):
#     class Meta:
#         model = Project
#         exclude = ('slug',)

# class ProjectCreationForm(ModelForm):
#     """
#     Form for creating a project. Must be passed a user.
#     """
#     join_project = forms.BooleanField(initial=True,
#                                       help_text='Join project after creation?')
#     class Meta:
#         model = Project
#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user')
#         super(ProjectCreationForm, self).__init__(*args, **kwargs)
#         self.user = user
#     def clean_slug(self):
#         data = self.cleaned_data['slug']
#         if data in BANNED_PROJECT_SLUGS:
#             raise ValidationError('This slug is a reserved word.')
#         return data
#     def save(self, *args, **kwargs):
#         obj = super(ProjectCreationForm, self).save()
#         if self.cleaned_data['join_project']:
#             role = obj.roles.get(role='Editor')
#             role.users.add(self.user)
#         return obj



