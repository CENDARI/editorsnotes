# -*- coding: utf-8 -*-
import os.path
from datetime import datetime, date
import calendar
import time
import re
import math
import unicodedata
from lxml import etree
from pytz import timezone, utc
import urllib
import json

import pdb

import logging

from rest_framework.views import exception_handler

from editorsnotes.main.models.documents import get_or_create_document

import datetime_safe


logger = logging.getLogger('cendari.utils')

WELL_KNOWN_DATE_FORMATS=[
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
    "%Y-%m-%d",
]

def parse_well_known_date(str):
    for format in WELL_KNOWN_DATE_FORMATS:
	dparts = []
        try:
	    #return datetime.strptime(str, format)  # does not work for dates < 1900
	    dparts = get_date_parts(str,format)
	    if len(dparts) == 3:
		    #res = datetime_safe.date(int(dparts[0]), int(dparts[1]), int(dparts[2])).strftime(format) # expecting date(year, month, day)
        	    return datetime_safe.date(int(dparts[0]), int(dparts[1]), int(dparts[2]))
	    else:
		return None
        except ValueError:
            pass
    return None


# gets date parts as list in this order: year, month, day
def get_date_parts(str, format):
	parts = []
 	if format == "%m/%d/%Y":
		res = str.split("/")
		if len(res) == 3:
			parts.append(res[2])
			parts.append(res[0])
			parts.append(res[1])
	elif format == "%Y/%m/%d":
		res = str.split("/")
		if len(res) == 3:
			parts.append(res[0])
			parts.append(res[1])
			parts.append(res[2])
	elif format == "%d.%m.%Y":
		res = str.split(".")
		if len(res) == 3:
			parts.append(res[2])
			parts.append(res[1])
			parts.append(res[0])
	elif format == "%Y-%m-%d":
		res = str.split("-")
		if len(res) == 3:
			parts.append(res[0])
			parts.append(res[1])
			parts.append(res[2])
	return parts


def change_to_well_known_format(d):
    if d:
	dparts = []
	if isinstance(d, datetime):
		d_iso = d.isoformat()
		cut = d_iso.find("T")
		d_str = d_iso[0:cut]
		dparts = get_date_parts(d_str,WELL_KNOWN_DATE_FORMATS[3])
	elif isinstance(d, string):
		dparts = get_date_parts(d,WELL_KNOWN_DATE_FORMATS[3])
	else:
		dparts = None

	if len(dparts) == 3:
		res = datetime_safe.date(int(dparts[0]), int(dparts[1]), int(dparts[2])).strftime(WELL_KNOWN_DATE_FORMATS[3])
		return res
	else:
		return None
    	#return d.strftime(WELL_KNOWN_DATE_FORMATS[3]) 
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

    # for t in project.topics.all():

    #     if len(t.get_related_notes())+ len(t.get_related_documents()) >0:
    #         topics.append(t)

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

GEOHASH_LENGTH = [
    5000, # 1
    1000, # 2
    156,  # 3
    30,   # 4
    5,    # 5
    1     # 6
]

def bounding_box_to_precision(lat1, long1, lat2, long2, max_buckets=70):
#    print "Bounding box is %f,%f %f,%f" % (lat1, long1, lat2, long2)
    dist = distance_on_earth_in_km(lat1, long1, lat2, long2)
#    print "distance_on_earth_in_km=%f" % dist
    dist = dist / math.sqrt(2)
    for i in range(0, len(GEOHASH_LENGTH)):
        if (dist / GEOHASH_LENGTH[i]) > max_buckets:
            break
#    print "precision is %d" % i
    return i

def timestamp2isodate(value):
    if value is None:
        return ''
    t = time.localtime(value/1000.0)
    return '%04d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)

# Timestamp for year 2000
TIMESTAMP_1 = calendar.timegm(datetime(1, 1, 1).timetuple())

def leap_gregorian(year):
    return (year % 4) == 0 and \
      not (((year % 100) == 0) and ((year % 400) != 0))

GREGORIAN_EPOCH = 1721425.5

def gregorian_to_jd(year, month, day):
    adj = 0 if (month <= 2) else (-1 if leap_gregorian(year) else -2)
    return (GREGORIAN_EPOCH - 1) + \
           (365 * (year - 1)) + \
           math.floor((year - 1) / 4) + \
           (-math.floor((year - 1) / 100)) + \
           math.floor((year - 1) / 400) + \
           math.floor((((367 * month) - 362) / 12) + adj + day)

J1970 = 2440587.5 # Julian date at Unix epoch: 1970-01-01

def jd_to_unix(jd):
    utime = (jd - J1970) * (60 * 60 * 24 * 1000);
    return round(utime / 1000)

def isodate2timestamp(iso):
    rem = iso
    time = None
    negative = False
    if iso.startswith('-'):
        rem = iso[1:]
        negative = True
    index = rem.find('T')
    if index:
        date = rem[:index]
        time = rem[index+1]
    else:
        date = rem
    try:
        (year,month,day) = map(int, rem.split('-'))
    except:
        return None

    # (hour, min, sec) = (0, 0, 0)
    # if time:
    #     if time.endswith('Z'):
    #         time = time[:-1]
    #     try:
    #         (hour, min, sec) = map(float, time.split(':'))
    #     except:
    #         pass

    if negative:
        year = -year
    return jd_to_unix(gregorian_to_jd(year, month, day))

SECOND_PER_DAY = 24*60*60
DAY_PER_YEAR = 365.25
SECOND_PER_YEAR = SECOND_PER_DAY*DAY_PER_YEAR

TIME_LENGTH = [
#    round(SECOND_PER_YEAR),
    round(SECOND_PER_YEAR/12), # number of seconds per month
    round(SECOND_PER_YEAR/52), # number of seconds per week
    SECOND_PER_DAY
]

TIME_UNIT = [
#    'y',
    'M', 'w', 'd' ]

def date_range_to_interval(date1, date2, max_buckets=20):
    #pdb.set_trace()
    if date2 < date1:
        (date1, date2) = (date2, date1)
    dist = (date2 - date1) / 1000 # using seconds units
    if dist == 0:
        return '1d'
    # for i in range(0, len(TIME_LENGTH)):
    #     if (dist / TIME_LENGTH[i]) > max_buckets:
    #         if i > 0:
    #             i -= 1
    #         break
    i = 2
    scale = math.floor(dist / (TIME_LENGTH[i] * (max_buckets-1)))
    return "%d%s" % (scale, TIME_UNIT[i])
