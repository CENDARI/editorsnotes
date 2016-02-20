#
# django-admin2 stuff
# 

# class to be registered
from editorsnotes.main.models.auth import Project,User, ProjectRole
from django.contrib.auth.models import Group, Permission
import django.contrib.auth.models
from django.core.exceptions import PermissionDenied

import djadmin2
from cendari.forms import UserCreationForm, UserChangeForm, ProjectChangeForm
from djadmin2.forms import floppify_form

#class ModelListView(djadmin2.views.ModelListView):
#def get_queryset(self):
#    print "myhack"
#    return super(djadmin2.views.ModelListView, self).get_queryset()


#
# ModelListView.get_queryset customized with a monkey patch
#

if not hasattr(djadmin2.views.ModelListView, 'get_queryset_'):
    # keep a reference to the genuine method

    djadmin2.views.ModelListView.get_queryset_ = djadmin2.views.ModelListView.get_queryset

# define the new method as a function (it calls the genuine method)
    def get_queryset(self):
        qset = self.get_queryset_()
        if self.request.user.is_superuser:
            return qset
        if(not qset) or type(qset[0]) != Project:
            return None
        #return Project.objects.filter(pk__in=[p.id for p in self.request.user.get_authorized_projects()])
        return Project.objects.filter(pk__in=[p.id for p in qset if p.is_owned_by(self.request.user)])

    # attach the customized method to the class
    djadmin2.views.ModelListView.get_queryset = get_queryset


#
# ModelEditFormView.forms_valid customized with a monkey patch
#

if not hasattr(djadmin2.views.ModelEditFormView, 'forms_valid_'):
    # keep a reference to the genuine method
    djadmin2.views.ModelEditFormView.forms_valid_ = djadmin2.views.ModelEditFormView.forms_valid

    # define the new method as a function (it calls the genuine method)
    def forms_valid(self, form, inlines):
        print "my forms_valid", self.object, self.request.user
        if self.request.user.is_superuser:
            return self.forms_valid_(form, inlines)
        obj = self.object
        if type(obj) == Project and obj.is_owned_by(self.request.user):
            return self.forms_valid_(form, inlines)
        raise PermissionDenied("not authorized on %s" % str(obj))

    # attach the customized method to the class
    djadmin2.views.ModelEditFormView.forms_valid = forms_valid



#djadmin2.ModelAdmin2.index_view = None #djadmin2.views.AdminView(r'^$', ModelListView, name='index')
# Incorporate the
class UserAdmin2(djadmin2.ModelAdmin2):
    #create_form_class = djadmin2.forms.UserCreationForm
    create_form_class = floppify_form(UserCreationForm)
    update_form_class = floppify_form(UserChangeForm)
    #update_form_class = djadmin2.forms.UserChangeForm
    search_fields = ['last_name','username']
    list_display =  ['username','first_name','last_name','email']
class ProjectAdmin2(djadmin2.ModelAdmin2):
    update_form_class = floppify_form(ProjectChangeForm)
    search_fields = ['name','slug']
    list_display =  ['name']
    def save(self, *args, **kwargs):
        print "my save"
        super(ProjectAdmin2, self).save(*args, **kwargs)
#djadmin2.default.autodiscover()
djadmin2.default.register(Project, ProjectAdmin2)
djadmin2.default.register(ProjectRole)
djadmin2.default.register(User, UserAdmin2)
#djadmin2.default.register(User)
djadmin2.default.register(Group)
djadmin2.default.register(Permission)
#djadmin2.default.register(django.contrib.auth.models.User)
