from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View,TemplateView, TemplateResponseMixin # CENDARI: used to be in generic.edit, TemplateView is brand new
from django.views.generic.edit import ModelFormMixin
from rest_framework.renderers import JSONRenderer  #CENDARI: JSONRenderer new
import reversion

from editorsnotes.main.models import Project
from editorsnotes.main.models.auth import RevisionProject

VIEW_ERROR_MSG = 'You do not have permission to view {}.'
CHANGE_ERROR_MSG = 'You do not have permission to change {}.'

###########################################################################
# Note, topic, document admin
###########################################################################

class ProcessInlineFormsetsView(View):
    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formsets = self.collect_formsets()
        return self.render_to_response(self.get_context_data(
            form=form, formsets=formsets))
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formsets = self.collect_formsets()
        for fs in formsets:
            valid = formsets[fs].is_valid()
        if all([form.is_valid()] + map(lambda fs: formsets[fs].is_valid(), formsets)):
            return self.form_valid(form, formsets)
        else:
            return self.form_invalid(form, formsets)

    def collect_formsets(self):
        fs = {}
        if hasattr(self, 'formset_classes'):
            for formset in self.formset_classes:
                prefix = formset.model._meta.module_name

                fs_kwargs = self.get_form_kwargs()
                fs_kwargs.pop('initial', 0)
                fs_kwargs['prefix'] = prefix

                fs[prefix] = formset(**fs_kwargs)
        return fs
    def save_formsets(self, formsets):
        for fs in formsets.values():
            save_method = (
                getattr(self, 'save_%s_formset_form' % fs.prefix, None)
                or self.save_formset_form)
            for form in fs:
                if not form.has_changed() or not form.is_valid():
                    continue
                if form.cleaned_data['DELETE']:
                    if form.instance and form.instance.id:
                        form.instance.delete()
                    continue
                save_method(form)
        return formsets
    def save_formset_form(self, form):
        raise NotImplementedError(
            'Child views must create a default formset saving method.')

# CENDARI : ProjectSpecificMixin is new
class ProjectSpecificMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.project = get_object_or_404(
            Project, slug=kwargs.pop('project_slug'))
        user = self.request.user
        if user and user.is_authenticated():
            can_access = user.is_superuser or user.belongs_to(self.project)
            if not can_access:
                raise PermissionDenied(
                    'You are not a member of {}.'.format(self.project.name))
        return super(ProjectSpecificMixin, self).dispatch(*args, **kwargs)
    def get(self, request, *args, **kwargs):
        self.object = self.get_object(**kwargs)
        self.check_perms()
        return super(ProjectSpecificMixin, self).get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object(**kwargs)
        self.check_perms()
        return super(ProjectSpecificMixin, self).post(request, *args, **kwargs)
    def get_default_perms(self):
        opts = self.model._meta
        add_action = self.object is None or not self.object.id
        perm = opts.get_add_permission() if add_action else opts.get_change_permission()
        return ['{}.{}'.format(opts.app_label, perm)]
    def check_perms(self):
        perms = getattr(self, 'permissions', self.get_default_perms())
        if not self.request.user.has_project_perms(self.project, perms):
            raise PermissionDenied()

    def get_object(self, project, *args, **kwargs):
        raise NotImplementedError(
            'Child views must create get_object method')

# CENDARI : BreadcrumbMixin is new
class BreadcrumbMixin(object):
    def get_context_data(self, **kwargs):
        context = super(BreadcrumbMixin, self).get_context_data(**kwargs)
        context['project'] = self.project
        context['breadcrumb'] = self.get_breadcrumb()
        return context
    def get_breadcrumb(self):
        "Override this method with (label, url) pairs to generate page breadcrumb."
        return ()

class BootstrappedBackboneView(ProjectSpecificMixin, BreadcrumbMixin, TemplateView):
    model = None
    serializer_class = None
    template_name = "backbone_bootstrap.html"
    def get_context_data(self, **kwargs):
        context = super(BootstrappedBackboneView, self).get_context_data(**kwargs)
        assert getattr(self, 'serializer_class'), ("Must define a django-rest"
                                                   "framework serializer as a "
                                                   "serializer class.")
        if self.object:
            serializer_context = { 'request': self.request }
            serializer = self.serializer_class(self.object, context=serializer_context)
            context['bootstrap'] = JSONRenderer().render(serializer.data)
        else:
            context['bootstrap'] = 'null';
        return context

# CENDARI : BaseAdminView has changed. 
# CHANGES: Derived also from ProjectSpecificMixin and BreadcrumbMixin
# CHANGES: change in has_project_field, 
# CHANGES: These are removed: dispatch, get_context_data, get_breadcrumb, get, post, get_default_perms, check_perms, get_object, decorator login required


class BaseAdminView(ProcessInlineFormsetsView, ProjectSpecificMixin, ModelFormMixin, BreadcrumbMixin, TemplateResponseMixin):
    def get_form_kwargs(self):
        kwargs = super(ModelFormMixin, self).get_form_kwargs()
        if hasattr(self, 'object') and self.object:
            kwargs.update({'instance': self.object})
        else:
            has_project_field = all([   #CENDARI : has_project filed changed
                hasattr(self.model, 'project'),
                hasattr(self.model.project, 'field'),
                hasattr(self.model.project.field, 'related'),
                self.model.project.field.related.parent_model == Project
            ])
            if has_project_field:
                # Then create an instance with the project already set
                instance = self.model(project=self.project)
                kwargs.update({ 'instance': instance })

        return kwargs

    def set_additional_object_properties(self, obj, form):
        """
        This must be called for additional object properties which must be set
        but are not edited by the user. A common example is an item's last
        updater or creator. It is called *after* the object instance is already
        cleaned.
        """
        return obj

    def save_object(self, form, formsets):
        obj = form.save(commit=False)
        self.set_additional_object_properties(obj, form)
        action = 'add' if not obj.id else 'change'
        if action == 'add':
            obj.creator = self.request.user
        obj.last_updater = self.request.user
        obj.save()
        return obj, action

    def form_valid(self, form, formsets):
        with reversion.create_revision():
            self.object, action = self.save_object(form, formsets)

            # Set reversion metadata
            reversion.set_user(self.request.user)
            reversion.set_comment('%sed %s.' % (action, self.object._meta.module_name))
            reversion.add_meta(RevisionProject, project=self.project)

            self.save_formsets(formsets)
            form.save_m2m()
        return redirect(self.get_success_url())
    def form_invalid(self, form, formsets):
        return self.render_to_response(
            self.get_context_data(form=form, formsets=formsets))

    def save_topicassignment_formset_form(self, form):
        if not form.cleaned_data['topic_qs']:
            return
        if form.instance and form.instance.id:
            return
        ta = form.save(commit=False)
        ta.topic = form.cleaned_data['topic_qs'].get(project__slug=self.project.slug)
        if ta.topic in self.object.related_topics.all():
            return
        ta.creator = self.request.user
        ta.content_object = self.object
        ta.save()
        return ta
