import sys, os, subprocess

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.core.files.move import file_move_safe
from django.contrib.sessions.backends.db import SessionStore
from django.utils._os import safe_join
from django.conf import settings

from editorsnotes.main.utils import copy_file
#from cendari_middleware import DATA_API_SESSION_KEY

import django_rq

import pdb

q = django_rq.get_queue("default")

class IIPImageStorage(FileSystemStorage):
    def get_tiff_path(self, name):
        root,ext = os.path.splitext(name)
#        if ext == ".tif":
#            root = root + "_"
        return root + ".tif"

    def _save(self, name, content):
        """
        If the file is not a tif pyramid file, replace with one.
        """
#        pdb.set_trace()
        name = super(IIPImageStorage, self)._save(name, content)
        nname = self.get_tiff_path(name)

        self.create_tiff_file(self.path(name), self.path(nname))
        return name

    def file_exists(self, name):
        return os.path.exists(name)

    def create_tiff_file(self, name, nname):
        if self.file_exists(nname):
            return
        # Show a logo until the image is copied
        copy_file(safe_join(settings.STATIC_ROOT, settings.CENDARI_LOGO_TIFF), nname)
        job = q.enqueue(convert_to_pyramid_tiff, name, nname)

def convert_to_pyramid_tiff(path,npath):
    print "Converting %s into %s" % (path, npath)
    if not subprocess.call(["convert", path, \
                            "-define", "tiff:tile-geometry=256x256", \
                            "-compress", "jpeg", \
                            'ptif:'+npath]):
    #if not subprocess.call(["vips", "im_vips2tiff", path, \
    #                            npath+":jpeg:75,tile:256x256,pyramid"]):
    #if not subprocess.call(["vips", "tiffsave", path, npath, \
    #                        "-tile", "--pyramid", "--compression", "deflate", \
    #                        "--tile-width", "256", "--tile-height", "256"]):
        print "Problem converting %s into %s" % (path, npath)
    else:
        print "Converted %s into %s" % (path, npath)
        
            
