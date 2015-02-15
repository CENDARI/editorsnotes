import forms as admin_forms
import subprocess
from parse import search

class ProjectAdminView:
    pass


def scan_to_dict(scan):
    try:
        res = subprocess.check_output(["tiffinfo", scan.image.path]).strip()
        #res = subprocess.check_output(["identify", "-format", "%n", scan.image.path]).strip()
    except subprocess.CalledProcessError:
        return None
    image_width = int(search('Image Width: {:d}', res).fixed[0])
    image_length = int(search('Image Length: {:d}', res).fixed[0])
    tile_width = int(search('Tile Width: {:d}', res).fixed[0])
    tile_length = int(search('Tile Length: {:d}', res).fixed[0])
    return { 'document': scan.document_id,
             'path': scan.image.name,
             'url': scan.image.url,
             'tiles': {"w": tile_width, "h": tile_length},
             'resolutions': res.count('TIFF Directory'),
             'size': { "w": image_width, "h": image_length } }

# def scan_to_dict(scan):
#     try:
#         res = subprocess.check_output(["identify", "-format", "%n", scan.image.path]).strip()
#     except subprocess.CalledProcessError:
#         res = ''
#     return { 'document': scan.document_id,
#              'path': scan.image.name,
#              'url': scan.image.url,
#              'tiles': {"w": 256, "h": 256},
#              'resolutions': res,
#              'size': { "w": scan.image.width, "h": scan.image.height } }

#def api_scan(request, scan_id):
#    scan = get_object_or_404(Scan, id=scan_id)
#    return HttpResponse(json.dumps(scan_to_dict(scan)), mimetype='text/plain')
