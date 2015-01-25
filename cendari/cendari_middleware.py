from django.contrib.auth import RemoteUserMiddleware

class CendariUserMiddleware(RemoteUserMiddleware):
    def process_request(self, request):
        (CendariUserMiddleware, self).process_request(self, request)
        try:
            memberof = request.META['isMemberOf']
        except KeyError:
            # not on a Cendari server
            return
        
