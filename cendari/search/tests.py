# -*- coding: utf-8 -*-

import unittest

from pyelasticsearch import ElasticHttpError
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from editorsnotes.api.tests import ClearContentTypesTransactionTestCase
from .index import CendariIndex

class SearchTestCase(unittest.TestCase):
    def test_create_index_no_alias(self):
        index = CendariIndex('test-cendari-index', alias=False)
        es=index.open()
        index.delete()

    def test_create_index_alias(self):
        index = CendariIndex('test-cendari-index', alias=True)
        es=index.open()
        index.delete()

if __name__ == '__main__':
    unittest.main()

