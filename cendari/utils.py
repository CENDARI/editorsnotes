# -*- coding: utf-8 -*-
import os.path
from datetime import datetime
import re
import unicodedata
from lxml import etree
from pytz import timezone, utc
import urllib
import json

import pdb

import logging


from rest_framework.views import exception_handler

logger = logging.getLogger('cendari.utils')

WELL_KNOWN_DATE_FORMATS=[
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
    "%Y-%m-%d"
]

def parse_well_known_date(str):
    for format in WELL_KNOWN_DATE_FORMATS:
        try:
            return datetime.strptime(str, format)
        except ValueError:
            pass
    return None

def custom_exception_handler(exc):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc)

    # Now add the HTTP status code to the response.
    if response is not None:
        logger.debug('Received exception %s: %s', type(exc), response.status_code)
        response.data['status_code'] = response.status_code
    else:
        logger.debug('Received exception %s', type(exc))
    return response

def update_delete_status(project):
    topics = project.topics.all()
    for topic in topics:
        if len(topic.get_related_documents()) == len(topic.get_related_notes()) == 0:
            topic.deleted = True
            topic.save()
        else:
            topic.deleted = False
            topic.save()
