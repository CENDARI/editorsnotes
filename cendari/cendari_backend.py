from django.contrib.auth.backends import RemoteUserBackend

class CendariUserBackend(RemoteUserBackend):
    """
    This backend is used to create users from the Cendari environment
    """
    
    def configure_user(self, user):
        # get data from the data api
        # create a private project for the user
        return user
