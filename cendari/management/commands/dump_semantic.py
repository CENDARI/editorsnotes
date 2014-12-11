from django.core.management.base import LabelCommand, CommandError

from cendari.semantic import Semantic

from optparse import make_option
import sys

class Command(LabelCommand):
    arg = 'RDF_filename'
    label = 'RDF filename'
    help = 'Dumps the RDF store.'
    option_list = LabelCommand.option_list + (
        make_option('-f',
                    '--format',
                    action='store',
                    default='n3',
                    type='choice', choices=['nt', 'n3', 'xml', 'turtle', 'prettyy-xml', 'trix'],

                    help='RDF serialization format: nt, n3, xml, turtle, pretty-xml, trix [default: n3]'),
    )

    def handle_label(self, filename, **options):
        Semantic.serialize(destination=filename, format=options['format'])

