import sys, os, subprocess

from django.core.files import locks
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.core.files.move import file_move_safe
from django.contrib.sessions.backends.db import SessionStore
from django.utils._os import safe_join
from django.conf import settings

from cendari_middleware import DATA_API_SESSION_KEY

import django_rq

import pdb

LOGO = 'cendari/img/cendari_logo.tif'

q = django_rq.get_queue("default")


class IIPImageStorage(FileSystemStorage):

    def _save(self, name, content):
        """
        If the file is not a tif pyramid file, replace with one.
        """
#        pdb.set_trace()
        name = super(IIPImageStorage, self)._save(name, content)
        root,ext = os.path.splitext(name)
        if ext == ".tif":
            root = root + "_"
        
        nname = root + ".tif"
        
        copy_file(safe_join(settings.STATIC_ROOT, LOGO), \
                  self.path(nname))
        job = q.enqueue(convert_to_pyramid_tiff, \
                        self.path(name), self.path(nname))
        
        return nname

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
        
def copy_file(old_file_name, new_file_name,chunk_size = 1024*64):
    print "Copying %s->%s" % (old_file_name, new_file_name)
    with open(old_file_name, 'rb') as old_file:
        # now open the new file, not forgetting allow_overwrite
        fd = os.open(new_file_name, os.O_WRONLY | os.O_CREAT | getattr(os, 'O_BINARY', 0))
        try:
            locks.lock(fd, locks.LOCK_EX)
            current_chunk = None
            while current_chunk != b'':
                current_chunk = old_file.read(chunk_size)
                os.write(fd, current_chunk)
        except:
            print "Problem copying: %s" % sys.exc_info()[0]
        finally:
            locks.unlock(fd)
            os.close(fd)
            
