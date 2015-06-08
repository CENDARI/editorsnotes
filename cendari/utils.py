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

from editorsnotes.main.models.documents import get_or_create_document


logger = logging.getLogger('cendari.utils')

WELL_KNOWN_DATE_FORMATS=[
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
    "%Y-%m-%d",
]

def parse_well_known_date(str):
    for format in WELL_KNOWN_DATE_FORMATS:
        try:
            return datetime.strptime(str, format)
        except ValueError:
            pass
    return None

def change_to_well_known_format(d):
    if d:
    	return d.strftime(WELL_KNOWN_DATE_FORMATS[3])
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

def get_all_active_topics_for_project(project):
    topics = set()

    for note in project.notes.all():
        topics.update(note.get_all_related_topics())
    for document in project.documents.all():
        topics.update(document.get_all_related_topics())

    return list(topics)

def get_image_placeholder_document(user,project):
    description= 'IMAGE PLACEHOLDER DO NOT DELETE !!!!'
    return get_or_create_document(user,project,description)

# From http://www.johndcook.com/blog/python_longitude_latitude/
def distance_on_unit_sphere(lat1, long1, lat2, long2):
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
         
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
         
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
         
    # Compute spherical distance from spherical coordinates.
         
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
     
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
 
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc

def distance_on_earth_in_km(lat1, long1, lat2, long2):
    return distance_on_unit_sphere(lat1, long1, lat2, long2)*6373
