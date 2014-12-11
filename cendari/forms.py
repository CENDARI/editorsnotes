from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class ImportFromJigsawForm(forms.Form):
    file = forms.FileField(label='Select a Jigsaw file')
    topics = forms.CharField(max_length=100,required=False)

    def _clean(self):
        super(ImportFromJigsawForm, self).clean()
        upload_to = 'jigsaw'
        if not 'filename' in self.cleaned_data:
            return self.cleaned_data
        upload_to += self.cleaned_data['file'].name
        print "Finishing cleaning jigsaw with path %s" % upload_to

from django.utils.translation import ugettext, ugettext_lazy as _
import django.contrib.auth.forms
from django.forms.models import (
    BaseModelFormSet, ModelForm, modelformset_factory, ValidationError)
from editorsnotes.main.models import (
    User, Project, ProjectInvitation, ProjectRole)
from editorsnotes.settings import AUTHENTICATION_BACKENDS

import cendari.utils

has_remote_auth  = 'django.contrib.auth.backends.RemoteUserBackend' in AUTHENTICATION_BACKENDS


content_type = ContentType.objects.get_for_model(Project)

if not Permission.objects.filter(content_type=content_type, codename='view_project'):
    obj=Permission.objects.create(content_type=content_type, codename='view_project')
    obj.save()

_permission_add = Permission.objects.get(content_type=content_type, codename='add_project')
_permission_chg = Permission.objects.get(content_type=content_type, codename='change_project')
_permission_del = Permission.objects.get(content_type=content_type, codename='delete_project')
_permission_view = Permission.objects.get(content_type=content_type, codename='view_project')

def _add_project_perms(user):
    if not user.has_perm('main.add_project'):
        user.user_permissions.add(_permission_add)
    if not user.has_perm('main.change_project'):
        user.user_permissions.add(_permission_chg)
    if not user.has_perm('main.delete_project'):
        user.user_permissions.add(_permission_del)
    if not user.has_perm('main.view_project'):
        user.user_permissions.add(_permission_view)

def _remove_project_perms(user):
    if user.has_perm('main.add_project'):
        user.user_permissions.remove(_permission_add)
    if user.has_perm('main.change_project'):
        user.user_permissions.remove(_permission_chg)
    if user.has_perm('main.delete_project'):
        user.user_permissions.remove(_permission_del)
    if user.has_perm('main.view_project'):
        user.user_permissions.remove(_permission_view)



class UserCreationForm(ModelForm):
    """
    Form for creating a user
    """
    if not has_remote_auth:
        password1 = forms.CharField(label=_("Password"),
                                    widget=forms.PasswordInput) 
        password2 = forms.CharField(label=_("Password confirmation"),
                                    widget=forms.PasswordInput,
                                    help_text=_("Enter the same password as above, for verification."))
    is_project_creator = forms.BooleanField(required=False, label=_("Can create projects"), help_text="The user (not necessarily superuser) can create/edit projects and manage access privileges on his own projects", widget=forms.CheckboxInput)
    class Meta:
        model = User
        fields = ("username","first_name","last_name","email","groups","is_superuser","is_staff","is_project_creator","is_active")
    def save(self, commit=True):
        user = super(UserCreationForm, self).save()
        if not has_remote_auth:
            user.set_password(self.cleaned_data["password1"])
        if self.cleaned_data["is_project_creator"]:
            user.is_staff = True
            _add_project_perms(user)
        user.save()
        return user


class UserChangeForm(ModelForm):
    username = forms.RegexField(
        label=_("Username"), max_length=30, regex=r"^[\w.@+-]+$",
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    if not has_remote_auth:
        password = django.contrib.auth.forms.ReadOnlyPasswordHashField(
            label=_("Password"),
            help_text=_("Raw passwords are not stored, so there is no way to see "
                        "this user's password, but you can change the password "
                        "using <a href=\"password/\">this form</a>."))
    is_project_creator = forms.BooleanField(
        required=False, 
        label=_("Can create projects"), 
        help_text="The user (not necessarily superuser) can create/edit projects and manage access privileges on his own projects", 
        widget=forms.CheckboxInput)
    class Meta:
        model = User
        if not has_remote_auth:
            fields = ("username","password","first_name","last_name","email","groups","is_superuser","is_staff","is_project_creator","is_active")
        else:
            fields = ("username","first_name","last_name","email","groups","is_superuser","is_staff","is_project_creator","is_active")
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields["is_project_creator"].initial = True if cendari.utils.is_project_creator(self.instance) else False
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
    def save(self, commit=True):
        user = super(UserChangeForm, self).save()
        if self.cleaned_data["is_project_creator"]:
            user.is_staff = True
            _add_project_perms(user)
        else:
            #user.is_staff = False
            _remove_project_perms(user)
        user.save()

        return user



class ProjectCreationForm(ModelForm):
    editors = forms.MultipleChoiceField( widget=forms.CheckboxSelectMultiple,
                                          choices=[])
    class Meta:
        model = Project
        fields = ('name', 'slug', 'image', 'description', 'default_license','editors')
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        del kwargs['user']
        super(ProjectCreationForm, self).__init__(*args, **kwargs)
        project = self.instance
        owners = [user for  role in project.roles.filter(role='Owner') for user in role.group.user_set.all()]
        users = [(u.username, "{} {}".format(u.first_name,u.last_name) if u.last_name else u.username) for u in User.objects.all() if u not in owners]
        self.fields["editors"].choices = [u for u in users if u not in owners]
        current_members = [u.username for u in project.members if  u not in owners]
        self.fields["editors"].initial =  current_members
    def save(self, commit=True):
        project = super(ProjectCreationForm, self).save()
        previous_members = [u.username for u in project.members]
        current_members = self.cleaned_data["editors"]
        to_remove = [e for e in previous_members if e not in current_members]
        to_add = [e for e in current_members if e not in previous_members]
        role = project.roles.get(role='Editor')
        for user in User.objects.filter(username__in=to_add):
            role.users.add(user)
        for user in User.objects.filter(username__in=to_remove):
            role.users.remove(user)

        return project


class ProjectChangeForm(ModelForm):
    editors = forms.MultipleChoiceField( widget=forms.CheckboxSelectMultiple,
                                          choices=[])
    class Meta:
        model = Project
        fields = ('name', 'slug', 'image', 'description', 'default_license','editors')
    def __init__(self, *args, **kwargs):
        super(ProjectChangeForm, self).__init__(*args, **kwargs)
        project = self.instance
        owners = [user for  role in project.roles.filter(role='Owner') for user in role.group.user_set.all()]
        users = [(u.username, "{} {}".format(u.first_name,u.last_name) if u.last_name else u.username) for u in User.objects.all() if u not in owners]
        self.fields["editors"].choices = [u for u in users if u not in owners]
        current_members = [u.username for u in project.members if  u not in owners]
        self.fields["editors"].initial =  current_members
    def save(self, commit=True):
        project = super(ProjectChangeForm, self).save(commit=False)
        previous_members = [u.username for u in project.members]
        current_members = self.cleaned_data["editors"]
        to_remove = [e for e in previous_members if e not in current_members]
        to_add = [e for e in current_members if e not in previous_members]
        role = project.roles.get(role='Editor')
        for user in User.objects.filter(username__in=to_add):
            role.users.add(user)
        for user in User.objects.filter(username__in=to_remove):
            role.users.remove(user)
        return project
