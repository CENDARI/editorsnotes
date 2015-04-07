# -*- coding: utf-8 -*-

from pyelasticsearch import ElasticHttpError
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from editorsnotes.api.tests import ClearContentTypesTransactionTestCase
from . import index

class SearchTestCase(ClearContentTypesTransactionTestCase):
    def setUp(self):
        try:
            cendari_index.delete()
        except ElasticHttpNotFoundError:
            pass
        cendari_index.create()

    def test_propagate_entity(self):
        "Doc "
        self.fail('test_propagate_entity raised an exception.')
        pass
    
