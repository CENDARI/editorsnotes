from django.core.management.base import NoArgsCommand, CommandError
from django.db import transaction
from os import path
from editorsnotes.main.models import Note, Document, Transcript, Topic, TopicAssignment
from cendari.semantic import semantic_process_note, semantic_process_topic, semantic_process_document

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        if options['verbosity'] > 0:
            self.stdout.write(self.style.NOTICE('Updating notes:'), ending=' ')
        for note in Note.objects.all():
            if options['verbosity'] > 1:
                self.stdout.write(self.style.NOTICE('%d' % note.id), ending=' ')
            semantic_process_note(note)
        if options['verbosity'] > 0:
            self.stdout.write('\n')
        if options['verbosity'] > 0:
            self.stdout.write(self.style.NOTICE('Updating documents:'), ending=' ')
        for document in Document.objects.all():
            if options['verbosity'] > 1:
                self.stdout.write(self.style.NOTICE('%d' % document.id), ending=' ')
            semantic_process_document(document)
        if options['verbosity'] > 0:
            self.stdout.write('\n')
        if options['verbosity'] > 0:
            self.stdout.write(self.style.NOTICE('Updating topics:'), ending=' ')
        for topic in Topic.objects.all():
            if options['verbosity'] > 1:
                self.stdout.write(self.style.NOTICE('%d' % topic.id), ending=' ')
            semantic_process_topic(topic)
        if options['verbosity'] > 0:
            self.stdout.write('\n')
