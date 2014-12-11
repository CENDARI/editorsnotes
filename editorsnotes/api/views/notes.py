from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
import reversion

from editorsnotes.main.models import Note, NoteSection
from editorsnotes.main.models.auth import RevisionProject

from .base import (BaseListAPIView, BaseDetailView, DeleteConfirmAPIView,
                   ElasticSearchListMixin, ProjectSpecificMixin)
from ..permissions import ProjectSpecificPermissions
from ..serializers.notes import (
    MinimalNoteSerializer, NoteSerializer, _serializer_from_section_type)

__all__ = ['NoteList', 'NoteDetail', 'NoteSectionDetail',
           'NormalizeSectionOrder', 'NoteConfirmDelete']

class NormalizeSectionOrder(ProjectSpecificMixin, APIView):
    parser_classes = (JSONParser,)
    permission_classes = (ProjectSpecificPermissions,)
    permissions = {
        'POST': ('main.change_note',)
    }
    def get_object(self):
        qs = Note.objects\
                .filter(project__id=self.request.project.id,
                        id=self.kwargs.get('note_id'))\
                .select_related('sections')
        return get_object_or_404(qs)
    def post(self, request, *args, **kwargs):
        note = self.get_object()
        self.check_object_permissions(self.request, note)
        step = int(request.GET.get('step', 100))
        note.sections.normalize_ordering_values('ordering', step=step, fill_in_empty=True)

        return Response([
            { 'section_id': _id, 'ordering': ordering }
            for _id, ordering in note.sections.values_list('note_section_id', 'ordering')
        ])

class NoteList(ElasticSearchListMixin, BaseListAPIView):
    model = Note
    serializer_class = MinimalNoteSerializer

class NoteDetail(BaseDetailView):
    model = Note
    serializer_class = NoteSerializer
    #permissions = {
    #    'GET': ('main.view_private_note',),
    #    'HEAD': ('main.view_private_note',),
    #}
    def post(self, request, *args, **kwargs):
        print "POST"
        """Add a new note section"""
        section_type = request.DATA.get('section_type', None)
        if section_type is None:
            raise Exception('need a section type')

        sec_serializer = _serializer_from_section_type(section_type)
        serializer = sec_serializer(
            data=request.DATA, context={
                'request': request,
                'create_revision': True
            })
        if serializer.is_valid():
            serializer.object.note = self.get_object()
            serializer.object.creator = request.user
            serializer.object.last_updater = request.user
            with reversion.create_revision():
                serializer.save()
                reversion.set_user(request.user)
                reversion.add_meta(RevisionProject, project=request.project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

class NoteSectionDetail(BaseDetailView):
    model = NoteSection
    permissions = {
        'GET': ('main.view_private_note',),
        'HEAD': ('main.view_private_note',),
    }
    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        obj = queryset.get()
        self.check_object_permissions(self.request, obj)
        return obj
    def get_queryset(self):
        note_id = self.kwargs.get('note_id')
        section_id = self.kwargs.get('section_id')
        note = Note.objects.get(id=note_id)
        qs = note.sections.all()\
                .select_subclasses()\
                .filter(note_section_id=section_id)
        if qs.count() != 1:
            raise Http404()
        self.model = qs[0].__class__
        return qs
    def get_serializer_class(self):
        section_type = getattr(self.object, 'section_type_label')
        return _serializer_from_section_type(section_type)

class NoteConfirmDelete(DeleteConfirmAPIView):
    model = Note
    permissions = {
        'GET': ('main.delete_note',),
        'HEAD': ('main.delete_note',)
    }
