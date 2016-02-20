from django import forms
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode

from rdflib import Graph, URIRef, Literal, BNode, exceptions

def update_attrs(attrs, extra_attrs):
    if attrs is None:
        attrs = extra_attrs
    else:
        for k, v in extra_attrs.iteritems():
            if k in attrs and k in ['class', 'style']:
                values = attrs[k].split()
                values.extend(extra_attrs[k].split())
                if k == 'class':
                    attrs[k] = ' '.join(values)
                elif k == 'style':
                    attrs[k] = '; '.join(values)
            else:
                attrs[k] = extra_attrs[k]

class RDFWidget(forms.Textarea):
    def _format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, str) or isinstance(value, unicode):
            return value

    def render(self, name, value, attrs=None):
        update_attrs(attrs, { 'class': 'rdf-textarea' })
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<textarea%s>%s</textarea>' % (
                forms.util.flatatt(final_attrs),
                conditional_escape(force_unicode(self._format_value(value)))))


class RDFField(models.Field):
    description = 'The URI of an RDF graph'
    __metaclass__ = models.SubfieldBase
    def __init__(self, *args, **kwargs):
        super(RDFField, self).__init__(*args, **kwargs)
    def db_type(self, connection):
        return 'text'
    def get_internal_type():
        return "TextField"
    def to_python(self, value):
        return value

    def get_prep_value(self, value):
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)
    def formfield(self, **kwargs):
        defaults = {'widget': RDFWidget}
        defaults.update(kwargs)
        return super(RDFField, self).formfield(**defaults)

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ['^cendari\.fields\.RDFField'])
