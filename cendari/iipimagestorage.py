import os, subprocess

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.core.files.move import file_move_safe
import django_rq


import pdb

def convert_to_pyramid_tiff(path,npath):
    print "Converting %s into %s" % (path, npath)
    # if not subprocess.call(["convert", path, \
    #                         "-define", "tiff:tile-geometry=256x256", \
    #                         "-depth", "8",\
    #                         "-compress", "jpeg", \
    #                         'ptif:'+npath]):
    if not subprocess.call(["vips", "im_vips2tiff", path, \
                                npath+":jpeg:75,tile:256x256,pyramid"]):
        print "Problem converting %s into %s" % (path, npath)
    else:
        print "Converted %s into %s" % (path, npath)
        
q = django_rq.get_queue("default")


class IIPImageStorage(FileSystemStorage):

    def _save(self, name, content):
        """
        If the file is not a tif pyramid file, replace with one.
        """
#        pdb.set_trace()
        name = super(IIPImageStorage, self)._save(name, content)
        root,ext = os.path.splitext(name)
        if not ext.lower() in [".tif", ".tiff", ".png", ".jpg", ".jp2"]:
            return name
        if ext == ".tif":
            #TODO Should check for right format
            #file_move_safe(self.path(name), self.path(root+".tiff"))
            #ext = ".tiff"
            #name = root + ext
            return name
        
        root,ext = os.path.splitext(name)
        nname = root + ".tif"
        job = q.enqueue(convert_to_pyramid_tiff, \
                        self.path(name), self.path(nname))
        
        return root + ".tif"

